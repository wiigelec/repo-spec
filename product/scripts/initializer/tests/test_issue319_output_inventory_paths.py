from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json"

EXPECTED = {
    "repo/docs/overview/README.md",
    "repo/docs/decompositions/README.md",
    "repo/docs/plans/README.md",
}
STALE = {
    "docs/overview/README.md",
    "docs/decompositions/README.md",
    "docs/plans/README.md",
}

class Issue319OutputInventoryPathTests(unittest.TestCase):
    def test_workspace_readme_destinations_use_repo_docs(self):
        data = json.loads(SPEC.read_text())
        fixed = data["fixed_worktree_files"]

        selected = [
            item for item in fixed
            if isinstance(item, dict)
            and item.get("producer") == "workspace-seeding"
            and item.get("operation") == "instantiate-template"
            and item.get("destination_path") in EXPECTED | STALE
        ]

        destinations = {item["destination_path"] for item in selected}
        self.assertEqual(destinations, EXPECTED)
        self.assertTrue(STALE.isdisjoint(destinations))

        for item in selected:
            self.assertEqual(item.get("mode"), "100644")
            self.assertIs(item.get("required"), True)

if __name__ == "__main__":
    unittest.main()
