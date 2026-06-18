# Goal Engine

The goal engine is the goal-management subsystem of the Founder Operating
System. It lets a founder define long-term objectives, track their timeframe and
status, and align priorities to the goals they serve so that day-to-day work
connects to meaningful outcomes. It is backed by SQLite and exposes both a Python
API and a command-line interface.

## Architecture

The engine is split into a storage interface and a concrete implementation,
mirroring the pattern established by the memory, decision, and priority engines:

- `founder_os.goals.store.GoalStore` — a `Protocol` that defines the storage
  contract: `create_goal`, `get_goal`, `list_goals`, `delete_goal`,
  `link_priority_to_goal`, and `get_goal_priorities`. Any backend that satisfies
  this protocol can be used.
- `founder_os.goals.sqlite_store.SQLiteGoalStore` — a SQLite-backed
  implementation of the protocol. It manages the connection lifecycle and the
  schema, and can be used as a context manager.

Goals are represented by the `GoalRecord` model in `founder_os.models`.

### Goal fields

- `title` — a short name for the goal.
- `description` — optional detail about the objective.
- `timeframe` — the horizon the goal is pursued over, one of `yearly`,
  `quarterly`, `monthly`, or `weekly`.
- `target_date` — an optional date the goal is aimed at (or `None`).
- `status` — one of `planned`, `active`, `completed`, or `abandoned` (new goals
  start `active`).
- `id`, `created_at`, and `updated_at` — the identifier and timestamps.

### Goal-priority alignment

Goals are the organizing structure for priorities. A priority can belong to zero
or one goal, and a goal can contain many priorities. The engine stores this
relationship only; it does not rank, recommend, or otherwise reason about it.

- `link_priority_to_goal(priority_id, goal_id)` aligns a priority with a goal.
  Because a priority belongs to at most one goal, re-linking it moves it to the
  new goal rather than creating a second alignment.
- `get_goal_priorities(goal_id)` returns the identifiers of the priorities
  aligned with a goal. The goal engine stores only the alignment, so callers can
  resolve those identifiers against the priority engine when they need full
  priority records.

### Storage schema

A `goals` table holds one row per goal, with columns for each field above.
Timestamps are stored as ISO 8601 text, `target_date` as an ISO date (or `NULL`),
`timeframe` as text defaulting to `quarterly`, and `status` as text defaulting to
`active`. A second `goal_priorities` table stores the alignment as a
`priority_id` (primary key, so one goal per priority) referencing `goal_id`. The
reference uses `ON DELETE CASCADE`, so deleting a goal removes its alignments.
Listing returns goals newest first.

## Python usage

```python
from datetime import date

from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.models import GoalRecord, GoalStatus, GoalTimeframe

with SQLiteGoalStore("goals.db") as store:
    goal = store.create_goal(
        GoalRecord(
            title="Reach 100 paying customers",
            description="Grow from design partners to a repeatable sales motion.",
            timeframe=GoalTimeframe.YEARLY,
            target_date=date(2026, 12, 31),
            status=GoalStatus.ACTIVE,
        )
    )

    store.get_goal(goal.id)
    store.list_goals()
    store.link_priority_to_goal("a-priority-id", goal.id)
    store.get_goal_priorities(goal.id)
    store.delete_goal(goal.id)
```

The store must be connected before use. Using it as a context manager (shown
above) opens the connection on entry and closes it on exit. You can also call
`connect()` and `close()` explicitly.

## Command-line usage

The `goal` command group wraps goal creation and listing. Each command accepts a
`--db` option pointing at the SQLite database file (it defaults to
`~/.founder-os/goals.db`).

```bash
# Define a goal with its timeframe and target date
founder-os goal create "Reach 100 paying customers" \
    --description "Grow from design partners to a repeatable sales motion." \
    --timeframe yearly \
    --target-date 2026-12-31 \
    --status active

# List all goals, newest first
founder-os goal list
```

## Founder examples

- **Set the destination first.** Capture the quarter's or year's objective as a
  goal, then create priorities and align them to it so the daily work has a clear
  purpose.
- **Keep priorities organized by outcome.** Because a priority can belong to one
  goal, `get_goal_priorities` gives you the slice of work that advances a given
  objective.
- **Retire goals cleanly.** Mark a goal `completed` or `abandoned`; deleting a
  goal automatically clears its priority alignments so nothing dangles.
