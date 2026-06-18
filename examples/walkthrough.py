"""An end-to-end walkthrough that exercises every engine on the demo dataset.

This loads the full demo dataset into temporary SQLite stores, then runs the
operating loop, historical insights, and reporting subsystems to produce a
:class:`FounderReport`. It uses the engines exactly as built; it adds no new
behavior.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

from founder_os.decisions.sqlite_store import SQLiteDecisionStore
from founder_os.goals.sqlite_store import SQLiteGoalStore
from founder_os.memory.sqlite_store import SQLiteMemoryStore
from founder_os.priorities.sqlite_store import SQLitePriorityStore
from founder_os.projects.sqlite_store import SQLiteProjectStore
from founder_os.reporting.markdown import render_markdown
from founder_os.reporting.models import FounderReport
from founder_os.reporting.service import build_founder_report
from founder_os.reviews.sqlite_store import SQLiteReviewStore

from .datasets import (
    demo_decisions,
    demo_goals,
    demo_memories,
    demo_priorities,
    demo_projects,
    demo_reviews,
)


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


def build_demo_report(stores: DemoStores) -> FounderReport:
    """Build a :class:`FounderReport` from the loaded ``stores``."""
    return build_founder_report(
        goal_store=stores.goals,
        project_store=stores.projects,
        priority_store=stores.priorities,
        decision_store=stores.decisions,
        memory_store=stores.memories,
        review_store=stores.reviews,
    )


def run_walkthrough() -> FounderReport:
    """Load the demo dataset into temporary stores and return a founder report."""
    with TemporaryDirectory() as tmp:
        stores = open_demo_stores(Path(tmp))
        try:
            load_demo_dataset(stores)
            return build_demo_report(stores)
        finally:
            stores.close()


def render_walkthrough_markdown() -> str:
    """Run the walkthrough and render the resulting report as Markdown."""
    return render_markdown(run_walkthrough())
