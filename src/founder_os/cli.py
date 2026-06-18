"""Command-line interface for the Founder Operating System."""

from __future__ import annotations

import typer

app = typer.Typer(
    name="founder-os",
    help="Founder Operating System command-line interface.",
    no_args_is_help=True,
    add_completion=False,
)
