from __future__ import annotations

import hashlib
import json
import os
import pathlib
import stat
import sys
import tempfile
import unittest
from unittest import mock

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


MANAGED_CANONICAL_PRODUCER = (
    REPO_ROOT / "repo/scripts/canonical-governed-state-validator"
)


def canonical_governed_body() -> str:
    return (
        "## Change type\nProduct-artifact implementation\n\n"
        "## Problem statement\nBounded canonical validation fixture.\n\n"
        "## Intended outcome\nValidate canonical governed structure.\n\n"
        "## Governing specifications\n"
        "repo.governing-issue, repo.development-workflow, repo.validation, "
        "repo.repository-structure, repo.artifact-taxonomy, "
        "repo.product-correspondence, repo.implementation-plan, "
        "product.issue-routing-governance, product.issue-routing-classification, "
        "product.governed-work-provenance, product.issue-authority-routing, "
        "product.governed-work-promotion, product.issue-routing-platform-validation, "
        "product.issue-intake-governance-routing, and the accepted "
        "`repo/docs/plans/REPOSITORY-IMPLEMENTATION-PLAN.md` composite.\n\n"
        "## Implementation-plan workstreams/stages\nIRP-I2\nIRP-I3\nIRP-I4\nIRP-I5\n\n"
        "## Accepted default-branch base\n"
        "main at 00030fcc48f2b7fefefacc42a4a4dd9cdba9cea4\n\n"
        "## In-scope behavior and paths\n- Canonical validation fixture.\n\n"
        "## Explicit exclusions\n- No unrelated work.\n\n"
        "## Dependencies and predecessor evidence\n""Issue #426 governs this bounded correction and follows merged PR #425. ""The accepted implementation baseline is ""`main@00030fcc48f2b7fefefacc42a4a4dd9cdba9cea4`; this fixture exists only ""to exercise the canonical governed-issue field-policy boundary.\n\n"
        "## Ordered patch plan\n1. Validate.\n\n"
        "## Validation plan\nRun field policy.\n\n"
        "## Acceptance criteria\nCanonical structure passes.\n\n"
        "## Completion gate\nManual merge.\n\n"
        "## Open decisions or authority conflicts\nNone.\n\n"
        "## Successor work explicitly not authorized\nAnything else.\n"
    )


class TrustedProducerFixture:
    def __init__(self, *, body: str | None = None):
        self.tmp = tempfile.TemporaryDirectory()
        self.body_path = pathlib.Path(self.tmp.name) / "canonical.md"
        self.body_path.write_text(
            canonical_governed_body() if body is None else body,
            encoding="utf-8",
        )
        self.revision = hashlib.sha256(self.body_path.read_bytes()).hexdigest()

    def __enter__(self):
        self.patch = mock.patch.dict(
            os.environ,
            {
                "REPO_SPEC_CANONICAL_VALIDATOR": str(MANAGED_CANONICAL_PRODUCER),
                "REPO_SPEC_CANONICAL_VALIDATION_SUBJECT": str(self.body_path),
            },
            clear=False,
        )
        self.patch.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.patch.stop()
        self.tmp.cleanup()


