"""Copy-pasteable ``founder-os`` command sequences for the demo scenarios.

These workflows mirror the scenarios using the real CLI. They are stored as
plain command strings so they can be shown in docs and checked by tests; running
them is optional and left to the reader.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CliWorkflow:
    """A named sequence of ``founder-os`` commands telling one story."""

    name: str
    description: str
    commands: list[str]


def cli_workflows() -> list[CliWorkflow]:
    """Return the demo CLI workflows in presentation order."""
    return [
        CliWorkflow(
            name="Start a new company",
            description="Capture the first goal, project, priorities, and decision.",
            commands=[
                'founder-os goal create "Validate the idea" '
                "--timeframe quarterly --status active --target-date 2026-03-31",
                'founder-os project create "Founder OS development" '
                "--status active --start-date 2026-01-05 --target-date 2026-06-30",
                'founder-os priority create "Interview 10 founders" '
                "--category research --urgency 5 --importance 5 --effort 3",
                'founder-os decision create "Bootstrap instead of raising" '
                '--decision "Bootstrap while validating demand" '
                '--rationale "Keeps focus on users, not fundraising"',
                'founder-os memory add "Founders track decisions in scattered notes" '
                "--tag research --tag insight",
            ],
        ),
        CliWorkflow(
            name="Plan a product launch",
            description="Line up the launch goal, projects, and priorities.",
            commands=[
                'founder-os goal create "Launch Founder OS v1" '
                "--timeframe quarterly --status active --target-date 2026-06-30",
                'founder-os project create "Demo preparation" '
                "--status active --start-date 2026-05-15 --target-date 2026-06-25",
                'founder-os priority create "Write launch post" '
                "--category marketing --urgency 5 --importance 4 --effort 2",
                'founder-os decision create "Delay the mobile application" '
                '--decision "Postpone the mobile app until after v1" '
                '--rationale "The CLI already covers the core workflow"',
            ],
        ),
        CliWorkflow(
            name="Review quarterly progress",
            description="Capture reviews, then read the status and insights.",
            commands=[
                'founder-os review create --type weekly --notes "Steady progress"',
                'founder-os review create --type monthly --notes "Engines stabilizing"',
                'founder-os review create --type quarterly --notes "Quarter close"',
                "founder-os status",
                "founder-os insights report",
            ],
        ),
        CliWorkflow(
            name="Handle competing priorities",
            description="Create several priorities and list them by score.",
            commands=[
                'founder-os priority create "Fix data-loss bug" '
                "--category engineering --urgency 5 --importance 5 --effort 2",
                'founder-os priority create "Improve onboarding" '
                "--category product --urgency 4 --importance 5 --effort 3",
                'founder-os priority create "Answer support emails" '
                "--category support --urgency 4 --importance 3 --effort 2",
                "founder-os priority list",
            ],
        ),
        CliWorkflow(
            name="Learn from previous decisions",
            description="Record a decision, then review its outcome later.",
            commands=[
                'founder-os decision create "Open source the project" '
                '--decision "Release under the MIT license" '
                '--rationale "Openness builds trust and invites contributors"',
                "founder-os decision list",
                "founder-os decision update-outcome <decision-id> "
                '--outcome successful --notes "Drove adoption" --review-date 2026-05-01',
                "founder-os report markdown",
            ],
        ),
    ]
