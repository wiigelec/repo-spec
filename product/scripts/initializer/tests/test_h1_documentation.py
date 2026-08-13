from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ROOT_README = ROOT / "README.md"
INIT_README = ROOT / "product/docs/initializer/README.md"
NORMAL_COMMAND = "product/scripts/repo-spec init --repo /path/to/new/repository-name"
LOWER_LEVEL = "product/scripts/repo-spec-init --request request.json"


class H1DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT_README.read_text()
        self.reference = INIT_README.read_text()

    def test_root_readme_leads_with_canonical_wrapper_workflow(self):
        self.assertLess(
            self.root.index("## Initialize a repository"),
            self.root.index("## Start here"),
        )
        self.assertIn(NORMAL_COMMAND, self.root)
        self.assertIn("web chat agent", self.root.lower())

    def test_docs_preserve_product_authority_boundary(self):
        text = self.root + chr(10) + self.reference
        self.assertIn("destination path is the only normal-user bootstrap input", text)
        self.assertIn("does **not** define the product", text)
        self.assertIn("Do not invent product identity or product direction", text)
        self.assertIn("product ID or product identity", text)
        self.assertIn("product direction material or direction evidence", text)

    def test_reference_leads_with_normal_workflow_before_internal_request(self):
        self.assertLess(
            self.reference.index("## Normal human workflow"),
            self.reference.index("## Internal canonical request"),
        )
        self.assertIn(LOWER_LEVEL, self.reference)
        self.assertIn("not the recommended normal-user workflow", self.reference)

    def test_docs_explicitly_exclude_non_bootstrap_behavior(self):
        section = self.reference[
            self.reference.index("## What bootstrap does not create"):
            self.reference.index("## Internal canonical request")
        ]
        for phrase in (
            "functional-set lifecycle",
            "product decomposition",
            "product specifications",
            "product implementation plan",
            "hosting-platform state",
        ):
            self.assertIn(phrase, section)

    def test_normal_command_matches_real_wrapper_path(self):
        self.assertTrue((ROOT / "product/scripts/repo-spec").is_file())
        self.assertIn(NORMAL_COMMAND, self.root)
        self.assertIn(NORMAL_COMMAND, self.reference)


if __name__ == "__main__":
    unittest.main()
