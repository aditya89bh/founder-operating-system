"""The operating loop service.

This module aggregates the state of every engine into a single
:class:`~founder_os.operating_loop.models.FounderSnapshot`. Each engine has its
own focused aggregation helper; together they form the deterministic workflow
that turns the collection of engines into one operating system. No scoring,
ranking, recommendation, or AI reasoning happens here -- only counting and
direct reads.
"""

from __future__ import annotations

# The number of most-recent records treated as "recent" activity for an engine.
DEFAULT_RECENT_LIMIT = 5
