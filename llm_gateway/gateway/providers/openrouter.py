from __future__ import annotations

from typing import Any

import httpx

from gateway.api.schemas import DispatchRequest
from gateway.config.settings import settings
from gateway.core.types import DispatchResult, ProviderPayload, TokenEstimate
from gateway.providers.base import ProviderAdapter, ProviderAdapterError
from gateway.storage.models import RouteConfig


class OpenRouterAdapter(ProviderAdapter):
    name = 'openrouter'
    base_url = 'https://openrouter.ai/api/v1'

    def _headers(self) -> dict[str, str]:
        if not settings.openrouter_api_key:
            raise ProviderAdapterError('Missing OpenRouter API key', error_code='missing_key')
        headers = {
            'Authorization': f'Bearer {settings.openrouter_api_key}',
            'Content-Type': 'application/json',
        }
        if settings.openrouter_site_url:
            headers['HTTP-Referer'] = settings.openrouter_site_url
        if settings.openrouter_app_name:
            headers['X-Title'] = settings.openrouter_app_name
        return headers

    def estimate_tokens(self, request: DispatchRequest, route: RouteConfig) -> TokenEstimate:
        text_len = sum(len(m.content) for m in request.messages)
        return TokenEstimate(input_tokens=max(1, text_len // 4), output_tokens=request.max_output_tokens or settings.default_max_output_tokens)

    def build_payload(self, request: DispatchRequest, route: RouteConfig) -> ProviderPayload:
        estimate = self.estimate_tokens(request, route)
        payload: dict[str, Any] = {
            'model': route.model_name,
            'messages': [m.model_dump() for m in request.messages],
            'max_tokens': request.max_output_tokens or settings.default_max_output_tokens,
        }
        if request.temperature is not None:
            payload['temperature'] = request.temperature
        if request.require_json:
            payload['response_format'] = {'type': 'json_object'}
        return ProviderPayload(payload=payload, token_estimate=estimate)

    async def invoke(self, payload: dict, route: RouteConfig) -> httpx.Response:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f'{self.base_url}/chat/completions', headers=self._headers(), json=payload)
        return response

    def parse_response(self, response: httpx.Response, route: RouteConfig) -> DispatchResult:
        if response.status_code >= 400:
            raise ProviderAdapterError('OpenRouter request failed', status_code=response.status_code, error_code='http_error')
        data = response.json()
        choice = data['choices'][0]
        usage = data.get('usage', {})
        return DispatchResult(
            provider=self.name,
            model=data.get('model', route.model_name),
            output_text=choice['message']['content'],
            finish_reason=choice.get('finish_reason'),
            input_tokens=usage.get('prompt_tokens'),
            output_tokens=usage.get('completion_tokens'),
            http_status=response.status_code,
            raw_response=data,
        )

    async def refresh_quota(self, route: RouteConfig) -> dict[str, Any] | None:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f'{self.base_url}/key', headers=self._headers())
        if response.status_code >= 400:
            return None
        return response.json()
