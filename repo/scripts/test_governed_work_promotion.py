import importlib.util
import json
import pathlib
import sys
import tempfile
import unittest


MODULE_PATH = pathlib.Path(__file__).with_name("governed_work_promotion.py")
SPEC = importlib.util.spec_from_file_location("governed_work_promotion", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def valid_body(base_sha: str) -> str:
    return f"""## Change type
Product-artifact implementation

## Problem statement
Bounded governed work needs a canonical promotion target.

## Intended outcome
Establish a canonical governed issue body for the bounded operation.

## Governing specifications
repo.governing-issue, repo.development-workflow, repo.validation, repo.implementation-plan, repo.development-document-base, product.issue-routing-governance, product.governed-work-provenance, product.issue-authority-routing, product.governed-work-promotion, and repo/docs/plans/REPOSITORY-IMPLEMENTATION-PLAN.md.

## Implementation-plan workstreams/stages
`IRP-I3`

## Accepted default-branch base
main at {base_sha}

## In-scope behavior and paths
- repo/scripts/governed_work_promotion.py
- repo/scripts/test_governed_work_promotion.py

## Explicit exclusions
Hosted event wiring is excluded.

## Dependencies and predecessor evidence
Issue #408 with predecessor revision {base_sha}.

## Ordered patch plan
1. Validate promotion state.
2. Preserve lifecycle boundaries.

## Validation plan
- [ ] focused tests
- [ ] repository validation

## Acceptance criteria
Canonical promotion constraints are satisfied.

## Completion gate
Manual merge and post-merge verification are required.

## Open decisions or authority conflicts
None.

## Successor work explicitly not authorized
IRP-I4 and IRP-I5.

## Optional context
Promotion planning remains platform-neutral.
"""


class GovernedWorkPromotionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo_root = pathlib.Path(__file__).resolve().parents[2]
        cls.base_sha = "0837f80441d78d2b93e2c19526695cce30e355f0"

    def test_in_place_promotion_is_supported(self):
        plan = MODULE.plan_promotion(
            form=MODULE.PromotionForm.IN_PLACE,
            intake_issue="#12",
            governing_issue="#12",
            governed_body=valid_body(self.base_sha),
            provenance_captured=True,
            repo_root=self.repo_root,
        )
        self.assertEqual(plan.form, MODULE.PromotionForm.IN_PLACE)
        self.assertTrue(plan.unique_governing_issue)

    def test_successor_promotion_is_supported(self):
        plan = MODULE.plan_promotion(
            form=MODULE.PromotionForm.SUCCESSOR,
            intake_issue="#12",
            governing_issue="#34",
            governed_body=valid_body(self.base_sha),
            provenance_captured=True,
            repo_root=self.repo_root,
        )
        self.assertEqual(plan.form, MODULE.PromotionForm.SUCCESSOR)
        self.assertTrue(plan.unique_governing_issue)

    def test_provenance_is_required_before_destructive_restructure(self):
        with self.assertRaisesRegex(ValueError, "provenance"):
            MODULE.plan_promotion(
                form=MODULE.PromotionForm.IN_PLACE,
                intake_issue="#12",
                governing_issue="#12",
                governed_body=valid_body(self.base_sha),
                provenance_captured=False,
                repo_root=self.repo_root,
            )

    def test_invalid_governed_body_is_rejected_by_canonical_policy(self):
        with self.assertRaises(Exception):
            MODULE.plan_promotion(
                form=MODULE.PromotionForm.IN_PLACE,
                intake_issue="#12",
                governing_issue="#12",
                governed_body="plain intake body",
                provenance_captured=True,
                repo_root=self.repo_root,
            )

    def test_in_place_requires_same_issue_identity(self):
        with self.assertRaisesRegex(ValueError, "in-place promotion"):
            MODULE.plan_promotion(
                form=MODULE.PromotionForm.IN_PLACE,
                intake_issue="#12",
                governing_issue="#34",
                governed_body=valid_body(self.base_sha),
                provenance_captured=True,
                repo_root=self.repo_root,
            )

    def test_successor_requires_distinct_governing_issue(self):
        with self.assertRaisesRegex(ValueError, "successor promotion"):
            MODULE.plan_promotion(
                form=MODULE.PromotionForm.SUCCESSOR,
                intake_issue="#12",
                governing_issue="#12",
                governed_body=valid_body(self.base_sha),
                provenance_captured=True,
                repo_root=self.repo_root,
            )

    def test_promotion_does_not_bypass_governed_lifecycle_gates(self):
        plan = MODULE.plan_promotion(
            form=MODULE.PromotionForm.SUCCESSOR,
            intake_issue="#12",
            governing_issue="#34",
            governed_body=valid_body(self.base_sha),
            provenance_captured=True,
            repo_root=self.repo_root,
        )
        self.assertFalse(plan.branch_bypass_authorized)
        self.assertFalse(plan.validation_bypass_authorized)
        self.assertFalse(plan.review_bypass_authorized)
        self.assertFalse(plan.acceptance_bypass_authorized)
        self.assertFalse(plan.merge_bypass_authorized)


if __name__ == "__main__":
    unittest.main()
