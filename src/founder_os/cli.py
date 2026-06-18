"""Command-line interface for the Founder Operating System."""

from __future__ import annotations

import typer

from founder_os.version import __version__

app = typer.Typer(
    name="founder-os",
    help="Founder Operating System command-line interface.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main() -> None:
    """Founder Operating System command-line interface."""


@app.command()
def version() -> None:
    """Print the installed Founder Operating System version."""
    typer.echo(__version__)
