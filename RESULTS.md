# Results

A summary of what the Founder Operating System is at v1.0.0: a local-first,
deterministic operating system for founders built from independent engines and a
thin integration layer. No AI, no network services, no dashboards.

## Architecture summary

The system is organized in three layers:

- **Interface and models.** A Typer CLI (`founder-os`) on top, and a set of
  strictly validated Pydantic v2 domain models (`founder_os.models`) underneath.
- **Engines.** Six independent, SQLite-backed engines, each exposing a `Store`
  protocol and a concrete `SQLite*Store` implementation.
- **Integration layer.** Three read-only subsystems that compose the engines:
  the operating loop (`FounderSnapshot` + health indicators), historical insights
  (growth across reviews), and the founder report (Markdown + JSON).

The diagram source is in [docs/architecture.mmd](docs/architecture.mmd) and the
rendered image is in [docs/images/architecture.png](docs/images/architecture.png).

## Engine summary

| Engine | Module | Responsibility |
| --- | --- | --- |
| Memory | `founder_os.memory` | Store, search, tag, and delete memories. |
| Decision | `founder_os.decisions` | Record decisions and track reviewed outcomes. |
| Priority | `founder_os.priorities` | Capture and rank priorities by `(urgency * importance) / effort`. |
| Goal | `founder_os.goals` | Define goals and align priorities to them. |
| Project | `founder_os.projects` | Organize work into projects and align them to goals. |
| Review | `founder_os.reviews` | Capture periodic point-in-time snapshots of every engine. |

Integration subsystems: `founder_os.operating_loop`, `founder_os.insights`, and
`founder_os.reporting`, plus the self-contained `founder_os.demo`.

## Test summary

- Test framework: Pytest, with Ruff (lint) and MyPy (strict typing) in CI.
- Coverage spans every engine's store, the snapshot generator, the operating
  loop, historical insights, the reporting exporters, the CLI, the bundled
  examples, and the demo.
- All checks pass: `ruff check .`, `mypy src`, and `pytest`.

See [docs/metrics.md](docs/metrics.md) for exact counts.

## CLI summary

The `founder-os` CLI exposes one command group per engine plus integration
commands:

- `founder-os memory` — `add`, `list`, `search`, `delete`
- `founder-os decision` — `create`, `list`, `show`, `update-outcome`
- `founder-os priority` — `create`, `list`
- `founder-os goal` — `create`, `list`
- `founder-os project` — `create`, `list`
- `founder-os review` — `create`, `list`
- `founder-os insights report`
- `founder-os report` — `markdown`, `json`
- `founder-os status` — the operating-loop status report
- `founder-os demo` — a safe, self-contained end-to-end demonstration
- `founder-os version` — the installed version
