from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .authority import (
    AuthorityPath,
    FEATURE_DEVELOPMENT_STAGES,
    route_labels,
)
from .classification import classify_labels
from .hosted_validation import HostedValidationDecision, activate_hosted_validation
from .promotion import (
    CanonicalGovernedStateEvidence,
    PromotionForm,
    PromotionPlan,
    plan_promotion,
)
from .provenance import IntakeProvenance, capture_intake_provenance


@dataclass(frozen=True)
class RoutingOutcome:
    classification_state: str
    authority_path: str
    provenance: IntakeProvenance
    promotion: PromotionPlan
    hosted_validation: HostedValidationDecision
    feature_development_stages: tuple[str, ...]
    mutation_authorized: bool = False


def route_intake_to_governed_work(
    *,
    labels: Iterable[str],
    intake_issue: str,
    original_body: str,
    governed_operation: str,
    promotion_form: PromotionForm,
    governing_issue: str,
    canonical_state_evidence: CanonicalGovernedStateEvidence,
    provenance_available: bool = True,
    hosted_governed_state_before_promotion: bool = False,
    repository_authority_conflict: bool = False,
) -> RoutingOutcome:
    classification = classify_labels(labels)
    if not classification.has_single_direction:
        raise ValueError(
            f"routing stopped: no unique classification direction ({classification.state.value})"
        )

    authority = route_labels(labels)
    if not authority.has_unique_path:
        raise ValueError(
            f"routing stopped: no permitted authority path ({authority.classification_state.value})"
        )
    if authority.mutation_authorized:
        raise ValueError("routing metadata must not authorize mutation")
    if hosted_governed_state_before_promotion:
        raise ValueError(
            "routing stopped: hosted governed-work state precedes canonical promotion"
        )
    if not provenance_available:
        raise ValueError("routing stopped: required intake provenance is unavailable")

    provenance = capture_intake_provenance(
        intake_issue=intake_issue,
        governed_operation=governed_operation,
        original_body=original_body,
        labels=labels,
    )

    promotion = plan_promotion(
        form=promotion_form,
        intake_issue=intake_issue,
        governing_issue=governing_issue,
        governed_operation=governed_operation,
        provenance=provenance,
        canonical_state_evidence=canonical_state_evidence,
    )

    hosted_validation = activate_hosted_validation(
        governed_work_state=True,
        canonical_governed_state=promotion.canonical_governed_state,
        repository_authority_conflict=repository_authority_conflict,
    )

    if any(
        (
            promotion.branch_bypass_authorized,
            promotion.validation_bypass_authorized,
            promotion.review_bypass_authorized,
            promotion.acceptance_bypass_authorized,
            promotion.merge_bypass_authorized,
        )
    ):
        raise ValueError("routing stopped: promotion attempted to bypass governed lifecycle gates")

    stages = (
        FEATURE_DEVELOPMENT_STAGES
        if authority.path is AuthorityPath.FEATURE_DEVELOPMENT
        else ()
    )

    return RoutingOutcome(
        classification_state=classification.state.value,
        authority_path=authority.path.value,
        provenance=provenance,
        promotion=promotion,
        hosted_validation=hosted_validation,
        feature_development_stages=stages,
        mutation_authorized=False,
    )
