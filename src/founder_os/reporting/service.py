"""The founder report service.

This module assembles a single, deterministic founder report by combining the
live operating-loop snapshot with the historical insights derived from stored
review snapshots. It only reads and composes existing results; it performs no
scoring, recommendation, forecasting, or AI reasoning.
"""

from __future__ import annotations
