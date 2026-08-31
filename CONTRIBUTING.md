# Contributing

Add fixture coverage for each new lint rule. Keep checks deterministic and local-first.

Run:

```bash
bash scripts/validate.sh
```

The validation script creates an owned virtual environment under the system
temporary directory, installs the project's development dependencies there,
and explicitly directs the documented npm commands (`npm test`, `npm run
check`, `npm run smoke`) to that interpreter. It also runs the pure-Python
quickstart check. Validation never creates, replaces, or removes the
repository's `.venv`, so an existing Quickstart environment is preserved. Set
`PYTHON_BIN` to choose the interpreter used to create both temporary validation
environments, for example:

```bash
PYTHON_BIN=python3.12 bash scripts/validate.sh
```
