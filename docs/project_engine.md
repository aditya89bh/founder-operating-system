# Project Engine

The project engine is the project-management subsystem of the Founder Operating
System. It lets a founder organize work into projects, track their status and
dates, and align projects to the goals they advance. Projects are the execution
layer between goals and priorities. The engine is backed by SQLite and exposes
both a Python API and a command-line interface.

## Architecture

The engine is split into a storage interface and a concrete implementation,
mirroring the pattern established by the memory, decision, priority, and goal
engines:

- `founder_os.projects.store.ProjectStore` — a `Protocol` that defines the
  storage contract: `create_project`, `get_project`, `list_projects`,
  `delete_project`, `link_project_to_goal`, and `get_goal_projects`. Any backend
  that satisfies this protocol can be used.
- `founder_os.projects.sqlite_store.SQLiteProjectStore` — a SQLite-backed
  implementation of the protocol. It manages the connection lifecycle and the
  schema, and can be used as a context manager.

Projects are represented by the `ProjectRecord` model in `founder_os.models`.

### Project fields

- `title` — a short name for the project.
- `description` — optional detail about the work.
- `status` — one of `planned`, `active`, `completed`, or `abandoned` (new
  projects start `planned`).
- `start_date` — an optional date the project starts (or `None`).
- `target_date` — an optional date the project is aimed at (or `None`).
- `id`, `created_at`, and `updated_at` — the identifier and timestamps.

### Goal-project alignment

Projects sit between goals and priorities: a project can belong to zero or one
goal, and a goal can contain many projects. The engine stores this relationship
only; it does not rank, recommend, or otherwise reason about it.

- `link_project_to_goal(project_id, goal_id)` aligns a project with a goal.
  Because a project belongs to at most one goal, re-linking it moves it to the
  new goal rather than creating a second alignment.
- `get_goal_projects(goal_id)` returns the identifiers of the projects aligned
  with a goal. The project engine stores only the alignment, so callers can
  resolve those identifiers against the project records when they need full
  details.

### Storage schema

A `projects` table holds one row per project, with columns for each field above.
Timestamps are stored as ISO 8601 text, `start_date` and `target_date` as ISO
dates (or `NULL`), and `status` as text defaulting to `planned`. A second
`goal_projects` table stores the alignment as a `project_id` (primary key, so one
goal per project) with its `goal_id`. The reference uses `ON DELETE CASCADE` on
`projects`, so deleting a project removes its alignment. Listing returns projects
newest first.

## Python usage

```python
from datetime import date

from founder_os.models import ProjectRecord, ProjectStatus
from founder_os.projects.sqlite_store import SQLiteProjectStore

with SQLiteProjectStore("projects.db") as store:
    project = store.create_project(
        ProjectRecord(
            title="Onboarding revamp",
            description="Rebuild the first-run experience.",
            status=ProjectStatus.ACTIVE,
            start_date=date(2026, 1, 1),
            target_date=date(2026, 3, 31),
        )
    )

    store.get_project(project.id)
    store.list_projects()
    store.link_project_to_goal(project.id, "a-goal-id")
    store.get_goal_projects("a-goal-id")
    store.delete_project(project.id)
```

The store must be connected before use. Using it as a context manager (shown
above) opens the connection on entry and closes it on exit. You can also call
`connect()` and `close()` explicitly.

## Command-line usage

The `project` command group wraps project creation and listing. Each command
accepts a `--db` option pointing at the SQLite database file (it defaults to
`~/.founder-os/projects.db`).

```bash
# Create a project with its status and dates
founder-os project create "Onboarding revamp" \
    --description "Rebuild the first-run experience." \
    --status active \
    --start-date 2026-01-01 \
    --target-date 2026-03-31

# List all projects, newest first
founder-os project list
```

## Founder examples

- **Turn a goal into execution.** Break a goal into one or more projects, then
  align each project to the goal so the path from objective to work is explicit.
- **See the work behind an objective.** Because a project belongs to one goal,
  `get_goal_projects` gives you the projects advancing a given goal.
- **Retire projects cleanly.** Mark a project `completed` or `abandoned`;
  deleting a project automatically clears its goal alignment so nothing dangles.
