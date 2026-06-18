"""Command-line interface for the Founder Operating System."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import MemoryRecord
from founder_os.version import __version__

DEFAULT_DB_PATH = Path.home() / ".founder-os" / "memory.db"


def _open_store(database: Path) -> SQLiteMemoryStore:
    """Open a connected SQLite memory store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteMemoryStore(database)
    store.connect()
    return store

app = typer.Typer(
    name="founder-os",
    help="Founder Operating System command-line interface.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Founder Operating System command-line interface."""


@app.command()
def version() -> None:
    """Print the installed Founder Operating System version."""
    typer.echo(__version__)


memory_app = typer.Typer(
    help="Store, retrieve, search, and delete memories.",
    no_args_is_help=True,
)


@memory_app.callback()
def memory() -> None:
    """Manage stored memories."""


app.add_typer(memory_app, name="memory")


@memory_app.command("add")
def memory_add(
    content: Annotated[str, typer.Argument(help="The memory text to store.")],
    tag: Annotated[
        list[str] | None,
        typer.Option("--tag", "-t", help="Attach a tag to the memory; repeatable."),
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DB_PATH,
) -> None:
    """Add a new memory and print its identifier."""
    store = _open_store(database)
    try:
        record = store.add_memory(MemoryRecord(content=content, tags=tag or []))
    finally:
        store.close()
    typer.echo(record.id)


def _format_memory(record: MemoryRecord) -> str:
    tags = f" [{', '.join(record.tags)}]" if record.tags else ""
    return f"{record.id}  {record.created_at.isoformat()}{tags}  {record.content}"


@memory_app.command("list")
def memory_list(
    tag: Annotated[
        str | None, typer.Option("--tag", "-t", help="Only show memories with this tag.")
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DB_PATH,
) -> None:
    """List stored memories, newest first."""
    store = _open_store(database)
    try:
        records = store.list_memories(tag=tag)
    finally:
        store.close()
    if not records:
        typer.echo("No memories found.")
        return
    for record in records:
        typer.echo(_format_memory(record))
