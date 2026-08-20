from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TARGET = "repo/validation/github/github_field_policy.py"
SPEC = ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json"
FRAMEWORK = ROOT / "product/src/initializer/framework-inventory.json"

def target_mode(path: Path) -> str:
    data = json.loads(path.read_text())
    found = []
    def walk(x):
        if isinstance(x, dict):
            target_path = x.get("source_path", x.get("destination_path"))
            if target_path == TARGET:
                found.append(x.get("mode"))
            for value in x.values():
                walk(value)
        elif isinstance(x, list):
            for value in x:
                walk(value)
    walk(data)
    if len(found) != 1:
        raise AssertionError(f"{path}: expected one target entry, found {len(found)}")
    return found[0]

class Issue318InventoryGitModeTests(unittest.TestCase):
    def test_product_and_runtime_inventory_match_committed_mode(self):
        git_mode = subprocess.run(
            ["git", "ls-tree", "HEAD", TARGET],
            cwd=ROOT, text=True, capture_output=True, check=True,
        ).stdout.split()[0]
        self.assertEqual(git_mode, "100755")
        self.assertEqual(target_mode(SPEC), git_mode)
        self.assertEqual(target_mode(FRAMEWORK), git_mode)

if __name__ == "__main__":
    unittest.main()
