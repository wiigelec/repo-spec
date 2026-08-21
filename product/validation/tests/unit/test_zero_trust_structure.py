from pathlib import Path
import tempfile
import unittest

from validation.checks.policy import check_product_source_layout, check_product_structural_envelopes
from validation.core.context import ValidationContext

def context(root: Path) -> ValidationContext:
    return ValidationContext(root, None, None, None)

def mkdirs(root: Path, rels: list[str]) -> None:
    for rel in rels:
        (root / rel).mkdir(parents=True, exist_ok=True)

class ZeroTrustProductStructureTests(unittest.TestCase):
    def valid(self, root: Path) -> None:
        mkdirs(root, ["product/derived/specs/product","product/docs","product/schemas/product","product/scripts","product/specs/product","product/src","product/validation"])

    def test_exact_shape(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.valid(root); check_product_structural_envelopes(context(root))

    def test_evidence_child_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.valid(root); (root/"product/evidence").mkdir()
            with self.assertRaises(Exception): check_product_structural_envelopes(context(root))

    def test_wrong_kind_specs_owner_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); self.valid(root); target=root/"product/specs/product"; target.rmdir(); target.write_text("x")
            with self.assertRaises(Exception): check_product_structural_envelopes(context(root))

    def test_nested_script_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); mkdirs(root, ["product/src","product/scripts/nested"])
            with self.assertRaises(Exception): check_product_source_layout(context(root))

    def test_python_script_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); mkdirs(root, ["product/src","product/scripts"])
            p=root/"product/scripts/tool.py"; p.write_text("#!/usr/bin/env python3\n"); p.chmod(0o755)
            with self.assertRaises(Exception): check_product_source_layout(context(root))

    def test_validation_under_src_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); mkdirs(root, ["product/src/validation","product/scripts"])
            with self.assertRaises(Exception): check_product_source_layout(context(root))
