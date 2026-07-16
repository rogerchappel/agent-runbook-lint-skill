from pathlib import Path

from agent_runbook_lint import lint_runbook


def test_good_runbook_passes():
    report = lint_runbook(Path("fixtures/good-runbook.md"))
    assert report.passed, report.to_markdown()


def test_bad_runbook_fails_required_topics():
    report = lint_runbook(Path("fixtures/bad-runbook.md"))
    assert not report.passed
    assert "risky actions need approval gate" in report.to_markdown()

