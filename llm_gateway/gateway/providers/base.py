from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx

from gateway.api.schemas import DispatchRequest
from gateway.core.types import DispatchResult, ProviderPayload, TokenEstimate
from gateway.storage.models import RouteConfig


class ProviderAdapterError(Exception):
    def __init__(self, message: str, *, status_code: int | None = None, error_code: str | None = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code


class ProviderAdapter(ABC):
    name: str

    @abstractmethod
    def estimate_tokens(self, request: DispatchRequest, route: RouteConfig) -> TokenEstimate:
        raise NotImplementedError

    @abstractmethod
    def build_payload(self, request: DispatchRequest, route: RouteConfig) -> ProviderPayload:
        raise NotImplementedError

    @abstractmethod
    async def invoke(self, payload: dict, route: RouteConfig) -> httpx.Response | dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def parse_response(self, response: httpx.Response | dict[str, Any], route: RouteConfig) -> DispatchResult:
        raise NotImplementedError

    async def refresh_quota(self, route: RouteConfig) -> dict[str, Any] | None:
        return None

    def supports_request(self, request: DispatchRequest, route: RouteConfig) -> bool:
        if request.task_type != 'chat':
            return False
        if request.require_json and not route.supports_json:
            return False
        return True
