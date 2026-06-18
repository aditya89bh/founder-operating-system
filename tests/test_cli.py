"""Tests for the Founder Operating System command-line interface."""

from __future__ import annotations

from typer.testing import CliRunner

from founder_os.cli import app
from founder_os.version import __version__

runner = CliRunner()


def test_help_lists_application() -> None:
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "Founder Operating System" in result.output


def test_version_command_prints_version() -> None:
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.output
