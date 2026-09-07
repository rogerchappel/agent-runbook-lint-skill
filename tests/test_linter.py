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


@pytest.mark.parametrize(
    ("filename", "rendered_path"),
    [
        ("ordinary.md", "`ordinary.md`"),
        ("runbook-with-`tick`.md", "``runbook-with-`tick`.md``"),
    ],
)
def test_markdown_report_renders_runbook_paths_as_code_spans(tmp_path, filename, rendered_path):
    runbook = tmp_path / filename
    runbook.write_text(Path("fixtures/good-runbook.md").read_text(encoding="utf-8"), encoding="utf-8")
    report = lint_runbook(runbook)

    expected = rendered_path.replace(filename, str(runbook))
    assert f"- Runbook: {expected}" in report.to_markdown()


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


@pytest.mark.parametrize("indent", ["", " ", "  ", "   "])
def test_required_topics_accept_commonmark_atx_heading_indentation(tmp_path, indent):
    runbook = tmp_path / "indented-heading.md"
    runbook.write_text(f"{indent}## Goal\n\nDeliver a verified result.\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert result.passed


def test_four_space_indented_atx_heading_is_code_not_a_section(tmp_path):
    runbook = tmp_path / "code-heading.md"
    runbook.write_text("    ## Goal\n\n    Example only.\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert not result.passed


def test_indented_atx_heading_inside_fence_is_ignored(tmp_path):
    runbook = tmp_path / "fenced-indented-heading.md"
    runbook.write_text("```markdown\n   ## Goal\n\nExample only.\n```\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert not result.passed


def test_indented_runbook_sections_and_approval_gate_pass_end_to_end(tmp_path):
    source = Path("fixtures/good-runbook.md").read_text(encoding="utf-8")
    runbook = tmp_path / "indented-runbook.md"
    runbook.write_text(
        "\n".join(f"   {line}" if line.startswith("#") else line for line in source.splitlines())
        + "\n",
        encoding="utf-8",
    )

    report = lint_runbook(runbook)

    assert report.passed, report.to_markdown()
    approval = next(
        result for result in report.results if result.name == "risky actions have approval gate"
    )
    assert approval.detail == "explicit approval gate covers: push, publish, deploy, send, delete, merge"


@pytest.mark.parametrize(
    ("opening", "closing"),
    [
        ("```text", "````"),
        ("~~~text", "~~~~"),
    ],
)
def test_required_topic_empty_fence_is_not_content(tmp_path, opening, closing):
    runbook = tmp_path / "empty-fenced-goal.md"
    runbook.write_text(f"## Goal\n\n{opening}\n{closing}\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert not result.passed


@pytest.mark.parametrize(
    ("opening", "closing"),
    [
        ("```text", "````"),
        ("~~~text", "~~~~"),
    ],
)
def test_required_topic_fenced_example_is_not_content(tmp_path, opening, closing):
    runbook = tmp_path / "non-empty-fenced-goal.md"
    runbook.write_text(
        f"## Goal\n\n{opening}\nDeliver a verified release.\n{closing}\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert not result.passed


@pytest.mark.parametrize(
    ("opening", "closing"),
    [
        ("```text", "````"),
        ("~~~text", "~~~~"),
    ],
)
def test_required_topic_prose_outside_fenced_example_is_content(tmp_path, opening, closing):
    runbook = tmp_path / "mixed-fenced-goal.md"
    runbook.write_text(
        f"## Goal\n\n{opening}\nExample only.\n{closing}\nDeliver a verified release.\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert result.passed


def test_required_topic_unbalanced_fence_does_not_expose_example_content(tmp_path):
    runbook = tmp_path / "unbalanced-fenced-goal.md"
    runbook.write_text("## Goal\n\n```text\nExample only.\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert not result.passed


@pytest.mark.parametrize(
    ("opening", "pseudo_closing", "closing"),
    [
        ("```text", "```not-a-closing-fence", "````"),
        ("~~~text", "~~~not-a-closing-fence", "~~~~"),
    ],
)
def test_required_topics_ignore_headings_after_invalid_fence_closer(
    tmp_path, opening, pseudo_closing, closing
):
    runbook = tmp_path / "fenced-heading.md"
    runbook.write_text(
        f"{opening}\n{pseudo_closing}\n## Goal\n\nExample only.\n{closing}\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert not result.passed


@pytest.mark.parametrize(
    ("opening", "pseudo_closing", "closing"),
    [
        ("```text", "```not-a-closing-fence", "````"),
        ("~~~text", "~~~not-a-closing-fence", "~~~~"),
    ],
)
def test_required_topics_accept_headings_after_eventual_valid_fence_closer(
    tmp_path, opening, pseudo_closing, closing
):
    runbook = tmp_path / "post-fence-heading.md"
    runbook.write_text(
        f"{opening}\n{pseudo_closing}\n## Goal\n\nExample only.\n{closing}\n"
        "## Goal\n\nReal objective.\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "required topic: goal"
    )

    assert result.passed


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


@pytest.mark.parametrize(
    "wording",
    [
        "Tag release 1.2.3.",
        "Tag a release for the verified commit.",
        "Tag the release after verification.",
        "Create a release tag for the verified commit.",
        "Create the release tag after verification.",
        "Tagging the release is the final step.",
    ],
)
def test_release_tagging_wording_requires_approval(tmp_path, wording):
    runbook = tmp_path / "release-tag.md"
    runbook.write_text(
        f"## Steps\n\n1. Verify the commit.\n2. {wording}\n\n"
        "## Approval\n\nApproval is not required before creating the release tag.\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert not result.passed
    assert result.detail == "risky actions need approval gate: tag release"


def test_release_tagging_wording_accepts_explicit_gate(tmp_path):
    runbook = tmp_path / "gated-release-tag.md"
    runbook.write_text(
        "## Steps\n\n1. Verify the commit.\n2. Create a release tag.\n\n"
        "## Approval\n\nObtain approval before creating the release tag.\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert result.passed
    assert result.detail == "explicit approval gate covers: tag release"


@pytest.mark.parametrize(
    "prose",
    [
        "The release-tag policy belongs to the maintainers.",
        "The release tag format is vMAJOR.MINOR.PATCH.",
        "Release tagging policy is documented elsewhere.",
    ],
)
def test_descriptive_release_tag_prose_is_not_a_risky_action(tmp_path, prose):
    runbook = tmp_path / "tag-policy.md"
    runbook.write_text(f"## Notes\n\n{prose}\n", encoding="utf-8")

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert result.passed
    assert result.detail == "no risky actions found"


def test_release_tagging_inside_fence_remains_an_example(tmp_path):
    runbook = tmp_path / "fenced-release-tag.md"
    runbook.write_text(
        "## Steps\n\n```text\nCreate a release tag.\n```\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "risky actions have approval gate"
    )

    assert result.passed
    assert result.detail == "no risky actions found"


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


@pytest.mark.parametrize(
    "command",
    [
        "pytest -q",
        "ruff check .",
        "tox -e py310",
        "uv run pytest -q",
    ],
)
def test_python_tool_commands_inside_fences_pass(tmp_path, command):
    runbook = tmp_path / "python-tool.md"
    runbook.write_text(
        f"## Steps\n\n```console\n{command}\n```\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "commands are fenced"
    )

    assert result.passed


@pytest.mark.parametrize(
    "line",
    [
        "pytest -q",
        "- ruff check .",
        "1. tox -e py310",
        "2) uv run pytest -q",
    ],
)
def test_python_tool_commands_outside_fences_fail(tmp_path, line):
    runbook = tmp_path / "unfenced-python-tool.md"
    runbook.write_text(
        f"## Steps\n\n{line}\n\n```console\npython --version\n```\n",
        encoding="utf-8",
    )

    result = next(
        result
        for result in lint_runbook(runbook).results
        if result.name == "commands are fenced"
    )

    assert not result.passed
    assert "outside fences on line 3" in result.detail


@pytest.mark.parametrize(
    "line",
    [
        "The pytest suite is quick.",
        "Use ruff when editing Python.",
        "Our tox environments cover supported versions.",
        "The uv guide explains environment setup.",
    ],
)
def test_python_tool_names_in_prose_are_not_commands(tmp_path, line):
    runbook = tmp_path / "python-tool-prose.md"
    runbook.write_text(
        f"## Steps\n\n{line}\n\n```console\npython --version\n```\n",
        encoding="utf-8",
    )

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
