from __future__ import annotations

import asyncio
from typing import List
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown

from .memory import ConversationMemory
from .search import web_search
from .scrape import scrape_pages
from .llm import LLMAdapter
from .models import ToolSearchResult


class ChatbotApp:
    def __init__(self) -> None:
        self.console = Console()
        self.memory = ConversationMemory()
        self.llm = LLMAdapter()
        # System prompt for style and citations requirement
        self.memory.add(
            "system",
            (
                "Eres un asistente útil. Cuando uses fuentes externas, cita al final "
                "con una lista de URLs. Si no encuentras información confiable, dilo claramente."
            ),
        )

    async def handle_question(self, question: str) -> None:
        self.memory.add_user(question)
        messages = self.memory.messages

        # Ask LLM if it wants to call web_search via function calling
        tool_call = await self.llm.decide_search(messages)

        tool_result: ToolSearchResult | None = None
        if tool_call and tool_call["name"] == "web_search":
            query = tool_call["arguments"].get("query") or question
            top_k = int(tool_call["arguments"].get("top_k", 5))

            self.console.print("[bold]🔎 Búsqueda en internet[/bold]")
            items = await web_search(query, top_k=top_k)

            processed: List[str] = []
            def on_processed(title: str, url: str) -> None:
                processed.append(f"- {title} ({url})")
                self.console.print(f"[green]Fuente procesada:[/green] {title} ({url})")

            pages = await scrape_pages(items, on_processed=on_processed)
            tool_result = ToolSearchResult(query=query, items=items, pages=pages)

        # Stream the final answer from the LLM
        with Live(auto_refresh=False) as live:
            buffer = ""
            async for token in self.llm.stream_final_answer(
                self.memory.messages,
                tool_call_id=tool_call["id"] if tool_call else None,
                tool_result=tool_result,
            ):
                buffer += token
                live.update(Markdown(buffer))
                live.refresh()

        # Append assistant full message to memory
        self.memory.add_assistant(buffer)

        # Print citations at the end if we used tool_result
        if tool_result and tool_result.pages:
            self.console.print("\n[bold]Referencias:[/bold]")
            for p in tool_result.pages:
                self.console.print(f"- {p.title} ({p.url})")


async def run_console() -> None:
    app = ChatbotApp()
    console = app.console
    console.print("[bold]Chatbot listo. Escribe tu pregunta (o 'salir').[/bold]")
    while True:
        try:
            user = console.input("[cyan]> Usuario:[/cyan] ")
        except (EOFError, KeyboardInterrupt):
            console.print("\nSaliendo...")
            break
        if not user:
            continue
        if user.strip().lower() in {"salir", "exit", "quit"}:
            console.print("Hasta luego 👋")
            break
        try:
            await app.handle_question(user)
        except Exception as e:
            console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    asyncio.run(run_console())
