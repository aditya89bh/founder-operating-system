"""A self-contained demonstration of the Founder Operating System.

This module powers the ``founder-os demo`` command. It loads a small, fixed
demo dataset into temporary SQLite stores and runs the operating loop, historical
insights, and reporting subsystems against it. It uses the engines exactly as
built and adds no new behavior; everything it touches already exists in the
package. The temporary databases are removed when the demo finishes, so running
it leaves nothing behind.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
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
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reviews.sqlite_store import SQLiteReviewStore


@dataclass
class DemoStores:
    """A bundle of connected SQLite stores, one per engine."""

    goals: SQLiteGoalStore
    projects: SQLiteProjectStore
    priorities: SQLitePriorityStore
    decisions: SQLiteDecisionStore
    memories: SQLiteMemoryStore
    reviews: SQLiteReviewStore

    def close(self) -> None:
        """Close every underlying store connection."""
        self.goals.close()
        self.projects.close()
        self.priorities.close()
        self.decisions.close()
        self.memories.close()
        self.reviews.close()


def open_demo_stores(directory: Path) -> DemoStores:
    """Open and connect one SQLite store per engine inside ``directory``."""
    directory.mkdir(parents=True, exist_ok=True)
    goals = SQLiteGoalStore(directory / "goals.db")
    projects = SQLiteProjectStore(directory / "projects.db")
    priorities = SQLitePriorityStore(directory / "priorities.db")
    decisions = SQLiteDecisionStore(directory / "decisions.db")
    memories = SQLiteMemoryStore(directory / "memories.db")
    reviews = SQLiteReviewStore(directory / "reviews.db")
    for store in (goals, projects, priorities, decisions, memories, reviews):
        store.connect()
    return DemoStores(
        goals=goals,
        projects=projects,
        priorities=priorities,
        decisions=decisions,
        memories=memories,
        reviews=reviews,
    )


@contextmanager
def demo_stores() -> Iterator[DemoStores]:
    """Yield connected demo stores backed by a throwaway temporary directory."""
    with TemporaryDirectory() as tmp:
        stores = open_demo_stores(Path(tmp))
        try:
            yield stores
        finally:
            stores.close()


def demo_goals() -> list[GoalRecord]:
    """Return the demo goals across planned, active, and completed states."""
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
    """Return the demo projects across planned, active, and completed states."""
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
    """Return the demo priorities spanning active, completed, and dropped."""
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
            outcome=DecisionOutcome.SUCCESSFUL,
            outcome_notes="Drove early adoption and useful contributions.",
            review_date=date(2026, 5, 1),
        ),
        DecisionRecord(
            title="Delay the mobile application",
            context="Limited engineering time before the v1 launch.",
            decision="Postpone the mobile app until after v1.",
            rationale="The CLI covers the core workflow for launch.",
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
    """Return the demo reviews as point-in-time snapshots, oldest first."""
    return [
        ReviewRecord(
            review_date=date(2026, 2, 1),
            review_type=ReviewType.WEEKLY,
            notes="Early days: validating the idea and shaping the engines.",
            active_goals=1,
            active_projects=1,
            active_priorities=2,
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


def load_demo_dataset(stores: DemoStores) -> None:
    """Persist the entire demo dataset into ``stores``."""
    for goal in demo_goals():
        stores.goals.create_goal(goal)
    for project in demo_projects():
        stores.projects.create_project(project)
    for priority in demo_priorities():
        stores.priorities.create_priority(priority)
    for decision in demo_decisions():
        stores.decisions.create_decision(decision)
    for memory in demo_memories():
        stores.memories.add_memory(memory)
    for review in demo_reviews():
        stores.reviews.create_review(review)
