from __future__ import annotations

import pathlib
import sys
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
PRODUCT_SCRIPTS = REPO_ROOT / "product" / "scripts"
if str(PRODUCT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PRODUCT_SCRIPTS))

import issue_intake_governance_routing.promotion as promotion_module
from issue_intake_governance_routing import (
    AuditDisposition,
    AuthorityPath,
    CanonicalGovernedStateEvidence,
    CanonicalGovernedStateObservation,
    CanonicalGovernedStateValidationResult,
    ClassificationState,
    PromotionForm,
    activate_hosted_validation,
    capture_intake_provenance,
    classify_labels,
    plan_promotion,
    route_audited_bug,
    route_intake_to_governed_work,
    route_labels,
    validate_canonical_governed_state,
)


class StaticCanonicalValidator:
    def __init__(
        self,
        *,
        governing_issue: str,
        governed_operation: str,
        validated_revision: str = "rev-1",
        validation_artifact_id: str = "canonical-governed-fields/rev-1",
        validator_id: str = "test.canonical-governed-state-validator",
        canonical_structure_valid: bool = True,
    ):
        self.result = CanonicalGovernedStateValidationResult(
            governing_issue=governing_issue,
            governed_operation=governed_operation,
            validated_revision=validated_revision,
            validation_artifact_id=validation_artifact_id,
            validator_id=validator_id,
            canonical_structure_valid=canonical_structure_valid,
        )

    def validate(self, observation):
        return self.result


def canonical_evidence(
    *,
    governing_issue: str,
    governed_operation: str,
    validated_revision: str = "rev-1",
    observed_revision: str = "rev-1",
    validation_artifact_id: str = "canonical-governed-fields/rev-1",
) -> CanonicalGovernedStateEvidence:
    observation = CanonicalGovernedStateObservation(
        governing_issue=governing_issue,
        governed_operation=governed_operation,
        observed_revision=observed_revision,
    )
    validator = StaticCanonicalValidator(
        governing_issue=governing_issue,
        governed_operation=governed_operation,
        validated_revision=validated_revision,
        validation_artifact_id=validation_artifact_id,
    )
    return validate_canonical_governed_state(
        observation=observation,
        validator=validator,
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

    def test_evidence_cannot_be_directly_constructed_or_forged_with_object_new(self):
        self.assertFalse(hasattr(promotion_module, "_VALIDATED_EVIDENCE_SEAL"))
        with self.assertRaisesRegex(ValueError, "issued by successful validation"):
            CanonicalGovernedStateEvidence()

        forged = object.__new__(CanonicalGovernedStateEvidence)
        forged._governing_issue = "#12"
        forged._governed_operation = "operation-12"
        forged._validated_revision = "rev-1"
        forged._observed_revision = "rev-1"
        forged._validation_artifact_id = "fabricated"
        forged._validator_id = "fabricated"

        provenance = capture_intake_provenance(
            intake_issue="#12",
            governed_operation="operation-12",
            original_body="body",
            labels=["bug-fix"],
        )
        with self.assertRaisesRegex(ValueError, "not issued by successful validation"):
            plan_promotion(
                form=PromotionForm.IN_PLACE,
                intake_issue="#12",
                governing_issue="#12",
                governed_operation="operation-12",
                provenance=provenance,
                canonical_state_evidence=forged,
            )

    def test_validator_mints_matching_fresh_canonical_evidence(self):
        evidence = canonical_evidence(
            governing_issue="#12",
            governed_operation="operation-12",
        )
        self.assertEqual(evidence.governing_issue, "#12")
        self.assertEqual(evidence.governed_operation, "operation-12")
        self.assertEqual(evidence.validator_id, "test.canonical-governed-state-validator")
        self.assertTrue(evidence.is_fresh)

    def test_canonical_validation_fails_closed_for_invalid_stale_or_mismatched_results(self):
        observation = CanonicalGovernedStateObservation(
            governing_issue="#12",
            governed_operation="operation-12",
            observed_revision="rev-2",
        )
        cases = (
            (
                StaticCanonicalValidator(
                    governing_issue="#12",
                    governed_operation="operation-12",
                    validated_revision="rev-2",
                    canonical_structure_valid=False,
                ),
                "validation failed",
            ),
            (
                StaticCanonicalValidator(
                    governing_issue="#34",
                    governed_operation="operation-12",
                    validated_revision="rev-2",
                ),
                "does not match governing issue",
            ),
            (
                StaticCanonicalValidator(
                    governing_issue="#12",
                    governed_operation="operation-99",
                    validated_revision="rev-2",
                ),
                "does not match governed operation",
            ),
            (
                StaticCanonicalValidator(
                    governing_issue="#12",
                    governed_operation="operation-12",
                    validated_revision="rev-1",
                ),
                "stale",
            ),
        )
        for validator, message in cases:
            with self.subTest(message=message):
                with self.assertRaisesRegex(ValueError, message):
                    validate_canonical_governed_state(
                        observation=observation,
                        validator=validator,
                    )

    def test_both_promotion_forms_require_validator_issued_canonical_evidence(self):
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
            canonical_state_evidence=canonical_evidence(
                governing_issue="#12",
                governed_operation="operation-12",
            ),
        )
        successor = plan_promotion(
            form=PromotionForm.SUCCESSOR,
            intake_issue="#12",
            governing_issue="#34",
            governed_operation="operation-12",
            provenance=provenance,
            canonical_state_evidence=canonical_evidence(
                governing_issue="#34",
                governed_operation="operation-12",
            ),
        )
        self.assertEqual(in_place.form, PromotionForm.IN_PLACE)
        self.assertEqual(successor.form, PromotionForm.SUCCESSOR)

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
            canonical_state_evidence=canonical_evidence(
                governing_issue="#12",
                governed_operation="operation-12",
            ),
        )
        self.assertEqual(outcome.classification_state, "bug-fix")
        self.assertEqual(outcome.authority_path, "audit")
        self.assertFalse(outcome.mutation_authorized)

    def test_end_to_end_feature_request_success_preserves_feature_gates(self):
        outcome = route_intake_to_governed_work(
            labels=["feature-request"],
            intake_issue="#12",
            original_body="new direction",
            governed_operation="operation-34",
            promotion_form=PromotionForm.SUCCESSOR,
            governing_issue="#34",
            canonical_state_evidence=canonical_evidence(
                governing_issue="#34",
                governed_operation="operation-34",
            ),
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
                        canonical_state_evidence=canonical_evidence(
                            governing_issue="#12",
                            governed_operation="operation-12",
                        ),
                    )

    def test_product_owned_implementation_has_no_importable_validation_sentinel(self):
        promotion_text = (
            PRODUCT_SCRIPTS / "issue_intake_governance_routing/promotion.py"
        ).read_text()
        self.assertNotIn("_VALIDATED_EVIDENCE_SEAL", promotion_text)
        self.assertIn("WeakSet", promotion_text)
        self.assertIn("not issued by successful validation", promotion_text)

    def test_product_owned_implementation_does_not_import_repository_helpers(self):
        package = PRODUCT_SCRIPTS / "issue_intake_governance_routing"
        for path in package.glob("*.py"):
            text = path.read_text()
            self.assertNotIn("repo/scripts", text, path.name)
            self.assertNotIn("github_field_policy", text, path.name)


if __name__ == "__main__":
    unittest.main()
