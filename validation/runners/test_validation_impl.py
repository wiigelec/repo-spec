#!/usr/bin/env python3

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


class RootValidationSelfTestError(RuntimeError):
    pass


def _run_driver(
    repo_root: Path,
    name: str,
    test_path: Path,
    body: str,
    pythonpath: list[Path],
    cwd: Path,
) -> None:
    driver = (
        "import importlib.util\n"
        "from pathlib import Path\n"
        f"test_path = Path({str(test_path)!r})\n"
        f"spec = importlib.util.spec_from_file_location({name!r}, test_path)\n"
        "if spec is None or spec.loader is None:\n"
        "    raise SystemExit(f'cannot load root validation self-test: {test_path}')\n"
        "module = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(module)\n"
        f"repo_root = Path({str(repo_root)!r})\n"
        + body
        + "\n"
    )
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(str(path) for path in pythonpath)
    result = subprocess.run(
        [sys.executable, "-c", driver],
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        detail = ((result.stdout or "") + (result.stderr or "")).strip()
        raise RootValidationSelfTestError(f"{name} failed: {detail}")


def run(repo_root: Path) -> None:
    repo_root = repo_root.resolve()
    tests_root = repo_root / "validation/tests/self"
    repo_scripts = repo_root / "repo/scripts"

    _run_driver(
        repo_root,
        "root_github_field_policy_tests",
        tests_root / "github_field_policy_tests.py",
        "module.run_github_field_policy_tests(repo_root)",
        [repo_root, repo_scripts],
        repo_root,
    )

    repo_owned_path = [repo_root, repo_scripts]

    _run_driver(
        repo_root,
        "root_github_profile_generation_tests",
        tests_root / "github_profile_generation_tests.py",
        "module.run_github_profile_generation_tests(repo_root)\n"
        "module.run_github_profile_mutation_tests(repo_root)",
        repo_owned_path,
        repo_root / "repo",
    )

    _run_driver(
        repo_root,
        "root_portable_self_tests",
        tests_root / "portable_self_tests.py",
        "module.run_reference_isolated_copy_tests(repo_root)",
        [repo_root, repo_scripts],
        repo_root,
    )

    result = subprocess.run(
        [sys.executable, str(tests_root / "mutation_tests.py")],
        cwd=repo_root,
        env={
            **os.environ,
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": os.pathsep.join([str(repo_root), str(repo_scripts)]),
        },
        text=True,
        capture_output=True,
    )
    if result.stdout:
        print(result.stdout, end="")
    if result.returncode != 0:
        detail = ((result.stdout or "") + (result.stderr or "")).strip()
        raise RootValidationSelfTestError(f"root_mutation_tests failed: {detail}")

    print("ok: root validation self-tests")


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"usage: {Path(argv[0]).name} [repo-root]", file=sys.stderr)
        return 2
    repo_root = Path(argv[1]).resolve() if len(argv) == 2 else Path.cwd().resolve()
    try:
        run(repo_root)
    except (AssertionError, OSError, RuntimeError) as exc:
        print(f"root validation self-test error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
