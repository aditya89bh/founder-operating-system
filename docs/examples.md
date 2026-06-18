# Examples: Founder Scenarios and Demo Dataset

The `examples/` package contains a realistic, deterministic demo dataset and a
set of founder scenarios that demonstrate the complete Founder Operating System.
It adds no new engines, databases, or behavior; it only constructs domain
records and exercises the existing stores, operating loop, insights, and
reporting subsystems.

## Layout

| Module | Purpose |
| --- | --- |
| `examples/datasets.py` | Demo goals, projects, priorities, decisions, memories, and reviews. |
| `examples/scenarios.py` | Five self-contained founder scenarios. |
| `examples/walkthrough.py` | Loads the dataset into temporary stores and builds a report. |
| `examples/cli_workflows.py` | Copy-pasteable `founder-os` command sequences. |
| `examples/sample_report.md` | The Markdown report produced by the walkthrough. |

## Demo dataset

Each function in `examples/datasets.py` returns freshly constructed records, so
callers can load them into stores without sharing mutable state. Dates and
statuses are fixed, so any report built from the dataset is reproducible.

- `demo_goals()` — four goals across planned, active, and completed states.
- `demo_projects()` — four projects across planned, active, and completed states.
- `demo_priorities()` — five priorities spanning active, completed, and dropped.
- `demo_decisions()` — five decisions with reviewed outcomes to learn from.
- `demo_memories()` — six memories: feedback, lessons, and launch observations.
- `demo_reviews()` — five review snapshots, oldest first, with growing counts.

## Scenarios

`examples/scenarios.py` exposes a frozen `Scenario` dataclass and five scenarios
via `all_scenarios()`:

1. **Founder starts a new company** — first goals, project, priorities, and decisions.
2. **Founder planning a product launch** — launch goal, projects, and priorities.
3. **Founder reviewing quarterly progress** — weekly, monthly, and quarterly reviews.
4. **Founder handling competing priorities** — priorities ranked by score.
5. **Founder learning from previous decisions** — reviewed outcomes and lessons.

Each scenario is a curated slice of domain records. It can be loaded into any set
of stores and then read back through the operating loop, insights, and reporting
engines exactly like real data.

## End-to-end walkthrough

`examples/walkthrough.py` ties everything together:

```python
from examples.walkthrough import run_walkthrough, render_walkthrough_markdown

report = run_walkthrough()          # FounderReport built from the full dataset
print(render_walkthrough_markdown())  # the same report rendered as Markdown
```

`run_walkthrough()` opens one temporary SQLite store per engine, loads the demo
dataset, and assembles a `FounderReport` using `build_founder_report`. The
temporary stores are removed afterwards, so the walkthrough leaves no files
behind.

## Sample report

`examples/sample_report.md` is the exact Markdown output of the walkthrough. It
is checked in so the expected report is easy to review, and a test asserts that
the committed file still matches what the code produces.

## CLI workflows

`examples/cli_workflows.py` mirrors the scenarios using the real `founder-os`
CLI. The commands are stored as plain strings for documentation and testing;
running them is optional. See `cli_workflows()` for the full sequences.
