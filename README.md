# Agent Runbook Lint Skill

Lint agent runbooks before automation follows them. `agent-runbook-lint` checks Markdown runbooks for clear goals, required inputs, verification, rollback, evidence capture, approval gates, and external-action boundaries.

## Quickstart

Python 3.10 or newer is required. This setup selects an installed supported
interpreter, verifies its version, and keeps the editable install isolated:

```bash
PYTHON_BIN="$(
  for candidate in python3.14 python3.13 python3.12 python3.11 python3.10 python3; do
    if command -v "$candidate" >/dev/null 2>&1 &&
       "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
      command -v "$candidate"
      break
    fi
  done
)"
test -n "$PYTHON_BIN" || { echo "Python 3.10 or newer is required" >&2; exit 1; }
"$PYTHON_BIN" --version
"$PYTHON_BIN" -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/agent-runbook-lint check fixtures/good-runbook.md --report report.md
```

Smoke test:

```bash
npm run smoke
```

See [Built-In Rules](docs/RULES.md) for the exact deterministic matching
semantics.

Release operations such as `tag the release` and `create a release tag` are
risky actions. They pass only when the approval section explicitly requires
approval for the same action; saying approval is not required does not pass.

## Use Cases

- Review release-candidate runbooks before a scheduled automation lane runs them.
- Catch missing rollback and verification steps in connector or repo-maintenance workflows.
- Produce a PR-ready Markdown checklist from a runbook fixture.

## Safety Notes

The checker is local-first and read-only for source runbooks. It does not execute commands found in the runbook. It writes only the report path requested by `--report`, and refuses a destination that resolves to the source runbook itself. Parent directories for any other report destination are created as needed.

## Exit Codes and Errors

`agent-runbook-lint check` exits with `0` when every lint check passes, `1`
when the runbook is readable but fails one or more checks, and `2` for command
usage or file I/O errors. Missing or unreadable inputs, directories supplied as
inputs, non-UTF-8 runbooks, and report creation or write failures produce one
concise `error:` line on stderr without a Python traceback.

## Limitations

The linter validates runbook structure and risky wording. It cannot prove that the documented workflow is operationally complete.
