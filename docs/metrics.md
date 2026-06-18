# Project metrics

A snapshot of the Founder Operating System at v1.0.0. These figures are simple,
verifiable counts; reproduce them with the commands listed below.

| Metric | Count |
| --- | --- |
| Tests | 123 |
| Source files (`src/founder_os`) | 37 |
| Test files (`tests`) | 15 |
| CLI commands | 22 |
| CLI command groups | 8 |
| Engines | 6 |
| Integration subsystems | 3 |
| Example modules (`examples`) | 5 |
| Documentation pages (`docs`) | 13 |

## CLI commands

The 22 commands span 8 engine and integration groups plus three top-level
commands:

- `memory`: `add`, `list`, `search`, `delete`
- `decision`: `create`, `list`, `show`, `update-outcome`
- `priority`: `create`, `list`
- `goal`: `create`, `list`
- `project`: `create`, `list`
- `review`: `create`, `list`
- `insights`: `report`
- `report`: `markdown`, `json`
- top-level: `status`, `demo`, `version`

## Reproducing the counts

```bash
# Tests
pytest --collect-only -q | tail -1

# Source and test files
find src -name "*.py" | wc -l
find tests -name "test_*.py" | wc -l

# Example modules and documentation pages
find examples -name "*.py" | wc -l
ls docs/*.md | wc -l
```
