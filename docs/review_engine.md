# Review Engine

The review engine is the periodic-review subsystem of the Founder Operating
System. It lets a founder capture a review at a point in time and record a
snapshot of where everything stands across goals, projects, priorities,
decisions, and memories. This is the first cross-system engine: it reads from
the other subsystems to build each snapshot, then stores those counts so the
review remains an accurate historical record even as the underlying data
changes. The engine is backed by SQLite and exposes both a Python API and a
command-line interface.

## Architecture

The engine follows the storage-interface-plus-implementation pattern established
by the memory, decision, priority, goal, and project engines, and adds a
standalone snapshot generator:

- `founder_os.reviews.store.ReviewStore` — a `Protocol` that defines the storage
  contract: `create_review`, `get_review`, `list_reviews`, and `delete_review`.
  A review is a historical record, so the store never recomputes snapshots; it
  only persists and returns them.
- `founder_os.reviews.sqlite_store.SQLiteReviewStore` — a SQLite-backed
  implementation of the protocol. It manages the connection lifecycle and the
  schema, and can be used as a context manager.
- `founder_os.reviews.snapshot` — `generate_snapshot(...)` and the
  `ReviewSnapshot` dataclass. The function reads the current state of the other
  engines and returns the counts to store on a review.

Reviews are represented by the `ReviewRecord` model in `founder_os.models`.

### Review fields

- `review_date` — the date the review covers (defaults to today).
- `review_type` — one of `weekly`, `monthly`, or `quarterly`.
- `notes` — free-form reflections for the review.
- `id` and `created_at` — the identifier and creation timestamp.

### Snapshot fields

Each review also stores the eight counts captured when it was created:

- `active_goals`, `completed_goals`
- `active_projects`, `completed_projects`
- `active_priorities`, `completed_priorities`
- `decision_count`
- `memory_count`

These values are computed once, at creation time, and stored. They are **not**
recomputed when the review is read later, which is what makes a review a stable
historical snapshot.

### Snapshot generation

`generate_snapshot` accepts a connected store for each engine (goals, projects,
priorities, decisions, and memory). It reads the current records, counts active
and completed goals, projects, and priorities by status, and totals the number
of decisions and memories recorded. It performs no scoring, ranking, or
recommendation — only counting.

### Storage schema

A `reviews` table holds one row per review, with columns for the review fields
and the eight snapshot counts. `review_date` is stored as an ISO date,
`created_at` as ISO 8601 text, `review_type` and `notes` as text, and the counts
as integers defaulting to zero. Listing returns reviews newest first.

## Python usage

```python
from founder_os.models import ReviewRecord, ReviewType
from founder_os.reviews.snapshot import generate_snapshot
from founder_os.reviews.sqlite_store import SQLiteReviewStore

# Each source store must be connected before generating a snapshot.
snapshot = generate_snapshot(
    goal_store=goal_store,
    project_store=project_store,
    priority_store=priority_store,
    decision_store=decision_store,
    memory_store=memory_store,
)

with SQLiteReviewStore("reviews.db") as store:
    review = store.create_review(
        ReviewRecord(
            review_type=ReviewType.WEEKLY,
            notes="Closed the seed round; shipped onboarding.",
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

    store.get_review(review.id)
    store.list_reviews()
    store.delete_review(review.id)
```

The store must be connected before use. Using it as a context manager (shown
above) opens the connection on entry and closes it on exit. You can also call
`connect()` and `close()` explicitly.

## Command-line usage

The `review` command group wraps review creation and listing. The `--db` option
points at the review database (it defaults to `~/.founder-os/reviews.db`).
`review create` reads the other engines from their default databases to build
the snapshot; each source path can be overridden with its own option.

```bash
# Capture a weekly review with an automatic system snapshot
founder-os review create \
    --type weekly \
    --notes "Closed the seed round; shipped onboarding."

# List all reviews, newest first
founder-os review list
```

## Founder examples

- **Run a weekly review.** Capture a review every week to record how many goals,
  projects, and priorities are active versus completed, plus how many decisions
  and memories you have logged.
- **Track momentum over time.** Because each review stores its own counts,
  listing reviews shows how the numbers moved between reviews without any
  recomputation.
- **Keep history honest.** Snapshots are frozen at creation, so a past review
  always reflects the state of the system on its review date.
