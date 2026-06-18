"""A realistic, deterministic demo dataset for the Founder Operating System.

Each function returns freshly constructed domain records, so callers can load
them into stores without sharing mutable state. Dates and statuses are fixed so
the dataset (and any report built from it) is reproducible.
"""

from __future__ import annotations

from datetime import date

from founder_os.models import (
    DecisionOutcome,
    DecisionRecord,
    GoalRecord,
    GoalStatus,
    GoalTimeframe,
    MemoryRecord,
    PriorityRecord,
    PriorityStatus,
    ProjectRecord,
    ProjectStatus,
    ReviewRecord,
    ReviewType,
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


def demo_priorities() -> list[PriorityRecord]:
    """Return the demo priorities with deterministic urgency, importance, effort."""
    return [
        PriorityRecord(
            title="Finish review engine",
            description="Complete the review subsystem so reviews can be captured.",
            category="engineering",
            urgency=5,
            importance=5,
            effort=2,
            status=PriorityStatus.ACTIVE,
        ),
        PriorityRecord(
            title="Improve onboarding",
            description="Reduce friction in the first-run experience.",
            category="product",
            urgency=4,
            importance=5,
            effort=3,
            status=PriorityStatus.ACTIVE,
        ),
        PriorityRecord(
            title="Create examples",
            description="Write realistic scenarios and a demo dataset.",
            category="docs",
            urgency=3,
            importance=4,
            effort=2,
            status=PriorityStatus.ACTIVE,
        ),
        PriorityRecord(
            title="Refactor logging",
            description="Tidy logging that is not blocking the launch.",
            category="engineering",
            urgency=2,
            importance=2,
            effort=4,
            status=PriorityStatus.DROPPED,
        ),
        PriorityRecord(
            title="Write launch post",
            description="Draft and publish the launch announcement.",
            category="marketing",
            urgency=4,
            importance=3,
            effort=2,
            status=PriorityStatus.COMPLETED,
        ),
    ]


def demo_decisions() -> list[DecisionRecord]:
    """Return the demo decisions, including reviewed outcomes to learn from."""
    return [
        DecisionRecord(
            title="Open source the project",
            context="Weighing community trust against losing some control.",
            decision="Release Founder OS under the MIT license.",
            rationale="Openness builds trust and invites contributors early.",
            assumptions="Founders prefer tools they can inspect and self-host.",
            outcome=DecisionOutcome.SUCCESSFUL,
            outcome_notes="Drove early adoption and useful contributions.",
            review_date=date(2026, 5, 1),
        ),
        DecisionRecord(
            title="Delay the mobile application",
            context="Limited engineering time before the v1 launch.",
            decision="Postpone the mobile app until after v1.",
            rationale="The CLI covers the core workflow for launch.",
            assumptions="Early founders are comfortable in a terminal.",
            outcome=DecisionOutcome.PENDING,
        ),
        DecisionRecord(
            title="Adopt weekly planning",
            context="Execution felt reactive and unfocused.",
            decision="Run a structured weekly planning session every Monday.",
            rationale="A fixed cadence reduces context switching.",
            outcome=DecisionOutcome.SUCCESSFUL,
            outcome_notes="Priorities became clearer week to week.",
            review_date=date(2026, 4, 1),
        ),
        DecisionRecord(
            title="Use SQLite for storage",
            context="Choosing a persistence layer for the engines.",
            decision="Store each engine's data in local SQLite databases.",
            rationale="Zero-config, file-based, and easy to reason about.",
            outcome=DecisionOutcome.SUCCESSFUL,
            outcome_notes="Kept the system dependency-light and portable.",
            review_date=date(2026, 3, 15),
        ),
        DecisionRecord(
            title="Skip a hosted backend for v1",
            context="Considered a sync service for the first release.",
            decision="Ship a local-only v1 with no hosted backend.",
            rationale="Avoids operational burden while validating demand.",
            outcome=DecisionOutcome.MIXED,
            outcome_notes="Simpler to ship, but some users wanted sync.",
            review_date=date(2026, 6, 1),
        ),
    ]


def demo_memories() -> list[MemoryRecord]:
    """Return the demo memories: feedback, lessons, and launch observations."""
    return [
        MemoryRecord(
            content="User feedback: onboarding felt confusing on first run.",
            tags=["feedback", "onboarding"],
        ),
        MemoryRecord(
            content="Product lesson: shipping smaller increments built momentum.",
            tags=["lessons", "product"],
        ),
        MemoryRecord(
            content="Launch observation: clear docs drove most early signups.",
            tags=["launch", "docs"],
        ),
        MemoryRecord(
            content="Investor call: focus the story on the operating loop.",
            tags=["fundraising"],
        ),
        MemoryRecord(
            content="Engineering note: timezone handling caused a subtle bug.",
            tags=["engineering", "lessons"],
        ),
        MemoryRecord(
            content="Support theme: founders want an at-a-glance status view.",
            tags=["feedback", "product"],
        ),
    ]


def demo_reviews() -> list[ReviewRecord]:
    """Return the demo reviews as point-in-time snapshots, oldest first.

    The snapshot counts climb over time so historical insights show real growth
    between the earliest and latest review.
    """
    return [
        ReviewRecord(
            review_date=date(2026, 2, 1),
            review_type=ReviewType.WEEKLY,
            notes="Early days: validating the idea and shaping the engines.",
            active_goals=1,
            completed_goals=0,
            active_projects=1,
            completed_projects=0,
            active_priorities=2,
            completed_priorities=0,
            decision_count=1,
            memory_count=2,
        ),
        ReviewRecord(
            review_date=date(2026, 3, 1),
            review_type=ReviewType.MONTHLY,
            notes="Idea validated; expanding the roadmap.",
            active_goals=2,
            completed_goals=1,
            active_projects=1,
            completed_projects=1,
            active_priorities=2,
            completed_priorities=0,
            decision_count=2,
            memory_count=3,
        ),
        ReviewRecord(
            review_date=date(2026, 5, 1),
            review_type=ReviewType.WEEKLY,
            notes="Engines coming together ahead of the launch.",
            active_goals=2,
            completed_goals=1,
            active_projects=2,
            completed_projects=1,
            active_priorities=3,
            completed_priorities=1,
            decision_count=4,
            memory_count=5,
        ),
        ReviewRecord(
            review_date=date(2026, 6, 1),
            review_type=ReviewType.MONTHLY,
            notes="Launch preparation in full swing.",
            active_goals=2,
            completed_goals=1,
            active_projects=2,
            completed_projects=1,
            active_priorities=3,
            completed_priorities=1,
            decision_count=5,
            memory_count=6,
        ),
        ReviewRecord(
            review_date=date(2026, 6, 15),
            review_type=ReviewType.QUARTERLY,
            notes="Quarter close: steady growth across the system.",
            active_goals=2,
            completed_goals=1,
            active_projects=2,
            completed_projects=1,
            active_priorities=3,
            completed_priorities=1,
            decision_count=5,
            memory_count=6,
        ),
    ]
