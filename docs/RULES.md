# Built-In Rules

The first release ships with deterministic Markdown checks:

## Required topic sections

Goal, inputs, steps, verification, rollback, evidence, approval, and stop
conditions must each be represented by a non-empty ATX-style Markdown section
(`#` through `######`). As in CommonMark, an ATX heading may have zero to three
leading spaces; four spaces make the line indented code, not a heading.
Incidental words in prose do not count. A heading matches when it contains one
of these whole-word terms (with an optional plural `s`):

- Goal: `goal`, `mission`, `objective`
- Inputs: `input`, `prerequisite`, `source`
- Steps: `steps`, `procedure`, `workflow`
- Verification: `verification`, `validate`, `check`, `test`
- Rollback: `rollback`, `revert`, `backout`
- Evidence: `evidence`, `artifact`, `report`, `log`
- Approval: `approval`, `permission`, `confirm`
- Stop conditions: `stop`, `blocked`, `abort`, `do not continue`

Headings inside fenced code blocks are ignored. A fence closes only with the
same marker (backtick or tilde), at least as many markers as the opening fence, and no
trailing info text. A fence-like line with trailing text remains example
content; headings after it are still ignored until a valid closing fence.

## Risky-action approval gates

The risky-action terms are `push`, `publish`, `deploy`, `send`, `delete`,
`merge`, and operational release-tag wording. Release-tag wording includes
`tag release`, `tag a release`, `tag the release`, `tagging the release`,
`create a release tag`, and `create the release tag`. Descriptive phrases such
as `release tag format` and `release tagging policy` do not count. If any risky
action appears in the document, every distinct action found must also appear on
a gating line inside an approval, permission, or confirmation section. A gating
line contains the action and at least one of:

- `ask`, `obtain`, `request`, `require`, `required`, `requires`, `receive`,
  `secure`, or `confirm`
- `before`, `until`, `unless`, `without`, or `prior to`

Approval language elsewhere in the document does not satisfy this rule.
Explicit denials such as `approval is not required` do not satisfy the gate,
even when the same line otherwise contains gating language such as `before`.
Risky-action terms and gating lines inside balanced backtick or tilde fences are
treated as examples: they neither introduce operational risky actions nor
satisfy approval gates. Closing fences follow the rule described above.

## Fenced commands

The document must contain at least one command-like line inside a balanced
backtick or tilde fence. Every command-like line must be fenced. Markdown
bullet markers and ordered-list markers using either `N.` or `N)` are ignored
before matching, as are shell prompts. A line is command-like
when its first executable is one of:

`npm`, `npx`, `pnpm`, `yarn`, `python`, `python3`, `pip`, `pip3`, `pytest`,
`ruff`, `tox`, `uv`, `git`, `gh`, `curl`, `wget`, `make`, `cmake`, `docker`,
`kubectl`, `terraform`, `cargo`, `go`, `java`, `mvn`, `gradle`, `bash`, `sh`,
`agent-runbook-lint`, or a relative `./...` executable. The executable must be
the first token after an optional Markdown list marker and optional `$` shell
prompt, so ordinary prose that mentions a tool name is not a command line.

Empty fences, unbalanced fences, and recognized command lines outside fences
fail this rule.

## Numbered procedure

At least two lines outside fenced code blocks must begin with an ordered-list
marker using either CommonMark delimiter: `N.` or `N)`. Up to three leading
spaces are accepted as normal Markdown indentation. Numbered lines in balanced
backtick or tilde fences are examples and do not count as procedure steps.
