# Founder Operating Loop

The Founder Operating Loop is the first integrated workflow of the Founder
Operating System. Every prior phase added a self-contained engine; this phase
connects them. The loop reads across memory, decisions, priorities, goals,
projects, and reviews and assembles a single, deterministic `FounderSnapshot`
describing where the whole system stands right now. It performs no scoring,
ranking, recommendation, or AI reasoning — only counting and direct reads.

## The loop

Conceptually, running a company is a continuous loop:

```
Observe → Remember → Decide → Prioritize → Execute → Review → Adapt
```

The engines already capture each step (memories, decisions, priorities, goals,
projects, reviews). The operating loop closes the cycle by observing the current
state of every engine at once, so the founder can adapt with full context. It is
the "Observe" and "Adapt" connective tissue rendered as a snapshot.

## Architecture

The package follows the same focused-module pattern as the engines:

- `founder_os.operating_loop.models` — the `FounderSnapshot` and
  `HealthIndicators` Pydantic models.
- `founder_os.operating_loop.service` — the aggregation functions and the
  `build_founder_snapshot` entry point.
- `founder_os.operating_loop.report` — `render_status_report`, which turns a
  snapshot into plain text for the CLI.

The loop depends on every engine's storage protocol but holds no references to
other records; it only reads counts and the latest review date. This keeps the
engines independent while letting the loop compose them.

### FounderSnapshot

`FounderSnapshot` stores the assembled view:

- `active_goal_count` — goals currently in the `active` state.
- `active_project_count` — projects currently `active`.
- `active_priority_count` — priorities currently `active`.
- `recent_decision_count` — number of recent decisions (capped at the recent
  limit, default 5).
- `recent_memory_count` — number of recent memories (capped at the recent limit).
- `latest_review_date` — the date of the most recent review, or `None`.
- `health` — the `HealthIndicators` for this snapshot.

"Recent" is defined deterministically as the most recent N records (newest
first), where N defaults to `DEFAULT_RECENT_LIMIT` (5). The count therefore never
exceeds N. There is no time-of-day or clock dependence, so snapshots are
reproducible.

### Health indicators

`HealthIndicators` is a set of boolean flags. Each is `True` when something is
missing — a plain observation, never a score or a recommendation:

- `no_active_goals` — `True` when there are no active goals.
- `no_active_projects` — `True` when there are no active projects.
- `no_active_priorities` — `True` when there are no active priorities.
- `no_recent_reviews` — `True` when no review has ever been recorded
  (`latest_review_date` is `None`).

## Python usage

```python
from founder_os.operating_loop.report import render_status_report
from founder_os.operating_loop.service import build_founder_snapshot

# Every store must be connected before building a snapshot.
snapshot = build_founder_snapshot(
    goal_store=goal_store,
    project_store=project_store,
    priority_store=priority_store,
    decision_store=decision_store,
    memory_store=memory_store,
    review_store=review_store,
)

print(snapshot.active_goal_count, snapshot.health.no_recent_reviews)
print(render_status_report(snapshot))
```

The recent window can be widened or narrowed with the `recent_limit` argument.

## Command-line usage

The `status` command runs the loop across every engine's default database and
prints a status report. Each source database can be overridden with its own
option.

```bash
founder-os status
```

Example output:

```
Founder Operating System status
  Active goals:      3
  Active projects:   2
  Active priorities: 4
  Recent decisions:  5
  Recent memories:   5
  Latest review:     2026-06-10
  Health:
    [-] No active goals: no
    [-] No active projects: no
    [-] No active priorities: no
    [-] No recent reviews: no
```

A `[!]` marker flags a raised indicator (something missing); a `[-]` marker means
the indicator is clear.

## Founder examples

- **Start the day with one command.** Run `founder-os status` to see active work
  and recent activity across the whole system without opening each engine.
- **Spot gaps immediately.** The health indicators surface when there are no
  active goals, projects, or priorities, or when you have never logged a review.
- **Stay deterministic.** The same data always produces the same snapshot, so the
  report is a trustworthy basis for deciding what to adapt next.
