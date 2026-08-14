"""Portable Issue Intake and Governance Routing product implementation."""

from .classification import (
    BUG_FIX,
    FEATURE_REQUEST,
    GOVERNED_WORK,
    ClassificationResult,
    ClassificationState,
    classify_labels,
)
from .authority import (
    AuditDisposition,
    AuthorityPath,
    AuthorityRoutingResult,
    FEATURE_DEVELOPMENT_STAGES,
    route_audited_bug,
    route_labels,
)
from .provenance import IntakeProvenance, capture_intake_provenance
from .promotion import (
    CanonicalGovernedStateEvidence,
    CanonicalGovernedStateObservation,
    CanonicalGovernedStateValidationResult,
    CanonicalGovernedStateValidator,
    PromotionForm,
    PromotionPlan,
    plan_promotion,
    validate_canonical_governed_state,
)
from .hosted_validation import HostedValidationDecision, activate_hosted_validation
from .orchestration import RoutingOutcome, route_intake_to_governed_work

__all__ = [
    "BUG_FIX",
    "FEATURE_REQUEST",
    "GOVERNED_WORK",
    "ClassificationResult",
    "ClassificationState",
    "classify_labels",
    "AuditDisposition",
    "AuthorityPath",
    "AuthorityRoutingResult",
    "FEATURE_DEVELOPMENT_STAGES",
    "route_audited_bug",
    "route_labels",
    "IntakeProvenance",
    "capture_intake_provenance",
    "CanonicalGovernedStateEvidence",
    "CanonicalGovernedStateObservation",
    "CanonicalGovernedStateValidationResult",
    "CanonicalGovernedStateValidator",
    "validate_canonical_governed_state",
    "PromotionForm",
    "PromotionPlan",
    "plan_promotion",
    "HostedValidationDecision",
    "activate_hosted_validation",
    "RoutingOutcome",
    "route_intake_to_governed_work",
]
