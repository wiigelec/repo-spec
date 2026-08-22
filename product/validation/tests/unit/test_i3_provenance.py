from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from initializer.inventory import ResolvedSourceMaterial
from initializer.models import I1DestinationPreflight
from initializer.provenance import (
    PROVENANCE_FIELD_ORDER,
    PROVENANCE_RELATIVE_PATH,
    ProvenanceError,
    ProvenanceInputs,
    build_provenance_record,
    serialize_provenance_record,
    write_provenance_record,
)
from initializer.staging import I2StagingInputs, establish_staging_workspace
from initializer.validation import validate_and_normalize

OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


class I3ProvenanceTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def make_workspace(self):
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
            I2StagingInputs(request, resolved, preflight)
        )
        self.addCleanup(td.cleanup)
        return workspace

    # validation-metadata: {"role": "helper"}
    def inputs(self) -> ProvenanceInputs:
        return ProvenanceInputs(
            "repo-spec-init",
            "1",
            "2026-08-08T19:00:00Z",
        )

    # validation-metadata: {"role": "helper"}
    def test_build_record_uses_exact_v2_closed_order(self):
        workspace = self.make_workspace()
        record = build_provenance_record(workspace, self.inputs())
        self.assertEqual(tuple(record.keys()), PROVENANCE_FIELD_ORDER)
        self.assertEqual(record["schema_version"], "2")
        self.assertEqual(
            record["framework_repository"],
            workspace.inputs.source.repository,
        )
        self.assertEqual(
            record["framework_revision"],
            {"object_format": "sha1", "object_id": OBJECT_ID},
        )
        self.assertEqual(
            record["request_fingerprint"],
            workspace.inputs.request.request_fingerprint,
        )
        self.assertNotIn("product_identifier", record)
        self.assertNotIn("request_identifier", record)

    # validation-metadata: {"role": "helper"}
    def test_serialization_is_deterministic(self):
        record = build_provenance_record(
            self.make_workspace(),
            self.inputs(),
        )
        first = serialize_provenance_record(record)
        self.assertEqual(first, serialize_provenance_record(record))
        self.assertTrue(first.endswith(b"\n"))
        self.assertEqual(
            list(json.loads(first).keys()),
            list(PROVENANCE_FIELD_ORDER),
        )

    # validation-metadata: {"role": "helper"}
    def test_write_places_record_at_exact_path(self):
        workspace = self.make_workspace()
        result = write_provenance_record(workspace, self.inputs())
        self.assertEqual(
            result.path,
            workspace.repository_path / PROVENANCE_RELATIVE_PATH,
        )
        self.assertTrue(result.path.is_file())

    # validation-metadata: {"role": "helper"}
    def test_rejects_invalid_timestamp(self):
        workspace = self.make_workspace()
        with self.assertRaises(ProvenanceError):
            write_provenance_record(
                workspace,
                ProvenanceInputs(
                    "repo-spec-init",
                    "1",
                    "2026-08-08T13:00:00-06:00",
                ),
            )

    # validation-metadata: {"role": "helper"}
    def test_rejects_extra_serialization_fields(self):
        record = build_provenance_record(
            self.make_workspace(),
            self.inputs(),
        )
        record["status"] = "completed"
        with self.assertRaises(ProvenanceError):
            serialize_provenance_record(record)


if __name__ == "__main__":
    unittest.main()
