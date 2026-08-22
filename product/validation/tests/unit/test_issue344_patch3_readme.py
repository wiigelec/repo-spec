from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
TEMPLATE = ROOT / "product/src/initializer/templates/initialized-repository-README.md"
FRAMEWORK = ROOT / "product/src/initializer/framework-inventory.json"
OUTPUT = ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json"


class Issue344Patch3ReadmeTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_root_readme_projection_uses_neutral_template(self) -> None:
        framework = json.loads(FRAMEWORK.read_text())
        output = json.loads(OUTPUT.read_text())

        output_matches = [
            entry
            for entry in output["material_index"]
            if entry.get("destination_path") == "README.md"
        ]
        self.assertEqual(len(output_matches), 1)

        material_key = output_matches[0]["material_key"]
        framework_matches = [
            entry
            for entry in framework["entries"]
            if entry.get("material_key") == material_key
        ]
        self.assertEqual(len(framework_matches), 1)
        self.assertEqual(
            framework_matches[0]["source_path"],
            "product/src/initializer/templates/initialized-repository-README.md",
        )

    # validation-metadata: {"role": "helper"}
    def test_neutral_readme_has_only_destination_discovery_surface(self) -> None:
        text = TEMPLATE.read_text()

        required = [
            "scripts/validate",
            "repo/scripts/validate",
            "product/scripts/validate",
            "repo/initializer/handoff.json",
            "repo/initializer/provenance.json",
            "repo/specs/repo/manifest.json",
            "repo/specs/repo/governing-issue.json",
            "repo/specs/repo/development-workflow.json",
            "governed successor work",
        ]
        for token in required:
            self.assertIn(token, text)

        forbidden = [
            "wiigelec/repo-spec",
            "product/docs/",
            "repo/docs/",
            "product/scripts/repo-spec",
            "product/scripts/repo-spec-init",
            "product/src/initializer/",
            "INITIALIZER-OVERVIEW",
            "INITIALIZER-IMPLEMENTATION-PLAN",
        ]
        for token in forbidden:
            self.assertNotIn(token, text)

        self.assertNotIn("# repo-spec", text.lower())


if __name__ == "__main__":
    unittest.main()
