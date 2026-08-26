#!/usr/bin/env bash
set -euo pipefail

python_bin="${PYTHON_BIN:-python3}"
"$python_bin" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'
"$python_bin" --version

venv_dir="$(mktemp -d "${TMPDIR:-/tmp}/agent-runbook-lint-validation.XXXXXX")"
trap 'rm -rf "$venv_dir" .venv' EXIT

# Repo-local .venv, exactly as the README Quickstart documents it. The npm
# scripts resolve this interpreter via scripts/python-for-npm.sh, so this is
# also the environment the documented `npm test` / `npm run check` /
# `npm run smoke` commands will use.
"$python_bin" -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"

# Exercise the documented cross-tool commands: a bare checkout that followed
# only the Quickstart must be able to run the suite via npm.
npm test
npm run check
npm run smoke
test -s /tmp/agent-runbook-lint-report.md

# Pure-python quickstart path (no npm required), kept as the CLI-level check.
PYTHON_BIN="$python_bin" bash scripts/validate-quickstart.sh