"""CLI for Dev-AID Local Search"""

import click
import json
import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from mcp_server.server import CodeSearchServer


console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """Dev-AID Local Search - 100% local semantic code search"""
    pass


@cli.command()
@click.argument('directory', type=click.Path(exists=True), default='.')
def index(directory):
    """Index a directory for code search"""
    directory = os.path.abspath(directory)

    console.print(f"[blue]Indexing directory:[/blue] {directory}")

    server = CodeSearchServer()

    with console.status("[bold green]Indexing..."):
        result = server.index_directory(directory)

    if "error" in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        return

    console.print("[green]✓ Indexing complete[/green]")
    console.print(f"  • Total chunks: {result.get('total_chunks', 0)}")
    console.print(f"  • Indexed files: {len(result.get('indexed_files', []))}")
    console.print(f"  • Storage: {result.get('storage_path', 'unknown')}")


@cli.command()
@click.argument('query')
@click.option('--project', '-p', type=click.Path(exists=True), default='.', help='Project directory')
@click.option('--top-k', '-k', default=5, help='Number of results')
def search(query, project, top_k):
    """Search code with natural language query"""
    project = os.path.abspath(project)

    console.print(f"[blue]Searching:[/blue] {query}")
    console.print(f"[dim]Project: {project}[/dim]")
    console.print()

    server = CodeSearchServer()

    with console.status("[bold green]Searching..."):
        results = server.search_code(query, project, top_k=top_k)

    if not results:
        console.print("[yellow]No results found[/yellow]")
        return

    if isinstance(results, list) and len(results) > 0 and "error" in results[0]:
        console.print(f"[red]Error:[/red] {results[0]['error']}")
        return

    # Display results
    for i, result in enumerate(results, 1):
        console.print(f"[bold cyan]Result #{i}[/bold cyan] (score: {result['score']:.4f})")
        console.print(f"[dim]{result['file_path']}:{result['start_line']}-{result['end_line']}[/dim]")
        console.print()

        # Show code snippet (first 10 lines)
        code_lines = result['content'].split('\n')[:10]
        for line in code_lines:
            console.print(f"  {line}")

        if len(result['content'].split('\n')) > 10:
            console.print("  [dim]...[/dim]")

        console.print()


@cli.command()
@click.option('--project', '-p', type=click.Path(exists=True), default=None, help='Project directory')
def status(project):
    """Show index status"""
    if project:
        project = os.path.abspath(project)

    server = CodeSearchServer()
    result = server.get_index_status(project)

    if "error" in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        return

    if "indexed_projects" in result:
        # Global status
        console.print(f"[bold]Total indexed projects:[/bold] {result['indexed_projects']}")
        console.print()

        if result.get("projects"):
            table = Table(title="Indexed Projects")
            table.add_column("Project Path", style="cyan")
            table.add_column("Hash", style="dim")

            for path, hash_val in result["projects"].items():
                table.add_row(path, hash_val)  # BUGFIX: was add_column

            console.print(table)
    else:
        # Project-specific status
        console.print(f"[bold]Index Status[/bold]")
        console.print(f"  • Total chunks: {result.get('total_chunks', 0)}")
        console.print(f"  • Indexed files: {len(result.get('indexed_files', []))}")
        console.print(f"  • Embedding dimension: {result.get('embedding_dim', 'unknown')}")
        console.print(f"  • Storage: {result.get('storage_path', 'unknown')}")


@cli.command()
def list_projects():
    """List all indexed projects"""
    server = CodeSearchServer()
    result = server.list_projects()

    if "error" in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        return

    console.print(f"[bold]Indexed Projects:[/bold] {result['total_projects']}")
    console.print()

    for project in result.get("projects", []):
        console.print(f"  • {project['path']} [dim]({project['hash']})[/dim]")


@cli.command()
@click.argument('project', type=click.Path(exists=True))
@click.confirmation_option(prompt='Are you sure you want to clear the index?')
def clear(project):
    """Clear index for a project"""
    project = os.path.abspath(project)

    server = CodeSearchServer()
    result = server.clear_index(project)

    if "error" in result:
        console.print(f"[red]Error:[/red] {result['error']}")
        return

    console.print(f"[green]✓ Index cleared for {project}[/green]")


def main():
    """Entry point"""
    cli()


if __name__ == "__main__":
    main()
