from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]


class Issue342Patch3AlignmentTests(unittest.TestCase):
    def test_repo_spec_product_runtime_is_not_in_destination_inventories(self) -> None:
        manifest = json.loads((ROOT / "product/scripts/initializer/framework-inventory.json").read_text())
        output = json.loads((ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json").read_text())

        manifest_paths = {
            entry["source_path"]
            for entry in manifest["entries"]
            if isinstance(entry, dict) and isinstance(entry.get("source_path"), str)
        }
        output_paths = {
            entry["destination_path"]
            for entry in output["material_index"]
            if isinstance(entry, dict) and isinstance(entry.get("destination_path"), str)
        }

        forbidden_exact = {
            "product/scripts/repo-spec",
            "product/scripts/repo-spec-init",
        }
        forbidden_prefix = "product/scripts/initializer/"

        self.assertTrue(forbidden_exact.isdisjoint(manifest_paths))
        self.assertTrue(forbidden_exact.isdisjoint(output_paths))
        self.assertFalse(any(path.startswith(forbidden_prefix) for path in manifest_paths))
        self.assertFalse(any(path.startswith(forbidden_prefix) for path in output_paths))

    def test_initialized_validation_surface_is_in_closed_inventories(self) -> None:
        manifest = json.loads((ROOT / "product/scripts/initializer/framework-inventory.json").read_text())
        output = json.loads((ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json").read_text())

        manifest_keys = {
            entry["material_key"]
            for entry in manifest["entries"]
            if isinstance(entry, dict) and isinstance(entry.get("material_key"), str)
        }
        output_by_destination = {
            entry["destination_path"]: entry
            for entry in output["material_index"]
            if isinstance(entry, dict) and isinstance(entry.get("destination_path"), str)
        }

        required = {
            "scripts/validate",
            "repo/scripts/validate",
            "product/scripts/validate",
        }
        self.assertTrue(required.issubset(output_by_destination))

        for destination in required:
            material_key = output_by_destination[destination]["material_key"]
            self.assertIn(material_key, manifest_keys)

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
