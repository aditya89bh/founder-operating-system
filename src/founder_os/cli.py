"""Command-line interface for the Founder Operating System."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import DecisionOutcome, DecisionRecord, MemoryRecord
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.version import __version__

DEFAULT_DB_PATH = Path.home() / ".founder-os" / "memory.db"
DEFAULT_DECISION_DB_PATH = Path.home() / ".founder-os" / "decisions.db"
DEFAULT_PRIORITY_DB_PATH = Path.home() / ".founder-os" / "priorities.db"


def _open_store(database: Path) -> SQLiteMemoryStore:
    """Open a connected SQLite memory store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteMemoryStore(database)
    store.connect()
    return store


def _open_decision_store(database: Path) -> SQLiteDecisionStore:
    """Open a connected SQLite decision store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteDecisionStore(database)
    store.connect()
    return store


def _open_priority_store(database: Path) -> SQLitePriorityStore:
    """Open a connected SQLite priority store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLitePriorityStore(database)
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


@memory_app.command("delete")
def memory_delete(
    memory_id: Annotated[str, typer.Argument(help="Identifier of the memory to delete.")],
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DB_PATH,
) -> None:
    """Delete a memory by its identifier."""
    store = _open_store(database)
    try:
        deleted = store.delete_memory(memory_id)
    finally:
        store.close()
    if not deleted:
        typer.echo(f"No memory found with id {memory_id}.")
        raise typer.Exit(code=1)
    typer.echo(f"Deleted memory {memory_id}.")


@memory_app.command("search")
def memory_search(
    query: Annotated[str, typer.Argument(help="Keyword to search for in memory content.")],
    tag: Annotated[
        str | None, typer.Option("--tag", "-t", help="Restrict the search to this tag.")
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DB_PATH,
) -> None:
    """Search memories by keyword, newest first."""
    store = _open_store(database)
    try:
        records = store.search_memories(query, tag=tag)
    finally:
        store.close()
    if not records:
        typer.echo("No memories found.")
        return
    for record in records:
        typer.echo(_format_memory(record))


decision_app = typer.Typer(
    help="Record, review, and manage decisions.",
    no_args_is_help=True,
)


@decision_app.callback()
def decision() -> None:
    """Manage recorded decisions."""


app.add_typer(decision_app, name="decision")


@decision_app.command("create")
def decision_create(
    title: Annotated[str, typer.Argument(help="Short title for the decision.")],
    decision_text: Annotated[str, typer.Option("--decision", help="The decision that was made.")],
    context: Annotated[
        str, typer.Option("--context", help="The situation prompting the decision.")
    ] = "",
    rationale: Annotated[str, typer.Option("--rationale", help="Why this decision was made.")] = "",
    assumptions: Annotated[
        str, typer.Option("--assumptions", help="Key assumptions behind the decision.")
    ] = "",
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DECISION_DB_PATH,
) -> None:
    """Record a new decision and print its identifier."""
    store = _open_decision_store(database)
    try:
        record = store.create_decision(
            DecisionRecord(
                title=title,
                decision=decision_text,
                context=context,
                rationale=rationale,
                assumptions=assumptions,
            )
        )
    finally:
        store.close()
    typer.echo(record.id)


def _format_decision(record: DecisionRecord) -> str:
    review = f" review={record.review_date.isoformat()}" if record.review_date else ""
    return (
        f"{record.id}  {record.created_at.isoformat()}  "
        f"[{record.outcome.value}]{review}  {record.title}"
    )


@decision_app.command("list")
def decision_list(
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DECISION_DB_PATH,
) -> None:
    """List recorded decisions, newest first."""
    store = _open_decision_store(database)
    try:
        records = store.list_decisions()
    finally:
        store.close()
    if not records:
        typer.echo("No decisions found.")
        return
    for record in records:
        typer.echo(_format_decision(record))


@decision_app.command("show")
def decision_show(
    decision_id: Annotated[str, typer.Argument(help="Identifier of the decision to show.")],
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DECISION_DB_PATH,
) -> None:
    """Show the full details of a single decision."""
    store = _open_decision_store(database)
    try:
        record = store.get_decision(decision_id)
    finally:
        store.close()
    if record is None:
        typer.echo(f"No decision found with id {decision_id}.")
        raise typer.Exit(code=1)
    review = record.review_date.isoformat() if record.review_date else "-"
    typer.echo(f"Id:            {record.id}")
    typer.echo(f"Title:         {record.title}")
    typer.echo(f"Created:       {record.created_at.isoformat()}")
    typer.echo(f"Context:       {record.context}")
    typer.echo(f"Decision:      {record.decision}")
    typer.echo(f"Rationale:     {record.rationale}")
    typer.echo(f"Assumptions:   {record.assumptions}")
    typer.echo(f"Outcome:       {record.outcome.value}")
    typer.echo(f"Outcome notes: {record.outcome_notes}")
    typer.echo(f"Review date:   {review}")


@decision_app.command("update-outcome")
def decision_update_outcome(
    decision_id: Annotated[str, typer.Argument(help="Identifier of the decision to update.")],
    outcome: Annotated[DecisionOutcome, typer.Option("--outcome", help="The reviewed outcome.")],
    notes: Annotated[str, typer.Option("--notes", help="Notes about the outcome.")] = "",
    review_date: Annotated[
        str | None, typer.Option("--review-date", help="Review date in YYYY-MM-DD format.")
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_DECISION_DB_PATH,
) -> None:
    """Record the outcome of a decision after reviewing it."""
    parsed_review: date | None = None
    if review_date is not None:
        try:
            parsed_review = date.fromisoformat(review_date)
        except ValueError as exc:
            raise typer.BadParameter("Review date must be in YYYY-MM-DD format.") from exc
    store = _open_decision_store(database)
    try:
        record = store.update_outcome(
            decision_id, outcome.value, outcome_notes=notes, review_date=parsed_review
        )
    finally:
        store.close()
    if record is None:
        typer.echo(f"No decision found with id {decision_id}.")
        raise typer.Exit(code=1)
    typer.echo(f"Updated outcome for decision {decision_id} to {record.outcome.value}.")


priority_app = typer.Typer(
    help="Capture, rank, and review priorities.",
    no_args_is_help=True,
)


@priority_app.callback()
def priority() -> None:
    """Manage priorities and rank them by deterministic score."""


app.add_typer(priority_app, name="priority")
