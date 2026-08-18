#!/usr/bin/env bash
set -euo pipefail

bash scripts/validate-quickstart.sh
python3 -m compileall src tests
python3 -m pytest
python3 -m agent_runbook_lint check fixtures/good-runbook.md --report /tmp/agent-runbook-lint-report.md
