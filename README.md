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
- **Priority** (`PriorityRecord`) — a priority scored by urgency, importance, and effort.
- **Goal** (`GoalRecord`) — a goal pursued over a timeframe, with priorities aligned to it.
- **Project** (`ProjectRecord`) — a body of work that advances a goal; the layer between goals and priorities.
- **Review** (`ReviewRecord`) — a periodic review storing a point-in-time snapshot of the whole system.

Each record is a strictly validated Pydantic v2 model with an opaque identifier
and a UTC creation timestamp.

These concepts compose into a single planning chain — **Goals → Projects →
Priorities → Decisions → Memory** — from long-term intent down to the durable
record of what happened. The review engine sits across the whole chain,
capturing historical snapshots of where everything stands.

## Architecture overview

The project uses a `src` layout with three focused modules:

- `founder_os.version` — the single source of truth for the package version.
- `founder_os.models` — the typed domain models and their validation rules.
- `founder_os.cli` — a Typer command-line application.

Quality is enforced with Ruff (linting), MyPy in strict mode (typing), and Pytest
(tests), all run in CI. See [docs/architecture.md](docs/architecture.md) for a
deeper description of the domain model, module boundaries, and design principles.

### Memory engine

The memory engine (`founder_os.memory`) provides durable storage and retrieval
for memories, backed by SQLite. It defines a `MemoryStore` protocol and a
`SQLiteMemoryStore` implementation supporting create, retrieve, list, tag
filtering, keyword search, and delete. See
[docs/memory_engine.md](docs/memory_engine.md) for full details.

### Decision engine

The decision engine (`founder_os.decisions`) provides durable storage,
retrieval, and outcome tracking for decisions, backed by SQLite. It defines a
`DecisionStore` protocol and a `SQLiteDecisionStore` implementation supporting
create, retrieve, list, delete, and outcome review. See
[docs/decision_engine.md](docs/decision_engine.md) for full details.

### Priority engine

The priority engine (`founder_os.priorities`) provides durable storage,
retrieval, and deterministic ranking for priorities, backed by SQLite. It defines
a `PriorityStore` protocol and a `SQLitePriorityStore` implementation supporting
create, retrieve, list, delete, and ranking by a transparent score of
`(urgency * importance) / effort`. See
[docs/priority_engine.md](docs/priority_engine.md) for full details.

### Goal engine

The goal engine (`founder_os.goals`) provides durable storage and retrieval for
long-term goals, backed by SQLite, plus the relationship storage that aligns
priorities to the goals they serve. It defines a `GoalStore` protocol and a
`SQLiteGoalStore` implementation supporting create, retrieve, list, delete,
priority linking, and goal-priority retrieval. See
[docs/goal_engine.md](docs/goal_engine.md) for full details.

### Project engine

The project engine (`founder_os.projects`) provides durable storage and retrieval
for projects, backed by SQLite, plus the relationship storage that aligns
projects to the goals they advance. It defines a `ProjectStore` protocol and a
`SQLiteProjectStore` implementation supporting create, retrieve, list, delete,
goal linking, and goal-project retrieval. See
[docs/project_engine.md](docs/project_engine.md) for full details.

### Review engine

The review engine (`founder_os.reviews`) is the first cross-system component. It
provides durable storage and retrieval for periodic reviews, backed by SQLite,
plus a snapshot generator that reads the goal, project, priority, decision, and
memory engines to count active and completed work and total decisions and
memories. It defines a `ReviewStore` protocol and a `SQLiteReviewStore`
implementation supporting create, retrieve, list, and delete. Snapshot counts are
computed once and stored, so each review is a frozen historical record. See
[docs/review_engine.md](docs/review_engine.md) for full details.

### Founder Operating Loop

The Founder Operating Loop (`founder_os.operating_loop`) is the first integrated
workflow and the layer that turns the engines into an operating system. It reads
across memory, decisions, priorities, goals, projects, and reviews and assembles
a deterministic `FounderSnapshot` — active goal, project, and priority counts;
recent decision and memory counts; the latest review date; and boolean
`HealthIndicators` that flag missing pieces. It does no scoring or recommendation.
The `founder-os status` command runs the loop and prints a report. See
[docs/founder_operating_loop.md](docs/founder_operating_loop.md) for full details.

The loop models running a company as a continuous cycle: **Observe → Remember →
Decide → Prioritize → Execute → Review → Adapt.**

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

Capture and retrieve memories:

```bash
founder-os memory add "Closed the seed round" --tag fundraising
founder-os memory list
founder-os memory search "seed"
founder-os memory delete <memory-id>
```

Record and review decisions:

```bash
founder-os decision create "Adopt weekly planning" --decision "Plan every Monday"
founder-os decision list
founder-os decision show <decision-id>
founder-os decision update-outcome <decision-id> --outcome successful
```

Capture and rank priorities:

```bash
founder-os priority create "Ship onboarding revamp" --urgency 5 --importance 4 --effort 2
founder-os priority list
founder-os priority list --all
```

Define goals and organize priorities under them:

```bash
founder-os goal create "Reach 100 paying customers" --timeframe yearly --target-date 2026-12-31
founder-os goal list
```

Organize work into projects:

```bash
founder-os project create "Onboarding revamp" --status active --target-date 2026-03-31
founder-os project list
```

Capture a periodic review with a system snapshot:

```bash
founder-os review create --type weekly --notes "Closed the seed round; shipped onboarding."
founder-os review list
```

See the whole system at a glance with the operating loop:

```bash
founder-os status
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

- **Phase 1: Foundation.** Typed domain models, a CLI skeleton with a version
  command, tooling (Ruff, MyPy strict, Pytest), CI, and documentation.
- **Phase 2: Memory engine.** SQLite-backed storage and retrieval for memories,
  with tag filtering, keyword search, and a `memory` CLI command group.
- **Phase 3: Decision engine.** SQLite-backed storage, retrieval, and outcome
  tracking for decisions, with a `decision` CLI command group.
- **Phase 4: Priority engine.** SQLite-backed storage and deterministic ranking
  for priorities using `(urgency * importance) / effort`, with a `priority` CLI
  command group.
- **Phase 5: Goal engine.** SQLite-backed storage for long-term goals with
  timeframes, target dates, and goal-priority alignment, with a `goal` CLI
  command group.
- **Phase 6: Project engine.** SQLite-backed storage for projects with status,
  start and target dates, and goal-project alignment, with a `project` CLI
  command group.
- **Phase 7: Review engine.** SQLite-backed storage for periodic reviews with a
  cross-system snapshot of active and completed goals, projects, and priorities
  plus decision and memory totals, with a `review` CLI command group.
- **Phase 8 (current): Founder Operating Loop.** The first integrated workflow,
  aggregating every engine into a deterministic `FounderSnapshot` with boolean
  health indicators, exposed through the `founder-os status` command.
- **Future phases.** Dashboards and analytics. These remain out of scope for now.

## License

Released under the MIT License.
