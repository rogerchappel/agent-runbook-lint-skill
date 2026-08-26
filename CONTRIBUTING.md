# Contributing

Add fixture coverage for each new lint rule. Keep checks deterministic and local-first.

Run:

```bash
bash scripts/validate.sh
```

The validation script creates the repo-local `.venv` exactly as the README
Quickstart documents, installs the project's development dependencies there,
then runs the documented npm commands (`npm test`, `npm run check`,
`npm run smoke`) plus the pure-python quickstart check without relying on an
ambient package install. Set `PYTHON_BIN` to validate with a specific
supported interpreter, for example:

```bash
PYTHON_BIN=python3.12 bash scripts/validate.sh
```
