# Release Candidate Automation Runbook

## Goal

Prepare a release-candidate PR with local evidence.

## Inputs

- Local repository path.
- Fixture command list.

## Steps

1. Inspect the repository status.
2. Run the verification command.
3. Write an evidence report.

```bash
npm test
```

## Verification

Confirm tests passed and attach the report.

## Rollback

Delete generated reports and leave source files unchanged.

## Evidence

Record command output and report path.

## Approval

Ask before push, publish, deploy, merge, send, or delete actions.

## Stop Conditions

Stop if credentials, private data, or destructive commands are required.
