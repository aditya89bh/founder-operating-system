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

Shared conventions across records:

- Every record carries an opaque string `id`, generated from a UUID when omitted.
- Every record carries a timezone-aware UTC `created_at` timestamp.
- Models forbid unknown fields (`extra="forbid"`) so malformed input fails fast.
- Lifecycle states (`GoalStatus`, `ProjectStatus`) are modeled as string enums.

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
- `founder_os.cli` — the Typer application and command wiring.

Dependencies flow in one direction. `cli` depends on `version`, `models`,
`memory`, `decisions`, `priorities`, `goals`, and `projects`; the `memory`,
`decisions`, `priorities`, `goals`, and `projects` engines depend on `models`;
`models` is standalone. Outside of the engines' SQLite storage, the package does
not depend on external services.

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
