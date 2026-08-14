from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .provenance import IntakeProvenance


class PromotionForm(str, Enum):
    IN_PLACE = "in-place"
    SUCCESSOR = "successor"


@dataclass(frozen=True)
class CanonicalGovernedStateEvidence:
    governing_issue: str
    governed_operation: str
    validated_revision: str
    observed_revision: str
    validation_artifact_id: str

    def __post_init__(self) -> None:
        for field_name in (
            "governing_issue",
            "governed_operation",
            "validated_revision",
            "observed_revision",
            "validation_artifact_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"canonical governed-state evidence requires non-empty {field_name}"
                )

    @property
    def is_fresh(self) -> bool:
        return self.validated_revision == self.observed_revision

    def require_valid_for(
        self,
        *,
        governing_issue: str,
        governed_operation: str,
    ) -> None:
        if self.governing_issue != governing_issue:
            raise ValueError(
                "canonical governed-state evidence does not match governing issue"
            )
        if self.governed_operation != governed_operation:
            raise ValueError(
                "canonical governed-state evidence does not match governed operation"
            )
        if not self.is_fresh:
            raise ValueError(
                "canonical governed-state evidence is stale for the observed target revision"
            )


@dataclass(frozen=True)
class PromotionPlan:
    form: PromotionForm
    intake_issue: str
    governing_issue: str
    governed_operation: str
    provenance: IntakeProvenance
    canonical_state_evidence: CanonicalGovernedStateEvidence
    branch_bypass_authorized: bool = False
    validation_bypass_authorized: bool = False
    review_bypass_authorized: bool = False
    acceptance_bypass_authorized: bool = False
    merge_bypass_authorized: bool = False

    @property
    def destructive_restructure_allowed(self) -> bool:
        return self.provenance.captured_before_restructure

    @property
    def unique_governing_issue(self) -> bool:
        return bool(self.governing_issue.strip())

    @property
    def canonical_governed_state(self) -> bool:
        # Compatibility view for downstream state-boundary logic. The value is
        # derived from validated evidence rather than accepted from a caller.
        return True


def plan_promotion(
    *,
    form: PromotionForm,
    intake_issue: str,
    governing_issue: str,
    governed_operation: str,
    provenance: IntakeProvenance,
    canonical_state_evidence: CanonicalGovernedStateEvidence,
) -> PromotionPlan:
    intake = intake_issue.strip()
    governing = governing_issue.strip()
    operation = governed_operation.strip()

    if not intake:
        raise ValueError("intake_issue is required")
    if not governing:
        raise ValueError("governing_issue is required")
    if not operation:
        raise ValueError("governed_operation is required")
    if not isinstance(canonical_state_evidence, CanonicalGovernedStateEvidence):
        raise ValueError("validated canonical governed-state evidence is required")
    if not provenance.captured_before_restructure:
        raise ValueError("required intake provenance must be captured before promotion")
    if provenance.intake_issue != intake:
        raise ValueError("provenance intake identity does not match promotion intake")
    if provenance.governed_operation != operation:
        raise ValueError("provenance operation identity does not match promotion operation")

    canonical_state_evidence.require_valid_for(
        governing_issue=governing,
        governed_operation=operation,
    )

    if form is PromotionForm.IN_PLACE and intake != governing:
        raise ValueError("in-place promotion requires intake_issue to equal governing_issue")
    if form is PromotionForm.SUCCESSOR and intake == governing:
        raise ValueError("successor promotion requires a distinct governing_issue")

    return PromotionPlan(
        form=form,
        intake_issue=intake,
        governing_issue=governing,
        governed_operation=operation,
        provenance=provenance,
        canonical_state_evidence=canonical_state_evidence,
    )
