import pytest
import respx
import httpx
from src.chatbot.models import SearchItem
from src.chatbot.scrape import scrape_pages


@respx.mock
@pytest.mark.asyncio
async def test_scrape_pages_extracts_text_and_reports():
    items = [
        SearchItem(title="A", url="https://a.com"),
        SearchItem(title="B", url="https://b.com"),
    ]

    respx.get("https://a.com").mock(return_value=httpx.Response(200, text="<html><body>A text</body></html>"))
    respx.get("https://b.com").mock(return_value=httpx.Response(200, text="<html><body>B text</body></html>"))

    processed = []

    def fake_extractor(html: str):
        return "EXTRACTED" if "text" in html else None

    pages = await scrape_pages(items, on_processed=lambda t, u: processed.append((t, u)), extractor=fake_extractor)
    assert len(pages) == 2
    assert pages[0].text == "EXTRACTED"
    assert processed and processed[0][0] == "A"
