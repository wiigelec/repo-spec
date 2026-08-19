from __future__ import annotations

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
from initializer.models import I1DestinationPreflight
from initializer.provenance import ProvenanceInputs, write_provenance_record
from initializer.staging import (
    I2RealizationResult,
    I2StagingInputs,
    establish_staging_workspace,
)
from initializer.validation import validate_and_normalize

OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


class I3HandoffTests(unittest.TestCase):
    def make_realization(self):
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        source = root / "source"
        source.mkdir()
        destination = root / "output"

        request = validate_and_normalize(
            {"schema_version": "2", "destination": str(destination)},
            str(root),
        ).request
        resolved = ResolvedSourceMaterial(
            repository=str(source),
            commit_id=OBJECT_ID,
            manifest=(),
            direction_material=(),
        )
        stat = destination.parent.stat()
        preflight = I1DestinationPreflight(
            destination=str(destination),
            destination_state="absent",
            destination_parent=str(destination.parent),
            filesystem_device=stat.st_dev,
            same_filesystem=True,
            decision="allowed",
        )
        workspace = establish_staging_workspace(
            I2StagingInputs(request, resolved, preflight)
        )

        framework = ("README.md", "repo/scripts/validate")
        for path in framework:
            target = workspace.repository_path / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(path + "\n", encoding="utf-8")

        realization = I2RealizationResult(
            workspace=workspace,
            framework_paths=framework,
            foundation_paths=(),
        )
        write_provenance_record(
            workspace,
            ProvenanceInputs(
                "repo-spec-init",
                "1",
                "2026-08-08T19:00:00Z",
            ),
        )
        self.addCleanup(td.cleanup)
        return realization

    def test_classification_is_framework_only_at_bootstrap(self):
        c = classify_handoff(self.make_realization())
        self.assertEqual(c.product, ())
        self.assertEqual(c.selected, ())
        self.assertEqual(c.omitted, ())
        self.assertEqual(c.deferred, ())
        self.assertIn("README.md", c.framework)
        self.assertIn("repo/initializer/provenance.json", c.generated)
        self.assertIn("repo/initializer/handoff.json", c.generated)

    def test_manifest_has_v2_closed_shape(self):
        manifest = build_handoff_manifest(
            classify_handoff(self.make_realization())
        )
        self.assertEqual(manifest["schema_version"], "2")
        self.assertEqual(manifest["foundations"]["product"], [])
        self.assertEqual(manifest["next_action"], NEXT_ACTION)

    def test_serialization_is_deterministic(self):
        manifest = build_handoff_manifest(
            classify_handoff(self.make_realization())
        )
        payload = serialize_handoff_manifest(manifest)
        self.assertEqual(
            payload,
            serialize_handoff_manifest(manifest),
        )
        self.assertTrue(payload.endswith(b"\n"))

    def test_write_classifies_handoff_itself(self):
        realization = self.make_realization()
        result = write_handoff_manifest(realization)
        self.assertEqual(
            result.path,
            realization.workspace.repository_path / HANDOFF_RELATIVE_PATH,
        )
        self.assertTrue(result.path.is_file())

    def test_rejects_undeclared_present_file(self):
        realization = self.make_realization()
        (realization.workspace.repository_path / "rogue.txt").write_text(
            "rogue",
            encoding="utf-8",
        )
        with self.assertRaises(HandoffError):
            classify_handoff(realization)


if __name__ == "__main__":
    unittest.main()
