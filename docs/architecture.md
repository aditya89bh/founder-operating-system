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
| `PriorityRecord` | A ranked priority that orders where attention should go.          |
| `GoalRecord`     | A goal pursued over a meaningful horizon, with a lifecycle state. |
| `ProjectRecord`  | A concrete body of work that advances one or more goals.          |

Shared conventions across records:

- Every record carries an opaque string `id`, generated from a UUID when omitted.
- Every record carries a timezone-aware UTC `created_at` timestamp.
- Models forbid unknown fields (`extra="forbid"`) so malformed input fails fast.
- Lifecycle states (`GoalStatus`, `ProjectStatus`) are modeled as string enums.

## Module boundaries

The package is split into focused modules with clear responsibilities:

- `founder_os.version` — single source of truth for the package version.
- `founder_os.models` — the typed domain models and their validation rules.
- `founder_os.cli` — the Typer application and command wiring.

Dependencies flow in one direction. `cli` depends on `version`; `models` is
standalone. Nothing in the package depends on I/O, a database, or external
services in Phase 1.

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
