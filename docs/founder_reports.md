# Founder Reports

The founder report system is the first founder-facing deliverable of the Founder
Operating System. It combines the live operating-loop snapshot with the
historical insights derived from stored review snapshots into a single,
deterministic report and exports it to Markdown and JSON. The report is
informational only: it carries no advice, recommendations, scoring, forecasting,
or AI reasoning.

## What the report contains

A `FounderReport` pairs two existing results:

- `snapshot` -- the operating-loop `FounderSnapshot` (current state and health).
- `insights` -- the `HistoricalInsights` (historical growth and review history).

Both exporters render the same four sections, in the same order, defined once by
the `ReportSection` enum:

1. **Current State** -- active goal, project, and priority counts; recent
   decision and memory counts; and the latest review date.
2. **Health Indicators** -- the four boolean flags (`no_active_goals`,
   `no_active_projects`, `no_active_priorities`, `no_recent_reviews`).
3. **Historical Growth** -- the growth of goals, projects, priorities,
   decisions, and memories (latest review snapshot minus earliest; may be
   negative).
4. **Review History** -- the number of reviews recorded and the oldest and
   newest review dates.

## Export formats

Two exporters produce identical information in different shapes:

- **Markdown** (`founder_os.reporting.markdown.render_markdown`) -- a headed
  document with one section per `##` heading and bulleted values. Growth values
  are signed (for example `+5` or `-2`) so direction is explicit.
- **JSON** (`founder_os.reporting.json_export.render_json`) -- an object with
  `current_state`, `health_indicators`, `historical_growth`, and `review_history`
  keys. Dates are ISO strings or `null`; growth values are plain integers.

The two formats differ only in presentation; the underlying values are the same.

## Architecture

The package follows the same focused-module pattern as the rest of the system:

- `founder_os.reporting.models` -- the `ReportSection` enum and the
  `FounderReport` model.
- `founder_os.reporting.service` -- `build_founder_report`, which composes the
  snapshot and insights from connected stores.
- `founder_os.reporting.markdown` -- the Markdown exporter.
- `founder_os.reporting.json_export` -- the JSON exporter.

The service depends on the operating loop and insights services (and through
them, the engine storage protocols). It only composes their results; it adds no
analysis of its own.

## Python usage

```python
from founder_os.reporting.json_export import render_json
from founder_os.reporting.markdown import render_markdown
from founder_os.reporting.service import build_founder_report

# Every store must be connected first.
report = build_founder_report(
    goal_store=goal_store,
    project_store=project_store,
    priority_store=priority_store,
    decision_store=decision_store,
    memory_store=memory_store,
    review_store=review_store,
)

print(render_markdown(report))
print(render_json(report))
```

## Command-line usage

The `report` command group exports the founder report. Each command reads every
engine from its default database; any source path can be overridden with its own
option.

```bash
# Export as Markdown
founder-os report markdown

# Export as JSON
founder-os report json
```

Redirect the output to a file to save a report:

```bash
founder-os report markdown > founder-report.md
founder-os report json > founder-report.json
```

## Founder examples

- **Share a status update.** Export the Markdown report and paste it into an
  investor update or a team doc -- it summarizes current state, health, growth,
  and review history in one place.
- **Feed another tool.** Export the JSON report to hand the same information to a
  script or spreadsheet without re-deriving anything.
- **Trust the output.** Because the report only composes the operating-loop
  snapshot and stored review snapshots, the same data always produces the same
  report in both formats.
