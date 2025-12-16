from __future__ import annotations

import json
from typing import AsyncIterator, Dict, List, Optional
from openai import OpenAI
from .config import get_settings
from .models import ChatMessage, ToolSearchResult


WEB_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "Buscar en Google (via serper.dev) y devolver los 5 enlaces más relevantes.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Consulta del usuario"},
                "top_k": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
}


class LLMAdapter:
    def __init__(self) -> None:
        settings = get_settings()
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.model

    def _convert_messages(self, messages: List[ChatMessage]) -> List[Dict]:
        return [m.model_dump(include={"role", "content", "name", "tool_call_id"}, by_alias=True) for m in messages]

    async def decide_search(self, messages: List[ChatMessage]) -> Optional[Dict]:
        """Return tool call if the model asks to use web_search, else None."""
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=self._convert_messages(messages),
            tools=[WEB_SEARCH_TOOL],
            tool_choice="auto",
            temperature=0.2,
        )
        choice = resp.choices[0]
        tool_calls = getattr(choice.message, "tool_calls", None)
        if tool_calls:
            for tc in tool_calls:
                f = tc.function
                if f and f.name == "web_search":
                    return {"id": tc.id, "name": f.name, "arguments": json.loads(f.arguments or "{}")}
        return None

    async def stream_final_answer(
        self,
        messages: List[ChatMessage],
        tool_call_id: Optional[str] = None,
        tool_result: Optional[ToolSearchResult] = None,
    ) -> AsyncIterator[str]:
        send_messages = list(messages)
        if tool_call_id and tool_result:
            payload = tool_result.model_dump_json()
            send_messages.append(ChatMessage(role="tool", content=payload, tool_call_id=tool_call_id))

        stream = self.client.chat.completions.create(
            model=self.model,
            messages=self._convert_messages(send_messages),
            stream=True,
            temperature=0.2,
        )
        for event in stream:
            delta = event.choices[0].delta
            text = getattr(delta, "content", None)
            if text:
                yield text
