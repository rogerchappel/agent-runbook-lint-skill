"""The canonical npm test command must reject a suite that collects nothing."""

import json
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_npm_test_fails_when_pytest_collects_no_tests(tmp_path: Path) -> None:
    empty_suite = tmp_path / "empty"
    empty_suite.mkdir()
    (empty_suite / "not_a_test.py").write_text("def helper():\n    pass\n")
    scripts = json.loads((REPO_ROOT / "package.json").read_text())["scripts"]
    command = scripts["test"]
    # Preserve the npm script's interpreter resolver, but point pytest at an
    # empty suite. Pytest's NO_TESTS_COLLECTED exit code must propagate.
    command = command.replace("-m pytest", f"-m pytest {empty_suite}")
    env = os.environ.copy()
    env["NPM_PYTHON_BIN"] = sys.executable
    result = subprocess.run(["bash", "-lc", command], cwd=REPO_ROOT, env=env)
    assert result.returncode == 5
