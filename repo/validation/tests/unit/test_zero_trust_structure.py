from pathlib import Path
import tempfile
import unittest

from validation.checks.policy import check_repository_source_layout, check_repository_structural_envelopes
from validation.core.context import ValidationContext

def context(root: Path) -> ValidationContext:
    return ValidationContext(root, None, None, None)

def mkdirs(root: Path, rels: list[str]) -> None:
    for rel in rels:
        (root / rel).mkdir(parents=True, exist_ok=True)

class ZeroTrustRepositoryStructureTests(unittest.TestCase):
    def valid(self, root: Path) -> None:
        mkdirs(root, ["repo/derived/specs/repo","repo/docs","repo/profiles","repo/schemas/repo","repo/scripts","repo/specs/repo","repo/src","repo/validation"])

    def test_exact_shape(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.valid(root); check_repository_structural_envelopes(context(root))

    def test_extra_owner_child_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.valid(root); (root/"repo/unexpected").mkdir()
            with self.assertRaises(Exception): check_repository_structural_envelopes(context(root))

    def test_loose_schema_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.valid(root); (root/"repo/schemas/loose.schema.json").write_text("{}")
            with self.assertRaises(Exception): check_repository_structural_envelopes(context(root))

    def test_nested_script_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); mkdirs(root, ["repo/src","repo/scripts/nested"])
            with self.assertRaises(Exception): check_repository_source_layout(context(root))

    def test_python_script_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); mkdirs(root, ["repo/src","repo/scripts"])
            p=root/"repo/scripts/tool.py"; p.write_text("#!/usr/bin/env python3\n"); p.chmod(0o755)
            with self.assertRaises(Exception): check_repository_source_layout(context(root))
