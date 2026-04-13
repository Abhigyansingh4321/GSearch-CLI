"""
Rich UI components for G-Search CLI.
"""

from __future__ import annotations

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.text import Text
from rich.theme import Theme

from .engine import SearchResult

THEME = Theme(
    {
        "logo.primary": "bold #60a5fa",
        "logo.secondary": "bold #22d3ee",
        "banner.border": "#2563eb",
        "banner.author": "dim #94a3b8",
        "banner.tagline": "#cbd5e1",
        "divider": "#475569",
        "title": "bold #e2e8f0",
        "accent": "bold #38bdf8",
        "muted": "dim #94a3b8",
        "success": "bold #16a34a",
        "error": "bold #dc2626",
        "warning": "bold #d97706",
        "url": "underline #60a5fa",
        "source": "bold #14b8a6",
        "prompt": "bold #22d3ee",
        "hint": "dim #94a3b8",
    }
)

console = Console(theme=THEME)

_LOGO_LINES = [
    "  ██████  ███████ ███████  █████  ██████   ██████ ██   ██",
    " ██       ██      ██      ██   ██ ██   ██ ██      ██   ██",
    " ██   ███ ███████ █████   ███████ ██████  ██      ███████",
    " ██    ██      ██ ██      ██   ██ ██   ██ ██      ██   ██",
    "  ██████  ███████ ███████ ██   ██ ██   ██  ██████ ██   ██",
]


def display_banner() -> None:
    """Displays the GSearch banner."""

    logo = Text()
    for index, line in enumerate(_LOGO_LINES):
        style = "logo.primary" if index % 2 == 0 else "logo.secondary"
        logo.append(line, style=style)
        if index < len(_LOGO_LINES) - 1:
            logo.append("\n")

    banner = Group(
        Align.center(logo),
        Text(""),
        Align.center(Text("Simple terminal web search.", style="banner.tagline")),
        Align.right(Text("Abhigyan Singh", style="banner.author")),
    )

    console.print(
        Panel(
            banner,
            box=box.HEAVY,
            border_style="banner.border",
            padding=(1, 2),
        )
    )


def display_results(
    results: list[SearchResult],
    query: str,
    provider: str,
    site: str | None = None,
) -> None:
    """Renders search results in a clean Rich table."""

    if not results:
        console.print(f"[warning]No results found for:[/warning] {query}")
        return

    provider_label = _provider_label(provider)
    site_suffix = f"  [muted]site:{site}[/muted]" if site else ""

    console.print(Rule(style="divider"))
    console.print(
        f"[accent]{len(results)} results[/accent] for [title]{query}[/title] "
        f"[muted]via {provider_label}[/muted]{site_suffix}"
    )
    console.print(Rule(style="divider"))

    table = Table(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold #93c5fd",
        expand=True,
        row_styles=["none", "dim"],
        padding=(0, 1),
    )

    table.add_column("#", style="muted", width=4, justify="right")
    table.add_column("Title & Snippet", min_width=42, ratio=4)
    table.add_column("URL", style="url", min_width=24, ratio=3, overflow="fold")
    table.add_column("Source", style="source", width=12)

    for index, result in enumerate(results, start=1):
        title_and_snippet = Text()
        title_style = "bold #f8fafc" if index == 1 else "title"
        title_and_snippet.append(f"{_truncate(result.title, 72)}\n", style=title_style)
        title_and_snippet.append(_truncate(result.description, 160), style="muted")

        table.add_row(
            str(index),
            title_and_snippet,
            result.url,
            result.source,
        )

    console.print(table)


def display_picker_help() -> None:
    """Shows concise interactive picker instructions."""

    console.print(
        "\n[hint]Enter a result number to open it, or type [/hint]"
        "[prompt]q[/prompt]"
        "[hint] to quit.[/hint]"
    )


def _provider_label(provider: str) -> str:
    labels = {
        "auto": "Best available",
        "duckduckgo": "DuckDuckGo",
        "google": "Google",
    }
    return labels.get(provider, provider.title())


def _truncate(text: str, limit: int) -> str:
    stripped = " ".join(text.split())
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3].rstrip()}..."


def show_error(message: str) -> None:
    """Utility to show a standard error message."""

    console.print(f"\n[error]Error:[/error] {message}")


def show_success(message: str) -> None:
    """Utility to show a standard success message."""

    console.print(f"\n[success]OK:[/success] {message}")


def show_status(message: str):
    """Returns a status context manager for progress feedback."""

    return console.status(f"[prompt]{message}...[/prompt]", spinner="dots")
