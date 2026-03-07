from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from gateway.storage.models import QuotaState, RouteConfig


DEFAULT_ROUTES = [
    {
        'provider_name': 'openrouter',
        'model_name': 'meta-llama/llama-3.3-8b-instruct:free',
        'is_free': True,
        'supports_json': True,
        'priority': 10,
        'quota': {'estimated_available_requests': None, 'estimated_available_input_tokens': None, 'estimated_available_output_tokens': None, 'source_of_truth': 'provider_api'},
    },
    {
        'provider_name': 'gemini',
        'model_name': 'gemini-2.5-flash',
        'is_free': True,
        'supports_json': True,
        'priority': 20,
        'quota': {'estimated_available_requests': None, 'estimated_available_input_tokens': None, 'estimated_available_output_tokens': None, 'source_of_truth': 'internal_estimate'},
    },
    {
        'provider_name': 'cohere',
        'model_name': 'command-a-03-2025',
        'is_free': True,
        'supports_json': True,
        'priority': 30,
        'quota': {'estimated_available_requests': None, 'estimated_available_input_tokens': None, 'estimated_available_output_tokens': None, 'source_of_truth': 'internal_estimate'},
    },
    {
        'provider_name': 'huggingface',
        'model_name': 'openai/gpt-oss-120b:cerebras',
        'is_free': True,
        'supports_json': True,
        'priority': 40,
        'quota': {'estimated_available_requests': None, 'estimated_available_input_tokens': None, 'estimated_available_output_tokens': None, 'source_of_truth': 'internal_estimate'},
    },
]


def seed_routes(db: Session) -> None:
    existing = {(r.provider_name, r.model_name) for r in db.execute(select(RouteConfig)).scalars()}
    for item in DEFAULT_ROUTES:
        key = (item['provider_name'], item['model_name'])
        if key in existing:
            continue
        route = RouteConfig(
            provider_name=item['provider_name'],
            model_name=item['model_name'],
            is_free=item['is_free'],
            supports_chat=True,
            supports_json=item['supports_json'],
            supports_streaming=False,
            enabled=True,
            priority=item['priority'],
            health_score=1.0,
        )
        db.add(route)
        db.flush()
        quota = QuotaState(route_id=route.id, **item['quota'])
        db.add(quota)
    db.commit()
