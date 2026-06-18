# Priority Engine

The priority engine is the priority-management subsystem of the Founder
Operating System. It lets a founder capture priorities, describe how urgent and
important they are and how much effort they take, and rank them deterministically
so the most valuable work surfaces first. It is backed by SQLite and exposes both
a Python API and a command-line interface.

## Architecture

The engine is split into a storage interface and a concrete implementation,
mirroring the pattern established by the memory and decision engines:

- `founder_os.priorities.store.PriorityStore` — a `Protocol` that defines the
  storage contract: `create_priority`, `get_priority`, `list_priorities`,
  `delete_priority`, and `rank_priorities`. Any backend that satisfies this
  protocol can be used.
- `founder_os.priorities.sqlite_store.SQLitePriorityStore` — a SQLite-backed
  implementation of the protocol. It manages the connection lifecycle and the
  schema, and can be used as a context manager.

Priorities are represented by the `PriorityRecord` model in `founder_os.models`,
which carries the descriptive fields plus the three integer inputs used to score
and rank them.

### Priority fields

- `title` — a short name for the priority.
- `description` — optional detail about the work.
- `category` — a grouping label (e.g. `product`, `hiring`).
- `urgency` — how time-sensitive it is, on a `1`–`5` scale.
- `importance` — how much it matters, on a `1`–`5` scale.
- `effort` — how much effort it takes, on a `1`–`5` scale.
- `status` — one of `active`, `completed`, or `dropped` (new priorities start
  `active`).
- `id`, `created_at`, and `updated_at` — the identifier and timestamps.

### Priority score

Scoring is deterministic and fully transparent. There is no AI and no learned
ranking. The score is computed as:

```
score = (urgency * importance) / effort
```

A higher score means the priority deserves attention sooner. Because `effort` is
constrained to be at least `1`, the score is always defined. The `score` is a
read-only property on `PriorityRecord`, so it always reflects the current inputs.

### Ranking

`rank_priorities` returns the `active` priorities ordered by score, highest
first. Completed and dropped priorities are excluded from the ranking. Ties keep
the underlying newest-first ordering, so the ranking is fully deterministic for a
given set of stored priorities.

### Storage schema

A single `priorities` table holds one row per priority, with columns for each of
the fields above. Timestamps are stored as ISO 8601 text, `status` as text
defaulting to `active`, and `urgency`, `importance`, and `effort` as integers
defaulting to `3`. Listing returns priorities newest first.

## Python usage

```python
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.models import PriorityRecord

with SQLitePriorityStore("priorities.db") as store:
    record = store.create_priority(
        PriorityRecord(
            title="Ship onboarding revamp",
            description="Reduce time-to-value for new users.",
            category="product",
            urgency=5,
            importance=4,
            effort=2,
        )
    )

    store.get_priority(record.id)
    store.list_priorities()
    store.rank_priorities()
    store.delete_priority(record.id)
```

The store must be connected before use. Using it as a context manager (shown
above) opens the connection on entry and closes it on exit. You can also call
`connect()` and `close()` explicitly.

## Command-line usage

The `priority` command group wraps the same operations. Each command accepts a
`--db` option pointing at the SQLite database file (it defaults to
`~/.founder-os/priorities.db`).

```bash
# Capture a priority with its ranking inputs
founder-os priority create "Ship onboarding revamp" \
    --description "Reduce time-to-value for new users." \
    --category product \
    --urgency 5 \
    --importance 4 \
    --effort 2

# List active priorities ranked by score, highest first (default)
founder-os priority list

# List every priority, newest first, regardless of status
founder-os priority list --all
```

## Founder examples

- **Decide what to work on next.** Capture each candidate as a priority with an
  honest urgency, importance, and effort, then run `priority list` to see them
  ranked by score.
- **Compare quick wins against big bets.** A high-importance, low-effort task
  scores higher than an equally important task that takes more effort, so cheap
  high-impact work rises to the top.
- **Keep the list focused.** Mark finished work `completed` and abandoned work
  `dropped`; ranking only considers `active` priorities, so the ranked view stays
  about what is still live.
