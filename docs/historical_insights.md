# Historical Insights

The historical insights subsystem introduces time awareness to the Founder
Operating System without any AI. It reads the snapshots already stored by the
review engine and derives a deterministic summary of how the system has evolved
across reviews. It reads stored snapshots only -- it never recomputes historical
state -- and it performs no scoring, forecasting, percentages, or recommendation.

## What it reports

A `HistoricalInsights` record contains:

- `review_count` -- the number of reviews recorded.
- `oldest_review_date` -- the date of the earliest review (or `None`).
- `newest_review_date` -- the date of the most recent review (or `None`).
- `goal_growth`, `project_growth`, `priority_growth`, `decision_growth`,
  `memory_growth` -- the growth of each dimension.

### How growth is defined

Growth is deliberately simple:

```
growth = latest review snapshot - earliest review snapshot
```

The "latest" snapshot is the review with the newest `review_date`; the
"earliest" is the review with the oldest `review_date`. Growth is a plain integer
delta and may be negative (for example, if active goals dropped between reviews).
There are no percentages and no scores.

The goal, project, and priority growth figures use the active counts stored on
each review snapshot (`active_goals`, `active_projects`, `active_priorities`).
Decision and memory growth use the cumulative `decision_count` and
`memory_count`. Because the values come straight from the stored snapshots, the
insights reflect exactly what was true at each review and never change as the
live engines move on.

### Edge cases

- **No reviews:** `review_count` is `0`, both dates are `None`, and every growth
  value is `0`.
- **One review:** the earliest and latest snapshot are the same record, so every
  growth value is `0` and both dates equal that review's date.

## Architecture

The package follows the same focused-module pattern as the other subsystems:

- `founder_os.insights.models` -- the `HistoricalInsights` Pydantic model.
- `founder_os.insights.service` -- `generate_insights`, which reads the review
  store and computes the insights.
- `founder_os.insights.report` -- `render_insights_report`, which turns the
  insights into plain text for the CLI.

The subsystem depends only on the review store's protocol; it reads stored
snapshots and holds no references to the other engines.

## Python usage

```python
from founder_os.insights.report import render_insights_report
from founder_os.insights.service import generate_insights

# review_store must be connected first.
insights = generate_insights(review_store)
print(insights.review_count, insights.goal_growth)
print(render_insights_report(insights))
```

## Command-line usage

The `insights` command group exposes the report. The `--db` option points at the
review database (it defaults to `~/.founder-os/reviews.db`).

```bash
founder-os insights report
```

Example output:

```
Historical insights
  Reviews recorded: 2
  Review range:     2026-01-01 -> 2026-06-01
  Growth since earliest review:
    Goals:      +4
    Projects:   +2
    Priorities: +7
    Decisions:  +16
    Memories:   +25
```

Each growth line is signed so the direction of change is explicit; a negative
value indicates a decrease between the earliest and latest review.

## Founder examples

- **See your trajectory.** Run `founder-os insights report` to see how many
  reviews you have logged and how your active goals, projects, and priorities
  have moved since the first one.
- **Trust the history.** Because insights are computed only from stored review
  snapshots, the same reviews always produce the same report, regardless of the
  current state of the live engines.
