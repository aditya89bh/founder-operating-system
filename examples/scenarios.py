"""Realistic founder scenarios built on the existing engines.

Each scenario is a self-contained :class:`Scenario` describing a moment in a
founder's journey using only the domain records the system already defines. The
scenarios add no new behavior; they are curated inputs that demonstrate how the
engines work together.
"""

from __future__ import annotations

from dataclasses import dataclass, field
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
)


@dataclass(frozen=True)
class Scenario:
    """A named, self-contained slice of founder data for demonstration."""

    name: str
    description: str
    goals: list[GoalRecord] = field(default_factory=list)
    projects: list[ProjectRecord] = field(default_factory=list)
    priorities: list[PriorityRecord] = field(default_factory=list)
    decisions: list[DecisionRecord] = field(default_factory=list)
    memories: list[MemoryRecord] = field(default_factory=list)
    reviews: list[ReviewRecord] = field(default_factory=list)


def founder_startup_scenario() -> Scenario:
    """A founder starting a new company: first goals, project, and decisions."""
    return Scenario(
        name="Founder starts a new company",
        description=(
            "The earliest days. The founder sets a first goal, spins up an "
            "initial project, captures a few priorities, and records the "
            "founding decisions and observations."
        ),
        goals=[
            GoalRecord(
                title="Validate the idea",
                description="Talk to founders and confirm the problem is real.",
                timeframe=GoalTimeframe.QUARTERLY,
                target_date=date(2026, 3, 31),
                status=GoalStatus.ACTIVE,
            ),
            GoalRecord(
                title="Launch Founder OS v1",
                description="Ship a first usable version of the system.",
                timeframe=GoalTimeframe.YEARLY,
                target_date=date(2026, 12, 31),
                status=GoalStatus.PLANNED,
            ),
        ],
        projects=[
            ProjectRecord(
                title="Founder OS development",
                description="Stand up the first engines of the system.",
                status=ProjectStatus.ACTIVE,
                start_date=date(2026, 1, 5),
                target_date=date(2026, 6, 30),
            ),
        ],
        priorities=[
            PriorityRecord(
                title="Interview 10 founders",
                description="Run problem-discovery interviews.",
                category="research",
                urgency=5,
                importance=5,
                effort=3,
                status=PriorityStatus.ACTIVE,
            ),
            PriorityRecord(
                title="Set up the repository",
                description="Create the project skeleton and tooling.",
                category="engineering",
                urgency=4,
                importance=4,
                effort=2,
                status=PriorityStatus.ACTIVE,
            ),
        ],
        decisions=[
            DecisionRecord(
                title="Bootstrap instead of raising",
                context="Deciding how to fund the earliest work.",
                decision="Bootstrap the company while validating demand.",
                rationale="Keeps focus on users rather than fundraising.",
                outcome=DecisionOutcome.PENDING,
            ),
        ],
        memories=[
            MemoryRecord(
                content="First interview: founders track decisions in scattered notes.",
                tags=["research", "insight"],
            ),
        ],
    )
