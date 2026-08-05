from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


REPO_SPEC_INIT = Path(__file__).resolve().parents[3] / "scripts" / "repo-spec-init"

FIXTURES = Path(__file__).resolve().parent / "fixtures"


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

if __name__ == "__main__":
    unittest.main()
