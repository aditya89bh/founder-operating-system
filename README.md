# Founder Operating System

A personal operating system for founders that brings memory, decisions, tasks,
priorities, goals, projects, and reviews into one coherent system.

## Vision

Founders carry an enormous amount of context in their heads: why a decision was
made, what matters most this week, which goals a project serves, and what they
learned along the way. Most of that context lives in scattered notes, chat
threads, and memory. The Founder Operating System is a single, typed system of
record for that context, designed to make a founder's thinking durable,
reviewable, and trustworthy.

## The founder problem

Running a company means making many consequential decisions under uncertainty,
quickly, and with incomplete information. Over time the reasoning behind those
decisions fades, priorities drift, and goals lose their connection to daily work.
The result is repeated mistakes, reactive execution, and lost institutional
memory. The Founder Operating System addresses this by giving each of these
concepts a precise, validated shape so they can be captured once and relied on
later.

## Core concepts

Phase 1 defines the foundational records the system is built on:

- **Memory** (`MemoryRecord`) — a captured note, fact, or observation worth keeping.
- **Decision** (`DecisionRecord`) — a decision with its context and rationale.
- **Priority** (`PriorityRecord`) — a ranked priority that orders attention.
- **Goal** (`GoalRecord`) — a goal pursued over a meaningful horizon, with a lifecycle state.
- **Project** (`ProjectRecord`) — a concrete body of work that advances goals.

Each record is a strictly validated Pydantic v2 model with an opaque identifier
and a UTC creation timestamp.

## Architecture overview

The project uses a `src` layout with three focused modules:

- `founder_os.version` — the single source of truth for the package version.
- `founder_os.models` — the typed domain models and their validation rules.
- `founder_os.cli` — a Typer command-line application.

Quality is enforced with Ruff (linting), MyPy in strict mode (typing), and Pytest
(tests), all run in CI. See [docs/architecture.md](docs/architecture.md) for a
deeper description of the domain model, module boundaries, and design principles.

## Installation

Requires Python 3.11 or newer.

```bash
git clone https://github.com/adityabhatia/founder-operating-system.git
cd founder-operating-system
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quickstart

Check the installed version through the CLI:

```bash
founder-os version
```

Use the domain models directly in Python:

```python
from founder_os.models import DecisionRecord

decision = DecisionRecord(
    title="Adopt weekly planning",
    context="Execution felt reactive.",
    decision="Run a structured weekly planning session every Monday.",
    rationale="A fixed cadence reduces context switching.",
)
print(decision.id, decision.created_at)
```

Run the checks locally:

```bash
ruff check .
mypy src
pytest
```

## Roadmap

- **Phase 1 (current): Foundation.** Typed domain models, a CLI skeleton with a
  version command, tooling (Ruff, MyPy strict, Pytest), CI, and documentation.
- **Future phases.** Persistence, memory retrieval and search, decision workflows,
  priority scoring, goal and project tracking, reviews, and dashboards. These are
  intentionally out of scope for Phase 1.

## License

Released under the MIT License.
