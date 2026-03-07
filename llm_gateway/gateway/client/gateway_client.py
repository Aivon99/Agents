from __future__ import annotations

import httpx


class GatewayClient:
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')

    async def dispatch(self, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=120) as client:
            response = await client.post(f'{self.base_url}/v1/dispatch', json=payload)
            response.raise_for_status()
            return response.json()
