from __future__ import annotations

from dataclasses import dataclass

from gateway.api.schemas import DispatchRequest


@dataclass(slots=True)
class TokenEstimate:
    input_tokens: int
    output_tokens: int


@dataclass(slots=True)
class DispatchResult:
    provider: str
    model: str
    output_text: str
    finish_reason: str | None
    input_tokens: int | None
    output_tokens: int | None
    http_status: int | None
    raw_response: dict


@dataclass(slots=True)
class RouteCandidate:
    route_id: int
    provider_name: str
    model_name: str
    is_free: bool
    supports_json: bool
    priority: int
    health_score: float


@dataclass(slots=True)
class ProviderPayload:
    payload: dict
    token_estimate: TokenEstimate


ProviderRequest = DispatchRequest
