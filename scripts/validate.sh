#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON_BIN:-python3}"
"$python_bin" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'

venv_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-runbook-lint-validation.XXXXXX")"
trap 'rm -rf "$venv_dir"' EXIT

"$python_bin" -m venv "$venv_dir/venv"
validation_python="$venv_dir/venv/bin/python"
"$validation_python" -m pip install -e ".[dev]"

PYTHON_BIN="$validation_python" bash scripts/validate-quickstart.sh
"$validation_python" -m compileall src tests
"$validation_python" -m pytest
"$validation_python" -m agent_runbook_lint check fixtures/good-runbook.md \
  --report "$venv_dir/report.md"
test -s "$venv_dir/report.md"
