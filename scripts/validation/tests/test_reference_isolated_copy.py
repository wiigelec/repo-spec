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


def expect_command_failure(description: str, command: list[str], cwd: Path, fragment: str) -> None:
    env = minimal_env(cwd)
    result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True)
    assert result.returncode != 0, f"reference isolated copy failed: {description} did not fail"
    output = result.stdout + result.stderr
    assert fragment in output, f"reference isolated copy failed: {description} (expected {fragment!r}, got {output!r})"


def expect_assertion_failure(description: str, func, fragment: str) -> None:
    try:
        func()
    except AssertionError as exc:
        assert fragment in str(exc), f"reference isolated copy failed: {description} (expected {fragment!r}, got {exc!s})"
    else:
        raise AssertionError(f"reference isolated copy failed: {description} did not fail")


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

        temp_reference = temp_root / "reference-missing-manifest"
        shutil.copytree(source_reference, temp_reference)
        (temp_reference / "specs/product/manifest.json").unlink()
        expect_command_failure(
            "missing product manifest",
            [str(temp_reference / "scripts/validate")],
            temp_reference,
            "missing required reference paths: specs/product/manifest.json",
        )

        temp_reference = temp_root / "reference-missing-readme"
        shutil.copytree(source_reference, temp_reference)
        (temp_reference / "README.md").unlink()
        expect_command_failure(
            "missing initialization document",
            [str(temp_reference / "scripts/validate")],
            temp_reference,
            "missing required reference paths: README.md",
        )

        temp_reference = temp_root / "reference-invalid-json"
        shutil.copytree(source_reference, temp_reference)
        (temp_reference / "specs/product/manifest.json").write_text("{\n", encoding="utf-8")
        expect_command_failure(
            "invalid JSON",
            [str(temp_reference / "scripts/validate")],
            temp_reference,
            "invalid JSON",
        )

        temp_reference = temp_root / "reference-invalid-root"
        shutil.copytree(source_reference, temp_reference)
        shutil.move(str(temp_reference / "specs/product"), str(temp_reference / "specs/product-root"))
        expect_command_failure(
            "invalid product root placement",
            [str(temp_reference / "scripts/validate")],
            temp_reference,
            "missing required reference paths: specs/product/manifest.json",
        )

        temp_reference = temp_root / "reference-parent-path"
        shutil.copytree(source_reference, temp_reference)
        parent_text = repo_root.resolve().as_posix()
        overview = temp_reference / "docs/overview/REFERENCE-OVERVIEW.md"
        overview.write_text(overview.read_text(encoding="utf-8") + f"\n{parent_text}\n", encoding="utf-8")
        expect_assertion_failure(
            "parent checkout dependency",
            lambda: assert_no_parent_checkout_references(temp_reference, repo_root),
            "parent checkout reference",
        )

        temp_reference = temp_root / "reference-symlink"
        shutil.copytree(source_reference, temp_reference)
        escape = temp_reference / "src/product/escape.py"
        if escape.exists() or escape.is_symlink():
            escape.unlink()
        escape.symlink_to("/etc/passwd")
        expect_assertion_failure(
            "escaping symlink",
            lambda: tree_fingerprint(temp_reference),
            "symlink escape",
        )

        temp_reference = temp_root / "reference-test-failure"
        shutil.copytree(source_reference, temp_reference)
        test_primitives = temp_reference / "tests/test_primitives.py"
        test_primitives.write_text(
            test_primitives.read_text(encoding="utf-8").replace(
                'self.assertEqual(primitive_identity(), "reference-kernel-primitives")',
                'self.assertEqual(primitive_identity(), "broken-reference-primitives")',
                1,
            ),
            encoding="utf-8",
        )
        expect_command_failure(
            "product test failure",
            [str(temp_reference / "scripts/validate")],
            temp_reference,
            "reference product tests failed",
        )

    print("ok: reference isolated copy tests")
