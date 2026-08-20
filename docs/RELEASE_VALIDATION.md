# Release Validation

## 2026-07-16

- `python3 -m venv .venv`: pass
- `. .venv/bin/activate && python -m pip install -e ".[dev]"`: pass
- `npm test`: pass, 2 tests
- `npm run check`: pass
- `npm run smoke`: pass
- `bash scripts/validate.sh`: pass from a clean checkout without an ambient
  package install; the script creates and removes its own development
  environment

## Generated Evidence

The smoke command writes its report inside the validation script's temporary
directory and validates `fixtures/good-runbook.md` without executing any
runbook commands.
