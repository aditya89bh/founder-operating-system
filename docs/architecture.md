# Architecture

This document describes the architecture of the Founder Operating System as it
exists in Phase 1. Phase 1 establishes the repository foundation: typed domain
models, a command-line entry point, tooling, and tests. It deliberately does not
include persistence, retrieval, or any decision/priority/goal logic.

## Domain model overview

The system is organized around a small set of records that capture the day-to-day
reality of running a company. Each record is a Pydantic v2 model with strict
validation and is intentionally free of behavior beyond shape and validation.

| Record           | Purpose                                                            |
| ---------------- | ----------------------------------------------------------------- |
| `MemoryRecord`   | A captured note, fact, or observation worth keeping.              |
| `DecisionRecord` | A decision with its surrounding context and rationale.            |
| `PriorityRecord` | A priority scored by urgency, importance, and effort.             |
| `GoalRecord`     | A goal pursued over a timeframe, with priorities aligned to it.   |
| `ProjectRecord`  | A body of work that advances a goal, between goals and priorities. |
| `ReviewRecord`   | A periodic review storing a point-in-time snapshot of the system.  |

Shared conventions across records:

- Every record carries an opaque string `id`, generated from a UUID when omitted.
- Every record carries a timezone-aware UTC `created_at` timestamp.
- Models forbid unknown fields (`extra="forbid"`) so malformed input fails fast.
- Lifecycle states (`GoalStatus`, `ProjectStatus`) and categories like
  `ReviewType` are modeled as string enums.

## Module boundaries

The package is split into focused modules with clear responsibilities:

- `founder_os.version` — single source of truth for the package version.
- `founder_os.models` — the typed domain models and their validation rules.
- `founder_os.memory` — the memory engine: a storage protocol and its
  SQLite-backed implementation (added in Phase 2). See
  [memory_engine.md](memory_engine.md).
- `founder_os.decisions` — the decision engine: a storage protocol and its
  SQLite-backed implementation with outcome tracking (added in Phase 3). See
  [decision_engine.md](decision_engine.md).
- `founder_os.priorities` — the priority engine: a storage protocol and its
  SQLite-backed implementation with deterministic ranking (added in Phase 4). See
  [priority_engine.md](priority_engine.md).
- `founder_os.goals` — the goal engine: a storage protocol and its SQLite-backed
  implementation with goal-priority alignment (added in Phase 5). See
  [goal_engine.md](goal_engine.md).
- `founder_os.projects` — the project engine: a storage protocol and its
  SQLite-backed implementation with goal-project alignment (added in Phase 6).
  See [project_engine.md](project_engine.md).
- `founder_os.reviews` — the review engine: a storage protocol, a SQLite-backed
  implementation, and a snapshot generator that reads the other engines (added
  in Phase 7). See [review_engine.md](review_engine.md).
- `founder_os.operating_loop` — the Founder Operating Loop: the first integrated
  workflow, which aggregates every engine into a single `FounderSnapshot` with
  boolean health indicators (added in Phase 8). See
  [founder_operating_loop.md](founder_operating_loop.md).
- `founder_os.cli` — the Typer application and command wiring.

Dependencies flow in one direction. `cli` depends on `version`, `models`, and
every engine; most engines depend only on `models`. The `reviews` engine is the
first cross-system component: its snapshot generator reads from the `goals`,
`projects`, `priorities`, `decisions`, and `memory` engines to compute counts,
but it stores only those counts and does not hold references to other records.
`models` is standalone. Outside of the engines' SQLite storage, the package does
not depend on external services.

## How the engines relate

The engines compose into a single planning chain, from long-term intent down to
the raw record of what happened:

```
Goals → Projects → Priorities → Decisions → Memory
```

- **Goals** define long-term objectives.
- **Projects** are the bodies of work that advance a goal.
- **Priorities** are the scored, near-term items that move projects forward.
- **Decisions** capture the choices made along the way.
- **Memory** is the durable record of notes, facts, and observations.

The **review engine** sits across all of these. Rather than extending the chain,
it observes it: when a review is created, it reads each engine and stores a
snapshot of the active and completed counts plus the totals for decisions and
memories. Each review is therefore a frozen, historical view of the whole system
at a moment in time, and is never recomputed afterward.

## The operating loop

Phase 8 turns the collection of engines into an operating system by adding the
Founder Operating Loop, the first workflow that reads across every engine at
once. It models running a company as a continuous cycle:

```
Observe → Remember → Decide → Prioritize → Execute → Review → Adapt
```

- **Observe / Remember** — the memory engine captures notes and observations.
- **Decide** — the decision engine records choices and their reasoning.
- **Prioritize** — the priority engine ranks what deserves attention.
- **Execute** — projects advance the goals they serve.
- **Review** — the review engine snapshots progress over time.
- **Adapt** — the operating loop reads the live state of every engine and
  assembles a deterministic `FounderSnapshot` so the founder can adjust course.

The loop computes active counts for goals, projects, and priorities, the number
of recent decisions and memories (capped at a fixed recent limit), and the
latest review date. It also derives boolean `HealthIndicators` that flag missing
pieces (no active goals, projects, priorities, or recorded reviews). The loop
depends on the engines' storage protocols but holds no references to their
records — it only reads and counts, performing no scoring or recommendation.

## Design principles

- **Typed core.** Every public surface is fully typed and checked with MyPy in
  strict mode. The domain models are the contract the rest of the system builds on.
- **Validation at the edges.** Records validate their own data on construction, so
  invalid state cannot enter the system.
- **Small, composable modules.** Each module does one thing and avoids hidden
  coupling, which keeps later phases easy to layer on.
- **Deterministic and dependency-light.** The foundation relies only on Pydantic
  and Typer, keeping behavior predictable and the surface area small.
- **No premature abstraction.** Only the concepts needed for Phase 1 are present.

## Repository layout

```
founder-operating-system/
├── .github/
│   └── workflows/
│       └── ci.yml            # Lint, type-check, and test on every push and PR
├── docs/
│   └── architecture.md       # This document
├── src/
│   └── founder_os/
│       ├── __init__.py       # Package entry point; exposes the version
│       ├── version.py        # Single source of truth for the version
│       ├── models.py         # Pydantic domain models
│       └── cli.py            # Typer command-line application
├── tests/
│   ├── __init__.py
│   ├── test_models.py        # Creation and validation tests for the models
│   └── test_cli.py           # Tests for the command-line interface
├── pyproject.toml            # Packaging, Ruff, MyPy, and Pytest configuration
└── README.md
```

## Future phase boundaries

Phase 1 intentionally stops at the foundation. The following capabilities are out
of scope for Phase 1 and are reserved for later phases:

- Persistence (for example a database) and any storage layer.
- Memory retrieval, search, and ranking.
- Decision workflows, priority scoring, goal tracking, and project tracking logic.
- Reviews, dashboards, analytics, and recommendations.
- Any AI features, embeddings, or vector databases.

These boundaries keep the foundation small and verifiable. Later phases will build
on the typed models and CLI defined here without reshaping them.
