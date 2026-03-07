from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from gateway.config.settings import settings
from gateway.core.types import TokenEstimate
from gateway.storage.models import QuotaState, Reservation, ReservationStatus, RouteConfig


class ReservationError(Exception):
    pass


def reserve_route_budget(db: Session, route_id: int, request_id: str, estimate: TokenEstimate) -> Reservation:
    route = db.execute(
        select(RouteConfig).where(RouteConfig.id == route_id).with_for_update()
    ).scalar_one()

    quota = route.quota
    if quota is None:
        quota = QuotaState(route_id=route.id, source_of_truth='internal_estimate')
        db.add(quota)
        db.flush()

    if quota.estimated_available_requests is not None and quota.estimated_available_requests <= 0:
        raise ReservationError('No request budget available')
    if quota.estimated_available_input_tokens is not None and quota.estimated_available_input_tokens < estimate.input_tokens:
        raise ReservationError('No input token budget available')
    if quota.estimated_available_output_tokens is not None and quota.estimated_available_output_tokens < estimate.output_tokens:
        raise ReservationError('No output token budget available')

    if quota.estimated_available_requests is not None:
        quota.estimated_available_requests -= 1
    if quota.estimated_available_input_tokens is not None:
        quota.estimated_available_input_tokens -= estimate.input_tokens
    if quota.estimated_available_output_tokens is not None:
        quota.estimated_available_output_tokens -= estimate.output_tokens

    reservation = Reservation(
        request_id=request_id,
        route_id=route.id,
        reserved_input_tokens=estimate.input_tokens,
        reserved_output_tokens=estimate.output_tokens,
        status=ReservationStatus.RESERVED,
        expires_at=datetime.utcnow() + timedelta(seconds=settings.reservation_ttl_seconds),
    )
    db.add(reservation)
    db.flush()
    return reservation


def release_reservation(db: Session, reservation: Reservation, restore_budget: bool = True) -> None:
    route = db.execute(
        select(RouteConfig).where(RouteConfig.id == reservation.route_id).with_for_update()
    ).scalar_one()
    quota = route.quota
    if quota and restore_budget:
        if quota.estimated_available_requests is not None:
            quota.estimated_available_requests += 1
        if quota.estimated_available_input_tokens is not None:
            quota.estimated_available_input_tokens += reservation.reserved_input_tokens
        if quota.estimated_available_output_tokens is not None:
            quota.estimated_available_output_tokens += reservation.reserved_output_tokens
    reservation.status = ReservationStatus.RELEASED
    db.flush()


def commit_reservation(db: Session, reservation: Reservation) -> None:
    reservation.status = ReservationStatus.COMMITTED
    db.flush()
