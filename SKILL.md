# Agent Runbook Lint

Use this skill when an agent is about to follow, publish, or delegate a runbook and needs a local readiness check first.

## Required Inputs

- Path to a Markdown runbook.
- Optional report path.

## Outputs

- Markdown lint report.
- Exit code `0` when required gates pass, otherwise `1`.

## Side-Effect Boundaries

The skill reads runbooks and may write a report file. It must not execute runbook commands, push branches, call connectors, or mutate external systems.

## Approval Requirements

Any follow-up action that writes to GitHub, Slack, CRM, project-management tools, or other external accounts requires explicit approval in the owning workflow.

## Examples

```bash
agent-runbook-lint check docs/ORCHESTRATION.md
agent-runbook-lint check RUNBOOK.md --report reports/runbook-lint.md
```

## Validation Workflow

Run `npm test`, `npm run check`, and `npm run smoke` before using the report in a release-candidate PR.

