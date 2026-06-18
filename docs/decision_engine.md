# Decision Engine

The decision engine is the decision-tracking subsystem of the Founder Operating
System. It lets a founder record decisions along with their context and
reasoning, retrieve and list them, and review their outcomes later so the team
can learn from past calls. It is backed by SQLite and exposes both a Python API
and a command-line interface.

## Architecture

The engine is split into a storage interface and a concrete implementation,
mirroring the pattern established by the memory engine:

- `founder_os.decisions.store.DecisionStore` — a `Protocol` that defines the
  storage contract: `create_decision`, `get_decision`, `list_decisions`,
  `delete_decision`, and `update_outcome`. Any backend that satisfies this
  protocol can be used.
- `founder_os.decisions.sqlite_store.SQLiteDecisionStore` — a SQLite-backed
  implementation of the protocol. It manages the connection lifecycle and the
  schema, and can be used as a context manager.

Decisions are represented by the `DecisionRecord` model in `founder_os.models`,
which carries the decision itself plus the reasoning behind it and the fields
used to review it later.

### Decision fields

- `title` — a short name for the decision.
- `context` — the situation that prompted the decision.
- `decision` — the choice that was made.
- `rationale` — the reasoning behind the choice.
- `assumptions` — the key assumptions the decision depends on.
- `outcome` — the reviewed result, one of `pending`, `successful`,
  `unsuccessful`, `mixed`, or `abandoned` (new decisions start `pending`).
- `outcome_notes` — free-form notes captured during review.
- `review_date` — the date the outcome was reviewed.
- `id` and `created_at` — the identifier and creation timestamp.

### Storage schema

A single `decisions` table holds one row per decision, with columns for each of
the fields above. The `created_at` timestamp is stored as ISO 8601 text, the
`review_date` as an ISO date (or `NULL` until a review happens), and `outcome`
as text defaulting to `pending`. Listing returns decisions newest first.

## Python usage

```python
from datetime import date

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.models import DecisionRecord

with SQLiteDecisionStore("decisions.db") as store:
    record = store.create_decision(
        DecisionRecord(
            title="Adopt weekly planning",
            context="Execution felt reactive.",
            decision="Run a structured weekly planning session every Monday.",
            rationale="A fixed cadence reduces context switching.",
            assumptions="The team is mostly synchronous.",
        )
    )

    store.get_decision(record.id)
    store.list_decisions()
    store.update_outcome(
        record.id,
        "successful",
        outcome_notes="Planning stuck and execution improved.",
        review_date=date(2026, 3, 1),
    )
    store.delete_decision(record.id)
```

The store must be connected before use. Using it as a context manager (shown
above) opens the connection on entry and closes it on exit. You can also call
`connect()` and `close()` explicitly.

## Command-line usage

The `decision` command group wraps the same operations. Each command accepts a
`--db` option pointing at the SQLite database file (it defaults to
`~/.founder-os/decisions.db`).

```bash
# Record a decision with its reasoning
founder-os decision create "Adopt weekly planning" \
    --decision "Run a structured weekly planning session every Monday." \
    --context "Execution felt reactive." \
    --rationale "A fixed cadence reduces context switching." \
    --assumptions "The team is mostly synchronous."

# List all decisions, newest first
founder-os decision list

# Show the full details of a single decision
founder-os decision show <decision-id>

# Record the outcome after reviewing the decision
founder-os decision update-outcome <decision-id> \
    --outcome successful \
    --notes "Planning stuck and execution improved." \
    --review-date 2026-03-01
```

## Founder examples

- **Capture the "why" in the moment.** When you decide to pause a hire, record
  the decision, the context (runway, priorities), and the assumptions (e.g. "we
  can revisit in Q3"). Months later the reasoning is still there.
- **Run a decision retrospective.** List recent decisions, open each with
  `decision show`, and use `decision update-outcome` to mark whether it worked,
  with notes on what you learned.
- **Track decisions awaiting review.** Decisions stay `pending` until you review
  them, so the list makes it obvious which past calls still need a verdict.
