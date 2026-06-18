"""Validation tests for the repository's documentation and assets."""

from __future__ import annotations

from pathlib import Path

from founder_os.demo import demo_report, demo_stores, load_demo_dataset
from founder_os.reporting.markdown import render_markdown

_ROOT = Path(__file__).resolve().parent.parent


def test_required_documents_exist() -> None:
    required = [
        "README.md",
        "RESULTS.md",
        "CHANGELOG.md",
        "docs/metrics.md",
        "docs/examples.md",
        "docs/architecture.md",
        "docs/architecture.mmd",
        "docs/images/architecture.png",
        "docs/images/workflow.png",
        "examples/sample_report.md",
    ]
    missing = [name for name in required if not (_ROOT / name).exists()]
    assert not missing, f"missing documents: {missing}"


def test_engine_docs_exist() -> None:
    engines = [
        "memory",
        "decision",
        "priority",
        "goal",
        "project",
        "review",
    ]
    for engine in engines:
        assert (_ROOT / "docs" / f"{engine}_engine.md").exists()


def test_readme_references_diagrams_and_demo() -> None:
    readme = (_ROOT / "README.md").read_text()
    assert "## Demo walkthrough" in readme
    assert "docs/images/architecture.png" in readme
    assert "docs/images/workflow.png" in readme
    assert "founder-os demo" in readme


def test_changelog_documents_v1() -> None:
    changelog = (_ROOT / "CHANGELOG.md").read_text()
    assert "[1.0.0]" in changelog


def test_diagram_images_are_non_empty_png() -> None:
    for name in ("architecture.png", "workflow.png"):
        data = (_ROOT / "docs" / "images" / name).read_bytes()
        assert data[:8] == b"\x89PNG\r\n\x1a\n"
        assert len(data) > 1000


def test_sample_report_matches_demo_report() -> None:
    saved = (_ROOT / "examples" / "sample_report.md").read_text().strip()
    with demo_stores() as stores:
        load_demo_dataset(stores)
        generated = render_markdown(demo_report(stores)).strip()
    assert saved == generated
