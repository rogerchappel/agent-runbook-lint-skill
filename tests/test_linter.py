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


def test_approval_word_outside_gate_does_not_cover_risky_action(tmp_path):
    text = Path("fixtures/good-runbook.md").read_text(encoding="utf-8")
    text = text.replace(
        "Ask before push, publish, deploy, merge, send, or delete actions.",
        "The approval owner is the release manager.",
    )
    text = text.replace(
        "3. Write an evidence report.",
        "3. Push the release branch.\n4. Write an evidence report.",
    )
    runbook = tmp_path / "unrelated-approval.md"
    runbook.write_text(text, encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert not result.passed
    assert "push" in result.detail
    assert "delete" in result.detail


def test_approval_gate_must_cover_each_risky_action(tmp_path):
    text = Path("fixtures/good-runbook.md").read_text(encoding="utf-8")
    text = text.replace(
        "Ask before push, publish, deploy, merge, send, or delete actions.",
        "Obtain confirmation before push.",
    )
    runbook = tmp_path / "partial-approval.md"
    runbook.write_text(text, encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert not result.passed
    assert "delete" in result.detail
