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
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RESOLVER = REPO_ROOT / "scripts" / "python-for-npm.sh"
NPM_SCRIPTS = ("test", "check", "smoke")


def _resolve(base_dir: Path, *, npm_python_bin: Path | None = None) -> str:
    env = os.environ.copy()
    env.pop("NPM_PYTHON_BIN", None)
    if npm_python_bin is not None:
        env["NPM_PYTHON_BIN"] = str(npm_python_bin)
    result = subprocess.run(
        ["bash", str(RESOLVER), str(base_dir)],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    return result.stdout.strip()


def test_resolver_prefers_repo_local_venv(tmp_path: Path) -> None:
    venv_python = tmp_path / ".venv" / "bin" / "python"
    venv_python.parent.mkdir(parents=True)
    venv_python.touch()
    venv_python.chmod(0o755)

    assert _resolve(tmp_path) == str(venv_python)


def test_resolver_prefers_explicit_validation_interpreter(tmp_path: Path) -> None:
    explicit_python = tmp_path / "validation-venv" / "bin" / "python"
    explicit_python.parent.mkdir(parents=True)
    explicit_python.touch()
    explicit_python.chmod(0o755)
    repo_python = tmp_path / ".venv" / "bin" / "python"
    repo_python.parent.mkdir(parents=True)
    repo_python.touch()
    repo_python.chmod(0o755)

    assert _resolve(tmp_path, npm_python_bin=explicit_python) == str(explicit_python)


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


def test_validation_preserves_a_preexisting_repo_venv(tmp_path: Path) -> None:
    if os.environ.get("VALIDATION_CONTRACT_PROBE") == "1":
        return

    checkout = tmp_path / "checkout"
    shutil.copytree(
        REPO_ROOT,
        checkout,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache"),
    )
    sentinel = checkout / ".venv" / "maintainer-sentinel"
    sentinel.parent.mkdir()
    sentinel.write_text("keep\n")
    env = os.environ.copy()
    env.update(PYTHON_BIN=sys.executable, VALIDATION_CONTRACT_PROBE="1")

    subprocess.run(
        ["bash", "scripts/validate.sh"],
        cwd=checkout,
        env=env,
        check=True,
    )

    assert sentinel.read_text() == "keep\n"
