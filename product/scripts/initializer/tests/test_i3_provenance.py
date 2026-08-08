from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from initializer.inventory import ResolvedSourceMaterial
from initializer.models import ImmutableRequest, I1DestinationPreflight
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


OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


class I3ProvenanceTests(unittest.TestCase):
    def make_workspace(self):
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
        immutable = ImmutableRequest(
            raw,
            canonical_request_bytes=b"canonical-request",
            request_fingerprint="request-fingerprint",
        )
        resolved = ResolvedSourceMaterial(
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
            I2StagingInputs(
                request=immutable,
                source=resolved,
                destination=preflight,
            )
        )
        self.addCleanup(td.cleanup)
        return workspace

    def inputs(self) -> ProvenanceInputs:
        return ProvenanceInputs(
            initializer_name="repo-spec-init",
            initializer_version="1",
            initialization_timestamp="2026-08-08T19:00:00Z",
        )

    def test_build_record_uses_exact_closed_order_and_carried_identity(self):
        workspace = self.make_workspace()
        record = build_provenance_record(workspace, self.inputs())

        self.assertEqual(tuple(record.keys()), PROVENANCE_FIELD_ORDER)
        self.assertEqual(record["schema_version"], "1")
        self.assertEqual(record["initializer_name"], "repo-spec-init")
        self.assertEqual(record["initializer_version"], "1")
        self.assertEqual(record["product_identifier"], "sample-product")
        self.assertEqual(record["source_repository"], workspace.inputs.request.source_repository)
        self.assertEqual(
            record["source_revision"],
            {"object_format": "sha1", "object_id": OBJECT_ID},
        )
        self.assertEqual(record["request_identifier"], "issue-281")

    def test_serialization_is_deterministic_two_space_json_with_one_newline(self):
        workspace = self.make_workspace()
        record = build_provenance_record(workspace, self.inputs())

        first = serialize_provenance_record(record)
        second = serialize_provenance_record(record)

        self.assertEqual(first, second)
        self.assertTrue(first.endswith(b"\n"))
        self.assertFalse(first.endswith(b"\n\n"))
        parsed = json.loads(first.decode("utf-8"))
        self.assertEqual(list(parsed.keys()), list(PROVENANCE_FIELD_ORDER))
        self.assertIn('\n  "initializer_name":', first.decode("utf-8"))

    def test_write_places_record_at_exact_repository_relative_path(self):
        workspace = self.make_workspace()
        result = write_provenance_record(workspace, self.inputs())

        expected = workspace.repository_path / PROVENANCE_RELATIVE_PATH
        self.assertEqual(result.path, expected)
        self.assertTrue(expected.is_file())
        self.assertEqual(result.byte_length, len(expected.read_bytes()))

    def test_rejects_invalid_timestamp_without_writing(self):
        workspace = self.make_workspace()
        bad = ProvenanceInputs(
            initializer_name="repo-spec-init",
            initializer_version="1",
            initialization_timestamp="2026-08-08T13:00:00-06:00",
        )
        with self.assertRaisesRegex(ProvenanceError, "YYYY-MM-DDTHH:MM:SSZ"):
            write_provenance_record(workspace, bad)
        self.assertFalse(
            (workspace.repository_path / PROVENANCE_RELATIVE_PATH).exists()
        )

    def test_rejects_unknown_or_reordered_serialization_fields(self):
        workspace = self.make_workspace()
        record = build_provenance_record(workspace, self.inputs())
        reordered = dict(reversed(list(record.items())))
        with self.assertRaisesRegex(ProvenanceError, "unknown, missing, or reordered"):
            serialize_provenance_record(reordered)

        with_extra = dict(record)
        with_extra["completed_stages"] = []
        with self.assertRaisesRegex(ProvenanceError, "unknown, missing, or reordered"):
            serialize_provenance_record(with_extra)

    def test_rejects_existing_provenance_destination(self):
        workspace = self.make_workspace()
        destination = workspace.repository_path / PROVENANCE_RELATIVE_PATH
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("existing\n", encoding="utf-8")
        with self.assertRaisesRegex(ProvenanceError, "already exists"):
            write_provenance_record(workspace, self.inputs())
        self.assertEqual(destination.read_text(encoding="utf-8"), "existing\n")

    def test_rejects_lifecycle_late_fields_by_closed_contract(self):
        workspace = self.make_workspace()
        record = build_provenance_record(workspace, self.inputs())
        record["status"] = "completed"
        with self.assertRaises(ProvenanceError):
            serialize_provenance_record(record)


if __name__ == "__main__":
    unittest.main()
