from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from initializer.destination import i1_destination_preflight
from initializer.foundations import build_foundation_plan
from initializer.inventory import MaterialEntry, ResolvedSourceMaterial
from initializer.staging import (
    I2StagingInputs,
    StagingError,
    establish_staging_workspace,
    realize_i2_materials,
)
from initializer.validation import validate_and_normalize


def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


class I2MaterializationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.base = Path(tempfile.mkdtemp())
        self.source_repo = self.base / "source"
        self.source_repo.mkdir()
        _git(self.source_repo, "init", "-q")
        _git(self.source_repo, "config", "user.name", "test")
        _git(self.source_repo, "config", "user.email", "test@example.invalid")

        self.product_id = "sample"
        self.direction = [
            "direction/first/note.txt",
            "direction/second/note.txt",
        ]
        self._write_source()
        _git(self.source_repo, "add", ".")
        _git(self.source_repo, "commit", "-q", "-m", "source")
        self.revision = _git(self.source_repo, "rev-parse", "HEAD")

        raw_request = {
            "schema_version": "1",
            "destination": str(self.base / "destination"),
            "authority": {"granted_by": "issue-279"},
            "source": {
                "repository": str(self.source_repo),
                "revision": {
                    "object_format": "sha1",
                    "object_id": self.revision,
                },
            },
            "product": {
                "id": self.product_id,
                "direction_material": list(self.direction),
            },
        }
        self.request = validate_and_normalize(
            raw_request,
            str(self.base),
        ).request
        self.destination = i1_destination_preflight(self.request.destination)
        self.source = ResolvedSourceMaterial(
            repository=str(self.source_repo),
            commit_id=self.revision,
            manifest=(
                MaterialEntry(
                    "root-readme",
                    "README.md",
                    "runtime-framework",
                    "copy-verbatim",
                    "blob",
                    "100644",
                ),
                MaterialEntry(
                    "tool",
                    "bin/tool",
                    "runtime-framework",
                    "copy-verbatim",
                    "blob",
                    "100755",
                ),
            ),
            direction_material=tuple(self.direction),
        )
        self.workspace = establish_staging_workspace(
            I2StagingInputs(self.request, self.source, self.destination)
        )
        self.plan = build_foundation_plan(
            self.product_id,
            list(self.direction),
            "issue-279",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.base, ignore_errors=True)

    def _write_source(self) -> None:
        (self.source_repo / "README.md").write_bytes(b"framework\nbytes\r\n")
        tool = self.source_repo / "bin" / "tool"
        tool.parent.mkdir(parents=True)
        tool.write_bytes(b"#!/bin/sh\nprintf patch2\n")
        os.chmod(tool, 0o755)
        for index, path in enumerate(self.direction):
            target = self.source_repo / path
            target.parent.mkdir(parents=True)
            target.write_bytes(
                b"\x00first\r\n" if index == 0 else b"\xffsecond\n"
            )

        output_inventory = {
            "spec_id": "product.initializer-output-inventory-v1",
            "material_index": [
                {
                    "material_key": "root-readme",
                    "destination_path": "README.md",
                    "producer": "framework-installation",
                    "operation": "copy-verbatim",
                    "mode": "100644",
                    "required": True,
                    "role": "runtime-framework",
                },
                {
                    "material_key": "tool",
                    "destination_path": "bin/tool",
                    "producer": "framework-installation",
                    "operation": "copy-verbatim",
                    "mode": "100755",
                    "required": True,
                    "role": "runtime-framework",
                },
            ],
            "dynamic_path_families": [
                {
                    "producer": "direction-evidence-installation",
                    "governing_spec": "product.foundation-seeding",
                    "required": True,
                },
                *[
                    {
                        "producer": "workspace-seeding",
                        "governing_spec": "product.foundation-seeding",
                        "required": True,
                    }
                    for _ in range(4)
                ],
            ],
            "fixed_worktree_files": [
                {
                    "destination_path": path,
                    "producer": producer,
                    "required": True,
                }
                for path, producer in (
                    ("product/docs/direction/manifest.json", "direction-evidence-installation"),
                    ("repo/docs/overview/README.md", "workspace-seeding"),
                    ("repo/docs/decompositions/README.md", "workspace-seeding"),
                    ("repo/docs/plans/README.md", "workspace-seeding"),
                    ("product/specs/product/README.md", "workspace-seeding"),
                    ("product/specs/product/manifest.json", "workspace-seeding"),
                    ("product/specs/product/level-0/README.md", "workspace-seeding"),
                    ("product/specs/product/level-1/README.md", "workspace-seeding"),
                    ("product/specs/product/level-2/README.md", "workspace-seeding"),
                    ("product/specs/product/level-3/README.md", "workspace-seeding"),
                )
            ],
            "prohibited_paths": [
                {"rule": "exact", "path": "reference/"},
                {"rule": "exact", "path": "validate/"},
                {"rule": "exact", "path": "product/src/"},
                {"rule": "exact", "path": "product/tests/"},
            ],
        }
        inventory_path = (
            self.source_repo
            / "product/specs/product/level-1/initializer-output-inventory-v1.json"
        )
        inventory_path.parent.mkdir(parents=True)
        inventory_path.write_text(json.dumps(output_inventory), encoding="utf-8")

    def test_realizes_closed_framework_and_foundations(self) -> None:
        result = realize_i2_materials(self.workspace, self.plan)
        repository = self.workspace.repository_path
        self.assertEqual(
            (repository / "README.md").read_bytes(),
            b"framework\nbytes\r\n",
        )
        self.assertEqual(
            stat.S_IMODE((repository / "README.md").stat().st_mode),
            0o644,
        )
        self.assertEqual(
            stat.S_IMODE((repository / "bin/tool").stat().st_mode),
            0o755,
        )
        self.assertEqual(
            (
                repository
                / "product/docs/direction/evidence/000-note.txt"
            ).read_bytes(),
            b"\x00first\r\n",
        )
        self.assertEqual(
            (
                repository
                / "product/docs/direction/evidence/001-note.txt"
            ).read_bytes(),
            b"\xffsecond\n",
        )
        manifest = json.loads(
            (repository / "product/docs/direction/manifest.json").read_text()
        )
        self.assertEqual(
            [entry["positional_index"] for entry in manifest["entries"]],
            [0, 1],
        )
        self.assertTrue(
            (
                repository
                / "product/docs/overview/sample-overview/chunk-01-identity-and-purpose.md"
            ).is_file()
        )
        self.assertTrue(
            (repository / "product/specs/product/manifest.json").is_file()
        )
        self.assertFalse((repository / ".git").exists())
        self.assertEqual(len(result.framework_paths), 2)

    def test_rejects_tree_material_before_writing(self) -> None:
        bad = ResolvedSourceMaterial(
            repository=self.source.repository,
            commit_id=self.source.commit_id,
            manifest=(
                MaterialEntry(
                    "root-readme",
                    "README.md",
                    "runtime-framework",
                    "copy-verbatim",
                    "tree",
                    "100644",
                ),
                self.source.manifest[1],
            ),
            direction_material=self.source.direction_material,
        )
        bad_workspace = self.workspace.__class__(
            root=self.workspace.root,
            root_inode=self.workspace.root_inode,
            transaction_path=self.workspace.transaction_path,
            repository_path=self.workspace.repository_path,
            staging_state_path=self.workspace.staging_state_path,
            execution_report_path=self.workspace.execution_report_path,
            validation_report_path=self.workspace.validation_report_path,
            inputs=I2StagingInputs(self.request, bad, self.destination),
        )
        with self.assertRaises(StagingError):
            realize_i2_materials(bad_workspace, self.plan)
        self.assertEqual(list(self.workspace.repository_path.iterdir()), [])

    def test_rejects_nonempty_repository_before_realization(self) -> None:
        sentinel = self.workspace.repository_path / "sentinel"
        sentinel.write_text("preserve")
        with self.assertRaises(StagingError):
            realize_i2_materials(self.workspace, self.plan)
        self.assertEqual(sentinel.read_text(), "preserve")

    def test_skeletons_do_not_embed_direction_content(self) -> None:
        realize_i2_materials(self.workspace, self.plan)
        overview = (
            self.workspace.repository_path
            / "product/docs/overview/sample-OVERVIEW.md"
        ).read_bytes()
        self.assertNotIn(b"first", overview)
        self.assertNotIn(b"second", overview)
        self.assertIn(
            b"Content is not synthesized by the initializer.",
            overview,
        )


if __name__ == "__main__":
    unittest.main()
