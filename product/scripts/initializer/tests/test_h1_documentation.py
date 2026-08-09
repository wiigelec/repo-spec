from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ROOT_README = ROOT / "README.md"
INIT_README = ROOT / "product/docs/initializer/README.md"
NORMAL_COMMAND = "product/scripts/repo-spec-init --request request.json"

class H1DocumentationTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT_README.read_text()
        self.reference = INIT_README.read_text()

    def test_root_readme_leads_with_reviewed_request_workflow(self):
        self.assertLess(self.root.index("## Initialize a repository"), self.root.index("## Start here"))
        self.assertIn(NORMAL_COMMAND, self.root)
        self.assertIn("AI coding agent", self.root)
        self.assertIn("review", self.root.lower())

    def test_agent_instruction_preserves_explicit_authority_boundary(self):
        text = self.root + chr(10) + self.reference
        for phrase in ("Do not infer", "product ID", "source revision", "direction material", "initialization authority", "complete request"):
            self.assertIn(phrase, text)

    def test_reference_leads_with_normal_workflow_before_request_intake(self):
        self.assertLess(self.reference.index("## Normal human workflow"), self.reference.index("## Request intake"))
        self.assertIn(NORMAL_COMMAND, self.reference)
        self.assertIn("diagnostic or development interfaces", self.reference)

    def test_docs_explicitly_exclude_future_behavior(self):
        text = self.root + chr(10) + self.reference[:self.reference.index("## Request intake")]
        for phrase in ("interactive", "infer", "dry-run", "status", "resume", "overwrite", "remote/cloud"):
            self.assertIn(phrase, text)

    def test_normal_command_matches_real_wrapper_path(self):
        self.assertTrue((ROOT / "product/scripts/repo-spec-init").is_file())
        self.assertIn(NORMAL_COMMAND, self.root)
        self.assertIn(NORMAL_COMMAND, self.reference)

if __name__ == "__main__":
    unittest.main()
