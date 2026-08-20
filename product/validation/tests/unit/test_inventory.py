from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from initializer.inventory import (
    MATERIAL_ROLES,
    InventoryError,
    resolve_source_material,
    validate_material_manifest,
)


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return p.stdout.strip()


class SourceMaterialTests(unittest.TestCase):
    def manifest_pair(self, role: str) -> tuple[dict, dict]:
        output = {"material_index": [{
            "material_key": "a",
            "operation": "copy-verbatim",
            "mode": "100644",
            "role": role,
        }]}
        manifest = {"schema_version": "1", "entries": [{
            "material_key": "a",
            "source_path": "README.md",
            "role": role,
            "operation": "copy-verbatim",
            "source_type": "blob",
            "mode": "100644",
        }]}
        return manifest, output

    def make_repo(self) -> tuple[tempfile.TemporaryDirectory, Path, str]:
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name)
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "user.name", "Test")
        (repo / "product/src/initializer").mkdir(parents=True)
        (repo / "product/specs/product/level-1").mkdir(parents=True)
        (repo / "docs").mkdir()
        (repo / "README.md").write_text("readme\n")
        (repo / "docs/OVERVIEW.md").write_text("direction\n")
        output = {"material_index": [{
            "material_key": "root-readme",
            "destination_path": "README.md",
            "producer": "framework-installation",
            "operation": "copy-verbatim",
            "mode": "100644",
            "required": True,
            "role": "runtime-framework",
        }]}
        manifest = {"schema_version": "1", "entries": [{
            "material_key": "root-readme",
            "source_path": "README.md",
            "role": "runtime-framework",
            "operation": "copy-verbatim",
            "source_type": "blob",
            "mode": "100644",
        }]}
        (repo / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(
            json.dumps(output) + "\n"
        )
        (repo / "product/src/initializer/framework-inventory.json").write_text(
            json.dumps(manifest) + "\n"
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "source")
        return td, repo, git(repo, "rev-parse", "HEAD")

    def test_resolves_exact_commit_tree_and_ignores_worktree(self) -> None:
        td, repo, oid = self.make_repo()
        with td:
            (repo / "README.md").write_text("dirty worktree\n")
            resolved = resolve_source_material(str(repo), oid, ("docs/OVERVIEW.md",))
            self.assertEqual(resolved.commit_id, oid)
            self.assertEqual(resolved.manifest[0].source_path, "README.md")
            self.assertEqual(resolved.direction_material, ("docs/OVERVIEW.md",))

    def test_rejects_missing_exact_revision_and_named_ref(self) -> None:
        td, repo, _oid = self.make_repo()
        with td:
            with self.assertRaises(InventoryError):
                resolve_source_material(str(repo), "0" * 40, ("docs/OVERVIEW.md",))
            with self.assertRaises(InventoryError):
                resolve_source_material(str(repo), "main", ("docs/OVERVIEW.md",))

    def test_manifest_mapping_is_closed_and_tree_source_is_rejected(self) -> None:
        output = {"material_index": [{
            "material_key": "a",
            "operation": "copy-verbatim",
            "mode": "100644",
            "role": "runtime-framework",
        }]}
        with self.assertRaises(InventoryError):
            validate_material_manifest({"schema_version": "1", "entries": []}, output)
        tree = {"schema_version": "1", "entries": [{
            "material_key": "a",
            "source_path": "tree",
            "role": "runtime-framework",
            "operation": "copy-verbatim",
            "source_type": "tree",
            "mode": "040000",
        }]}
        with self.assertRaises(InventoryError):
            validate_material_manifest(tree, output)

    def test_direction_material_requires_regular_commit_tree_file(self) -> None:
        td, repo, oid = self.make_repo()
        with td:
            with self.assertRaises(InventoryError):
                resolve_source_material(str(repo), oid, ("missing.md",))
            with self.assertRaises(InventoryError):
                resolve_source_material(str(repo), oid, ("docs",))

    def test_accepts_each_declared_framework_output_role(self) -> None:
        for role in MATERIAL_ROLES:
            with self.subTest(role=role):
                manifest, output = self.manifest_pair(role)
                self.assertEqual(validate_material_manifest(manifest, output)[0].role, role)

    def test_rejects_unknown_and_development_only_output_roles(self) -> None:
        for role in ("unknown-role", "development-only"):
            with self.subTest(role=role):
                manifest, output = self.manifest_pair(role)
                with self.assertRaises(InventoryError):
                    validate_material_manifest(manifest, output)

    def test_rejects_unknown_and_development_only_manifest_roles(self) -> None:
        for role in ("unknown-role", "development-only"):
            with self.subTest(role=role):
                manifest, output = self.manifest_pair("runtime-framework")
                manifest["entries"][0]["role"] = role
                with self.assertRaises(InventoryError):
                    validate_material_manifest(manifest, output)

    def test_rejects_role_disagreement(self) -> None:
        manifest, output = self.manifest_pair("runtime-framework")
        manifest["entries"][0]["role"] = "validation-utility"
        with self.assertRaisesRegex(InventoryError, "disagrees.*role"):
            validate_material_manifest(manifest, output)


if __name__ == "__main__":
    unittest.main()
