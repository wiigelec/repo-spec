from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from initializer.upgrade_resolution import UpgradeResolutionError, resolve_upgrade_set


# validation-metadata: {"role": "helper"}
def git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return p.stdout.strip()


class UP1DeltaAndUpgradeSetTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def make_framework(self):
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name).resolve()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "user.name", "Test")
        (repo / "product/src/initializer").mkdir(parents=True)
        (repo / "product/specs/product/level-1").mkdir(parents=True)
        return td, repo

    # validation-metadata: {"role": "helper"}
    def write_inventory(self, repo: Path, definitions: dict[str, tuple[str, str]]):
        manifest_entries = []
        output_entries = []
        source_root = repo / "materials"
        source_root.mkdir(exist_ok=True)
        for key, (destination, content) in sorted(definitions.items()):
            source_path = f"materials/{key}.txt"
            (repo / source_path).write_text(content, encoding="utf-8")
            manifest_entries.append({
                "material_key": key,
                "source_path": source_path,
                "role": "runtime-framework",
                "operation": "copy-verbatim",
                "source_type": "blob",
                "mode": "100644",
            })
            output_entries.append({
                "material_key": key,
                "destination_path": destination,
                "producer": "framework-installation",
                "operation": "copy-verbatim",
                "mode": "100644",
                "required": True,
                "role": "runtime-framework",
            })
        (repo / "product/src/initializer/framework-inventory.json").write_text(
            json.dumps({"schema_version": "1", "entries": manifest_entries}, indent=2) + "\n",
            encoding="utf-8",
        )
        (repo / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(
            json.dumps({
                "spec_id": "product.initializer-output-inventory-v1",
                "status": "accepted",
                "schema_version": "1",
                "material_index": output_entries,
            }, indent=2) + "\n",
            encoding="utf-8",
        )

    # validation-metadata: {"role": "helper"}
    def commit(self, repo: Path, message: str) -> str:
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", message)
        return git(repo, "rev-parse", "HEAD")

    # validation-metadata: {"role": "helper"}
    def make_target(self, framework: Path, baseline_revision: str):
        td = tempfile.TemporaryDirectory()
        target = Path(td.name).resolve()
        git(target, "init", "-q")
        git(target, "config", "user.email", "target@example.invalid")
        git(target, "config", "user.name", "Target")
        (target / "repo/initializer").mkdir(parents=True)
        provenance = {
            "schema_version": "2",
            "initializer_name": "repo-spec-init",
            "initializer_version": "1",
            "framework_repository": str(framework),
            "framework_revision": {
                "object_format": "sha1",
                "object_id": baseline_revision,
            },
            "initialization_timestamp": "2026-01-01T00:00:00Z",
            "request_fingerprint": "a" * 64,
        }
        (target / "repo/initializer/provenance.json").write_text(
            json.dumps(provenance, indent=2) + "\n",
            encoding="utf-8",
        )
        (target / "README.md").write_text("target\n", encoding="utf-8")
        git(target, "add", "-A")
        git(target, "commit", "-qm", "initialized")
        return td, target

    # validation-metadata: {"role": "helper"}
    def test_classifies_union_by_stable_material_key_and_exact_source_identity(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {
                "unchanged": ("same.txt", "same\n"),
                "modified": ("modified.txt", "before\n"),
                "removed": ("removed.txt", "gone\n"),
                "retargeted": ("old/path.txt", "retarget\n"),
            })
            baseline = self.commit(framework, "baseline")
            ttd, target = self.make_target(framework, baseline)
            with ttd:
                self.write_inventory(framework, {
                    "unchanged": ("same.txt", "same\n"),
                    "modified": ("modified.txt", "after\n"),
                    "added": ("added.txt", "new\n"),
                    "retargeted": ("new/path.txt", "retarget\n"),
                })
                self.commit(framework, "target")
                result = resolve_upgrade_set(str(target), str(framework))
                classes = {entry.material_key: entry.classification for entry in result.delta}
                self.assertEqual(classes, {
                    "added": "added",
                    "modified": "modified",
                    "removed": "removed",
                    "retargeted": "retargeted",
                    "unchanged": "unchanged",
                })
                self.assertEqual(
                    set(result.selected_material_keys),
                    {"added", "modified", "removed", "retargeted"},
                )
                self.assertEqual(result.excluded_material_keys, ())
                self.assertEqual(result.deferred_material_keys, ())
                evidence = result.to_dict()
                self.assertEqual(evidence["baseline_revision"]["object_id"], baseline)
                self.assertTrue(evidence["baseline_endpoint"]["manifest_blob_id"])
                self.assertTrue(evidence["target_endpoint"]["output_inventory_blob_id"])

    # validation-metadata: {"role": "helper"}
    def test_target_owned_qualification_only_constrains_existing_transitions(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {
                "a": ("a.txt", "old-a\n"),
                "b": ("b.txt", "old-b\n"),
                "c": ("c.txt", "old-c\n"),
            })
            baseline = self.commit(framework, "baseline")
            ttd, target = self.make_target(framework, baseline)
            with ttd:
                self.write_inventory(framework, {
                    "a": ("a.txt", "new-a\n"),
                    "b": ("b.txt", "new-b\n"),
                    "c": ("c.txt", "new-c\n"),
                })
                (framework / "product/src/initializer/upgrade-qualification.json").write_text(
                    json.dumps({
                        "schema_version": "1",
                        "transitions": [
                            {"material_key": "a", "order": 10},
                            {"material_key": "b", "disposition": "exclude"},
                            {"material_key": "c", "disposition": "defer"},
                        ],
                    }, indent=2) + "\n",
                    encoding="utf-8",
                )
                self.commit(framework, "qualified target")
                result = resolve_upgrade_set(str(target), str(framework))
                self.assertEqual(result.selected_material_keys, ("a",))
                self.assertEqual(result.excluded_material_keys, ("b",))
                self.assertEqual(result.deferred_material_keys, ("c",))
                self.assertEqual(
                    {q.material_key for q in result.qualification},
                    {"a", "b", "c"},
                )

    # validation-metadata: {"role": "helper"}
    def test_qualification_cannot_expand_to_unmanaged_or_unchanged_material(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {"same": ("same.txt", "same\n")})
            baseline = self.commit(framework, "baseline")
            ttd, target = self.make_target(framework, baseline)
            with ttd:
                self.write_inventory(framework, {"same": ("same.txt", "same\n")})
                qpath = framework / "product/src/initializer/upgrade-qualification.json"
                qpath.write_text(
                    json.dumps({
                        "schema_version": "1",
                        "transitions": [{"material_key": "unmanaged", "order": 1}],
                    }) + "\n",
                    encoding="utf-8",
                )
                self.commit(framework, "bad unmanaged qualification")
                with self.assertRaisesRegex(UpgradeResolutionError, "unmanaged material"):
                    resolve_upgrade_set(str(target), str(framework))

                qpath.write_text(
                    json.dumps({
                        "schema_version": "1",
                        "transitions": [{"material_key": "same", "order": 1}],
                    }) + "\n",
                    encoding="utf-8",
                )
                self.commit(framework, "bad unchanged qualification")
                with self.assertRaisesRegex(UpgradeResolutionError, "non-transition material"):
                    resolve_upgrade_set(str(target), str(framework))

    # validation-metadata: {"role": "helper"}
    def test_dirty_reconciliation_target_fails_closed_before_set_resolution(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {"a": ("a.txt", "old\n")})
            baseline = self.commit(framework, "baseline")
            ttd, target = self.make_target(framework, baseline)
            with ttd:
                self.write_inventory(framework, {"a": ("a.txt", "new\n")})
                self.commit(framework, "target")
                (framework / "untracked.txt").write_text("dirty\n", encoding="utf-8")
                with self.assertRaisesRegex(
                    UpgradeResolutionError, "reconciliation-target framework cannot be resolved"
                ):
                    resolve_upgrade_set(str(target), str(framework))


if __name__ == "__main__":
    unittest.main()
