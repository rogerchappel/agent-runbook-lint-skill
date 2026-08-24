from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .linter import lint_runbook


def _io_diagnostic(error: BaseException) -> str:
    if isinstance(error, UnicodeDecodeError):
        return "is not valid UTF-8"
    if isinstance(error, FileNotFoundError):
        return "file does not exist"
    if isinstance(error, IsADirectoryError):
        return "is a directory"
    if isinstance(error, (NotADirectoryError, FileExistsError)):
        return "path component is not a directory"
    if isinstance(error, PermissionError):
        return "permission denied"
    return "I/O operation failed"


def _print_io_error(operation: str, path: Path, error: BaseException) -> None:
    print(f"error: cannot {operation} '{path}': {_io_diagnostic(error)}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-runbook-lint")
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="lint an agent runbook")
    check.add_argument("runbook", type=Path)
    check.add_argument("--report", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "check":
        try:
            report = lint_runbook(args.runbook)
        except (OSError, UnicodeError) as error:
            _print_io_error("read runbook", args.runbook, error)
            return 2
        output = report.to_markdown()
        if args.report:
            if args.report.resolve() == args.runbook.resolve():
                print(
                    "error: report destination must not be the source runbook",
                    file=sys.stderr,
                )
                return 2
            try:
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(output, encoding="utf-8")
            except OSError as error:
                _print_io_error("write report", args.report, error)
                return 2
        else:
            print(output)
        return 0 if report.passed else 1
    return 2
