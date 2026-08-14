from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
PRODUCT_SCRIPTS = REPO_ROOT / "product" / "scripts"
if str(PRODUCT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PRODUCT_SCRIPTS))

from issue_intake_governance_routing import (
    AuditDisposition,
    AuthorityPath,
    ClassificationState,
    PromotionForm,
    activate_hosted_validation,
    capture_intake_provenance,
    classify_labels,
    plan_promotion,
    route_audited_bug,
    route_intake_to_governed_work,
    route_labels,
)


class ProductOwnedIssueIntakeGovernanceRoutingTests(unittest.TestCase):
    def test_classification_states_and_governed_state_are_orthogonal(self):
        self.assertEqual(classify_labels([]).state, ClassificationState.UNCLASSIFIED)
        self.assertEqual(classify_labels(["bug-fix"]).state, ClassificationState.BUG_FIX)
        self.assertEqual(
            classify_labels(["feature-request"]).state,
            ClassificationState.FEATURE_REQUEST,
        )
        self.assertEqual(
            classify_labels(["bug-fix", "feature-request"]).state,
            ClassificationState.CONFLICT,
        )
        governed = classify_labels(["bug-fix", "governed-work"])
        self.assertEqual(governed.state, ClassificationState.BUG_FIX)
        self.assertTrue(governed.governed_work)

    def test_authority_routing_and_audit_redirect_preserve_no_mutation_authority(self):
        bug = route_labels(["bug-fix"])
        feature = route_labels(["feature-request"])
        ambiguous = route_labels(["bug-fix", "feature-request"])
        self.assertEqual(bug.path, AuthorityPath.AUDIT)
        self.assertEqual(feature.path, AuthorityPath.FEATURE_DEVELOPMENT)
        self.assertEqual(ambiguous.path, AuthorityPath.NO_PATH)
        self.assertFalse(bug.mutation_authorized)
        self.assertFalse(feature.mutation_authorized)
        self.assertEqual(
            route_audited_bug(AuditDisposition.MISSING_OR_UNACCEPTED_BEHAVIOR),
            AuthorityPath.FEATURE_DEVELOPMENT,
        )

    def test_provenance_preserves_original_body_and_pre_promotion_routing_labels(self):
        provenance = capture_intake_provenance(
            intake_issue="#12",
            governed_operation="operation-12",
            original_body="ordinary unformatted intake body",
            labels=["documentation", "bug-fix"],
        )
        self.assertEqual(provenance.routing_labels, ("bug-fix",))
        self.assertEqual(provenance.original_body, "ordinary unformatted intake body")
        self.assertTrue(provenance.captured_before_restructure)
        self.assertIn("`bug-fix`", provenance.to_comment())
        self.assertIn("ordinary unformatted intake body", provenance.to_comment())

    def test_both_promotion_forms_require_provenance_and_canonical_state(self):
        provenance = capture_intake_provenance(
            intake_issue="#12",
            governed_operation="operation-12",
            original_body="body",
            labels=["bug-fix"],
        )
        in_place = plan_promotion(
            form=PromotionForm.IN_PLACE,
            intake_issue="#12",
            governing_issue="#12",
            governed_operation="operation-12",
            provenance=provenance,
            canonical_governed_state=True,
        )
        successor = plan_promotion(
            form=PromotionForm.SUCCESSOR,
            intake_issue="#12",
            governing_issue="#34",
            governed_operation="operation-12",
            provenance=provenance,
            canonical_governed_state=True,
        )
        self.assertEqual(in_place.form, PromotionForm.IN_PLACE)
        self.assertEqual(successor.form, PromotionForm.SUCCESSOR)
        with self.assertRaisesRegex(ValueError, "canonical governed state"):
            plan_promotion(
                form=PromotionForm.IN_PLACE,
                intake_issue="#12",
                governing_issue="#12",
                governed_operation="operation-12",
                provenance=provenance,
                canonical_governed_state=False,
            )

    def test_hosted_validation_activates_only_after_canonical_governed_state(self):
        inactive = activate_hosted_validation(
            governed_work_state=False,
            canonical_governed_state=False,
        )
        active = activate_hosted_validation(
            governed_work_state=True,
            canonical_governed_state=True,
        )
        self.assertFalse(inactive.validation_active)
        self.assertTrue(active.validation_active)
        with self.assertRaisesRegex(ValueError, "cannot precede"):
            activate_hosted_validation(
                governed_work_state=True,
                canonical_governed_state=False,
            )
        with self.assertRaisesRegex(ValueError, "conflicts with repository authority"):
            activate_hosted_validation(
                governed_work_state=True,
                canonical_governed_state=True,
                repository_authority_conflict=True,
            )

    def test_end_to_end_bug_fix_success(self):
        outcome = route_intake_to_governed_work(
            labels=["bug-fix"],
            intake_issue="#12",
            original_body="ordinary unformatted intake body",
            governed_operation="operation-12",
            promotion_form=PromotionForm.IN_PLACE,
            governing_issue="#12",
            canonical_governed_state=True,
        )
        self.assertEqual(outcome.classification_state, "bug-fix")
        self.assertEqual(outcome.authority_path, "audit")
        self.assertEqual(outcome.provenance.routing_labels, ("bug-fix",))
        self.assertEqual(outcome.promotion.governing_issue, "#12")
        self.assertTrue(outcome.hosted_validation.validation_active)
        self.assertEqual(outcome.feature_development_stages, ())
        self.assertFalse(outcome.mutation_authorized)

    def test_end_to_end_feature_request_success_preserves_feature_gates(self):
        outcome = route_intake_to_governed_work(
            labels=["feature-request"],
            intake_issue="#12",
            original_body="new direction",
            governed_operation="operation-34",
            promotion_form=PromotionForm.SUCCESSOR,
            governing_issue="#34",
            canonical_governed_state=True,
        )
        self.assertEqual(outcome.authority_path, "feature-development")
        self.assertEqual(
            outcome.feature_development_stages,
            (
                "whiteboard",
                "analysis",
                "candidate-functional-set",
                "explicit-functional-set-approval",
            ),
        )
        self.assertFalse(outcome.promotion.branch_bypass_authorized)
        self.assertFalse(outcome.promotion.validation_bypass_authorized)
        self.assertFalse(outcome.promotion.review_bypass_authorized)
        self.assertFalse(outcome.promotion.acceptance_bypass_authorized)
        self.assertFalse(outcome.promotion.merge_bypass_authorized)

    def test_end_to_end_fails_closed_for_ambiguous_or_unclassified_intake(self):
        for labels in ([], ["bug-fix", "feature-request"]):
            with self.subTest(labels=labels):
                with self.assertRaisesRegex(ValueError, "no unique classification"):
                    route_intake_to_governed_work(
                        labels=labels,
                        intake_issue="#12",
                        original_body="body",
                        governed_operation="operation-12",
                        promotion_form=PromotionForm.IN_PLACE,
                        governing_issue="#12",
                        canonical_governed_state=True,
                    )

    def test_end_to_end_fails_closed_for_provenance_promotion_and_hosting_failures(self):
        common = dict(
            labels=["bug-fix"],
            intake_issue="#12",
            original_body="body",
            governed_operation="operation-12",
            promotion_form=PromotionForm.IN_PLACE,
            governing_issue="#12",
            canonical_governed_state=True,
        )
        with self.assertRaisesRegex(ValueError, "provenance"):
            route_intake_to_governed_work(**common, provenance_available=False)
        bad_promotion = dict(common)
        bad_promotion["canonical_governed_state"] = False
        with self.assertRaisesRegex(ValueError, "canonical governed state"):
            route_intake_to_governed_work(**bad_promotion)
        with self.assertRaisesRegex(ValueError, "precedes canonical promotion"):
            route_intake_to_governed_work(
                **common,
                hosted_governed_state_before_promotion=True,
            )
        with self.assertRaisesRegex(ValueError, "conflicts with repository authority"):
            route_intake_to_governed_work(
                **common,
                repository_authority_conflict=True,
            )

    def test_product_owned_implementation_does_not_import_repository_helpers(self):
        package = PRODUCT_SCRIPTS / "issue_intake_governance_routing"
        for path in package.glob("*.py"):
            text = path.read_text()
            self.assertNotIn("repo/scripts", text, path.name)
            self.assertNotIn("github_field_policy", text, path.name)


if __name__ == "__main__":
    unittest.main()