def canonical_evidence(*, governing_issue: str, governed_operation: str):
    with TrustedProducerFixture() as fixture:
        observation = CanonicalGovernedStateObservation(
            governing_issue=governing_issue,
            governed_operation=governed_operation,
            observed_revision=fixture.revision,
        )
        return validate_canonical_governed_state(
            observation=observation,
            producer_id="repository-canonical-validator",
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

    def test_arbitrary_validator_objects_are_not_an_api_surface(self):
        observation = CanonicalGovernedStateObservation(
            governing_issue="#12",
            governed_operation="operation-12",
            observed_revision="rev-1",
        )

        class CallerValidator:
            def validate(self, observation):
                return {"canonical_structure_valid": True}

        with self.assertRaises(TypeError):
            validate_canonical_governed_state(
                observation=observation,
                validator=CallerValidator(),
            )

    def test_unrecognized_or_unavailable_producer_fails_closed(self):
        with TrustedProducerFixture() as fixture:
            observation = CanonicalGovernedStateObservation(
                governing_issue="#12",
                governed_operation="operation-12",
                observed_revision=fixture.revision,
            )
            with self.assertRaisesRegex(ValueError, "unrecognized"):
                validate_canonical_governed_state(
                    observation=observation,
                    producer_id="caller-supplied-validator",
                )

        with mock.patch.dict(
            os.environ,
            {
                "REPO_SPEC_CANONICAL_VALIDATOR": "",
                "REPO_SPEC_CANONICAL_VALIDATION_SUBJECT": "",
            },
            clear=False,
        ):
            observation = CanonicalGovernedStateObservation(
                governing_issue="#12",
                governed_operation="operation-12",
                observed_revision="rev-1",
            )
            with self.assertRaisesRegex(ValueError, "unavailable"):
                validate_canonical_governed_state(
                    observation=observation,
                    producer_id="repository-canonical-validator",
                )

    def test_same_name_substituted_producer_fails_artifact_identity(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = pathlib.Path(tmp) / "canonical-governed-state-validator"
            fake.write_text(
                "#!/usr/bin/env python3\nprint('fabricated')\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            subject = pathlib.Path(tmp) / "canonical.md"
            subject.write_text(canonical_governed_body(), encoding="utf-8")
            revision = hashlib.sha256(subject.read_bytes()).hexdigest()
            observation = CanonicalGovernedStateObservation(
                governing_issue="#12",
                governed_operation="operation-12",
                observed_revision=revision,
            )
            with mock.patch.dict(
                os.environ,
                {
                    "REPO_SPEC_CANONICAL_VALIDATOR": str(fake),
                    "REPO_SPEC_CANONICAL_VALIDATION_SUBJECT": str(subject),
                    "PATH": str(pathlib.Path(tmp)),
                },
                clear=False,
            ):
                with self.assertRaisesRegex(ValueError, "artifact identity mismatch"):
                    validate_canonical_governed_state(
                        observation=observation,
                        producer_id="repository-canonical-validator",
                    )

    def test_trusted_producer_result_is_bound_and_fresh(self):
        evidence = canonical_evidence(
            governing_issue="#12",
            governed_operation="operation-12",
        )
        self.assertEqual(evidence.governing_issue, "#12")
        self.assertEqual(evidence.governed_operation, "operation-12")
        self.assertEqual(evidence.producer_id, "repository-canonical-validator")
        self.assertTrue(evidence.is_fresh)

    def test_managed_producer_rejects_stale_subject_revision(self):
        with TrustedProducerFixture() as fixture:
            observation = CanonicalGovernedStateObservation(
                governing_issue="#12",
                governed_operation="operation-12",
                observed_revision="0" * 64,
            )
            with self.assertRaisesRegex(ValueError, "revision mismatch"):
                validate_canonical_governed_state(
                    observation=observation,
                    producer_id="repository-canonical-validator",
                )

    def test_managed_producer_rejects_noncanonical_subject(self):
        with TrustedProducerFixture(body="ordinary unformatted intake body") as fixture:
            observation = CanonicalGovernedStateObservation(
                governing_issue="#12",
                governed_operation="operation-12",
                observed_revision=fixture.revision,
            )
            with self.assertRaisesRegex(ValueError, "field policy failed"):
                validate_canonical_governed_state(
                    observation=observation,
                    producer_id="repository-canonical-validator",
                )

    def test_no_module_level_evidence_issuance_or_verification_helpers(self):
        self.assertFalse(hasattr(promotion_module, "_issue_validated_evidence"))
        self.assertFalse(hasattr(promotion_module, "_require_issued_evidence_for"))
        with self.assertRaisesRegex(ValueError, "issued by trusted validation"):
            CanonicalGovernedStateEvidence()

        forged = object.__new__(CanonicalGovernedStateEvidence)
        forged._governing_issue = "#12"
        forged._governed_operation = "operation-12"
        forged._validated_revision = "rev-1"
        forged._observed_revision = "rev-1"
        forged._validation_artifact_id = "fabricated"
        forged._producer_id = "repository-canonical-validator"
        provenance = capture_intake_provenance(
            intake_issue="#12",
            governed_operation="operation-12",
            original_body="body",
            labels=["bug-fix"],
        )
        with self.assertRaisesRegex(ValueError, "not issued by trusted validation"):
            plan_promotion(
                form=PromotionForm.IN_PLACE,
                intake_issue="#12",
                governing_issue="#12",
                governed_operation="operation-12",
                provenance=provenance,
                canonical_state_evidence=forged,
            )

    def test_both_promotion_forms_require_trusted_producer_evidence(self):
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

    def test_product_owned_implementation_does_not_import_repository_helpers(self):
        package = PRODUCT_SCRIPTS / "issue_intake_governance_routing"
        for path in package.glob("*.py"):
            text = path.read_text()
            self.assertNotIn("repo/scripts", text, path.name)
            self.assertNotIn("github_field_policy", text, path.name)


if __name__ == "__main__":
    unittest.main()
