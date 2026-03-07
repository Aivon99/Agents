from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from gateway.config.settings import settings
from gateway.core.types import DispatchResult, TokenEstimate
from gateway.storage.models import RequestLog, Reservation, RouteConfig


def apply_success(db: Session, route: RouteConfig, reservation: Reservation, result: DispatchResult, estimate: TokenEstimate, latency_ms: int, payload_log_path: str | None) -> RequestLog:
    route.health_score = min(1.0, route.health_score + 0.02)
    route.last_error_type = None

    if route.quota is not None:
        # Adjust internal estimate if actual is known.
        if route.quota.estimated_available_output_tokens is not None and result.output_tokens is not None:
            delta = reservation.reserved_output_tokens - result.output_tokens
            route.quota.estimated_available_output_tokens += max(0, delta)
        if route.quota.estimated_available_input_tokens is not None and result.input_tokens is not None:
            delta = reservation.reserved_input_tokens - result.input_tokens
            route.quota.estimated_available_input_tokens += max(0, delta)

    log = RequestLog(
        request_id=reservation.request_id,
        provider_name=route.provider_name,
        model_name=route.model_name,
        task_type='chat',
        input_token_estimate=estimate.input_tokens,
        input_tokens_actual=result.input_tokens,
        output_tokens_actual=result.output_tokens,
        success=True,
        http_status=result.http_status,
        latency_ms=latency_ms,
        finish_reason=result.finish_reason,
        payload_log_path=payload_log_path,
    )
    db.add(log)
    db.flush()
    return log


def apply_failure(db: Session, route: RouteConfig, reservation: Reservation, *, status_code: int | None, error_code: str | None, estimate: TokenEstimate) -> RequestLog:
    route.health_score = max(0.0, route.health_score - 0.15)
    route.last_error_type = error_code
    if status_code == 429:
        route.cooldown_until = datetime.utcnow() + timedelta(seconds=settings.short_cooldown_seconds)
    elif status_code and status_code >= 500:
        route.cooldown_until = datetime.utcnow() + timedelta(seconds=settings.short_cooldown_seconds)
    elif status_code in (401, 403):
        route.cooldown_until = datetime.utcnow() + timedelta(seconds=settings.long_cooldown_seconds)

    log = RequestLog(
        request_id=reservation.request_id,
        provider_name=route.provider_name,
        model_name=route.model_name,
        task_type='chat',
        input_token_estimate=estimate.input_tokens,
        success=False,
        http_status=status_code,
        error_code=error_code,
    )
    db.add(log)
    db.flush()
    return log
