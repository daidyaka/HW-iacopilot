from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    serper_api_key: str
    openai_api_key: str
    model: str


def get_settings() -> Settings:
    load_dotenv()
    serper = os.getenv("SERPER_API_KEY", "")
    openai = os.getenv("OPENAI_API_KEY", "")
    model = os.getenv("MODEL", "gpt-4o-mini")

    if not serper:
        raise RuntimeError("Missing SERPER_API_KEY in environment")
    if not openai:
        raise RuntimeError("Missing OPENAI_API_KEY in environment")
    return Settings(serper_api_key=serper, openai_api_key=openai, model=model)
