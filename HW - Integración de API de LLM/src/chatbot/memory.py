from __future__ import annotations

from typing import List
from .models import ChatMessage


class ConversationMemory:
    def __init__(self) -> None:
        self._messages: List[ChatMessage] = []

    @property
    def messages(self) -> List[ChatMessage]:
        return list(self._messages)

    def add(self, role: str, content: str, *, name: str | None = None, tool_call_id: str | None = None) -> None:
        self._messages.append(ChatMessage(role=role, content=content, name=name, tool_call_id=tool_call_id))

    def add_user(self, content: str) -> None:
        self.add("user", content)

    def add_assistant(self, content: str) -> None:
        self.add("assistant", content)

    def add_tool(self, content: str, tool_call_id: str) -> None:
        self.add("tool", content, tool_call_id=tool_call_id)
