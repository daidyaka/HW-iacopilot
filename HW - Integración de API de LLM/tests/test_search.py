import pytest
import respx
import httpx
from src.chatbot.search import web_search, SERPER_ENDPOINT


@respx.mock
@pytest.mark.asyncio
async def test_web_search_parses_top5():
    payload = {
        "organic": [
            {"title": "A", "link": "https://a.com", "snippet": "a"},
            {"title": "B", "link": "https://b.com", "snippet": "b"},
            {"title": "C", "link": "https://c.com", "snippet": "c"},
            {"title": "D", "link": "https://d.com", "snippet": "d"},
            {"title": "E", "link": "https://e.com", "snippet": "e"},
            {"title": "F", "link": "https://f.com", "snippet": "f"},
        ]
    }
    respx.post(SERPER_ENDPOINT).mock(return_value=httpx.Response(200, json=payload))

    results = await web_search("query")
    assert len(results) == 5
    assert results[0].title == "A"
    assert str(results[0].url).startswith("https://a.com")
