from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from initializer.handoff import (
    HANDOFF_RELATIVE_PATH,
    NEXT_ACTION,
    HandoffError,
    build_handoff_manifest,
    classify_handoff,
    serialize_handoff_manifest,
    write_handoff_manifest,
)
from initializer.inventory import ResolvedSourceMaterial
from initializer.models import ImmutableRequest, I1DestinationPreflight
from initializer.provenance import ProvenanceInputs, write_provenance_record
from initializer.staging import (
    I2RealizationResult,
    I2StagingInputs,
    establish_staging_workspace,
)


OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


class I3HandoffTests(unittest.TestCase):
    def make_realization(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        source = root / "source"
        source.mkdir()
        destination = root / "output"
        raw = {
            "schema_version": "1",
            "destination": str(destination),
            "authority": {"granted_by": "issue-281"},
            "source": {
                "repository": str(source),
                "revision": {"object_format": "sha1", "object_id": OBJECT_ID},
            },
            "product": {
                "id": "sample-product",
                "direction_material": ["direction/one.md"],
            },
        }
        request = ImmutableRequest(
            raw,
            canonical_request_bytes=b"canonical",
            request_fingerprint="fingerprint",
        )
        source_material = ResolvedSourceMaterial(
            repository=str(source),
            commit_id=OBJECT_ID,
            manifest=(),
            direction_material=("direction/one.md",),
        )
        parent_stat = destination.parent.stat()
        preflight = I1DestinationPreflight(
            destination=str(destination),
            destination_state="absent",
            destination_parent=str(destination.parent),
            filesystem_device=parent_stat.st_dev,
            same_filesystem=True,
            decision="allowed",
        )
        workspace = establish_staging_workspace(
            I2StagingInputs(request, source_material, preflight)
        )

        framework = (
            "README.md",
            "repo/scripts/validate",
        )
        foundations = (
            "docs/overview/sample-product-OVERVIEW.md",
            "docs/overview/sample-product-overview/chunk-01-identity-and-purpose.md",
            "docs/decompositions/sample-product-DECOMPOSITION.md",
            "docs/plans/sample-product-IMPLEMENTATION-PLAN.md",
            "product/specs/product/level-0/README.md",
            "product/specs/product/level-1/README.md",
            "product/specs/product/level-2/README.md",
            "product/specs/product/level-3/README.md",
            "product/docs/direction/evidence/000-one.md",
            "product/docs/direction/manifest.json",
            "docs/overview/README.md",
            "product/specs/product/README.md",
            "product/specs/product/manifest.json",
        )
        for path in framework + foundations:
            target = workspace.repository_path / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(path + "\n", encoding="utf-8")

        realization = I2RealizationResult(
            workspace=workspace,
            framework_paths=framework,
            foundation_paths=foundations,
        )
        write_provenance_record(
            workspace,
            ProvenanceInputs(
                initializer_name="repo-spec-init",
                initializer_version="1",
                initialization_timestamp="2026-08-08T19:00:00Z",
            ),
        )
        self.addCleanup(td.cleanup)
        return realization

    def test_classification_is_disjoint_sorted_and_complete(self):
        realization = self.make_realization()
        c = classify_handoff(realization)

        self.assertEqual(c.framework, tuple(sorted(c.framework)))
        self.assertEqual(c.product, tuple(sorted(c.product)))
        self.assertEqual(c.generated, tuple(sorted(c.generated)))
        self.assertEqual(c.selected, tuple(sorted(c.selected)))
        self.assertEqual(len(c.all_paths()), len(set(c.all_paths())))
        self.assertIn("README.md", c.framework)
        self.assertIn("docs/overview/sample-product-OVERVIEW.md", c.product)
        self.assertIn(
            "product/docs/direction/evidence/000-one.md",
            c.selected,
        )
        self.assertIn("product/docs/direction/manifest.json", c.generated)
        self.assertIn("repo/initializer/provenance.json", c.generated)
        self.assertIn("repo/initializer/handoff.json", c.generated)

    def test_manifest_has_exact_closed_shape_and_constants(self):
        realization = self.make_realization()
        manifest = build_handoff_manifest(classify_handoff(realization))
        self.assertEqual(list(manifest), [
            "schema_version", "foundations", "material", "provenance", "next_action"
        ])
        self.assertEqual(manifest["schema_version"], "2")
        self.assertEqual(manifest["provenance"], "repo/initializer/provenance.json")
        self.assertEqual(manifest["next_action"], NEXT_ACTION)
        self.assertEqual(list(manifest["foundations"]), ["framework", "product"])
        self.assertEqual(
            list(manifest["material"]),
            ["generated", "selected", "omitted", "deferred"],
        )

    def test_serialization_is_deterministic_and_has_one_final_newline(self):
        realization = self.make_realization()
        manifest = build_handoff_manifest(classify_handoff(realization))
        a = serialize_handoff_manifest(manifest)
        b = serialize_handoff_manifest(manifest)
        self.assertEqual(a, b)
        self.assertTrue(a.endswith(b"\n"))
        self.assertFalse(a.endswith(b"\n\n"))
        self.assertEqual(json.loads(a.decode("utf-8"))["schema_version"], "2")

    def test_write_classifies_handoff_itself_and_all_regular_files(self):
        realization = self.make_realization()
        result = write_handoff_manifest(realization)
        expected = realization.workspace.repository_path / HANDOFF_RELATIVE_PATH
        self.assertEqual(result.path, expected)
        self.assertTrue(expected.is_file())
        self.assertIn(HANDOFF_RELATIVE_PATH.as_posix(), result.classifications.generated)

    def test_rejects_undeclared_present_regular_file(self):
        realization = self.make_realization()
        rogue = realization.workspace.repository_path / "rogue.txt"
        rogue.write_text("rogue\n", encoding="utf-8")
        with self.assertRaisesRegex(HandoffError, "undeclared"):
            classify_handoff(realization)

    def test_rejects_present_omitted_path(self):
        realization = self.make_realization()
        with self.assertRaises(HandoffError):
            classify_handoff(realization, omitted=("README.md",))

    def test_rejects_duplicate_cross_classification_path(self):
        realization = self.make_realization()
        with self.assertRaisesRegex(HandoffError, "mutually disjoint"):
            classify_handoff(
                realization,
                deferred=("README.md",),
            )

    def test_rejects_git_administrative_state_before_handoff(self):
        realization = self.make_realization()
        git_dir = realization.workspace.repository_path / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        with self.assertRaisesRegex(HandoffError, "Git administrative state"):
            classify_handoff(realization)

    def test_handoff_does_not_claim_completion_or_observed_git_state(self):
        realization = self.make_realization()
        manifest = build_handoff_manifest(classify_handoff(realization))
        text = json.dumps(manifest)
        self.assertNotIn('"status"', text)
        self.assertNotIn("completed", text.lower())
        self.assertNotIn('"branch"', text)
        self.assertNotIn('"commit"', text)
        self.assertNotIn('"remote"', text)


if __name__ == "__main__":
    unittest.main()
