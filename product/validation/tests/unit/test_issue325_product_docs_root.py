from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INVENTORY = (
    ROOT
    / "product/specs/product/level-1/initializer-output-inventory-v1.json"
)


class Issue325ProductDocsRootTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_product_document_families_are_not_bootstrap_outputs(self):
        inventory = json.loads(INVENTORY.read_text())
        self.assertEqual(inventory["dynamic_path_families"], [])
        text = json.dumps(inventory)
        for prefix in (
            "product/docs/overview/",
            "product/docs/decompositions/",
            "product/docs/plans/",
            "product/docs/direction/evidence/",
        ):
            self.assertNotIn(prefix, text)


if __name__ == "__main__":
    unittest.main()
