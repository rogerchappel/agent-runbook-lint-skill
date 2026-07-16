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


@dataclass(frozen=True)
class LintResult:
    name: str
    passed: bool
    detail: str


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
    lowered = text.lower()
    results: list[LintResult] = []
    for topic, needles in REQUIRED_TOPICS.items():
        found = any(needle in lowered for needle in needles)
        results.append(LintResult(f"required topic: {topic}", found, "covered" if found else "missing"))
    results.append(_check_risky_approval(lowered))
    results.append(_check_command_blocks(text))
    results.append(_check_numbered_steps(text))
    return RunbookReport(path=path, results=tuple(results))


def _check_risky_approval(lowered: str) -> LintResult:
    risky = [word for word in RISKY_ACTIONS if re.search(rf"\b{re.escape(word)}\b", lowered)]
    has_approval = "approval" in lowered or "permission" in lowered or "confirm" in lowered
    passed = not risky or has_approval
    detail = "approval gate present" if passed and risky else "no risky actions found" if passed else f"risky actions need approval gate: {', '.join(risky)}"
    return LintResult("risky actions have approval gate", passed, detail)


def _check_command_blocks(text: str) -> LintResult:
    fences = len(re.findall(r"```", text))
    passed = fences >= 2
    return LintResult("commands are fenced", passed, f"found {fences} fence markers")


def _check_numbered_steps(text: str) -> LintResult:
    steps = len(re.findall(r"(?m)^\d+\.\s+", text))
    return LintResult("numbered procedure steps", steps >= 2, f"found {steps} numbered steps")

