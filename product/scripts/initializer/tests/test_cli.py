from __future__ import annotations

import inspect
import initializer.cli as cli

import json
import shutil
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
    def make_source_repo(self, root: Path) -> tuple[Path, str]:
        source = root / "source"
        source.mkdir()
        subprocess.run(["git", "-C", str(source), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(source), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(source), "config", "user.name", "Test"], check=True)
        (source / "product/scripts/initializer").mkdir(parents=True)
        (source / "product/specs/product/level-1").mkdir(parents=True)
        (source / "README.md").write_text("source\n")
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
        (source / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(
            json.dumps(output) + "\n"
        )
        (source / "product/scripts/initializer/framework-inventory.json").write_text(
            json.dumps(manifest) + "\n"
        )
        subprocess.run(["git", "-C", str(source), "add", "."], check=True)
        subprocess.run(["git", "-C", str(source), "commit", "-qm", "source"], check=True)
        revision = subprocess.run(
            ["git", "-C", str(source), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        return source, revision

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

    def test_establish_staging_composes_only_i1_and_patch_1_topology(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            source_repo, revision = self.make_source_repo(cwd)
            destination = cwd / "destination"
            raw = {
                "schema_version": "1",
                "destination": str(destination),
                "authority": {"granted_by": "issue-279"},
                "source": {
                    "repository": str(source_repo),
                    "revision": {"object_format": "sha1", "object_id": revision},
                },
                "product": {
                    "id": "sample-product",
                    "direction_material": ["README.md", "README.md"],
                },
            }
            request_path = cwd / "request.json"
            request_path.write_text(json.dumps(raw), encoding="utf-8")

            proc = self.run_command("establish-staging", request_path)

            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            output = json.loads(proc.stdout)
            root = Path(output["root"])
            try:
                self.assertEqual(output["status"], "i2-staging-established")
                self.assertEqual({path.name for path in root.iterdir()}, {"transaction", "repository"})
                self.assertEqual(list(Path(output["transaction_path"]).iterdir()), [])
                self.assertEqual(list(Path(output["repository_path"]).iterdir()), [])
                self.assertFalse(destination.exists())
                self.assertFalse((Path(output["repository_path"]) / ".git").exists())
            finally:
                shutil.rmtree(root, ignore_errors=True)

    def test_establish_staging_fails_before_mutation_for_invalid_source(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            request_path = cwd / "request.json"
            request_path.write_text(json.dumps(request()), encoding="utf-8")

            proc = self.run_command("establish-staging", request_path)

            self.assertNotEqual(proc.returncode, 0)
            self.assertIn("source repository is not a local Git repository", proc.stderr)
            self.assertEqual([path.name for path in cwd.iterdir()], ["request.json"])


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
