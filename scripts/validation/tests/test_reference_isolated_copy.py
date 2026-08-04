from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import tempfile
from pathlib import Path


def minimal_env(cwd: Path) -> dict[str, str]:
    return {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(cwd),
        "LANG": "C",
        "LC_ALL": "C",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def run_command(command: list[str], cwd: Path) -> None:
    env = minimal_env(cwd)
    subprocess.run(command, cwd=cwd, env=env, check=True)


def tree_fingerprint(root: Path) -> tuple[tuple[str, str], str]:
    inventory: list[tuple[str, str]] = []
    hasher = hashlib.sha256()
    for path in sorted(root.rglob("*")):
        if path.is_dir():
            continue
        relpath = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise AssertionError(f"reference isolated copy failed: symlink escape at {relpath}")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        inventory.append((relpath, digest))
        hasher.update(relpath.encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(digest.encode("utf-8"))
        hasher.update(b"\0")
    return tuple(inventory), hasher.hexdigest()


def assert_no_parent_checkout_references(root: Path, parent_root: Path) -> None:
    parent_text = parent_root.resolve().as_posix()
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            contents = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        assert parent_text not in contents, f"reference isolated copy failed: parent checkout reference in {path.relative_to(root).as_posix()}"


def run_reference_isolated_copy_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-reference-copy-") as temp_root_name:
        temp_root = Path(temp_root_name)
        source_reference = repo_root / "reference"

        temp_reference_a = temp_root / "reference-a"
        temp_reference_b = temp_root / "reference-b"
        shutil.copytree(source_reference, temp_reference_a)
        shutil.copytree(source_reference, temp_reference_b)

        inventory_a, digest_a = tree_fingerprint(temp_reference_a)
        inventory_b, digest_b = tree_fingerprint(temp_reference_b)
        source_inventory, source_digest = tree_fingerprint(source_reference)

        assert inventory_a == inventory_b == source_inventory
        assert digest_a == digest_b == source_digest
        assert_no_parent_checkout_references(temp_reference_a, repo_root)
        assert_no_parent_checkout_references(temp_reference_b, repo_root)

        run_command([str(temp_reference_a / "scripts/generate-docs")], temp_reference_a)
        run_command([str(temp_reference_a / "scripts/validate")], temp_reference_a)
        run_command([str(temp_reference_a / "scripts/validate"), "--mutation-tests"], temp_reference_a)

        run_command([str(temp_reference_b / "scripts/generate-docs")], temp_reference_b)
        run_command([str(temp_reference_b / "scripts/validate")], temp_reference_b)
        run_command([str(temp_reference_b / "scripts/validate"), "--mutation-tests"], temp_reference_b)

    print("ok: reference isolated copy tests")
