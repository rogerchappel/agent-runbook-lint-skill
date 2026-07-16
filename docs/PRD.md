# PRD: Agent Runbook Lint Skill

## Status

in-progress

## Problem

Automation runbooks often omit the practical guardrails agents need: approvals, rollback, evidence, validation, and stop conditions. A missing section can turn a routine scheduled run into an unclear or risky workflow.

## Users

- Agent operators preparing cron payloads.
- Maintainers reviewing connector or repository automation.
- Agents delegating work to other agents.

## MVP

- CLI lints one Markdown runbook.
- Markdown report with pass/fail checks.
- Fixture-backed tests and smoke command.
- Skill documentation that states boundaries and approvals.

## Non-Goals

- Executing runbook commands.
- Enforcing organization policy remotely.
- Mutating connected applications.

## Classification

ship when checks pass and a release-candidate PR includes validation output.

