from pathlib import Path

import pytest

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


@pytest.mark.parametrize(("opening", "closing"), [("```text", "````"), ("~~~text", "~~~~")])
def test_risky_actions_inside_fences_do_not_require_approval(tmp_path, opening, closing):
    runbook = tmp_path / "fenced-risk.md"
    runbook.write_text(
        f"## Steps\n\n{opening}\npush and deploy this example\n{closing}\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert result.passed
    assert result.detail == "no risky actions found"


@pytest.mark.parametrize(("opening", "closing"), [("```text", "````"), ("~~~text", "~~~~")])
def test_approval_gates_inside_fences_do_not_cover_real_actions(tmp_path, opening, closing):
    runbook = tmp_path / "fenced-gate.md"
    runbook.write_text(
        "## Steps\n\n1. Prepare.\n2. Push the branch.\n\n"
        f"## Approval\n\n{opening}\nAsk before push.\n{closing}\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert not result.passed
    assert result.detail == "risky actions need approval gate: push"


def test_real_approval_gate_outside_fence_covers_real_action(tmp_path):
    runbook = tmp_path / "real-gate.md"
    runbook.write_text(
        "## Steps\n\n1. Prepare.\n2. Push the branch.\n\n"
        "## Approval\n\nAsk before push.\n\n```text\nDeploy without approval.\n```\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert result.passed
    assert result.detail == "explicit approval gate covers: push"


def test_empty_fence_does_not_count_as_fenced_command():
    report = lint_runbook(Path("fixtures/incidental-words-runbook.md"))
    result = next(result for result in report.results if result.name == "commands are fenced")

    assert not result.passed
    assert "found 0 fenced commands" in result.detail


def test_unbalanced_command_fence_fails(tmp_path):
    runbook = tmp_path / "unbalanced.md"
    runbook.write_text("## Steps\n\n```bash\nnpm test\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "commands are fenced"
    )

    assert not result.passed
    assert "unbalanced fence" in result.detail


def test_command_like_content_outside_fence_fails(tmp_path):
    runbook = tmp_path / "outside.md"
    runbook.write_text("## Steps\n\n1. npm test\n2. Record output.\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "commands are fenced"
    )

    assert not result.passed
    assert "outside fences on line 3" in result.detail


@pytest.mark.parametrize("marker", ["1)", "  1)"])
def test_parenthesized_ordered_command_outside_fence_fails(tmp_path, marker):
    runbook = tmp_path / "outside-parenthesized.md"
    runbook.write_text(f"## Steps\n\n{marker} npm test\n2) Record output.\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "commands are fenced"
    )

    assert not result.passed
    assert "outside fences on line 3" in result.detail


def test_tilde_fence_with_command_passes_command_check(tmp_path):
    runbook = tmp_path / "tilde.md"
    runbook.write_text("## Steps\n\n~~~shell\npython -m pytest\n~~~\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "commands are fenced"
    )

    assert result.passed


@pytest.mark.parametrize(("opening", "closing"), [("```text", "````"), ("~~~text", "~~~~")])
def test_numbered_steps_inside_fence_do_not_count(tmp_path, opening, closing):
    runbook = tmp_path / "fenced-steps.md"
    runbook.write_text(
        f"## Steps\n\nAn example only:\n\n{opening}\n1. First example\n2. Second example\n{closing}\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "numbered procedure steps"
    )

    assert not result.passed
    assert result.detail == "found 0 numbered steps"


def test_numbered_steps_outside_fence_count(tmp_path):
    runbook = tmp_path / "real-steps.md"
    runbook.write_text(
        "## Steps\n\n1. Prepare the input.\n2. Record the result.\n\n```text\n"
        "1. Example only\n2. Still an example\n```\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "numbered procedure steps"
    )

    assert result.passed
    assert result.detail == "found 2 numbered steps"


def test_parenthesized_and_indented_numbered_steps_outside_fence_count(tmp_path):
    runbook = tmp_path / "parenthesized-steps.md"
    runbook.write_text(
        "## Steps\n\n  1) Prepare the input.\n   2) Record the result.\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "numbered procedure steps"
    )

    assert result.passed
    assert result.detail == "found 2 numbered steps"


def test_parenthesized_numbered_steps_inside_fence_do_not_count(tmp_path):
    runbook = tmp_path / "fenced-parenthesized-steps.md"
    runbook.write_text(
        "## Steps\n\n```text\n  1) npm test\n   2) Record the result.\n```\n",
        encoding="utf-8",
    )

    results = {result.name: result for result in lint_runbook(runbook).results}

    assert results["commands are fenced"].passed
    assert not results["numbered procedure steps"].passed
    assert results["numbered procedure steps"].detail == "found 0 numbered steps"
