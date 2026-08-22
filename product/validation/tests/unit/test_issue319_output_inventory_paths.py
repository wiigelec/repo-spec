from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
INVENTORY = (
    ROOT
    / "product/specs/product/level-1/initializer-output-inventory-v1.json"
)


class Issue319OutputInventoryPathTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_bootstrap_inventory_does_not_seed_product_workspace_readmes(self):
        inventory = json.loads(INVENTORY.read_text())
        destinations = {
            item["destination_path"]
            for item in (
                inventory["material_index"]
                + inventory["fixed_worktree_files"]
            )
        }
        for path in (
            "repo/docs/overview/README.md",
            "repo/docs/decompositions/README.md",
            "repo/docs/plans/README.md",
            "product/specs/product/manifest.json",
        ):
            self.assertNotIn(path, destinations)

    # validation-metadata: {"role": "helper"}
    def test_bootstrap_fixed_outputs_are_only_initializer_records(self):
        inventory = json.loads(INVENTORY.read_text())
        self.assertEqual(
            {
                item["destination_path"]
                for item in inventory["fixed_worktree_files"]
            },
            {
                "repo/initializer/provenance.json",
                "repo/initializer/handoff.json",
            },
        )


if __name__ == "__main__":
    unittest.main()
