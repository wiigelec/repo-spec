from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from initializer.upgrade_resolution import (
    FrameworkLineageEntry,
    GitObjectIdentity,
    UpgradeResolutionError,
    resolve_accepted_baseline,
    resolve_upgrade_set,
    serialize_framework_lineage,
    serialize_upgrade_set_evidence,
    upgrade_set_evidence_fingerprint,
)


# validation-metadata: {"role": "helper"}
def git(repo: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and p.returncode:
        raise RuntimeError(p.stderr)
    return p.stdout.strip()


class UP1ConformanceTests(unittest.TestCase):
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
    def write_inventory(self, repo: Path, defs: dict[str, tuple[str, str]]):
        manifest = []
        output = []
        for key, (destination, content) in sorted(defs.items()):
            source = f"materials/{key}.txt"
            (repo / source).parent.mkdir(parents=True, exist_ok=True)
            (repo / source).write_text(content, encoding="utf-8")
            manifest.append({
                "material_key": key,
                "source_path": source,
                "role": "runtime-framework",
                "operation": "copy-verbatim",
                "source_type": "blob",
                "mode": "100644",
            })
            output.append({
                "material_key": key,
                "destination_path": destination,
                "producer": "framework-installation",
                "operation": "copy-verbatim",
                "mode": "100644",
                "required": True,
                "role": "runtime-framework",
            })
        (repo / "product/src/initializer/framework-inventory.json").write_text(
            json.dumps({"schema_version": "1", "entries": manifest}, indent=2) + "\n",
            encoding="utf-8",
        )
        (repo / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(
            json.dumps({
                "spec_id": "product.initializer-output-inventory-v1",
                "status": "accepted",
                "schema_version": "1",
                "material_index": output,
            }, indent=2) + "\n",
            encoding="utf-8",
        )

    # validation-metadata: {"role": "helper"}
    def commit(self, repo: Path, message: str) -> str:
        git(repo, "add", "-A")
        git(repo, "commit", "-qm", message)
        return git(repo, "rev-parse", "HEAD")

    # validation-metadata: {"role": "helper"}
    def make_target(self, framework: Path, revision: str, *, provenance=True):
        td = tempfile.TemporaryDirectory()
        target = Path(td.name).resolve()
        git(target, "init", "-q")
        git(target, "config", "user.email", "target@example.invalid")
        git(target, "config", "user.name", "Target")
        (target / "README.md").write_text("target\n", encoding="utf-8")
        if provenance:
            (target / "repo/initializer").mkdir(parents=True)
            record = {
                "schema_version": "2",
                "initializer_name": "repo-spec-init",
                "initializer_version": "1",
                "framework_repository": str(framework),
                "framework_revision": {
                    "object_format": "sha1",
                    "object_id": revision,
                },
                "initialization_timestamp": "2026-01-01T00:00:00Z",
                "request_fingerprint": "a" * 64,
            }
            (target / "repo/initializer/provenance.json").write_text(
                json.dumps(record, indent=2) + "\n",
                encoding="utf-8",
            )
        git(target, "add", "-A")
        git(target, "commit", "-qm", "target")
        return td, target

    # validation-metadata: {"role": "helper"}
    def test_invalid_noninitialized_and_incomplete_provenance_fail_closed(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {"a": ("a.txt", "a\n")})
            revision = self.commit(framework, "framework")

            ttd, target = self.make_target(framework, revision, provenance=False)
            with ttd:
                with self.assertRaisesRegex(
                    UpgradeResolutionError, "neither accepted framework lineage"
                ):
                    resolve_accepted_baseline(str(target))

            ttd, target = self.make_target(framework, revision)
            with ttd:
                p = target / "repo/initializer/provenance.json"
                raw = json.loads(p.read_text(encoding="utf-8"))
                del raw["request_fingerprint"]
                p.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")
                git(target, "add", "repo/initializer/provenance.json")
                git(target, "commit", "-qm", "invalid committed provenance")
                with self.assertRaisesRegex(
                    UpgradeResolutionError, "canonical ordered provenance fields"
                ):
                    resolve_accepted_baseline(str(target))

    # validation-metadata: {"role": "helper"}
    def test_subsequent_reconciliation_uses_latest_accepted_lineage_entry(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {"a": ("a.txt", "one\n")})
            first = self.commit(framework, "first")
            self.write_inventory(framework, {"a": ("a.txt", "two\n")})
            second = self.commit(framework, "second")

            ttd, target = self.make_target(framework, first)
            with ttd:
                lineage = (
                    FrameworkLineageEntry(
                        str(framework), GitObjectIdentity("sha1", first)
                    ),
                    FrameworkLineageEntry(
                        str(framework), GitObjectIdentity("sha1", second)
                    ),
                )
                (target / "repo/initializer/framework-lineage.json").write_bytes(
                    serialize_framework_lineage(lineage)
                )
                git(target, "add", "-A")
                git(target, "commit", "-qm", "accepted lineage")
                result = resolve_accepted_baseline(str(target))
                self.assertEqual(
                    result.active_baseline.framework_revision.object_id, second
                )

    # validation-metadata: {"role": "helper"}
    def test_evidence_is_deterministic_complete_and_up1_is_non_mutating(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {
                "modified": ("modified.txt", "before\n"),
                "removed": ("removed.txt", "removed\n"),
                "retargeted": ("old/path.txt", "same\n"),
            })
            baseline = self.commit(framework, "baseline")
            ttd, target = self.make_target(framework, baseline)
            with ttd:
                before_head = git(target, "rev-parse", "HEAD")
                before_status = git(
                    target, "status", "--porcelain=v1", "--untracked-files=all"
                )

                self.write_inventory(framework, {
                    "added": ("added.txt", "added\n"),
                    "modified": ("modified.txt", "after\n"),
                    "retargeted": ("new/path.txt", "same\n"),
                })
                (framework / "product/src/initializer/upgrade-qualification.json").write_text(
                    json.dumps({
                        "schema_version": "1",
                        "transitions": [
                            {"material_key": "modified", "order": 2},
                            {"material_key": "added", "order": 1},
                            {"material_key": "removed", "disposition": "defer"},
                        ],
                    }, indent=2) + "\n",
                    encoding="utf-8",
                )
                target_revision = self.commit(framework, "target")

                result = resolve_upgrade_set(str(target), str(framework))
                evidence1 = serialize_upgrade_set_evidence(result)
                evidence2 = serialize_upgrade_set_evidence(result)

                self.assertEqual(evidence1, evidence2)
                parsed = json.loads(evidence1)
                self.assertEqual(
                    parsed["baseline_revision"]["object_id"], baseline
                )
                self.assertEqual(
                    parsed["reconciliation_target_revision"]["object_id"],
                    target_revision,
                )
                self.assertIn("manifest_blob_id", parsed["baseline_endpoint"])
                self.assertIn("output_inventory_blob_id", parsed["baseline_endpoint"])
                self.assertIn("manifest_blob_id", parsed["target_endpoint"])
                self.assertIn("output_inventory_blob_id", parsed["target_endpoint"])

                classes = {
                    item["material_key"]: item["classification"]
                    for item in parsed["delta"]
                }
                self.assertEqual(classes, {
                    "added": "added",
                    "modified": "modified",
                    "removed": "removed",
                    "retargeted": "retargeted",
                })
                self.assertEqual(
                    parsed["selected_material_keys"], ["added", "modified", "retargeted"]
                )
                self.assertEqual(
                    parsed["deferred_material_keys"], ["removed"]
                )
                self.assertEqual(parsed["excluded_material_keys"], [])
                self.assertEqual(
                    upgrade_set_evidence_fingerprint(result),
                    hashlib.sha256(evidence1).hexdigest(),
                )

                self.assertEqual(git(target, "rev-parse", "HEAD"), before_head)
                self.assertEqual(
                    git(target, "status", "--porcelain=v1", "--untracked-files=all"),
                    before_status,
                )

    # validation-metadata: {"role": "helper"}
    def test_evidence_fingerprint_changes_when_authoritative_target_changes(self):
        ftd, framework = self.make_framework()
        with ftd:
            self.write_inventory(framework, {"a": ("a.txt", "one\n")})
            baseline = self.commit(framework, "baseline")
            ttd, target = self.make_target(framework, baseline)
            with ttd:
                self.write_inventory(framework, {"a": ("a.txt", "two\n")})
                self.commit(framework, "target-one")
                first = upgrade_set_evidence_fingerprint(
                    resolve_upgrade_set(str(target), str(framework))
                )

                self.write_inventory(framework, {"a": ("a.txt", "three\n")})
                self.commit(framework, "target-two")
                second = upgrade_set_evidence_fingerprint(
                    resolve_upgrade_set(str(target), str(framework))
                )

                self.assertNotEqual(first, second)


if __name__ == "__main__":
    unittest.main()
