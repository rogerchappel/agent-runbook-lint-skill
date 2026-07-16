# Orchestration

## Inputs

- Markdown runbook path.
- Optional report destination.

## Steps

1. Run `agent-runbook-lint check RUNBOOK.md --report reports/runbook-lint.md`.
2. Review failed gates.
3. Update the runbook with missing approval, rollback, validation, or evidence sections.
4. Re-run before opening a release-candidate PR.

## Outputs

- Markdown report.
- Non-zero exit code when required runbook gates are missing.

## Rollback

Delete the generated report if it is no longer needed. Source runbooks are never modified.

