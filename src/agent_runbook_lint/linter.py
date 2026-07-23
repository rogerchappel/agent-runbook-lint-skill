from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


REQUIRED_TOPICS = {
    "goal": ("goal", "mission", "objective"),
    "inputs": ("input", "prerequisite", "source"),
    "steps": ("steps", "procedure", "workflow"),
    "verification": ("verification", "validate", "check", "test"),
    "rollback": ("rollback", "revert", "backout"),
    "evidence": ("evidence", "artifact", "report", "log"),
    "approval": ("approval", "permission", "confirm"),
    "stop conditions": ("stop", "blocked", "abort", "do not continue"),
}

RISKY_ACTIONS = ("push", "publish", "deploy", "send", "delete", "merge", "tag release")
ATX_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
FENCE_START = re.compile(r"^[ \t]{0,3}(`{3,}|~{3,})(.*)$")
GATE_LANGUAGE = re.compile(
    r"\b(?:ask|obtain|request|require(?:d|s)?|receive|secure|confirm)\b"
    r"|\b(?:before|until|unless|without|prior[ \t]+to)\b"
)
COMMAND_LINE = re.compile(
    r"^(?:\$\s*)?"
    r"(?:npm|npx|pnpm|yarn|python(?:3)?|pip(?:3)?|git|gh|curl|wget|make|cmake|"
    r"docker|kubectl|terraform|cargo|go|java|mvn|gradle|bash|sh|"
    r"\./[\w./-]+|agent-runbook-lint)"
    r"(?:\s|$)"
)


@dataclass(frozen=True)
class LintResult:
    name: str
    passed: bool
    detail: str


@dataclass(frozen=True)
class MarkdownSection:
    heading: str
    body: str


@dataclass(frozen=True)
class RunbookReport:
    path: Path
    results: tuple[LintResult, ...]

    @property
    def passed(self) -> bool:
        return all(result.passed for result in self.results)

    @property
    def score(self) -> str:
        total = len(self.results)
        passed = sum(1 for result in self.results if result.passed)
        return f"{passed}/{total}"

    def to_markdown(self) -> str:
        lines = [
            "# Agent Runbook Lint Report",
            "",
            f"- Runbook: `{self.path}`",
            f"- Score: {self.score}",
            f"- Result: {'pass' if self.passed else 'fail'}",
            "",
            "## Checks",
            "",
        ]
        for result in self.results:
            marker = "PASS" if result.passed else "FAIL"
            lines.append(f"- {marker}: {result.name} - {result.detail}")
        lines.append("")
        return "\n".join(lines)


def lint_runbook(path: Path) -> RunbookReport:
    text = path.read_text(encoding="utf-8")
    sections = _parse_sections(text)
    results: list[LintResult] = []
    for topic, needles in REQUIRED_TOPICS.items():
        found = any(
            section.body.strip() and _heading_matches(section.heading, needles)
            for section in sections
        )
        detail = "non-empty Markdown section found" if found else "missing non-empty Markdown section"
        results.append(LintResult(f"required topic: {topic}", found, detail))
    results.append(_check_risky_approval(text, sections))
    results.append(_check_command_blocks(text))
    results.append(_check_numbered_steps(text))
    return RunbookReport(path=path, results=tuple(results))


def _parse_sections(text: str) -> tuple[MarkdownSection, ...]:
    sections: list[MarkdownSection] = []
    heading: str | None = None
    body: list[str] = []
    fence: tuple[str, int] | None = None

    for line in text.splitlines():
        fence_match = FENCE_START.match(line)
        if fence_match:
            marker = fence_match.group(1)
            marker_type = marker[0]
            if fence is None:
                fence = (marker_type, len(marker))
            elif marker_type == fence[0] and len(marker) >= fence[1]:
                fence = None
            if heading is not None:
                body.append(line)
            continue

        heading_match = ATX_HEADING.match(line) if fence is None else None
        if heading_match:
            if heading is not None:
                sections.append(MarkdownSection(heading=heading, body="\n".join(body)))
            heading = heading_match.group(2).strip()
            body = []
        elif heading is not None:
            body.append(line)

    if heading is not None:
        sections.append(MarkdownSection(heading=heading, body="\n".join(body)))
    return tuple(sections)


def _heading_matches(heading: str, needles: tuple[str, ...]) -> bool:
    normalized = re.sub(r"[*_`~]", "", heading).lower()
    return any(re.search(rf"\b{re.escape(needle)}s?\b", normalized) for needle in needles)


def _check_risky_approval(
    text: str, sections: tuple[MarkdownSection, ...]
) -> LintResult:
    lowered = text.lower()
    risky = [
        action
        for action in RISKY_ACTIONS
        if re.search(rf"\b{re.escape(action)}\b", lowered)
    ]
    if not risky:
        return LintResult("risky actions have approval gate", True, "no risky actions found")

    approval_lines = [
        line.lower()
        for section in sections
        if _heading_matches(section.heading, REQUIRED_TOPICS["approval"])
        for line in section.body.splitlines()
        if line.strip()
    ]
    gated = {
        action
        for action in risky
        if any(
            re.search(rf"\b{re.escape(action)}\b", line) and GATE_LANGUAGE.search(line)
            for line in approval_lines
        )
    }
    missing = [action for action in risky if action not in gated]
    passed = not missing
    detail = (
        f"explicit approval gate covers: {', '.join(risky)}"
        if passed
        else f"risky actions need approval gate: {', '.join(missing)}"
    )
    return LintResult("risky actions have approval gate", passed, detail)


def _check_command_blocks(text: str) -> LintResult:
    blocks: list[list[str]] = []
    current: list[str] | None = None
    fence: tuple[str, int] | None = None
    balanced = True
    outside_commands: list[int] = []

    for line_number, line in enumerate(text.splitlines(), start=1):
        marker_match = FENCE_START.match(line)
        if fence is None and marker_match:
            marker = marker_match.group(1)
            fence = (marker[0], len(marker))
            current = []
            continue
        if fence is not None:
            closing = re.fullmatch(
                rf"[ \t]{{0,3}}{re.escape(fence[0])}{{{fence[1]},}}[ \t]*",
                line,
            )
            if closing:
                blocks.append(current or [])
                current = None
                fence = None
            else:
                assert current is not None
                current.append(line)
            continue
        if _is_command_like(line):
            outside_commands.append(line_number)

    if fence is not None:
        balanced = False

    inside_commands = sum(
        1 for block in blocks for line in block if _is_command_like(line)
    )
    passed = balanced and inside_commands > 0 and not outside_commands
    details = [
        f"found {inside_commands} fenced command{'s' if inside_commands != 1 else ''}",
        "fences balanced" if balanced else "unbalanced fence",
    ]
    if outside_commands:
        details.append(
            "command-like content outside fences on "
            + ", ".join(f"line {line_number}" for line_number in outside_commands)
        )
    return LintResult("commands are fenced", passed, "; ".join(details))


def _is_command_like(line: str) -> bool:
    stripped = re.sub(r"^(?:[-*+]|\d+\.)[ \t]+", "", line.strip())
    return bool(COMMAND_LINE.match(stripped))


def _check_numbered_steps(text: str) -> LintResult:
    steps = len(re.findall(r"(?m)^\d+\.\s+", text))
    return LintResult("numbered procedure steps", steps >= 2, f"found {steps} numbered steps")
