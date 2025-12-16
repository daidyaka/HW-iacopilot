import pytest
from src.chatbot.models import ChatMessage, ToolSearchResult
from src.chatbot.console import ChatbotApp


class FakeLLM:
    async def decide_search(self, messages):
        return {"id": "tool_1", "name": "web_search", "arguments": {"query": messages[-1].content, "top_k": 3}}

    async def stream_final_answer(self, messages, tool_call_id=None, tool_result: ToolSearchResult | None = None):
        # Stream a simple deterministic answer
        for chunk in ["Según las fuentes, ", "esto funciona."]:
            yield chunk


@pytest.mark.asyncio
async def test_orchestrator_flow(monkeypatch):
    app = ChatbotApp()
    # Inject fake LLM
    app.llm = FakeLLM()

    # Mock search and scrape to return predictable data
    from src.chatbot import search, scrape

    async def fake_web_search(query: str, top_k: int = 5, client=None):
        from src.chatbot.models import SearchItem
        return [
            SearchItem(title="A", url="https://a.com"),
            SearchItem(title="B", url="https://b.com"),
            SearchItem(title="C", url="https://c.com"),
        ]

    async def fake_scrape_pages(items, on_processed=None, client=None, extractor=None):
        from src.chatbot.models import ScrapedPage
        pages = [ScrapedPage(title=i.title, url=i.url, text=f"Text {i.title}") for i in items]
        if on_processed:
            for i in items:
                on_processed(i.title, str(i.url))
        return pages

    # Patch symbols used inside console module
    monkeypatch.setattr("src.chatbot.console.web_search", fake_web_search)
    monkeypatch.setattr("src.chatbot.console.scrape_pages", fake_scrape_pages)

    await app.handle_question("¿Cómo plantar un árbol de manzanas?")

    # Expect assistant message appended
    msgs = app.memory.messages
    assert any(m.role == "assistant" and "funciona" in m.content for m in msgs)
