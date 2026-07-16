# Release Validation

## 2026-07-16

- `python3 -m venv .venv`: pass
- `. .venv/bin/activate && python -m pip install -e ".[dev]"`: pass
- `npm test`: pass, 2 tests
- `npm run check`: pass
- `npm run smoke`: pass
- `bash scripts/validate.sh`: pass

## Generated Evidence

The smoke command writes `/tmp/agent-runbook-lint-report.md` and validates `fixtures/good-runbook.md` without executing any runbook commands.

