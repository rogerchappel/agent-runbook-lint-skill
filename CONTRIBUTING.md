# Contributing

Add fixture coverage for each new lint rule. Keep checks deterministic and local-first.

Run:

```bash
bash scripts/validate.sh
```

The validation script creates a temporary virtual environment, installs the
project's development dependencies there, and runs the quickstart, compile,
test, and CLI smoke checks without relying on an ambient package install. Set
`PYTHON_BIN` to validate with a specific supported interpreter, for example:

```bash
PYTHON_BIN=python3.12 bash scripts/validate.sh
```
