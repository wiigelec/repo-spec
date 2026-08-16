from __future__ import annotations

import contextlib
import inspect
import io
import json
import subprocess
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

import initializer.cli as cli

REPO_SPEC_INIT = Path(__file__).resolve().parents[3] / "scripts" / "repo-spec-init"


def request(destination: str = "missing-output") -> dict[str, object]:
    return {"schema_version": "2", "destination": destination}


class CliTests(unittest.TestCase):
    def run_request(self, raw: object, cwd: Path) -> subprocess.CompletedProcess[str]:
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
            self.assertEqual(proc.returncode, 0, proc.stderr)
            output = json.loads(proc.stdout)
            self.assertEqual(output["status"], "valid")
            self.assertEqual(output["destination"], str(cwd / "missing-output"))
            self.assertRegex(output["request_fingerprint"], r"^[0-9a-f]{64}$")

    def test_validate_request_does_not_create_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            proc = self.run_request(request(), cwd)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertFalse((cwd / "missing-output").exists())

    def test_validate_request_rejects_legacy_authority(self) -> None:
        raw = request()
        raw["authority"] = {"granted_by": "issue-old"}
        with tempfile.TemporaryDirectory() as directory:
            proc = self.run_request(raw, Path(directory))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("invalid-structure", proc.stderr)

    def test_validate_request_rejects_unknown_and_profile_fields(self) -> None:
        for field, value in (("metadata", {}), ("profile", "dry-run")):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as directory:
                raw = request()
                raw[field] = value
                proc = self.run_request(raw, Path(directory))
                self.assertNotEqual(proc.returncode, 0)

    def test_validate_request_requires_json_object(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            proc = self.run_request([], Path(directory))
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("invalid-structure", proc.stderr)

    def test_public_usage_is_consistent_for_empty_and_unknown_command_paths(self) -> None:
        public_forms = (
            "usage: repo-spec init --repo <destination>",
            "repo-spec upgrade --repo <existing-repo>",
        )
        cases = (
            ["/path/to/cli.py", "/framework/root"],
            ["/path/to/cli.py", "/framework/root", "upgrade"],
        )

        for argv in cases:
            with self.subTest(argv=argv):
                stderr = io.StringIO()
                with contextlib.redirect_stderr(stderr):
                    rc = cli.main(argv)

                self.assertEqual(rc, 1)
                rendered = stderr.getvalue()
                for public_form in public_forms:
                    self.assertIn(public_form, rendered)


    def test_upgrade_cli_uses_human_presentation_not_json(self) -> None:
        result = SimpleNamespace(
            terminal_result="promoted-success",
            succeeded=True,
            failure_reason=None,
        )
        with mock.patch(
            "initializer.upgrade_orchestration.execute_repository_upgrade",
            return_value=result,
        ), mock.patch(
            "initializer.human_presentation.present_upgrade_terminal_result"
        ) as present:
            rc = cli.main(
                [
                    "/path/to/cli.py",
                    "/framework/root",
                    "upgrade",
                    "--repo",
                    "/target/root",
                ]
            )

        self.assertEqual(rc, 0)
        present.assert_called_once_with(result, "/target/root", mock.ANY)

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
                    proc = subprocess.run(
                        [str(REPO_SPEC_INIT), command, str(path)],
                        cwd=cwd,
                        capture_output=True,
                        text=True,
                    )
                    self.assertNotEqual(proc.returncode, 0)
                    self.assertIn("unavailable", proc.stderr)

    def test_preflight_request_remains_bounded_i1_path(self):
        source = inspect.getsource(cli._cmd_preflight_request)
        self.assertIn("validate_and_normalize", source)
        self.assertIn("resolve_source_material", source)
        self.assertIn("i1_destination_preflight", source)
        self.assertNotIn("promote", source)


if __name__ == "__main__":
    unittest.main()
