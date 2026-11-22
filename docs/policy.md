# Custom lint policies

Use an optional UTF-8 JSON policy to add organization-specific required
Markdown sections. Custom topics supplement the built-in checks; they do not
replace the built-in topics or risky-action approval checks.

## Schema

The top-level object contains exactly one property, `required_topics`. Its
value is an object mapping each custom check name to a non-empty array of
non-empty strings. Each string is a heading alias matched case-insensitively
against Markdown headings using whole-word matching. Names must be non-empty
and must not duplicate a built-in topic name. For each configured topic, a
matching heading must have non-blank prose outside fenced code blocks.

Example `.runbook-policy.json`:

```json
{
  "required_topics": {
    "Escalation": ["on-call", "escalation path"],
    "Data handling": ["data handling", "privacy"]
  }
}
```

## CLI

Pass the policy to the `check` command with `--policy`; use `--report` as
usual to write the Markdown report:

```bash
agent-runbook-lint check runbook.md --policy .runbook-policy.json --report report.md
```

Without `--policy`, the fixed built-in checks run as before. Invalid JSON,
unsupported properties, malformed topic mappings, duplicate built-in names,
and unreadable policy files produce an `error:` diagnostic and exit code 2.
The CLI validates the policy before linting the runbook.
