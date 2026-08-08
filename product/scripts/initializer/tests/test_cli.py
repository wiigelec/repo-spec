from __future__ import annotations

import inspect
import initializer.cli as cli

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_SPEC_INIT = Path(__file__).resolve().parents[3] / "scripts" / "repo-spec-init"
OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"


def request() -> dict[str, object]:
    return {
        "schema_version": "1",
        "destination": "missing-output",
        "authority": {"granted_by": "issue-273"},
        "source": {
            "repository": "missing-source",
            "revision": {"object_format": "sha1", "object_id": OBJECT_ID},
        },
        "product": {
            "id": "sample-product",
            "direction_material": ["missing/OVERVIEW.md", "missing/OVERVIEW.md"],
        },
    }


class CliTests(unittest.TestCase):
    def run_command(
        self, command: str, request_path: Path
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [str(REPO_SPEC_INIT), command, str(request_path)],
            cwd=request_path.parent,
            capture_output=True,
            text=True,
        )

    def run_request(
        self, raw: object, cwd: Path
    ) -> subprocess.CompletedProcess[str]:
        path = cwd / "request.json"
        path.write_text(json.dumps(raw), encoding="utf-8")
        return subprocess.run(
            [str(REPO_SPEC_INIT), "validate-request", str(path)],
            cwd=cwd,
            capture_output=True,
            text=True,
        )

    def test_validate_request_reports_normalized_path_and_fingerprint(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            proc = self.run_request(request(), cwd)

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)
        output = json.loads(proc.stdout)
        self.assertEqual(output["status"], "valid")
        self.assertEqual(output["destination"], f"{cwd}/missing-output")
        self.assertEqual(output["authority_granted_by"], "issue-273")
        self.assertRegex(output["request_fingerprint"], r"^[0-9a-f]{64}$")

    def test_validate_request_does_not_inspect_source_or_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            proc = self.run_request(request(), cwd)
            self.assertFalse((cwd / "missing-source").exists())
            self.assertFalse((cwd / "missing-output").exists())

        self.assertEqual(proc.returncode, 0, msg=proc.stderr)

    def test_validate_request_rejects_missing_authority_without_fallback(self) -> None:
        raw = request()
        del raw["authority"]["granted_by"]
        with tempfile.TemporaryDirectory() as directory:
            proc = self.run_request(raw, Path(directory))

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("missing-required", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_validate_request_reports_each_rejection_category(self) -> None:
        cases = {
            "missing-required": lambda raw: raw.pop("product"),
            "empty-authority": lambda raw: raw["authority"].__setitem__("granted_by", " "),
            "invalid-structure": lambda raw: raw.__setitem__("metadata", {}),
            "contradictory-combination": lambda raw: raw["source"]["revision"].__setitem__("object_id", "a" * 64),
            "excluded-behavior": lambda raw: raw.__setitem__("profile", "dry-run"),
        }
        for category, mutate in cases.items():
            with self.subTest(category=category), tempfile.TemporaryDirectory() as directory:
                raw = request()
                mutate(raw)
                proc = self.run_request(raw, Path(directory))
                self.assertNotEqual(proc.returncode, 0)
                self.assertIn(category, proc.stderr)

    def test_validate_request_requires_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            proc = self.run_request([], Path(directory))

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("invalid-structure", proc.stderr)

    def test_validate_request_missing_argument_is_rejected(self) -> None:
        proc = subprocess.run(
            [str(REPO_SPEC_INIT), "validate-request"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_inspect_source_rejects_malformed_request_without_traceback(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "request.json"
            path.write_text("{", encoding="utf-8")
            proc = self.run_command("inspect-source", path)

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("invalid-structure", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)

    def test_inspect_source_fails_closed_until_patch_2(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            path = cwd / "request.json"
            path.write_text(json.dumps(request()), encoding="utf-8")
            proc = self.run_command("inspect-source", path)

            self.assertFalse((cwd / "missing-source").exists())
            self.assertFalse((cwd / "missing-output").exists())

        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("source repository is not a local Git repository", proc.stderr)

    def test_request_driven_staging_commands_are_unavailable(self) -> None:
        commands = (
            "stage-framework",
            "stage-framework-and-foundations",
            "promote-staging",
            "stage-and-promote",
            "stage-promote-and-git",
        )
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            path = cwd / "request.json"
            path.write_text(json.dumps(request()), encoding="utf-8")
            for command in commands:
                with self.subTest(command=command):
                    proc = self.run_command(command, path)
                    self.assertNotEqual(proc.returncode, 0)
                    self.assertIn("unavailable", proc.stderr)
            self.assertEqual([entry.name for entry in cwd.iterdir()], ["request.json"])


if __name__ == "__main__":
    unittest.main()


class I1IntegratedPreflightTests(unittest.TestCase):
    def test_preflight_request_is_bounded_i1_path(self):
        source = inspect.getsource(cli._cmd_preflight_request)
        self.assertIn("validate_and_normalize", source)
        self.assertIn("resolve_source_material", source)
        self.assertIn("i1_destination_preflight", source)
        self.assertNotIn("stage_framework", source)
        self.assertNotIn("promote", source)
        self.assertNotIn("git_establish", source)
