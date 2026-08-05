# Built-In Rules

The first release ships with deterministic Markdown checks:

## Required topic sections

Goal, inputs, steps, verification, rollback, evidence, approval, and stop
conditions must each be represented by a non-empty ATX-style Markdown section
(`#` through `######`). Incidental words in prose do not count. A heading
matches when it contains one of these whole-word terms (with an optional plural
`s`):

- Goal: `goal`, `mission`, `objective`
- Inputs: `input`, `prerequisite`, `source`
- Steps: `steps`, `procedure`, `workflow`
- Verification: `verification`, `validate`, `check`, `test`
- Rollback: `rollback`, `revert`, `backout`
- Evidence: `evidence`, `artifact`, `report`, `log`
- Approval: `approval`, `permission`, `confirm`
- Stop conditions: `stop`, `blocked`, `abort`, `do not continue`

Headings inside fenced code blocks are ignored.

## Risky-action approval gates

The risky-action terms are `push`, `publish`, `deploy`, `send`, `delete`,
`merge`, and `tag release`. If any appears in the document, every distinct
action found must also appear on a gating line inside an approval, permission,
or confirmation section. A gating line contains the action and at least one of:

- `ask`, `obtain`, `request`, `require`, `required`, `requires`, `receive`,
  `secure`, or `confirm`
- `before`, `until`, `unless`, `without`, or `prior to`

Approval language elsewhere in the document does not satisfy this rule.
Risky-action terms and gating lines inside balanced backtick or tilde fences are
treated as examples: they neither introduce operational risky actions nor
satisfy approval gates. A closing fence may use more markers than its opening
fence.

## Fenced commands

The document must contain at least one command-like line inside a balanced
backtick or tilde fence. Every command-like line must be fenced. Markdown
bullet markers and ordered-list markers using either `N.` or `N)` are ignored
before matching, as are shell prompts. A line is command-like
when its first executable is one of:

`npm`, `npx`, `pnpm`, `yarn`, `python`, `python3`, `pip`, `pip3`, `git`, `gh`,
`curl`, `wget`, `make`, `cmake`, `docker`, `kubectl`, `terraform`, `cargo`,
`go`, `java`, `mvn`, `gradle`, `bash`, `sh`, `agent-runbook-lint`, or a
relative `./...` executable.

Empty fences, unbalanced fences, and recognized command lines outside fences
fail this rule.

## Numbered procedure

At least two lines outside fenced code blocks must begin with an ordered-list
marker using either CommonMark delimiter: `N.` or `N)`. Up to three leading
spaces are accepted as normal Markdown indentation. Numbered lines in balanced
backtick or tilde fences are examples and do not count as procedure steps.
