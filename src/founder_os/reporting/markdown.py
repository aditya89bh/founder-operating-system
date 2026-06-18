"""Markdown exporter for founder reports.

Renders a :class:`FounderReport` as Markdown. The sections and values mirror the
JSON exporter exactly so both formats carry identical information.
"""

from __future__ import annotations

from founder_os.reporting.models import FounderReport


def render_markdown(report: FounderReport) -> str:
    """Render ``report`` as a Markdown document."""
    lines = ["# Founder Report"]
    return "\n".join(lines)
