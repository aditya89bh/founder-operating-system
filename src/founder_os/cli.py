"""Command-line interface for the Founder Operating System."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Annotated

import typer

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import (
    DecisionOutcome,
    DecisionRecord,
    GoalRecord,
    GoalStatus,
    GoalTimeframe,
    MemoryRecord,
    PriorityRecord,
    ProjectRecord,
    ProjectStatus,
    ReviewRecord,
    ReviewType,
)
from founder_os.operating_loop.service import build_founder_snapshot
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reviews.snapshot import generate_snapshot
from founder_os.reviews.sqlite_store import SQLiteReviewStore
from founder_os.version import __version__

DEFAULT_DB_PATH = Path.home() / ".founder-os" / "memory.db"
DEFAULT_DECISION_DB_PATH = Path.home() / ".founder-os" / "decisions.db"
DEFAULT_PRIORITY_DB_PATH = Path.home() / ".founder-os" / "priorities.db"
DEFAULT_GOAL_DB_PATH = Path.home() / ".founder-os" / "goals.db"
DEFAULT_PROJECT_DB_PATH = Path.home() / ".founder-os" / "projects.db"
DEFAULT_REVIEW_DB_PATH = Path.home() / ".founder-os" / "reviews.db"


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


def _open_goal_store(database: Path) -> SQLiteGoalStore:
    """Open a connected SQLite goal store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteGoalStore(database)
    store.connect()
    return store


