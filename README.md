# Agent Runbook Lint Skill

Lint agent runbooks before automation follows them. `agent-runbook-lint` checks Markdown runbooks for clear goals, required inputs, verification, rollback, evidence capture, approval gates, and external-action boundaries.

## Quickstart

```bash
python3 -m pip install -e ".[dev]"
agent-runbook-lint check docs/ORCHESTRATION.md --report report.md
```

Smoke test:

```bash
npm run smoke
```

## Use Cases

- Review release-candidate runbooks before a scheduled automation lane runs them.
- Catch missing rollback and verification steps in connector or repo-maintenance workflows.
- Produce a PR-ready Markdown checklist from a runbook fixture.

## Safety Notes

The checker is local-first and read-only for source runbooks. It does not execute commands found in the runbook. It writes only the report path requested by `--report`.

## Limitations

The linter validates runbook structure and risky wording. It cannot prove that the documented workflow is operationally complete.

