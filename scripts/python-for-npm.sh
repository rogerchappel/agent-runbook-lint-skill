#!/usr/bin/env bash
# Resolve the Python interpreter used by the npm scripts.
#
# The README Quickstart installs the package into a repo-local virtual
# environment at `./` + `.venv`. The documented npm commands (`npm test`,
# `npm run check`, `npm run smoke`) must run against that interpreter so they
# work from a fresh checkout that followed the Quickstart, even when the
# ambient `python3` has none of the project's packages installed.
#
# Resolution order:
#   1. <base>/.venv/bin/python          (macOS/Linux: the Quickstart layout)
#   2. <base>/.venv/Scripts/python.exe  (Windows layout, kept for parity)
#   3. ambient `python3`                (documented fallback)
#
# Usage: scripts/python-for-npm.sh [base-dir]
#   base-dir defaults to the repository root (parent of this script).
set -euo pipefail

base_dir="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
cd "$base_dir"

if [[ -x .venv/bin/python ]]; then
  echo "$PWD/.venv/bin/python"
elif [[ -x .venv/Scripts/python.exe ]]; then
  echo "$PWD/.venv/Scripts/python.exe"
elif command -v python3 >/dev/null 2>&1; then
  command -v python3
else
  echo "python3 not found: follow the README Quickstart to create .venv, or install Python 3.10+" >&2
  exit 1
fi