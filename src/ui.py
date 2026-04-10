"""
Rich UI components for G-Search CLI.
"""

from __future__ import annotations

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .engine import SearchResult

console = Console()


def display_banner() -> None:
    """Displays a colorful ASCII banner for G-Search CLI."""

    banner_text = Text("G-SEARCH CLI", style="bold white on blue", justify="center")
    banner_subtitle = Text(
        "\nSearch the web from your terminal without losing context.",
        style="italic cyan",
        justify="center",
    )

    console.print(
        Panel(
            Text.assemble(banner_text, banner_subtitle),
            box=box.DOUBLE,
            border_style="bright_blue",
        )
    )


def display_results(
    results: list[SearchResult],
    query: str,
    provider: str,
    site: str | None = None,
) -> None:
    """Renders search results in a Rich table."""

    if not results:
        console.print(f"[bold red]No results found for:[/bold red] {query}")
        return

    provider_label = provider.title() if provider != "auto" else "Best available"
    site_suffix = f" [dim](site:{site})[/dim]" if site else ""
    title = (
        f"\n[bold green]{len(results)} results[/bold green] for "
        f"[italic magenta]'{query}'[/italic magenta] "
        f"[dim]via {provider_label}[/dim]{site_suffix}"
    )

    table = Table(
        title=title,
        box=box.SIMPLE_HEAD,
        show_header=True,
        header_style="bold cyan",
        expand=True,
    )

    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("Title & Snippet", style="white", ratio=3)
    table.add_column("URL", style="blue underline", ratio=2, overflow="fold")
    table.add_column("Source", style="dim green", width=12)

    for index, result in enumerate(results, start=1):
        title_and_snippet = Text()
        title_and_snippet.append(f"{result.title}\n", style="bold yellow")
        title_and_snippet.append(_truncate(result.description), style="dim italic")

        table.add_row(
            str(index),
            title_and_snippet,
            result.url,
            result.source,
        )

    console.print(table)


def _truncate(text: str, limit: int = 180) -> str:
    stripped = " ".join(text.split())
    if len(stripped) <= limit:
        return stripped
    return f"{stripped[: limit - 3].rstrip()}..."


def show_error(message: str) -> None:
    """Utility to show a standard error message."""

    console.print(f"\n[bold red]Error:[/bold red] {message}")


def show_success(message: str) -> None:
    """Utility to show a standard success message."""

    console.print(f"\n[bold green]✔[/bold green] {message}")


def show_status(message: str):
    """Returns a status context manager for progress feedback."""

    return console.status(f"[bold yellow]{message}...")
