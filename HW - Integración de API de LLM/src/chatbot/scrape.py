from __future__ import annotations

import asyncio
from typing import Callable, Iterable, List
import httpx
import trafilatura
from .models import SearchItem, ScrapedPage


async def _extract_from_html(html: str) -> str | None:
    # trafilatura.extract is synchronous; run in a thread to avoid blocking
    return await asyncio.to_thread(trafilatura.extract, html)


async def scrape_pages(
    items: Iterable[SearchItem],
    *,
    client: httpx.AsyncClient | None = None,
    on_processed: Callable[[str, str], None] | None = None,
    extractor: Callable[[str], str | None] | None = None,
) -> List[ScrapedPage]:
    extractor = extractor or (lambda html: trafilatura.extract(html))
    owns_client = client is None
    client = client or httpx.AsyncClient(timeout=20)

    async def scrape_item(item: SearchItem) -> ScrapedPage | None:
        try:
            resp = await client.get(str(item.url))
            resp.raise_for_status()
            html = resp.text
            text = await asyncio.to_thread(extractor, html)
            if not text:
                return None
            if on_processed:
                on_processed(item.title, str(item.url))
            return ScrapedPage(title=item.title, url=item.url, text=text)
        except Exception:
            return None

    try:
        tasks = [scrape_item(item) for item in items]
        results = await asyncio.gather(*tasks)
        return [r for r in results if r is not None]
    finally:
        if owns_client:
            await client.aclose()
