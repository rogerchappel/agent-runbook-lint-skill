# Custom lint policies

Use `--policy PATH` to add organization-specific required Markdown sections. The
policy is UTF-8 JSON with one `required_topics` object; each key is the check
name and each value is a non-empty list of heading words/phrases that match
that section (case-insensitively). The built-in checks and risky-action rules
remain enabled whether or not a policy is supplied.

```json
{
  "required_topics": {
    "Escalation": ["on-call", "escalation path"],
    "Data handling": ["data handling", "privacy"]
  }
}
```

```bash
agent-runbook-lint check runbook.md --policy .runbook-policy.json --report report.md
```

A configured topic must have a non-empty name and at least one non-empty string
alias. The policy object may contain only `required_topics`; that value must be
an object, and custom names may not duplicate built-in topics. Invalid JSON,
invalid shapes, duplicate names, and unreadable policy files fail with exit code
2 and an `error:` diagnostic. A policy is optional; omitting `--policy` keeps
the existing fixed checks unchanged.
