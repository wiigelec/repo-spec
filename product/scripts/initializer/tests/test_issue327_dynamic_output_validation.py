from __future__ import annotations

import json
import unittest
from pathlib import Path

from initializer.validation import _i4_match_dynamic


ROOT = Path(__file__).resolve().parents[4]
INVENTORY = ROOT / "product/specs/product/level-1/initializer-output-inventory-v1.json"


class Issue327DynamicOutputValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory = json.loads(INVENTORY.read_text())

    def test_accepts_each_declared_dynamic_expansion_family(self) -> None:
        accepted = (
            "product/docs/direction/evidence/000-README.md",
            "product/docs/overview/audit-sample-OVERVIEW.md",
            "product/docs/decompositions/audit-sample-DECOMPOSITION.md",
            "product/docs/plans/audit-sample-IMPLEMENTATION-PLAN.md",
            "product/docs/overview/audit-sample-overview/chunk-01-identity-and-purpose.md",
            "product/docs/decompositions/audit-sample-decomposition/chunk-01-invocation-and-authority.md",
            "product/docs/plans/audit-sample-implementation-plan/chunk-01-scope-and-preconditions.md",
        )
        for path in accepted:
            with self.subTest(path=path):
                self.assertTrue(_i4_match_dynamic(path, self.inventory))

    def test_rejects_adjacent_undeclared_paths(self) -> None:
        rejected = (
            "docs/overview/audit-sample-OVERVIEW.md",
            "repo/docs/overview/audit-sample-OVERVIEW.md",
            "product/docs/overview/nested/audit-sample-OVERVIEW.md",
            "product/docs/overview/audit-sample-overview/nested/chunk-01-identity-and-purpose.md",
            "product/docs/decompositions/audit-sample-decomposition.txt",
            "product/docs/plans/audit-sample-implementation-plan/chunk-01-scope-and-preconditions.txt",
            "product/docs/direction/evidence/nested/000-README.md",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertFalse(_i4_match_dynamic(path, self.inventory))


if __name__ == "__main__":
    unittest.main()
