from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from initializer.upgrade_reconciliation import (
    stage_managed_reconciliation,
    staged_reconciliation_evidence_fingerprint,
)
from initializer.upgrade_resolution import (
    GitObjectIdentity,
    InventoryEndpoint,
    ManagedMaterialDeltaEntry,
)


def git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


def commit_blob(repo: Path, path: str, content: str) -> tuple[str, str]:
    full = repo / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content, encoding="utf-8")
    git(repo, "add", path)
    git(repo, "commit", "-qm", f"add {path}")
    return git(repo, "rev-parse", "HEAD"), git(repo, "rev-parse", f"HEAD:{path}")


def evidence(key: str, destination: str, blob: str):
    return {
        "material_key": key,
        "destination_path": destination,
        "producer": "framework-installation",
        "operation": "copy-verbatim",
        "mode": "100644",
        "required": True,
        "role": "runtime-framework",
        "source_path": f"materials/{key}.txt",
        "source_type": "blob",
        "profile": None,
        "exclusion_rationale": None,
        "source_blob_id": blob,
    }


class UP2StagedManagedReconciliationTests(unittest.TestCase):
    def make_repo(self):
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name).resolve()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "user.name", "Test")
        return td, repo

    def build_resolution(self, target, baseline_repo, target_repo, delta, selected):
        baseline_endpoint = InventoryEndpoint(
            repository=str(baseline_repo),
            revision=GitObjectIdentity("sha1", git(baseline_repo, "rev-parse", "HEAD")),
            manifest_blob_id="1" * 40,
            output_inventory_blob_id="2" * 40,
            materials={x.material_key: x.baseline for x in delta if x.baseline is not None},
        )
        target_endpoint = InventoryEndpoint(
            repository=str(target_repo),
            revision=GitObjectIdentity("sha1", git(target_repo, "rev-parse", "HEAD")),
            manifest_blob_id="3" * 40,
            output_inventory_blob_id="4" * 40,
            materials={x.material_key: x.target for x in delta if x.target is not None},
        )
        return SimpleNamespace(
            baseline=SimpleNamespace(request=SimpleNamespace(target_repository=str(target))),
            baseline_endpoint=baseline_endpoint,
            target_endpoint=target_endpoint,
            delta=tuple(delta),
            selected_material_keys=tuple(selected),
        )

    def test_selected_operations_preserve_unmanaged_and_original_target(self):
        btd, baseline = self.make_repo()
        std, source = self.make_repo()
        ttd, target = self.make_repo()
        with btd, std, ttd:
            _, modified_old = commit_blob(baseline, "materials/modified.txt", "old\n")
            _, removed_old = commit_blob(baseline, "materials/removed.txt", "remove\n")
            _, retarget_old = commit_blob(baseline, "materials/retarget.txt", "move\n")

            _, added_new = commit_blob(source, "materials/added.txt", "added\n")
            _, modified_new = commit_blob(source, "materials/modified.txt", "new\n")
            _, retarget_new = commit_blob(source, "materials/retarget.txt", "move-new\n")

            (target / "managed").mkdir()
            (target / "managed/modified.txt").write_text("old\n")
            (target / "managed/removed.txt").write_text("remove\n")
            (target / "managed/old.txt").write_text("move\n")
            (target / "product-owned.txt").write_text("preserve\n")
            git(target, "add", "-A")
            git(target, "commit", "-qm", "target")
            original_head = git(target, "rev-parse", "HEAD")
            original_status = git(target, "status", "--porcelain=v1", "--untracked-files=all")

            delta = (
                ManagedMaterialDeltaEntry("added", "added", None,
                    evidence("added", "managed/added.txt", added_new)),
                ManagedMaterialDeltaEntry("modified", "modified",
                    evidence("modified", "managed/modified.txt", modified_old),
                    evidence("modified", "managed/modified.txt", modified_new)),
                ManagedMaterialDeltaEntry("removed", "removed",
                    evidence("removed", "managed/removed.txt", removed_old), None),
                ManagedMaterialDeltaEntry("retarget", "retargeted",
                    evidence("retarget", "managed/old.txt", retarget_old),
                    evidence("retarget", "managed/new.txt", retarget_new)),
            )
            resolution = self.build_resolution(
                target, baseline, source, delta,
                ("added", "modified", "removed", "retarget"),
            )
            result = stage_managed_reconciliation(resolution)
            self.addCleanup(__import__("shutil").rmtree, result.staging_root, True)

            staged = Path(result.repository_path)
            self.assertEqual(result.status, "staged")
            self.assertEqual((staged / "managed/added.txt").read_text(), "added\n")
            self.assertEqual((staged / "managed/modified.txt").read_text(), "new\n")
            self.assertFalse((staged / "managed/removed.txt").exists())
            self.assertFalse((staged / "managed/old.txt").exists())
            self.assertEqual((staged / "managed/new.txt").read_text(), "move-new\n")
            self.assertEqual((staged / "product-owned.txt").read_text(), "preserve\n")
            self.assertEqual(list(Path(result.transaction_path).iterdir()), [])
            self.assertEqual(git(target, "rev-parse", "HEAD"), original_head)
            self.assertEqual(
                git(target, "status", "--porcelain=v1", "--untracked-files=all"),
                original_status,
            )
            self.assertEqual(
                staged_reconciliation_evidence_fingerprint(result),
                staged_reconciliation_evidence_fingerprint(result),
            )

    def test_dirty_managed_state_conflicts_before_any_operation(self):
        btd, baseline = self.make_repo()
        std, source = self.make_repo()
        ttd, target = self.make_repo()
        with btd, std, ttd:
            _, old_blob = commit_blob(baseline, "materials/a.txt", "old\n")
            _, new_blob = commit_blob(source, "materials/a.txt", "new\n")
            _, add_blob = commit_blob(source, "materials/b.txt", "added\n")

            (target / "managed").mkdir()
            (target / "managed/a.txt").write_text("local edit\n")
            git(target, "add", "-A")
            git(target, "commit", "-qm", "target")

            delta = (
                ManagedMaterialDeltaEntry("a", "modified",
                    evidence("a", "managed/a.txt", old_blob),
                    evidence("a", "managed/a.txt", new_blob)),
                ManagedMaterialDeltaEntry("b", "added", None,
                    evidence("b", "managed/b.txt", add_blob)),
            )
            result = stage_managed_reconciliation(
                self.build_resolution(target, baseline, source, delta, ("a", "b"))
            )
            self.addCleanup(__import__("shutil").rmtree, result.staging_root, True)
            staged = Path(result.repository_path)

            self.assertEqual(result.status, "conflict")
            self.assertEqual(result.operations, ())
            self.assertEqual(len(result.conflicts), 1)
            self.assertEqual(result.conflicts[0].material_key, "a")
            self.assertEqual((staged / "managed/a.txt").read_text(), "local edit\n")
            self.assertFalse((staged / "managed/b.txt").exists())

    def test_unselected_transition_is_preserved(self):
        btd, baseline = self.make_repo()
        std, source = self.make_repo()
        ttd, target = self.make_repo()
        with btd, std, ttd:
            _, old_blob = commit_blob(baseline, "materials/a.txt", "old\n")
            _, new_blob = commit_blob(source, "materials/a.txt", "new\n")
            (target / "managed").mkdir()
            (target / "managed/a.txt").write_text("old\n")
            git(target, "add", "-A")
            git(target, "commit", "-qm", "target")

            delta = (
                ManagedMaterialDeltaEntry("a", "modified",
                    evidence("a", "managed/a.txt", old_blob),
                    evidence("a", "managed/a.txt", new_blob)),
            )
            result = stage_managed_reconciliation(
                self.build_resolution(target, baseline, source, delta, ())
            )
            self.addCleanup(__import__("shutil").rmtree, result.staging_root, True)

            self.assertEqual(result.operations, ())
            self.assertEqual(result.conflicts, ())
            self.assertEqual(
                (Path(result.repository_path) / "managed/a.txt").read_text(),
                "old\n",
            )


if __name__ == "__main__":
    unittest.main()
