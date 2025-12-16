from __future__ import annotations

import json
from typing import List
import httpx
from .config import get_settings
from .models import SearchItem

SERPER_ENDPOINT = "https://google.serper.dev/search"


async def web_search(query: str, *, top_k: int = 5, client: httpx.AsyncClient | None = None) -> List[SearchItem]:
    settings = get_settings()
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=20)

    try:
        payload = {"q": query, "num": top_k}
        headers = {"X-API-KEY": settings.serper_api_key, "Content-Type": "application/json"}
        resp = await client.post(SERPER_ENDPOINT, headers=headers, content=json.dumps(payload))
        resp.raise_for_status()
        data = resp.json()
        organic = data.get("organic", [])[:top_k]
        results: List[SearchItem] = []
        for item in organic:
            title = item.get("title") or item.get("titleRaw") or ""
            url = item.get("link") or item.get("url")
            snippet = item.get("snippet") or item.get("snippetRaw")
            if not (title and url):
                continue
            try:
                results.append(SearchItem(title=title, url=url, snippet=snippet))
            except Exception:
                # skip invalid URLs
                continue
        return results
    finally:
        if owns_client:
            await client.aclose()
