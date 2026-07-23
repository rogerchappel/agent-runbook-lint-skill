from pathlib import Path

from agent_runbook_lint import lint_runbook


def test_good_runbook_passes():
    report = lint_runbook(Path("fixtures/good-runbook.md"))
    assert report.passed, report.to_markdown()


def test_bad_runbook_fails_required_topics():
    report = lint_runbook(Path("fixtures/bad-runbook.md"))
    assert not report.passed
    assert "risky actions need approval gate" in report.to_markdown()


def test_required_topics_ignore_incidental_prose():
    report = lint_runbook(Path("fixtures/incidental-words-runbook.md"))
    topic_results = [result for result in report.results if result.name.startswith("required topic:")]

    assert topic_results
    assert all(not result.passed for result in topic_results)


def test_required_topic_section_must_have_content(tmp_path):
    runbook = tmp_path / "empty-goal.md"
    runbook.write_text("# Runbook\n\n## Goal\n\n## Inputs\n\nA repository.\n", encoding="utf-8")

    report = lint_runbook(runbook)

    assert not next(result for result in report.results if result.name == "required topic: goal").passed
