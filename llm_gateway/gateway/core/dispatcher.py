from __future__ import annotations

import time

from fastapi import HTTPException
from sqlalchemy.orm import Session

from gateway.api.schemas import DispatchRequest, DispatchResponse, UsageInfo
from gateway.config.settings import settings
from gateway.core.accounting import apply_failure, apply_success
from gateway.core.logging_store import maybe_save_payload_log
from gateway.core.reservation import ReservationError, commit_reservation, release_reservation, reserve_route_budget
from gateway.core.selector import select_candidate_routes
from gateway.providers.base import ProviderAdapterError
from gateway.providers.registry import PROVIDERS


class Dispatcher:
    async def dispatch(self, db: Session, request: DispatchRequest) -> DispatchResponse:
        candidates = select_candidate_routes(db, request)
        if not candidates:
            raise HTTPException(status_code=503, detail='No eligible routes available')

        fallbacks_used = 0
        last_error: str | None = None

        for route in candidates:
            adapter = PROVIDERS.get(route.provider_name)
            if adapter is None or not adapter.supports_request(request, route):
                continue

            try:
                provider_payload = adapter.build_payload(request, route)
            except Exception as exc:
                last_error = f'payload_build_failed:{exc}'
                continue

            try:
                reservation = reserve_route_budget(db, route.id, request.request_id, provider_payload.token_estimate)
                db.commit()
            except ReservationError as exc:
                db.rollback()
                last_error = f'reservation_failed:{exc}'
                continue

            started = time.perf_counter()
            try:
                raw_response = await adapter.invoke(provider_payload.payload, route)
                result = adapter.parse_response(raw_response, route)
                payload_log_path = maybe_save_payload_log(
                    request.request_id,
                    provider_payload.payload,
                    result.raw_response,
                    enabled=(settings.save_debug_payloads or request.save_payloads),
                )
                db.refresh(route)
                db.refresh(reservation)
                commit_reservation(db, reservation)
                latency_ms = int((time.perf_counter() - started) * 1000)
                apply_success(db, route, reservation, result, provider_payload.token_estimate, latency_ms, payload_log_path)
                db.commit()
                return DispatchResponse(
                    request_id=request.request_id,
                    provider=result.provider,
                    model=result.model,
                    output_text=result.output_text,
                    finish_reason=result.finish_reason,
                    usage=UsageInfo(input_tokens=result.input_tokens, output_tokens=result.output_tokens),
                    fallbacks_used=fallbacks_used,
                    payload_log_path=payload_log_path,
                )
            except ProviderAdapterError as exc:
                db.rollback()
                db.refresh(route)
                db.refresh(reservation)
                apply_failure(
                    db,
                    route,
                    reservation,
                    status_code=exc.status_code,
                    error_code=exc.error_code,
                    estimate=provider_payload.token_estimate,
                )
                release_reservation(db, reservation, restore_budget=True)
                db.commit()
                fallbacks_used += 1
                last_error = f'{route.provider_name}:{exc.error_code or exc.status_code or "error"}'
                continue
            except Exception as exc:
                db.rollback()
                db.refresh(route)
                db.refresh(reservation)
                apply_failure(
                    db,
                    route,
                    reservation,
                    status_code=None,
                    error_code='unexpected_error',
                    estimate=provider_payload.token_estimate,
                )
                release_reservation(db, reservation, restore_budget=True)
                db.commit()
                fallbacks_used += 1
                last_error = f'{route.provider_name}:unexpected_error:{exc}'
                continue

        raise HTTPException(status_code=503, detail=f'All routes failed. last_error={last_error}')
