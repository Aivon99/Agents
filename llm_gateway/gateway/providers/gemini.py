from __future__ import annotations

from typing import Any

from google import genai
from google.genai import types

from gateway.api.schemas import DispatchRequest
from gateway.config.settings import settings
from gateway.core.types import DispatchResult, ProviderPayload, TokenEstimate
from gateway.providers.base import ProviderAdapter, ProviderAdapterError
from gateway.storage.models import RouteConfig


class GeminiAdapter(ProviderAdapter):
    name = 'gemini'

    def _client(self) -> genai.Client:
        if not settings.gemini_api_key:
            raise ProviderAdapterError('Missing Gemini API key', error_code='missing_key')
        return genai.Client(api_key=settings.gemini_api_key)

    @staticmethod
    def _messages_to_text(request: DispatchRequest) -> str:
        return '\n'.join(f'{m.role}: {m.content}' for m in request.messages)

    def estimate_tokens(self, request: DispatchRequest, route: RouteConfig) -> TokenEstimate:
        client = self._client()
        text = self._messages_to_text(request)
        counted = client.models.count_tokens(model=route.model_name, contents=text)
        total = getattr(counted, 'total_tokens', None) or 0
        return TokenEstimate(input_tokens=total, output_tokens=request.max_output_tokens or settings.default_max_output_tokens)

    def build_payload(self, request: DispatchRequest, route: RouteConfig) -> ProviderPayload:
        estimate = self.estimate_tokens(request, route)
        payload = {
            'contents': self._messages_to_text(request),
            'config': types.GenerateContentConfig(
                max_output_tokens=request.max_output_tokens or settings.default_max_output_tokens,
                temperature=request.temperature,
                response_mime_type='application/json' if request.require_json else 'text/plain',
            ),
        }
        return ProviderPayload(payload=payload, token_estimate=estimate)

    async def invoke(self, payload: dict, route: RouteConfig) -> dict[str, Any]:
        client = self._client()
        response = client.models.generate_content(
            model=route.model_name,
            contents=payload['contents'],
            config=payload['config'],
        )
        return response.model_dump(mode='json')

    def parse_response(self, response: dict[str, Any], route: RouteConfig) -> DispatchResult:
        candidates = response.get('candidates', [])
        if not candidates:
            raise ProviderAdapterError('Gemini returned no candidates', error_code='empty_response')
        text = response.get('text')
        if text is None:
            text_parts: list[str] = []
            content = candidates[0].get('content', {})
            for part in content.get('parts', []):
                if 'text' in part:
                    text_parts.append(part['text'])
            text = ''.join(text_parts)
        usage = response.get('usage_metadata', {})
        return DispatchResult(
            provider=self.name,
            model=response.get('model_version', route.model_name),
            output_text=text or '',
            finish_reason=candidates[0].get('finish_reason'),
            input_tokens=usage.get('prompt_token_count'),
            output_tokens=usage.get('candidates_token_count'),
            http_status=200,
            raw_response=response,
        )
