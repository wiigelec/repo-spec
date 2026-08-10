from __future__ import annotations

import json
import unittest
from pathlib import Path

from initializer.inventory import validate_material_manifest

ROOT = Path(__file__).resolve().parents[4]
SPEC = ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json"
FRAMEWORK = ROOT / "product/scripts/initializer/framework-inventory.json"

EXISTING = {
    "repo/schemas/repo/development-document-base.schema.json",
    "repo/schemas/repo/product-overview.schema.json",
    "repo/schemas/repo/product-decomposition.schema.json",
    "repo/schemas/repo/implementation-plan.schema.json",
}

NEW = {
    "repo/schemas/repo-manifest.schema.json",
    "repo/schemas/repo-artifact-taxonomy.schema.json",
    "repo/schemas/repo-platform-profiles.schema.json",
    "repo/schemas/repo-spec.schema.json",
    "product/schemas/product/product-manifest.schema.json",
    "product/schemas/product/product-spec-base.schema.json",
    "product/schemas/product/product-level-0.schema.json",
    "product/schemas/product/product-level-1.schema.json",
    "product/schemas/product/product-level-2.schema.json",
    "product/schemas/product/product-level-3.schema.json",
}

EXPECTED = EXISTING | NEW

class Issue323ValidatorSchemaMaterialTests(unittest.TestCase):
    def test_real_material_manifest_parser_accepts_complete_schema_set(self):
        output = json.loads(SPEC.read_text())
        framework = json.loads(FRAMEWORK.read_text())
        parsed = validate_material_manifest(framework, output)

        schema_entries = {
            entry.source_path: entry
            for entry in parsed
            if entry.source_path.startswith(("repo/schemas/", "product/schemas/"))
        }
        self.assertEqual(set(schema_entries), EXPECTED)

        for rel, entry in schema_entries.items():
            self.assertEqual(entry.role, "validation-utility", rel)
            self.assertEqual(entry.operation, "copy-verbatim", rel)
            self.assertEqual(entry.source_type, "blob", rel)
            self.assertEqual(entry.mode, "100644", rel)

    def test_all_new_schema_sources_exist_and_are_mode_100644(self):
        for rel in NEW:
            p = ROOT / rel
            self.assertTrue(p.is_file(), rel)
            self.assertEqual(oct(p.stat().st_mode & 0o777), "0o644", rel)

if __name__ == "__main__":
    unittest.main()
