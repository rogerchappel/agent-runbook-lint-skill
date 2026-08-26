"""Regression tests for the npm <-> Python interpreter contract.

The README Quickstart installs the project into a repo-local ``.venv``.
The documented `npm test`, `npm run check`, and `npm run smoke` commands must
resolve that interpreter (with a documented fallback to an ambient
``python3``) so they work from a fresh checkout that followed the Quickstart,
even when the ambient interpreter has none of the project's packages
installed. These tests pin that behaviour via scripts/python-for-npm.sh.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER = REPO_ROOT / "scripts" / "python-for-npm.sh"
NPM_SCRIPTS = ("test", "check", "smoke")


def _resolve(base_dir: Path) -> str:
    result = subprocess.run(
        ["bash", str(RESOLVER), str(base_dir)],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def test_resolver_prefers_repo_local_venv(tmp_path: Path) -> None:
    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()
    venv_python.chmod(0o755)

    assert _resolve(tmp_path) == str(venv_python)


def test_resolver_falls_back_to_ambient_python(tmp_path: Path) -> None:
    resolved = _resolve(tmp_path)
    assert Path(resolved).name == "python3"
    assert Path(resolved).is_absolute()


def test_npm_scripts_resolve_the_repo_local_interpreter() -> None:
    scripts = json.loads((REPO_ROOT / "package.json").read_text())["scripts"]
    for script in NPM_SCRIPTS:
        command = scripts[script]
        assert "python-for-npm.sh" in command, (
            f"npm {script} must resolve the repo-local .venv interpreter via "
            f"scripts/python-for-npm.sh, got: {command!r}"
        )