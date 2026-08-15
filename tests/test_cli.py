from pathlib import Path

import pytest

from agent_runbook_lint.cli import main


@pytest.mark.parametrize(
    "report_path",
    [
        lambda source: source,
        lambda source: source.resolve(),
        lambda source: source.parent / "." / source.name,
        lambda source: source.parent / "nested" / ".." / source.name,
    ],
)
def test_report_cannot_overwrite_source_runbook(tmp_path, capsys, report_path):
    source = tmp_path / "runbook.md"
    original = Path("fixtures/good-runbook.md").read_text(encoding="utf-8")
    source.write_text(original, encoding="utf-8")

    result = main(["check", str(source), "--report", str(report_path(source))])

    assert result == 2
    assert "report destination must not be the source runbook" in capsys.readouterr().err
    assert source.read_text(encoding="utf-8") == original


def test_report_still_creates_nested_destination(tmp_path):
    source = tmp_path / "runbook.md"
    source.write_text(
        Path("fixtures/good-runbook.md").read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    destination = tmp_path / "reports" / "nested" / "report.md"

    result = main(["check", str(source), "--report", str(destination)])

    assert result == 0
    assert destination.read_text(encoding="utf-8").startswith("# Agent Runbook Lint Report")
