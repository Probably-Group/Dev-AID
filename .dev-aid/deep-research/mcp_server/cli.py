"""CLI interface for Dev-AID Deep Research.

Provides direct command-line access to research functionality
without going through the MCP protocol.

Usage:
    dev-aid-research "What is the latest version of Node.js?"
    dev-aid-research --depth deep "Compare React vs Vue in 2025"
    dev-aid-research --provider tavily "Python syntax for list comprehension"
"""

import asyncio
import json
import sys
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from .server import DeepResearchServer

console = Console()


def run_async(coro):
    """Run async function in sync context."""
    return asyncio.run(coro)


@click.group()
@click.version_option(version="1.0.0", prog_name="dev-aid-research")
def cli():
    """Dev-AID Deep Research - Multi-provider research tool.

    Supports Tavily (quick/standard), Perplexity Sonar (standard/deep),
    and Gemini Deep Research (deep).
    """
    pass


@cli.command()
@click.argument("query")
@click.option(
    "--depth",
    "-d",
    type=click.Choice(["quick", "standard", "deep", "auto"]),
    default="auto",
    help="Research depth level",
)
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["tavily", "perplexity-sonar", "gemini-deep-research"]),
    default=None,
    help="Specific provider to use",
)
@click.option(
    "--no-cache",
    is_flag=True,
    help="Skip cache, force fresh results",
)
@click.option(
    "--sources",
    "-s",
    type=int,
    default=10,
    help="Maximum sources to return",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
def search(
    query: str,
    depth: str,
    provider: Optional[str],
    no_cache: bool,
    sources: int,
    output_json: bool,
):
    """Execute a research query.

    Examples:
        dev-aid-research search "What is GraphQL?"
        dev-aid-research search --depth deep "Compare Redis vs Memcached"
        dev-aid-research search --provider tavily "Latest Python version"
    """
    server = DeepResearchServer()

    if not server.providers:
        console.print(
            "[red]Error:[/red] No research providers available. "
            "Set API keys: TAVILY_API_KEY, PERPLEXITY_API_KEY, or GOOGLE_API_KEY"
        )
        sys.exit(1)

    async def do_search():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                f"Researching ({depth})...",
                total=None,
            )

            result = await server.research(
                query=query,
                depth=depth,
                provider=provider,
                max_sources=sources,
                use_cache=not no_cache,
            )

            progress.update(task, completed=True)
            return result

    try:
        result = run_async(do_search())

        if output_json:
            console.print(json.dumps(result, indent=2))
        else:
            _display_result(result)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--no-cache", is_flag=True, help="Skip cache")
def quick(query: str, no_cache: bool):
    """Quick factual lookup.

    Uses Tavily basic search for fast results.

    Example:
        dev-aid-research quick "Python list append syntax"
    """
    server = DeepResearchServer()

    async def do_quick():
        return await server.quick_research(query=query, use_cache=not no_cache)

    try:
        result = run_async(do_quick())
        _display_result(result)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--no-cache", is_flag=True, help="Skip cache")
@click.option("--timeout", type=int, default=300, help="Timeout in seconds")
def deep(query: str, no_cache: bool, timeout: int):
    """Comprehensive deep research.

    Uses Gemini Deep Research or Perplexity Sonar Deep for
    thorough multi-step analysis.

    Example:
        dev-aid-research deep "Compare Kubernetes vs Docker Swarm architecture"
    """
    server = DeepResearchServer()

    async def do_deep():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(
                "Deep research in progress (may take 2-5 minutes)...",
                total=None,
            )
            return await server.deep_research(
                query=query,
                use_cache=not no_cache,
                timeout_seconds=timeout,
            )

    try:
        result = run_async(do_deep())
        _display_result(result)
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        sys.exit(1)


@cli.command()
def providers():
    """Show available research providers."""
    server = DeepResearchServer()
    status = server.get_providers_status()

    table = Table(title="Research Providers")
    table.add_column("Provider", style="cyan")
    table.add_column("Available", style="green")
    table.add_column("Depths", style="yellow")
    table.add_column("API Key Env", style="dim")

    for name, info in status["providers"].items():
        available = "[green]Yes[/green]" if info["available"] else "[red]No[/red]"
        depths = ", ".join(info["supported_depths"])
        table.add_row(name, available, depths, info["env_var"])

    console.print(table)
    console.print(f"\nTotal available: {status['total_available']}/3")


@cli.command()
@click.option("--entries", is_flag=True, help="Show cached entries")
def cache(entries: bool):
    """Show cache status."""
    server = DeepResearchServer()
    status = server.get_cache_status(include_entries=entries)

    console.print(
        Panel(
            f"[bold]Cache Statistics[/bold]\n\n"
            f"Total entries: {status['total_entries']}\n"
            f"Size: {status['total_size_mb']} MB\n"
            f"Directory: {status['cache_directory']}\n"
            f"Expired cleaned: {status.get('expired_cleaned', 0)}",
            title="Research Cache",
        )
    )

    if status.get("providers"):
        console.print("\n[bold]Entries by Provider:[/bold]")
        for provider, count in status["providers"].items():
            console.print(f"  {provider}: {count}")

    if entries and status.get("entries"):
        console.print("\n[bold]Cached Entries:[/bold]")
        for entry in status["entries"]:
            console.print(
                f"  [{entry['provider']}] ({entry['depth']}) "
                f"{entry['query_preview'][:60]}..."
            )


@cli.command("clear-cache")
@click.option("--provider", "-p", help="Clear only this provider's entries")
@click.option("--all", "clear_all", is_flag=True, help="Clear all entries")
@click.confirmation_option(prompt="Are you sure you want to clear cache?")
def clear_cache(provider: Optional[str], clear_all: bool):
    """Clear research cache."""
    server = DeepResearchServer()
    result = server.clear_cache(provider=provider, clear_all=clear_all or not provider)

    console.print(
        f"[green]Cache cleared:[/green] {result['entries_removed']} entries removed"
    )


def _display_result(result: dict) -> None:
    """Display research result nicely."""
    # Header info
    cached_str = " [dim](cached)[/dim]" if result.get("cached") else ""
    console.print(
        f"\n[bold blue]{result['provider']}[/bold blue] "
        f"[dim]({result['depth']})[/dim]{cached_str}"
    )
    console.print(f"[dim]Routing: {result.get('routing_reasoning', 'N/A')}[/dim]")
    console.print(f"[dim]Time: {result['processing_time_ms']}ms[/dim]\n")

    # Main content
    console.print(Panel(result["content"], title="Research Result"))

    # Sources
    if result.get("sources"):
        console.print("\n[bold]Sources:[/bold]")
        for i, source in enumerate(result["sources"][:5], 1):
            title = source.get("title", "Untitled")
            url = source.get("url", "")
            console.print(f"  {i}. [link={url}]{title}[/link]")
            if source.get("snippet"):
                console.print(f"     [dim]{source['snippet'][:100]}...[/dim]")


def main():
    """Entry point for CLI."""
    cli()


if __name__ == "__main__":
    main()
