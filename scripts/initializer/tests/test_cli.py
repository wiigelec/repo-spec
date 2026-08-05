from __future__ import annotations

import shutil
import subprocess
import unittest
from pathlib import Path


REPO_SPEC_INIT = Path(__file__).resolve().parents[3] / "scripts" / "repo-spec-init"

FIXTURES = Path(__file__).resolve().parent / "fixtures"
INVENTORY_FIXTURES = FIXTURES / "inventory"


class CliTests(unittest.TestCase):
    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(REPO_SPEC_INIT), *args],
            capture_output=True,
            text=True,
        )

    def test_validate_accepts_minimal(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("validate-request", str(path))
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

    def test_validate_accepts_full(self) -> None:
        path = FIXTURES / "valid-full.json"
        proc = self._run("validate-request", str(path))
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

    def test_validate_rejects_invalid_json(self) -> None:
        path = FIXTURES / "invalid-not-json.json"
        proc = self._run("validate-request", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_validate_rejects_unsupported_version(self) -> None:
        path = FIXTURES / "invalid-unsupported-version.json"
        proc = self._run("validate-request", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_validate_rejects_missing_destination(self) -> None:
        path = FIXTURES / "invalid-missing-destination.json"
        proc = self._run("validate-request", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_validate_rejects_missing_authority(self) -> None:
        path = FIXTURES / "invalid-missing-authority.json"
        proc = self._run("validate-request", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_validate_rejects_unknown_field(self) -> None:
        path = FIXTURES / "invalid-unknown-field.json"
        proc = self._run("validate-request", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_no_arguments_shows_usage(self) -> None:
        proc = self._run()
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_unknown_command_shows_usage(self) -> None:
        proc = self._run("unknown-command", str(FIXTURES / "valid-minimal.json"))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("unknown command", proc.stderr.lower())

    def test_valid_output_contains_status(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("validate-request", str(path))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("valid", proc.stdout)

    def test_diagnostics_are_deterministic(self) -> None:
        path = FIXTURES / "invalid-missing-destination.json"
        proc1 = self._run("validate-request", str(path))
        proc2 = self._run("validate-request", str(path))
        self.assertEqual(proc1.returncode, proc2.returncode)
        self.assertEqual(proc1.stderr, proc2.stderr)

    def test_validation_does_not_create_destination(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("validate-request", str(path))
        self.assertEqual(proc.returncode, 0)
        dest = Path("/tmp/test-dest")
        self.assertFalse(dest.exists())

    def test_inspect_source_with_minimal_request(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("inspection_complete", proc.stdout)
        self.assertIn("classifications", proc.stdout)

    def test_inspect_source_with_source_request(self) -> None:
        path = FIXTURES / "valid-with-source.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        self.assertIn("source_selection", proc.stdout)

    def test_inspect_source_with_invalid_request(self) -> None:
        path = FIXTURES / "invalid-missing-destination.json"
        proc = self._run("inspect-source", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_inspect_source_output_deterministic(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc1 = self._run("inspect-source", str(path))
        proc2 = self._run("inspect-source", str(path))
        self.assertEqual(proc1.returncode, proc2.returncode)
        self.assertEqual(proc1.stdout, proc2.stdout)

    def test_inspect_source_does_not_create_destination(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0)
        dest = Path("/tmp/test-dest")
        self.assertFalse(dest.exists())

    def test_inspect_source_reports_framework_material(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("framework-authoritative", proc.stdout)
        self.assertIn("framework-support", proc.stdout)

    def test_inspect_source_reports_excluded_material(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("excluded", proc.stdout)

    def test_inspect_source_reports_derived_material(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("derived", proc.stdout)

    def test_inspect_source_reports_profile_controlled(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("profile-source", proc.stdout)
        self.assertIn("installed-adapter", proc.stdout)

    def test_inspect_source_no_source_silent_default(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("inspect-source", str(path))
        self.assertEqual(proc.returncode, 0)
        self.assertIn("source_selection", proc.stdout)
        import json
        output = json.loads(proc.stdout)
        self.assertIsNone(output["source_selection"])

    def test_inspect_source_invalid_output_nonzero(self) -> None:
        path = FIXTURES / "invalid-not-json.json"
        proc = self._run("inspect-source", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_inspect_source_missing_args(self) -> None:
        proc = self._run("inspect-source")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_stage_framework_missing_args(self) -> None:
        proc = self._run("stage-framework")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_stage_framework_invalid_request(self) -> None:
        path = FIXTURES / "invalid-missing-destination.json"
        proc = self._run("stage-framework", str(path))
        self.assertNotEqual(proc.returncode, 0)

    def test_stage_framework_no_source(self) -> None:
        path = FIXTURES / "valid-minimal.json"
        proc = self._run("stage-framework", str(path))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("source", proc.stderr.lower())

    def test_stage_framework_creates_staging_workspace(self) -> None:
        path = FIXTURES / "valid-with-source.json"
        proc = self._run("stage-framework", str(path))
        if proc.returncode != 0:
            self.fail(f"stage-framework failed: {proc.stderr}")
        import json
        output = json.loads(proc.stdout)
        self.assertEqual(output["status"], "staging_complete")
        self.assertIn("staging_workspace", output)
        ws = Path(output["staging_workspace"])
        self.assertTrue(ws.exists())
        shutil.rmtree(ws, ignore_errors=True)

    def test_stage_framework_lists_installed(self) -> None:
        path = FIXTURES / "valid-with-source.json"
        proc = self._run("stage-framework", str(path))
        if proc.returncode != 0:
            self.fail(f"stage-framework failed: {proc.stderr}")
        import json
        output = json.loads(proc.stdout)
        self.assertIn("installed", output)
        self.assertGreater(len(output["installed"]), 0)

    def test_stage_framework_output_deterministic(self) -> None:
        path = FIXTURES / "valid-with-source.json"
        proc1 = self._run("stage-framework", str(path))
        proc2 = self._run("stage-framework", str(path))
        self.assertEqual(proc1.returncode, proc2.returncode)
        if proc1.returncode == 0:
            import json
            out1 = json.loads(proc1.stdout)
            out2 = json.loads(proc2.stdout)
            self.assertEqual(
                [i["path"] for i in out1["installed"]],
                [i["path"] for i in out2["installed"]],
            )

    def test_stage_framework_does_not_create_destination(self) -> None:
        path = FIXTURES / "valid-with-source.json"
        dest = Path("/tmp/repo-spec-test-dest")
        dest_before = dest.exists()
        proc = self._run("stage-framework", str(path))
        dest_after = dest.exists()
        self.assertEqual(dest_before, dest_after)
        if proc.returncode == 0:
            import json
            output = json.loads(proc.stdout)
            ws = Path(output["staging_workspace"])
            shutil.rmtree(ws, ignore_errors=True)

    def test_stage_framework_unknown_command_shown(self) -> None:
        proc = self._run("stage-framework")
        self.assertNotEqual(proc.returncode, 0)

    def test_preflight_destination_missing_args(self) -> None:
        proc = self._run("preflight-destination")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_preflight_destination_absent(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td) / "stage"
            staging.mkdir()
            dest = Path(td) / "new_dest"
            proc = self._run("preflight-destination", str(staging), str(dest))
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            import json
            output = json.loads(proc.stdout)
            self.assertEqual(output["decision"], "allowed")
            self.assertEqual(output["destination_classification"], "absent")

    def test_preflight_destination_rejects_nonempty(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td) / "stage"
            staging.mkdir()
            dest = Path(td) / "nonempty"
            dest.mkdir()
            (dest / "file.txt").write_text("x")
            proc = self._run("preflight-destination", str(staging), str(dest))
            self.assertNotEqual(proc.returncode, 0)
            import json
            output = json.loads(proc.stdout)
            self.assertEqual(output["decision"], "rejected")

    def test_promote_missing_args(self) -> None:
        proc = self._run("promote")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_promote_to_absent(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td) / "stage"
            staging.mkdir()
            (staging / "file.txt").write_text("content")
            dest = Path(td) / "new_repo"
            proc = self._run("promote", str(staging), str(dest))
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            import json
            output = json.loads(proc.stdout)
            self.assertEqual(output["status"], "success")
            self.assertTrue(dest.exists())
            self.assertTrue((dest / "file.txt").exists())

    def test_promote_to_nonempty_rejected(self) -> None:
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            staging = Path(td) / "stage"
            staging.mkdir()
            (staging / "file.txt").write_text("content")
            dest = Path(td) / "existing"
            dest.mkdir()
            (dest / "existing.txt").write_text("existing")
            proc = self._run("promote", str(staging), str(dest))
            self.assertNotEqual(proc.returncode, 0)
            import json
            output = json.loads(proc.stdout)
            self.assertEqual(output["status"], "failed")


if __name__ == "__main__":
    unittest.main()
