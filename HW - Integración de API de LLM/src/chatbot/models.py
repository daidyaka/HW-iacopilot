from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, HttpUrl


class SearchItem(BaseModel):
    title: str
    url: HttpUrl
    snippet: Optional[str] = None


class ScrapedPage(BaseModel):
    title: str
    url: HttpUrl
    text: str


class ToolSearchResult(BaseModel):
    query: str
    items: List[SearchItem]
    pages: List[ScrapedPage]


class ChatMessage(BaseModel):
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: Optional[str] = None
    tool_call_id: Optional[str] = None
