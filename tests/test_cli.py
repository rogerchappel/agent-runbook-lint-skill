from pathlib import Path

import pytest

from agent_runbook_lint.cli import main


def _missing(path):
    return path


def _directory(path):
    path.mkdir()
    return path


def _non_utf8(path):
    path.write_bytes(b"\xff")
    return path


def _blocked_parent(path):
    parent_file = path.parent / "file"
    parent_file.write_text("occupied", encoding="utf-8")
    return parent_file / path.name


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


@pytest.mark.parametrize(
    ("input_factory", "diagnostic"),
    [
        (_missing, "file does not exist"),
        (_directory, "is a directory"),
        (_non_utf8, "is not valid UTF-8"),
    ],
)
def test_runbook_read_errors_are_concise(tmp_path, capsys, input_factory, diagnostic):
    source = input_factory(tmp_path / "runbook.md")

    result = main(["check", str(source)])

    captured = capsys.readouterr()
    assert result == 2
    assert captured.out == ""
    assert captured.err == f"error: cannot read runbook '{source}': {diagnostic}\n"
    assert "Traceback" not in captured.err


@pytest.mark.parametrize(
    ("destination_factory", "diagnostic"),
    [
        (_directory, "is a directory"),
        (_blocked_parent, "path component is not a directory"),
    ],
)
def test_report_write_errors_are_concise(
    tmp_path, capsys, destination_factory, diagnostic
):
    source = Path("fixtures/good-runbook.md")
    destination = destination_factory(tmp_path / "report.md")

    result = main(["check", str(source), "--report", str(destination)])

    captured = capsys.readouterr()
    assert result == 2
    assert captured.out == ""
    assert captured.err == f"error: cannot write report '{destination}': {diagnostic}\n"
    assert "Traceback" not in captured.err
