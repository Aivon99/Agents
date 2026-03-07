from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from gateway.config.settings import settings


def maybe_save_payload_log(request_id: str, payload: dict, response: dict, enabled: bool) -> str | None:
    if not enabled:
        return None
    root = Path(settings.payload_log_dir)
    root.mkdir(parents=True, exist_ok=True)
    day_dir = root / datetime.utcnow().strftime('%Y-%m-%d')
    day_dir.mkdir(parents=True, exist_ok=True)
    path = day_dir / f'{request_id}.json'
    with path.open('w', encoding='utf-8') as f:
        json.dump({'request_payload': payload, 'provider_response': response}, f, ensure_ascii=False, indent=2)
    return str(path)