def _open_project_store(database: Path) -> SQLiteProjectStore:
    """Open a connected SQLite project store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteProjectStore(database)
    store.connect()
    return store


def _open_review_store(database: Path) -> SQLiteReviewStore:
    """Open a connected SQLite review store at ``database``."""
    database.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteReviewStore(database)
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


@priority_app.command("create")
def priority_create(
    title: Annotated[str, typer.Argument(help="Short title for the priority.")],
    description: Annotated[
        str, typer.Option("--description", help="Optional details about the priority.")
    ] = "",
    category: Annotated[
        str, typer.Option("--category", help="Grouping label for the priority.")
    ] = "",
    urgency: Annotated[
        int, typer.Option("--urgency", min=1, max=5, help="How time-sensitive (1-5).")
    ] = 3,
    importance: Annotated[
        int, typer.Option("--importance", min=1, max=5, help="How much it matters (1-5).")
    ] = 3,
    effort: Annotated[
        int, typer.Option("--effort", min=1, max=5, help="How much effort it needs (1-5).")
    ] = 3,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_PRIORITY_DB_PATH,
) -> None:
    """Create a new priority and print its identifier."""
    store = _open_priority_store(database)
    try:
        record = store.create_priority(
            PriorityRecord(
                title=title,
                description=description,
                category=category,
                urgency=urgency,
                importance=importance,
                effort=effort,
            )
        )
    finally:
        store.close()
    typer.echo(record.id)


def _format_priority(record: PriorityRecord) -> str:
    return (
        f"{record.id}  score={record.score:.2f}  "
        f"[u{record.urgency}/i{record.importance}/e{record.effort}]  "
        f"{record.status.value}  {record.title}"
    )


@priority_app.command("list")
def priority_list(
    ranked: Annotated[
        bool,
        typer.Option(
            "--ranked/--all",
            help="Rank active priorities by score (default) or list all, newest first.",
        ),
    ] = True,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_PRIORITY_DB_PATH,
) -> None:
    """List priorities, ranked by score (default) or newest first."""
    store = _open_priority_store(database)
    try:
        records = store.rank_priorities() if ranked else store.list_priorities()
    finally:
        store.close()
    if not records:
        typer.echo("No priorities found.")
        return
    for record in records:
        typer.echo(_format_priority(record))


goal_app = typer.Typer(
    help="Define goals and align priorities to them.",
    no_args_is_help=True,
)


@goal_app.callback()
def goal() -> None:
    """Manage long-term goals and their aligned priorities."""


app.add_typer(goal_app, name="goal")


@goal_app.command("create")
def goal_create(
    title: Annotated[str, typer.Argument(help="Short title for the goal.")],
    description: Annotated[
        str, typer.Option("--description", help="Optional details about the goal.")
    ] = "",
    timeframe: Annotated[
        GoalTimeframe, typer.Option("--timeframe", help="The horizon for the goal.")
    ] = GoalTimeframe.QUARTERLY,
    status: Annotated[
        GoalStatus, typer.Option("--status", help="The goal's lifecycle state.")
    ] = GoalStatus.ACTIVE,
    target_date: Annotated[
        str | None, typer.Option("--target-date", help="Target date in YYYY-MM-DD format.")
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_GOAL_DB_PATH,
) -> None:
    """Create a new goal and print its identifier."""
    parsed_target: date | None = None
    if target_date is not None:
        try:
            parsed_target = date.fromisoformat(target_date)
        except ValueError as exc:
            raise typer.BadParameter("Target date must be in YYYY-MM-DD format.") from exc
    store = _open_goal_store(database)
    try:
        record = store.create_goal(
            GoalRecord(
                title=title,
                description=description,
                timeframe=timeframe,
                target_date=parsed_target,
                status=status,
            )
        )
    finally:
        store.close()
    typer.echo(record.id)


def _format_goal(record: GoalRecord) -> str:
    target = record.target_date.isoformat() if record.target_date else "-"
    return (
        f"{record.id}  [{record.timeframe.value}/{record.status.value}]  "
        f"target={target}  {record.title}"
    )


@goal_app.command("list")
def goal_list(
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_GOAL_DB_PATH,
) -> None:
    """List goals, newest first."""
    store = _open_goal_store(database)
    try:
        records = store.list_goals()
    finally:
        store.close()
    if not records:
        typer.echo("No goals found.")
        return
    for record in records:
        typer.echo(_format_goal(record))


project_app = typer.Typer(
    help="Organize work into projects and align them to goals.",
    no_args_is_help=True,
)


@project_app.callback()
def project() -> None:
    """Manage projects and the goals they advance."""


app.add_typer(project_app, name="project")


@project_app.command("create")
def project_create(
    title: Annotated[str, typer.Argument(help="Short title for the project.")],
    description: Annotated[
        str, typer.Option("--description", help="Optional details about the project.")
    ] = "",
    status: Annotated[
        ProjectStatus, typer.Option("--status", help="The project's lifecycle state.")
    ] = ProjectStatus.PLANNED,
    start_date: Annotated[
        str | None, typer.Option("--start-date", help="Start date in YYYY-MM-DD format.")
    ] = None,
    target_date: Annotated[
        str | None, typer.Option("--target-date", help="Target date in YYYY-MM-DD format.")
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_PROJECT_DB_PATH,
) -> None:
    """Create a new project and print its identifier."""
    parsed_start: date | None = None
    if start_date is not None:
        try:
            parsed_start = date.fromisoformat(start_date)
        except ValueError as exc:
            raise typer.BadParameter("Start date must be in YYYY-MM-DD format.") from exc
    parsed_target: date | None = None
    if target_date is not None:
        try:
            parsed_target = date.fromisoformat(target_date)
        except ValueError as exc:
            raise typer.BadParameter("Target date must be in YYYY-MM-DD format.") from exc
    store = _open_project_store(database)
    try:
        record = store.create_project(
            ProjectRecord(
                title=title,
                description=description,
                status=status,
                start_date=parsed_start,
                target_date=parsed_target,
            )
        )
    finally:
        store.close()
    typer.echo(record.id)


def _format_project(record: ProjectRecord) -> str:
    start = record.start_date.isoformat() if record.start_date else "-"
    target = record.target_date.isoformat() if record.target_date else "-"
    return f"{record.id}  [{record.status.value}]  start={start} target={target}  {record.title}"


@project_app.command("list")
def project_list(
    database: Annotated[
        Path, typer.Option("--db", help="Path to the SQLite database.")
    ] = DEFAULT_PROJECT_DB_PATH,
) -> None:
    """List projects, newest first."""
    store = _open_project_store(database)
    try:
        records = store.list_projects()
    finally:
        store.close()
    if not records:
        typer.echo("No projects found.")
        return
    for record in records:
        typer.echo(_format_project(record))


review_app = typer.Typer(
    help="Capture periodic reviews with system snapshots.",
    no_args_is_help=True,
)


@review_app.callback()
def review() -> None:
    """Create and browse periodic reviews of the whole system."""


app.add_typer(review_app, name="review")


@review_app.command("create")
def review_create(
    review_type: Annotated[
        ReviewType, typer.Option("--type", help="The review cadence.")
    ] = ReviewType.WEEKLY,
    notes: Annotated[str, typer.Option("--notes", help="Reflections for this review.")] = "",
    review_date: Annotated[
        str | None, typer.Option("--date", help="Review date in YYYY-MM-DD format.")
    ] = None,
    database: Annotated[
        Path, typer.Option("--db", help="Path to the review SQLite database.")
    ] = DEFAULT_REVIEW_DB_PATH,
    goal_db: Annotated[
        Path, typer.Option("--goal-db", help="Path to the goal database.")
    ] = DEFAULT_GOAL_DB_PATH,
    project_db: Annotated[
        Path, typer.Option("--project-db", help="Path to the project database.")
    ] = DEFAULT_PROJECT_DB_PATH,
    priority_db: Annotated[
        Path, typer.Option("--priority-db", help="Path to the priority database.")
    ] = DEFAULT_PRIORITY_DB_PATH,
    decision_db: Annotated[
        Path, typer.Option("--decision-db", help="Path to the decision database.")
    ] = DEFAULT_DECISION_DB_PATH,
    memory_db: Annotated[
        Path, typer.Option("--memory-db", help="Path to the memory database.")
    ] = DEFAULT_DB_PATH,
) -> None:
    """Capture a review with a point-in-time snapshot of every engine."""
    if review_date is None:
        parsed_date = date.today()
    else:
        try:
            parsed_date = date.fromisoformat(review_date)
        except ValueError as exc:
            raise typer.BadParameter("Review date must be in YYYY-MM-DD format.") from exc
    goal_store = _open_goal_store(goal_db)
    project_store = _open_project_store(project_db)
    priority_store = _open_priority_store(priority_db)
    decision_store = _open_decision_store(decision_db)
    memory_store = _open_store(memory_db)
    try:
        snapshot = generate_snapshot(
            goal_store=goal_store,
            project_store=project_store,
            priority_store=priority_store,
            decision_store=decision_store,
            memory_store=memory_store,
        )
    finally:
        goal_store.close()
        project_store.close()
        priority_store.close()
        decision_store.close()
        memory_store.close()
    review_store = _open_review_store(database)
    try:
        record = review_store.create_review(
            ReviewRecord(
                review_date=parsed_date,
                review_type=review_type,
                notes=notes,
                active_goals=snapshot.active_goals,
                completed_goals=snapshot.completed_goals,
                active_projects=snapshot.active_projects,
                completed_projects=snapshot.completed_projects,
                active_priorities=snapshot.active_priorities,
                completed_priorities=snapshot.completed_priorities,
                decision_count=snapshot.decision_count,
                memory_count=snapshot.memory_count,
            )
        )
    finally:
        review_store.close()
    typer.echo(record.id)


def _format_review(record: ReviewRecord) -> str:
    return (
        f"{record.id}  {record.review_date.isoformat()}  [{record.review_type.value}]  "
        f"goals={record.active_goals}/{record.completed_goals} "
        f"projects={record.active_projects}/{record.completed_projects} "
        f"priorities={record.active_priorities}/{record.completed_priorities} "
        f"decisions={record.decision_count} memories={record.memory_count}"
    )


@review_app.command("list")
def review_list(
    database: Annotated[
        Path, typer.Option("--db", help="Path to the review SQLite database.")
    ] = DEFAULT_REVIEW_DB_PATH,
) -> None:
    """List reviews, newest first."""
    store = _open_review_store(database)
    try:
        records = store.list_reviews()
    finally:
        store.close()
    if not records:
        typer.echo("No reviews found.")
        return
    for record in records:
        typer.echo(_format_review(record))


@app.command("status")
def status(
    memory_db: Annotated[
        Path, typer.Option("--memory-db", help="Path to the memory database.")
    ] = DEFAULT_DB_PATH,
    decision_db: Annotated[
        Path, typer.Option("--decision-db", help="Path to the decision database.")
    ] = DEFAULT_DECISION_DB_PATH,
    priority_db: Annotated[
        Path, typer.Option("--priority-db", help="Path to the priority database.")
    ] = DEFAULT_PRIORITY_DB_PATH,
    goal_db: Annotated[
        Path, typer.Option("--goal-db", help="Path to the goal database.")
    ] = DEFAULT_GOAL_DB_PATH,
    project_db: Annotated[
        Path, typer.Option("--project-db", help="Path to the project database.")
    ] = DEFAULT_PROJECT_DB_PATH,
    review_db: Annotated[
        Path, typer.Option("--review-db", help="Path to the review database.")
    ] = DEFAULT_REVIEW_DB_PATH,
) -> None:
    """Run the Founder Operating Loop and show a snapshot of the whole system."""
    goal_store = _open_goal_store(goal_db)
    project_store = _open_project_store(project_db)
    priority_store = _open_priority_store(priority_db)
    decision_store = _open_decision_store(decision_db)
    memory_store = _open_store(memory_db)
    review_store = _open_review_store(review_db)
    try:
        snapshot = build_founder_snapshot(
            goal_store=goal_store,
            project_store=project_store,
            priority_store=priority_store,
            decision_store=decision_store,
            memory_store=memory_store,
            review_store=review_store,
        )
    finally:
        goal_store.close()
        project_store.close()
        priority_store.close()
        decision_store.close()
        memory_store.close()
        review_store.close()
    typer.echo(snapshot.model_dump_json())
