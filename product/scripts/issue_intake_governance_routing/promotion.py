from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .provenance import IntakeProvenance


class PromotionForm(str, Enum):
    IN_PLACE = "in-place"
    SUCCESSOR = "successor"


@dataclass(frozen=True)
class PromotionPlan:
    form: PromotionForm
    intake_issue: str
    governing_issue: str
    governed_operation: str
    provenance: IntakeProvenance
    canonical_governed_state: bool
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


def plan_promotion(
    *,
    form: PromotionForm,
    intake_issue: str,
    governing_issue: str,
    governed_operation: str,
    provenance: IntakeProvenance,
    canonical_governed_state: bool,
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
    if not provenance.captured_before_restructure:
        raise ValueError("required intake provenance must be captured before promotion")
    if provenance.intake_issue != intake:
        raise ValueError("provenance intake identity does not match promotion intake")
    if provenance.governed_operation != operation:
        raise ValueError("provenance operation identity does not match promotion operation")
    if not canonical_governed_state:
        raise ValueError("canonical governed state is required before governed-work promotion")
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
        canonical_governed_state=True,
    )
