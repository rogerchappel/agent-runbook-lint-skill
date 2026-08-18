#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON_BIN:-python3}"
"$python_bin" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'
"$python_bin" --version

venv_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-runbook-lint-quickstart.XXXXXX")"
trap 'rm -rf "$venv_dir"' EXIT

"$python_bin" -m venv "$venv_dir/venv"
"$venv_dir/venv/bin/python" -m pip install -e ".[dev]"
"$venv_dir/venv/bin/agent-runbook-lint" check fixtures/good-runbook.md \
  --report "$venv_dir/report.md"
test -s "$venv_dir/report.md"
