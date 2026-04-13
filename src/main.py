"""
CLI entry point for G-Search CLI.
"""

from __future__ import annotations

import json
import sys
import webbrowser

import click
from dotenv import load_dotenv

from .engine import SearchEngine, SearchError
from .ui import (
    console,
    display_banner,
    display_picker_help,
    display_results,
    show_error,
    show_status,
    show_success,
)

load_dotenv()


@click.command()
@click.argument("query", required=True)
@click.option(
    "-n",
    "--num",
    default=10,
    show_default=True,
    type=click.IntRange(1, 50),
    help="Number of search results to fetch.",
)
@click.option(
    "-e",
    "--engine",
    "provider",
    default="auto",
    show_default=True,
    type=click.Choice(["auto", "duckduckgo", "google"], case_sensitive=False),
    help="Search provider to use.",
)
@click.option(
    "-s",
    "--site",
    help="Restrict results to a specific domain, e.g. docs.python.org.",
)
@click.option(
    "-j",
    "--json-output",
    is_flag=True,
    help="Print JSON output for scripting instead of the Rich UI.",
)
@click.option(
    "--no-prompt",
    is_flag=True,
    help="Skip the interactive result picker after displaying results.",
)
@click.option(
    "-l",
    "--lucky",
    is_flag=True,
    help="Open the first result directly in the browser.",
)
def main(
    query: str,
    num: int,
    provider: str,
    site: str | None,
    json_output: bool,
    no_prompt: bool,
    lucky: bool,
) -> None:
    """
    Search the web from your terminal.

    QUERY is the term you want to look up.
    """

    normalized_provider = provider.lower()
    engine = SearchEngine()

    try:
        if not json_output:
            display_banner()

        with show_status(build_status_message(query, normalized_provider, site)):
            results = engine.perform_search(
                query,
                num_results=num,
                provider=normalized_provider,
                site=site,
            )

        if not results:
            if json_output:
                click.echo(
                    json.dumps(
                        {
                            "query": query,
                            "provider": normalized_provider,
                            "site": site,
                            "count": 0,
                            "results": [],
                        },
                        indent=2,
                    )
                )
            else:
                show_error(f"No results found for '{query}'.")
            raise click.exceptions.Exit(0)

        if lucky:
            first_url = results[0].url
            show_success(f"Opening the top result: {first_url}")
            webbrowser.open(first_url, new=2)
            raise click.exceptions.Exit(0)

        if json_output:
            click.echo(
                json.dumps(
                    {
                        "query": query,
                        "provider": normalized_provider,
                        "site": site,
                        "count": len(results),
                        "results": [result.to_dict() for result in results],
                    },
                    indent=2,
                )
            )
            raise click.exceptions.Exit(0)

        display_results(results, query=query, provider=normalized_provider, site=site)

        if should_prompt(no_prompt):
            handle_interactive_mode(results)

    except click.exceptions.Exit:
        raise
    except SearchError as exc:
        render_error(str(exc), json_output)
        raise click.exceptions.Exit(1)
    except Exception as exc:  # pragma: no cover - defensive fallback
        render_error(f"Something went wrong: {exc}", json_output)
        raise click.exceptions.Exit(1)


def build_status_message(query: str, provider: str, site: str | None) -> str:
    target = f" via {provider}" if provider != "auto" else ""
    restriction = f" on {site}" if site else ""
    return f"Searching for '{query}'{restriction}{target}"


def should_prompt(no_prompt: bool) -> bool:
    return not no_prompt and sys.stdin.isatty() and sys.stdout.isatty()


def render_error(message: str, json_output: bool) -> None:
    if json_output:
        click.echo(json.dumps({"error": message}, indent=2))
        return

    show_error(message)


def handle_interactive_mode(results) -> None:
    """Allows users to select a result by index and open it in their browser."""

    display_picker_help()

    while True:
        choice = console.input(
            "\n[prompt]Select a result to open[/prompt] [hint](q to quit)[/hint]: "
        ).strip().lower()

        if choice in {"q", "exit", "quit"}:
            show_success("Done.")
            return

        try:
            index = int(choice)
        except ValueError:
            show_error("Enter a valid result number or 'q' to quit.")
            continue

        if not 1 <= index <= len(results):
            show_error(f"Choose a number between 1 and {len(results)}.")
            continue

        url_to_open = results[index - 1].url
        show_success(f"Opening: [bold]{url_to_open}[/bold]")
        webbrowser.open(url_to_open, new=2)


if __name__ == "__main__":
    main()
