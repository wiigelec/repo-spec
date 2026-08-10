from __future__ import annotations

import json
import unittest
from pathlib import Path

from initializer.foundations import (
    DECOMPOSITION_CHUNK_COVERAGE,
    OVERVIEW_CHUNK_COVERAGE,
    PLAN_CHUNK_COVERAGE,
)
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

    def test_accepts_every_fixed_chunk_basename(self) -> None:
        families = (
            (
                "product/docs/overview/audit-sample-overview/",
                OVERVIEW_CHUNK_COVERAGE,
            ),
            (
                "product/docs/decompositions/audit-sample-decomposition/",
                DECOMPOSITION_CHUNK_COVERAGE,
            ),
            (
                "product/docs/plans/audit-sample-implementation-plan/",
                PLAN_CHUNK_COVERAGE,
            ),
        )
        for prefix, coverage in families:
            for item in coverage:
                path = prefix + "chunk-" + item[0]
                with self.subTest(path=path):
                    self.assertTrue(_i4_match_dynamic(path, self.inventory))

    def test_rejects_fabricated_chunk_placeholder_values(self) -> None:
        rejected = (
            "product/docs/overview/audit-sample-overview/chunk-99-made-up.md",
            "product/docs/overview/audit-sample-overview/chunk-01-made-up.md",
            "product/docs/decompositions/audit-sample-decomposition/chunk-99-made-up.md",
            "product/docs/decompositions/audit-sample-decomposition/chunk-01-made-up.md",
            "product/docs/plans/audit-sample-implementation-plan/chunk-99-made-up.md",
            "product/docs/plans/audit-sample-implementation-plan/chunk-01-made-up.md",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertFalse(_i4_match_dynamic(path, self.inventory))

    def test_enforces_declared_slug_and_evidence_index_shapes(self) -> None:
        rejected = (
            "product/docs/overview/Invalid_ID-OVERVIEW.md",
            "product/docs/overview/a--bad-OVERVIEW.md",
            "product/docs/direction/evidence/1-README.md",
            "product/docs/direction/evidence/0000-README.md",
            "product/docs/direction/evidence/abc-README.md",
        )
        for path in rejected:
            with self.subTest(path=path):
                self.assertFalse(_i4_match_dynamic(path, self.inventory))
        self.assertTrue(
            _i4_match_dynamic(
                "product/docs/direction/evidence/000-README.md",
                self.inventory,
            )
        )

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
