# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-06-18

First public release. The Founder Operating System is feature complete: a
local-first, deterministic system built from six engines and an integration
layer, driven entirely by the `founder-os` CLI.

### Added

- **Foundation.** Typed Pydantic v2 domain models, a Typer CLI skeleton,
  packaging, Ruff + MyPy (strict) + Pytest tooling, CI, and documentation.
- **Memory engine.** SQLite-backed storage with tag filtering, keyword search,
  and a `memory` command group.
- **Decision engine.** SQLite-backed storage and reviewed-outcome tracking, with
  a `decision` command group.
- **Priority engine.** SQLite-backed storage and deterministic ranking by
  `(urgency * importance) / effort`, with a `priority` command group.
- **Goal engine.** SQLite-backed goals with timeframes, target dates, and
  goal-priority alignment, with a `goal` command group.
- **Project engine.** SQLite-backed projects with status and dates, plus
  goal-project alignment, with a `project` command group.
- **Review engine.** Periodic reviews that capture a cross-system point-in-time
  snapshot of every engine, with a `review` command group.
- **Founder operating loop.** A deterministic `FounderSnapshot` with boolean
  health indicators, exposed through `founder-os status`.
- **Historical insights.** Deterministic growth and date-range reporting derived
  only from stored review snapshots, exposed through `founder-os insights report`.
- **Founder report system.** A combined report exported to Markdown and JSON via
  the `founder-os report` command group.
- **Founder scenarios and demo dataset.** A deterministic demo dataset and five
  founder scenarios in the `examples/` package, with an end-to-end walkthrough,
  matching CLI workflows, and a sample report.
- **Release polish.** A self-contained `founder-os demo` command, architecture
  and workflow diagrams, an expanded README, and project documentation
  (`RESULTS.md`, `CHANGELOG.md`, `docs/metrics.md`, release notes).

### Out of scope

No AI, machine learning, embeddings, dashboards, web applications, or hosted
backends. The system is intentionally local-first and deterministic.

[1.0.0]: https://github.com/aditya89bh/founder-operating-system/releases/tag/v1.0.0
