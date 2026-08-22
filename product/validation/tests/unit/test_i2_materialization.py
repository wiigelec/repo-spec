from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

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


# validation-metadata: {"role": "helper"}
def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode:
        raise AssertionError(p.stderr)
    return p.stdout.strip()


class I2MaterializationTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self) -> None:
        self.base = Path(tempfile.mkdtemp())
        self.source_repo = self.base / "source"
        self.source_repo.mkdir()
        _git(self.source_repo, "init", "-q")
        _git(self.source_repo, "config", "user.name", "test")
        _git(self.source_repo, "config", "user.email", "test@example.invalid")
        _git(self.source_repo, "config", "core.autocrlf", "false")

        (self.source_repo / "README.md").write_bytes(b"framework\nbytes\r\n")
        tool = self.source_repo / "bin/tool"
        tool.parent.mkdir(parents=True)
        tool.write_bytes(b"#!/bin/sh\nprintf bootstrap\n")
        os.chmod(tool, 0o755)

        output = {
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
            "dynamic_path_families": [],
            "fixed_worktree_files": [],
            "prohibited_paths": [],
        }
        inv = (
            self.source_repo
            / "product/specs/product/level-1/initializer-output-inventory-v1.json"
        )
        inv.parent.mkdir(parents=True)
        inv.write_text(json.dumps(output), encoding="utf-8")

        _git(self.source_repo, "add", ".")
        _git(self.source_repo, "commit", "-qm", "source")
        self.revision = _git(self.source_repo, "rev-parse", "HEAD")

        self.request = validate_and_normalize(
            {
                "schema_version": "2",
                "destination": str(self.base / "destination"),
            },
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
            direction_material=(),
        )
        self.workspace = establish_staging_workspace(
            I2StagingInputs(self.request, self.source, self.destination)
        )

    # validation-metadata: {"role": "helper"}
    def tearDown(self) -> None:
        shutil.rmtree(self.base, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_realizes_closed_framework_only(self) -> None:
        result = realize_i2_materials(self.workspace)
        repo = self.workspace.repository_path
        self.assertEqual(
            (repo / "README.md").read_bytes(),
            b"framework\nbytes\r\n",
        )
        self.assertEqual(
            stat.S_IMODE((repo / "bin/tool").stat().st_mode),
            0o755,
        )
        self.assertEqual(result.framework_paths, ("README.md", "bin/tool"))
        self.assertEqual(result.foundation_paths, ())
        self.assertFalse((repo / ".git").exists())

    # validation-metadata: {"role": "helper"}
    def test_rejects_product_foundation_plan(self) -> None:
        plan = build_foundation_plan("sample", ["/direction.md"], "issue-old")
        with self.assertRaisesRegex(
            StagingError,
            "does not accept a product foundation plan",
        ):
            realize_i2_materials(self.workspace, plan)

    # validation-metadata: {"role": "helper"}
    def test_rejects_nonempty_repository_before_realization(self) -> None:
        sentinel = self.workspace.repository_path / "sentinel"
        sentinel.write_text("preserve", encoding="utf-8")
        with self.assertRaises(StagingError):
            realize_i2_materials(self.workspace)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
