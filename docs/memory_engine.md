# Memory Engine

The memory engine is the storage subsystem of the Founder Operating System. It
lets a founder capture memories and later retrieve, search, filter, and delete
them. It is backed by SQLite and exposes both a Python API and a command-line
interface.

## Architecture

The engine is split into a storage interface and a concrete implementation:

- `founder_os.memory.store.MemoryStore` — a `Protocol` that defines the storage
  contract: `add_memory`, `get_memory`, `list_memories`, `search_memories`, and
  `delete_memory`. Any backend that satisfies this protocol can be used.
- `founder_os.memory.sqlite_store.SQLiteMemoryStore` — a SQLite-backed
  implementation of the protocol. It manages the connection lifecycle and the
  schema, and can be used as a context manager.

Memories are represented by the `MemoryRecord` model defined in
`founder_os.models`, which carries an `id`, `content`, `tags`, and a UTC
`created_at` timestamp.

### Storage schema

Two tables hold the data:

- `memories` — one row per memory: `id` (primary key), `content`, and
  `created_at` (ISO 8601 text).
- `memory_tags` — one row per (memory, tag) pair, with a foreign key back to
  `memories(id)` using `ON DELETE CASCADE`, so deleting a memory removes its
  tags. Foreign key enforcement is enabled per connection.

Listing and searching return memories newest first. Searching matches a keyword
against memory content using a `LIKE` query whose wildcard characters are
escaped, so search terms are matched literally.

## Python usage

```python
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.models import MemoryRecord

with SQLiteMemoryStore("memory.db") as store:
    record = store.add_memory(
        MemoryRecord(content="Closed the seed round", tags=["fundraising"])
    )

    store.get_memory(record.id)
    store.list_memories(tag="fundraising")
    store.search_memories("seed")
    store.delete_memory(record.id)
```

The store must be connected before use. Using it as a context manager (shown
above) opens the connection on entry and closes it on exit. You can also call
`connect()` and `close()` explicitly.

## Command-line usage

The `memory` command group wraps the same operations. Each command accepts a
`--db` option pointing at the SQLite database file (it defaults to
`~/.founder-os/memory.db`).

```bash
# Add a memory with two tags
founder-os memory add "Closed the seed round" --tag fundraising --tag milestone

# List all memories, or only those with a given tag
founder-os memory list
founder-os memory list --tag fundraising

# Search memory content by keyword, optionally restricted to a tag
founder-os memory search "seed"
founder-os memory search "seed" --tag fundraising

# Delete a memory by id
founder-os memory delete <memory-id>
```

`memory add` prints the new memory's identifier. `memory list` and
`memory search` print one memory per line, newest first, including the id,
timestamp, tags, and content. `memory delete` reports whether a memory was
removed and exits with a non-zero status if no matching memory was found.
