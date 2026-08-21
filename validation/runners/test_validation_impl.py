#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def run(repo_root: Path) -> int:
    repo_root = repo_root.resolve()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    pythonpath = [str(repo_root), str(repo_root / "repo/scripts")]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(repo_root / "validation/tests/unit"),
            "-p",
            "test_*.py",
        ],
        cwd=repo_root,
        env=env,
    )
    return result.returncode
run.__validation_metadata__ = {"role": "helper"}


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"usage: {Path(argv[0]).name} [repo-root]", file=sys.stderr)
        return 2
    repo_root = Path(argv[1]).resolve() if len(argv) == 2 else Path.cwd().resolve()
    return run(repo_root)
main.__validation_metadata__ = {"role": "helper"}


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
