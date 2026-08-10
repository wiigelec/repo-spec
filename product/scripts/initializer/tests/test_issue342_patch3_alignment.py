from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


class Issue342Patch3AlignmentTests(unittest.TestCase):
    def test_wrapper_is_in_both_closed_inventories(self) -> None:
        manifest = json.loads((ROOT / "product/scripts/initializer/framework-inventory.json").read_text())
        output = json.loads((ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json").read_text())
        m = {e["material_key"]: e for e in manifest["entries"]}
        o = {e["material_key"]: e for e in output["material_index"]}
        self.assertIn("repo-spec", m)
        self.assertIn("repo-spec", o)
        self.assertEqual(m["repo-spec"]["source_path"], "product/scripts/repo-spec")
        self.assertEqual(o["repo-spec"]["destination_path"], "product/scripts/repo-spec")
        self.assertEqual(m["repo-spec"]["mode"], "100755")
        self.assertEqual(o["repo-spec"]["mode"], "100755")

    def test_output_inventory_has_no_product_foundation_producer(self) -> None:
        output = json.loads((ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json").read_text())
        forbidden = {"direction-evidence-installation", "workspace-seeding"}
        for key in ("fixed_worktree_files", "dynamic_path_families"):
            for entry in output.get(key, []):
                if isinstance(entry, dict):
                    self.assertNotIn(entry.get("producer"), forbidden)

    def test_generated_repository_contract_defers_product_definition(self) -> None:
        text = (ROOT / "product/specs/product/level-1/generated-repository.json").read_text()
        self.assertIn("shall not generate a product manifest", text)
        self.assertIn("Product-definition paths may be absent after bootstrap", text)

    def test_wrapper_no_argument_help_uses_canonical_command(self) -> None:
        cli = (ROOT / "product/scripts/initializer/cli.py").read_text()
        self.assertIn('usage: repo-spec init --repo <destination>', cli)

    def test_normal_docs_use_repo_spec_init(self) -> None:
        for path in ("README.md", "product/docs/initializer/README.md"):
            text = (ROOT / path).read_text()
            self.assertIn("repo-spec init --repo", text)


if __name__ == "__main__":
    unittest.main()
