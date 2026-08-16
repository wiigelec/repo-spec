from __future__ import annotations

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
    serialize_framework_lineage,
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

class UP1RequestBaselineTests(unittest.TestCase):
    def make_framework(self):
        td = tempfile.TemporaryDirectory()
        repo = Path(td.name).resolve()
        git(repo, "init", "-q")
        git(repo, "config", "user.email", "test@example.invalid")
        git(repo, "config", "user.name", "Test")
        (repo / "product/scripts/initializer").mkdir(parents=True)
        (repo / "product/specs/product/level-1").mkdir(parents=True)
        (repo / "README.md").write_text("framework-v1\n", encoding="utf-8")
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
            json.dumps(output) + "\n", encoding="utf-8"
        )
        (repo / "product/scripts/initializer/framework-inventory.json").write_text(
            json.dumps(manifest) + "\n", encoding="utf-8"
        )
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "framework-v1")
        return td, repo, git(repo, "rev-parse", "HEAD")

    def make_target(self, framework_repo: Path, framework_revision: str):
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
            "framework_repository": str(framework_repo),
            "framework_revision": {"object_format": "sha1", "object_id": framework_revision},
            "initialization_timestamp": "2026-01-01T00:00:00Z",
            "request_fingerprint": "a" * 64,
        }
        (target / "repo/initializer/provenance.json").write_text(
            json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
        )
        (target / "README.md").write_text("target\n", encoding="utf-8")
        git(target, "add", ".")
        git(target, "commit", "-qm", "initialized")
        return td, target

    def test_first_reconciliation_bootstraps_from_valid_provenance_without_mutation(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            ttd, target = self.make_target(framework, first)
            with ttd:
                before_head = git(target, "rev-parse", "HEAD")
                before_status = git(target, "status", "--porcelain=v1", "--untracked-files=all")
                result = resolve_accepted_baseline(str(target))
                self.assertEqual(result.baseline_source, "legacy-provenance-bootstrap")
                self.assertEqual(result.active_baseline.framework_revision.object_id, first)
                self.assertEqual(
                    [x.material_key for x in result.baseline_material.manifest],
                    ["root-readme"],
                )
                self.assertEqual(git(target, "rev-parse", "HEAD"), before_head)
                self.assertEqual(
                    git(target, "status", "--porcelain=v1", "--untracked-files=all"),
                    before_status,
                )
                self.assertFalse((target / "repo/initializer/framework-lineage.json").exists())

    def test_existing_lineage_selects_most_recent_accepted_entry(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            (framework / "README.md").write_text("framework-v2\n", encoding="utf-8")
            git(framework, "add", "README.md")
            git(framework, "commit", "-qm", "framework-v2")
            second = git(framework, "rev-parse", "HEAD")
            ttd, target = self.make_target(framework, first)
            with ttd:
                entries = (
                    FrameworkLineageEntry(str(framework), GitObjectIdentity("sha1", first)),
                    FrameworkLineageEntry(str(framework), GitObjectIdentity("sha1", second)),
                )
                (target / "repo/initializer/framework-lineage.json").write_bytes(
                    serialize_framework_lineage(entries)
                )
                git(target, "add", "repo/initializer/framework-lineage.json")
                git(target, "commit", "-qm", "accepted lineage")
                result = resolve_accepted_baseline(str(target))
                self.assertEqual(result.baseline_source, "accepted-lineage")
                self.assertEqual(len(result.lineage), 2)
                self.assertEqual(result.active_baseline.framework_revision.object_id, second)

    def test_present_invalid_lineage_fails_closed_without_provenance_fallback(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            ttd, target = self.make_target(framework, first)
            with ttd:
                (target / "repo/initializer/framework-lineage.json").write_text(
                    '{"schema_version":"1","entries":[]}\n', encoding="utf-8"
                )
                git(target, "add", "repo/initializer/framework-lineage.json")
                git(target, "commit", "-qm", "invalid committed lineage")
                with self.assertRaisesRegex(
                    UpgradeResolutionError, "entries must be a non-empty array"
                ):
                    resolve_accepted_baseline(str(target))

    def test_missing_or_unresolvable_bootstrap_authority_fails_closed(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            ttd, target = self.make_target(framework, first)
            with ttd:
                provenance_path = target / "repo/initializer/provenance.json"
                provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
                provenance["framework_revision"]["object_id"] = "0" * 40
                provenance_path.write_text(
                    json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
                )
                git(target, "add", "repo/initializer/provenance.json")
                git(target, "commit", "-qm", "unresolvable committed provenance")
                with self.assertRaisesRegex(
                    UpgradeResolutionError, "inventory authority cannot be resolved"
                ):
                    resolve_accepted_baseline(str(target))

    def test_dirty_lineage_cannot_replace_committed_accepted_baseline(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            (framework / "README.md").write_text("framework-v2\n", encoding="utf-8")
            git(framework, "add", "README.md")
            git(framework, "commit", "-qm", "framework-v2")
            second = git(framework, "rev-parse", "HEAD")
            (framework / "README.md").write_text("framework-v3\n", encoding="utf-8")
            git(framework, "add", "README.md")
            git(framework, "commit", "-qm", "framework-v3")
            third = git(framework, "rev-parse", "HEAD")

            ttd, target = self.make_target(framework, first)
            with ttd:
                committed = (
                    FrameworkLineageEntry(str(framework), GitObjectIdentity("sha1", first)),
                    FrameworkLineageEntry(str(framework), GitObjectIdentity("sha1", second)),
                )
                lineage_path = target / "repo/initializer/framework-lineage.json"
                lineage_path.write_bytes(serialize_framework_lineage(committed))
                git(target, "add", "repo/initializer/framework-lineage.json")
                git(target, "commit", "-qm", "accepted lineage")

                dirty = committed + (
                    FrameworkLineageEntry(str(framework), GitObjectIdentity("sha1", third)),
                )
                lineage_path.write_bytes(serialize_framework_lineage(dirty))

                result = resolve_accepted_baseline(str(target))
                self.assertEqual(result.baseline_source, "accepted-lineage")
                self.assertEqual(result.active_baseline.framework_revision.object_id, second)

    def test_dirty_provenance_cannot_replace_committed_bootstrap_authority(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            (framework / "README.md").write_text("framework-v2\n", encoding="utf-8")
            git(framework, "add", "README.md")
            git(framework, "commit", "-qm", "framework-v2")
            second = git(framework, "rev-parse", "HEAD")

            ttd, target = self.make_target(framework, first)
            with ttd:
                provenance_path = target / "repo/initializer/provenance.json"
                dirty = json.loads(provenance_path.read_text(encoding="utf-8"))
                dirty["framework_revision"]["object_id"] = second
                provenance_path.write_text(
                    json.dumps(dirty, indent=2) + "\n", encoding="utf-8"
                )

                result = resolve_accepted_baseline(str(target))
                self.assertEqual(result.baseline_source, "legacy-provenance-bootstrap")
                self.assertEqual(result.active_baseline.framework_revision.object_id, first)

    def test_untracked_lineage_cannot_shadow_committed_legacy_provenance(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            (framework / "README.md").write_text("framework-v2\n", encoding="utf-8")
            git(framework, "add", "README.md")
            git(framework, "commit", "-qm", "framework-v2")
            second = git(framework, "rev-parse", "HEAD")

            ttd, target = self.make_target(framework, first)
            with ttd:
                lineage_path = target / "repo/initializer/framework-lineage.json"
                lineage_path.write_bytes(
                    serialize_framework_lineage(
                        (
                            FrameworkLineageEntry(
                                str(framework),
                                GitObjectIdentity("sha1", second),
                            ),
                        )
                    )
                )
                result = resolve_accepted_baseline(str(target))
                self.assertEqual(result.baseline_source, "legacy-provenance-bootstrap")
                self.assertEqual(result.active_baseline.framework_revision.object_id, first)

    def test_unrelated_dirty_content_does_not_block_committed_authority_resolution(self):
        ftd, framework, first = self.make_framework()
        with ftd:
            ttd, target = self.make_target(framework, first)
            with ttd:
                (target / "README.md").write_text("locally customized\n", encoding="utf-8")
                (target / "untracked-product-note.txt").write_text("keep me\n", encoding="utf-8")
                before = git(target, "status", "--porcelain=v1", "--untracked-files=all")

                result = resolve_accepted_baseline(str(target))

                self.assertEqual(result.active_baseline.framework_revision.object_id, first)
                self.assertEqual(
                    git(target, "status", "--porcelain=v1", "--untracked-files=all"),
                    before,
                )

    def test_remote_like_target_and_nested_target_are_rejected(self):
        with self.assertRaisesRegex(UpgradeResolutionError, "local filesystem"):
            resolve_accepted_baseline("https://example.invalid/repo.git")
        ftd, framework, first = self.make_framework()
        with ftd:
            ttd, target = self.make_target(framework, first)
            with ttd:
                nested = target / "nested"
                nested.mkdir()
                with self.assertRaisesRegex(UpgradeResolutionError, "repository root exactly"):
                    resolve_accepted_baseline(str(nested))

    def test_lineage_serialization_is_deterministic_and_status_free(self):
        entry = FrameworkLineageEntry(
            "/framework", GitObjectIdentity("sha1", "1" * 40)
        )
        payload = serialize_framework_lineage((entry,))
        self.assertTrue(payload.endswith(b"\n"))
        self.assertNotIn(b"accepted", payload)
        self.assertNotIn(b"prospective", payload)
        self.assertEqual(payload, serialize_framework_lineage((entry,)))

if __name__ == "__main__":
    unittest.main()
