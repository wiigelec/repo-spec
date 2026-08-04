from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def run_command(command: list[str], cwd: Path) -> None:
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    subprocess.run(command, cwd=cwd, env=env, check=True)


def run_reference_isolated_copy_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-reference-copy-") as temp_root_name:
        temp_root = Path(temp_root_name)
        temp_reference = temp_root / "reference"
        shutil.copytree(repo_root / "reference", temp_reference)

        run_command([str(temp_reference / "scripts/generate-docs")], temp_root)
        run_command([str(temp_reference / "scripts/validate")], temp_root)
        run_command([str(temp_reference / "scripts/validate"), "--mutation-tests"], temp_root)

    print("ok: reference isolated copy tests")
