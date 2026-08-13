from __future__ import annotations

import json
import unittest
from pathlib import Path


class FunctionalSetTransportTests(unittest.TestCase):
    def test_framework_transport_boundary(self) -> None:
        repo_root = Path(__file__).resolve().parents[4]
        inventory_path = repo_root / "product/scripts/initializer/framework-inventory.json"
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
        source_paths = {entry["source_path"] for entry in inventory["entries"]}

        required_framework_sources = {
            "repo/specs/repo/artifact-taxonomy.json",
            "repo/specs/repo/development-document-base.json",
            "repo/specs/repo/development-workflow.json",
            "repo/specs/repo/functional-set-process.json",
            "repo/specs/repo/product-decomposition.json",
            "repo/specs/repo/validation.json",
            "repo/schemas/repo-artifact-taxonomy.schema.json",
            "repo/schemas/repo/development-document-base.schema.json",
            "repo/schemas/repo/functional-set-process.schema.json",
            "repo/derived/specs/repo/artifact-taxonomy.md",
            "repo/derived/specs/repo/development-document-base.md",
            "repo/derived/specs/repo/development-workflow.md",
            "repo/derived/specs/repo/functional-set-process.md",
            "repo/derived/specs/repo/product-decomposition.md",
            "repo/derived/specs/repo/validation.md",
            "AGENTS.md",
            "product/scripts/initializer/templates/initialized-repository-README.md",
        }
        self.assertTrue(required_framework_sources <= source_paths)

        forbidden_working_sources = {
            source_path
            for source_path in source_paths
            if source_path == "user/functional-set-init.md"
            or "WHITEBOARD" in Path(source_path).name.upper()
            or "ANALYSIS" in Path(source_path).name.upper()
            or "FUNCTIONAL-SET" in Path(source_path).name.upper()
        }
        self.assertEqual(forbidden_working_sources, set())

        transported_repo_validation = {
            source_path
            for source_path in source_paths
            if source_path.startswith("repo/scripts/validation/")
        }
        self.assertEqual(transported_repo_validation, set())


if __name__ == "__main__":
    unittest.main()
