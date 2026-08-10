from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PLAN = ROOT / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
CHUNKS = [
    ROOT / "product/docs/plans/initializer-implementation-plan/01-authority-scope-and-specification-map.md",
    ROOT / "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md",
    ROOT / "product/docs/plans/initializer-implementation-plan/03-validation-gates-and-completion.md",
]

class Issue334PlanFreshnessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plan = PLAN.read_text()
        cls.chunk_text = "\n".join(path.read_text() for path in CHUNKS)
        cls.all_text = cls.plan + "\n" + cls.chunk_text

    def test_h1_machine_authority_mapping_is_unchanged(self) -> None:
        block = self.plan[
            self.plan.index('"id": "H1"'):
            self.plan.index('  ],\n  "required_content_areas"')
        ]
        expected = [
            "product.initializer-level-0",
            "product.initialization-request",
            "product.source-revision-identity",
            "product.execution-profile",
            "product.product-identity",
            "product.execution-report",
            "product.lifecycle-stages",
            "product.execution-orchestration",
            "product.request-intake",
            "product.full-initialization",
        ]
        for spec_id in expected:
            self.assertIn(f'"{spec_id}"', block)
        self.assertEqual(block.count('"product.'), len(expected))

    def test_completed_h1_history_is_recorded(self) -> None:
        self.assertIn("#311", self.plan)
        self.assertIn("#313", self.plan)
        self.assertIn("#318", self.plan)
        self.assertIn("H1 are completed historical work", self.all_text)

    def test_pending_h1_instructions_are_gone(self) -> None:
        forbidden = [
            "H1 implementation still requires a separate Product-artifact implementation governing issue",
            "H1 implementation proceeds only through a separate Product-artifact implementation governing issue",
            "After this planning amendment is accepted, H1 implementation requires",
            "After this amended plan is accepted on the default branch, the next authorized action is",
            "requires a later Product-artifact implementation issue",
        ]
        for phrase in forbidden:
            self.assertNotIn(phrase, self.all_text)

    def test_future_extension_boundary_remains_deferred(self) -> None:
        self.assertIn("Future-extension specs remain candidate and deferred", self.all_text)
        for feature in ("dry-run", "platform", "remote", "resume", "recovery", "overwrite"):
            self.assertIn(feature, self.all_text)

    def test_no_new_successor_is_authorized(self) -> None:
        self.assertIn("No new successor implementation scope is authorized", self.all_text)

if __name__ == "__main__":
    unittest.main()
