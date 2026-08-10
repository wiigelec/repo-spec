from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from initializer.foundations import (
    build_foundation_plan,
    establish_product_foundations,
)

ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json"

class Issue325ProductDocsRootTests(unittest.TestCase):
    def test_dynamic_product_document_paths_are_product_rooted(self):
        data = json.loads(SPEC.read_text())
        text = json.dumps(data, sort_keys=True)
        self.assertNotIn('"docs/overview/', text)
        self.assertNotIn('"docs/decompositions/', text)
        self.assertNotIn('"docs/plans/', text)
        self.assertIn("product/docs/overview/", text)
        self.assertIn("product/docs/decompositions/", text)
        self.assertIn("product/docs/plans/", text)

    def test_foundation_generator_emits_no_top_level_docs(self):
        plan = build_foundation_plan("audit-sample", ["README.md"], "issue-325")
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            establish_product_foundations(plan, root)
            created = {
                p.relative_to(root).as_posix()
                for p in root.rglob("*")
                if p.is_file()
            }

            self.assertTrue(any(p.startswith("product/docs/overview/") for p in created))
            self.assertTrue(any(p.startswith("product/docs/decompositions/") for p in created))
            self.assertTrue(any(p.startswith("product/docs/plans/") for p in created))
            self.assertFalse(any(p.startswith("docs/") for p in created))
            self.assertFalse(any(p.startswith("repo/docs/") for p in created))

            # Direction evidence is a separate product/docs family and remains canonical.
            self.assertFalse(any(p.startswith("repo/docs/direction/") for p in created))

if __name__ == "__main__":
    unittest.main()
