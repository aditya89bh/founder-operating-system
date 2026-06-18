"""A realistic, deterministic demo dataset for the Founder Operating System.

Each function returns freshly constructed domain records, so callers can load
them into stores without sharing mutable state. Dates and statuses are fixed so
the dataset (and any report built from it) is reproducible.
"""

from __future__ import annotations

from datetime import date

from founder_os.models import (
    GoalRecord,
    GoalStatus,
    GoalTimeframe,
    ProjectRecord,
    ProjectStatus,
)


def demo_goals() -> list[GoalRecord]:
    """Return the demo goals spanning planned, active, and completed work."""
    return [
        GoalRecord(
            title="Launch Founder OS v1",
            description="Ship the first public version of the operating system.",
            timeframe=GoalTimeframe.YEARLY,
            target_date=date(2026, 12, 31),
            status=GoalStatus.ACTIVE,
        ),
        GoalRecord(
            title="Reach 100 users",
            description="Grow to 100 active founders using the system.",
            timeframe=GoalTimeframe.QUARTERLY,
            target_date=date(2026, 9, 30),
            status=GoalStatus.ACTIVE,
        ),
        GoalRecord(
            title="Publish founder essays",
            description="Write and publish a short series of founder essays.",
            timeframe=GoalTimeframe.MONTHLY,
            target_date=date(2026, 7, 31),
            status=GoalStatus.PLANNED,
        ),
        GoalRecord(
            title="Validate the idea",
            description="Confirm there is real demand before building widely.",
            timeframe=GoalTimeframe.QUARTERLY,
            target_date=date(2026, 3, 31),
            status=GoalStatus.COMPLETED,
        ),
    ]


def demo_projects() -> list[ProjectRecord]:
    """Return the demo projects spanning planned, active, and completed work."""
    return [
        ProjectRecord(
            title="Founder OS development",
            description="Build the engines that make up the operating system.",
            status=ProjectStatus.ACTIVE,
            start_date=date(2026, 1, 5),
            target_date=date(2026, 6, 30),
        ),
        ProjectRecord(
            title="Documentation refresh",
            description="Bring the docs in line with the shipped engines.",
            status=ProjectStatus.ACTIVE,
            start_date=date(2026, 5, 1),
            target_date=date(2026, 7, 15),
        ),
        ProjectRecord(
            title="Demo preparation",
            description="Assemble scenarios and a demo dataset for launch.",
            status=ProjectStatus.PLANNED,
            target_date=date(2026, 8, 1),
        ),
        ProjectRecord(
            title="Landing page",
            description="Ship the first marketing landing page.",
            status=ProjectStatus.COMPLETED,
            start_date=date(2026, 1, 1),
            target_date=date(2026, 2, 1),
        ),
    ]
