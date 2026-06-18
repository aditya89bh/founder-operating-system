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
    ReviewType,
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


def product_launch_scenario() -> Scenario:
    """A founder planning a product launch: goal, project, and launch priorities."""
    return Scenario(
        name="Founder planning a product launch",
        description=(
            "The v1 launch is approaching. The founder lines up the launch "
            "goal, a dedicated project, the priorities that must land first, "
            "and the decision to defer non-essential work."
        ),
        goals=[
            GoalRecord(
                title="Launch Founder OS v1",
                description="Ship the first public version to early founders.",
                timeframe=GoalTimeframe.QUARTERLY,
                target_date=date(2026, 6, 30),
                status=GoalStatus.ACTIVE,
            ),
        ],
        projects=[
            ProjectRecord(
                title="Demo preparation",
                description="Build scenarios and a demo dataset for launch.",
                status=ProjectStatus.ACTIVE,
                start_date=date(2026, 5, 15),
                target_date=date(2026, 6, 25),
            ),
            ProjectRecord(
                title="Documentation refresh",
                description="Make the docs launch-ready.",
                status=ProjectStatus.ACTIVE,
                start_date=date(2026, 5, 1),
                target_date=date(2026, 6, 20),
            ),
        ],
        priorities=[
            PriorityRecord(
                title="Write launch post",
                description="Draft and publish the announcement.",
                category="marketing",
                urgency=5,
                importance=4,
                effort=2,
                status=PriorityStatus.ACTIVE,
            ),
            PriorityRecord(
                title="Improve onboarding",
                description="Smooth the first-run experience before launch.",
                category="product",
                urgency=4,
                importance=5,
                effort=3,
                status=PriorityStatus.ACTIVE,
            ),
        ],
        decisions=[
            DecisionRecord(
                title="Delay the mobile application",
                context="Limited time before the launch date.",
                decision="Postpone the mobile app until after v1.",
                rationale="The CLI already covers the core workflow.",
                outcome=DecisionOutcome.PENDING,
            ),
        ],
        memories=[
            MemoryRecord(
                content="Launch observation: clear docs drove most early signups.",
                tags=["launch", "docs"],
            ),
        ],
    )


def quarterly_review_scenario() -> Scenario:
    """A founder reviewing quarterly progress across recorded reviews."""
    return Scenario(
        name="Founder reviewing quarterly progress",
        description=(
            "The quarter is closing. The founder looks back across the weekly "
            "and monthly reviews captured so far and records a quarterly review "
            "snapshot of where the system stands."
        ),
        goals=[
            GoalRecord(
                title="Reach 100 users",
                description="Grow to 100 active founders this quarter.",
                timeframe=GoalTimeframe.QUARTERLY,
                target_date=date(2026, 9, 30),
                status=GoalStatus.ACTIVE,
            ),
        ],
        reviews=[
            ReviewRecord(
                review_date=date(2026, 4, 6),
                review_type=ReviewType.WEEKLY,
                notes="Steady progress; onboarding still rough.",
                active_goals=2,
                active_projects=2,
                active_priorities=3,
                decision_count=3,
                memory_count=4,
            ),
            ReviewRecord(
                review_date=date(2026, 5, 4),
                review_type=ReviewType.MONTHLY,
                notes="Engines stabilizing; docs catching up.",
                active_goals=2,
                completed_goals=1,
                active_projects=2,
                completed_projects=1,
                active_priorities=3,
                decision_count=4,
                memory_count=5,
            ),
            ReviewRecord(
                review_date=date(2026, 6, 30),
                review_type=ReviewType.QUARTERLY,
                notes="Quarter close: launch-ready and growing.",
                active_goals=2,
                completed_goals=1,
                active_projects=2,
                completed_projects=1,
                active_priorities=3,
                completed_priorities=1,
                decision_count=5,
                memory_count=6,
            ),
        ],
    )


def competing_priorities_scenario() -> Scenario:
    """A founder handling competing priorities ranked by the score formula."""
    return Scenario(
        name="Founder handling competing priorities",
        description=(
            "Too much to do and not enough time. Several active priorities "
            "compete for attention; the deterministic score "
            "(urgency * importance / effort) makes the order explicit."
        ),
        goals=[
            GoalRecord(
                title="Launch Founder OS v1",
                description="Keep the launch on track despite competing work.",
                timeframe=GoalTimeframe.QUARTERLY,
                target_date=date(2026, 6, 30),
                status=GoalStatus.ACTIVE,
            ),
        ],
        priorities=[
            PriorityRecord(
                title="Fix data-loss bug",
                description="A rare bug can drop a record on shutdown.",
                category="engineering",
                urgency=5,
                importance=5,
                effort=2,
                status=PriorityStatus.ACTIVE,
            ),
            PriorityRecord(
                title="Improve onboarding",
                description="First-run experience needs polish.",
                category="product",
                urgency=4,
                importance=5,
                effort=3,
                status=PriorityStatus.ACTIVE,
            ),
            PriorityRecord(
                title="Answer support emails",
                description="A backlog of user questions is building up.",
                category="support",
                urgency=4,
                importance=3,
                effort=2,
                status=PriorityStatus.ACTIVE,
            ),
            PriorityRecord(
                title="Redesign the logo",
                description="A nicer logo would be pleasant to have.",
                category="brand",
                urgency=2,
                importance=2,
                effort=4,
                status=PriorityStatus.ACTIVE,
            ),
        ],
        memories=[
            MemoryRecord(
                content="Lesson: ranking priorities by score keeps focus on impact.",
                tags=["lessons", "prioritization"],
            ),
        ],
    )
