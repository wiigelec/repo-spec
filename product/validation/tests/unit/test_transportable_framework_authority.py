from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from initializer.framework_authority import (
    FrameworkAuthorityError,
    build_framework_authority_bundle,
    materialize_bundle_repository,
    verify_bundle_directory,
)
from initializer.inventory import resolve_source_material


# validation-metadata: {"role": "helper"}
def _run(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return p.stdout.strip()


# validation-metadata: {"role": "helper"}
def _fixture_framework(root: Path) -> tuple[Path, str]:
    repo = root / "framework"
    repo.mkdir()
    _run(repo, "init", "-q")
    _run(repo, "config", "user.name", "Test")
    _run(repo, "config", "user.email", "test@example.invalid")
    (repo / "product/src/initializer").mkdir(parents=True)
    (repo / "product/specs/product/level-1").mkdir(parents=True)
    (repo / "repo/scripts").mkdir(parents=True)
    manifest = {
        "schema_version": "1",
        "entries": [{
            "material_key": "m",
            "source_path": "repo/scripts/x",
            "role": "runtime-framework",
            "operation": "copy-verbatim",
            "source_type": "blob",
            "mode": "100644",
        }],
    }
    output = {
        "material_index": [{
            "material_key": "m",
            "destination_path": "repo/scripts/x",
            "producer": "initializer",
            "operation": "copy-verbatim",
            "mode": "100644",
            "required": True,
            "role": "runtime-framework",
        }],
    }
    (repo / "product/src/initializer/framework-inventory.json").write_text(json.dumps(manifest) + "\n")
    (repo / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(json.dumps(output) + "\n")
    (repo / "repo/scripts/x").write_text("authority\n")
    _run(repo, "add", ".")
    _run(repo, "commit", "-q", "-m", "fixture")
    return repo, _run(repo, "rev-parse", "HEAD")


# validation-metadata: {"role": "helper"}
def _blob_oid(content: bytes) -> str:
    return hashlib.sha1(f"blob {len(content)}\0".encode("ascii") + content).hexdigest()


class TransportableFrameworkAuthorityTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_bundle_is_deterministic_and_materializable(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, sha = _fixture_framework(root)
            first = root / "a" / sha
            second = root / "b" / sha
            build_framework_authority_bundle(str(source), sha, first)
            build_framework_authority_bundle(str(source), sha, second)
            one = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
            two = {p.relative_to(second): p.read_bytes() for p in second.rglob("*") if p.is_file()}
            self.assertEqual(one, two)
            bundle = verify_bundle_directory(first, sha)
            material_repo = materialize_bundle_repository(bundle)
            resolved = resolve_source_material(material_repo, sha, (), require_full_connectivity=False)
            self.assertEqual(resolved.commit_id, sha)
            self.assertEqual(resolved.manifest[0].source_path, "repo/scripts/x")

    # validation-metadata: {"role": "helper"}
    def test_bundle_tamper_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, sha = _fixture_framework(root)
            bundle_dir = root / "bundle" / sha
            build_framework_authority_bundle(str(source), sha, bundle_dir)
            obj = next((bundle_dir / "objects").iterdir())
            raw = json.loads(obj.read_text())
            raw["content_base64"] = raw["content_base64"][:-4] + "AAAA"
            obj.write_text(json.dumps(raw))
            with self.assertRaises(FrameworkAuthorityError):
                verify_bundle_directory(bundle_dir, sha)

    # validation-metadata: {"role": "helper"}
    def test_subordinate_index_cannot_reauthorize_forged_source_blob(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, sha = _fixture_framework(root)
            bundle_dir = root / "bundle" / sha
            build_framework_authority_bundle(str(source), sha, bundle_dir)
            bundle = verify_bundle_directory(bundle_dir, sha)
            _mode, _content, source_oid = bundle.read_path("repo/scripts/x")

            forged = b"forged authority\n"
            forged_oid = _blob_oid(forged)
            forged_record = {
                "content_base64": base64.b64encode(forged).decode("ascii"),
                "object_type": "blob",
            }
            (bundle_dir / "objects" / source_oid).unlink()
            (bundle_dir / "objects" / forged_oid).write_text(
                json.dumps(forged_record, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )

            index_path = bundle_dir / "bundle.json"
            index = json.loads(index_path.read_text(encoding="utf-8"))
            index["object_ids"] = [
                forged_oid if oid == source_oid else oid
                for oid in index["object_ids"]
            ]
            index["object_ids"] = sorted(index["object_ids"])
            index_path.write_text(
                json.dumps(index, sort_keys=True, separators=(",", ":")) + "\n",
                encoding="utf-8",
            )

            with self.assertRaises(FrameworkAuthorityError):
                verify_bundle_directory(bundle_dir, sha)

    # validation-metadata: {"role": "helper"}
    def test_missing_or_incomplete_bundle_fails_closed(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, sha = _fixture_framework(root)
            bundle_dir = root / "bundle" / sha
            build_framework_authority_bundle(str(source), sha, bundle_dir)

            (bundle_dir / "bundle.json").unlink()
            with self.assertRaises(FrameworkAuthorityError):
                verify_bundle_directory(bundle_dir, sha)

            build_framework_authority_bundle(str(source), sha, bundle_dir)
            obj = next((bundle_dir / "objects").iterdir())
            obj.unlink()
            with self.assertRaises(FrameworkAuthorityError):
                verify_bundle_directory(bundle_dir, sha)

    # validation-metadata: {"role": "helper"}
    def test_bundle_directory_must_be_anchored_to_exact_commit_identity(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source, sha = _fixture_framework(root)
            correct = root / "bundle" / sha
            wrong = root / "bundle" / ("0" * 40)
            build_framework_authority_bundle(str(source), sha, correct)
            shutil.copytree(correct, wrong)
            with self.assertRaises(FrameworkAuthorityError):
                verify_bundle_directory(wrong, sha)


if __name__ == "__main__":
    unittest.main()
