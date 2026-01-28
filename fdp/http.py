from __future__ import annotations

import httpx

_HTTP_CLIENT = httpx.Client(timeout=30, follow_redirects=True)


def fetch_json(url: str) -> dict:
    response = _HTTP_CLIENT.get(url)
    response.raise_for_status()
    return response.json()
