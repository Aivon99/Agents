from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from gateway.api.schemas import DispatchRequest
from gateway.config.settings import settings
from gateway.storage.models import RouteConfig


def select_candidate_routes(db: Session, request: DispatchRequest) -> list[RouteConfig]:
    now = datetime.utcnow()
    routes = list(
        db.execute(
            select(RouteConfig)
            .options(joinedload(RouteConfig.quota))
            .where(RouteConfig.enabled.is_(True), RouteConfig.supports_chat.is_(True))
        ).scalars()
    )

    filtered: list[RouteConfig] = []
    for route in routes:
        if route.cooldown_until and route.cooldown_until > now:
            continue
        if request.require_json and not route.supports_json:
            continue
        if not settings.allow_paid_fallback and not route.is_free:
            continue
        filtered.append(route)

    free_routes = [r for r in filtered if r.is_free]
    paid_routes = [r for r in filtered if not r.is_free]

    sort_key = lambda r: (r.priority, -r.health_score, r.provider_name, r.model_name)
    free_routes.sort(key=sort_key)
    paid_routes.sort(key=sort_key)
    return free_routes + paid_routes
