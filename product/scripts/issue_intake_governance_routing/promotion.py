from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .provenance import IntakeProvenance


class PromotionForm(str, Enum):
    IN_PLACE = "in-place"
    SUCCESSOR = "successor"


@dataclass(frozen=True)
class CanonicalGovernedStateObservation:
    governing_issue: str
    governed_operation: str
    observed_revision: str

    def __post_init__(self) -> None:
        for field_name in (
            "governing_issue",
            "governed_operation",
            "observed_revision",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"canonical governed-state observation requires non-empty {field_name}"
                )


@dataclass(frozen=True)
class CanonicalGovernedStateValidationResult:
    governing_issue: str
    governed_operation: str
    validated_revision: str
    validation_artifact_id: str
    validator_id: str
    canonical_structure_valid: bool

    def __post_init__(self) -> None:
        for field_name in (
            "governing_issue",
            "governed_operation",
            "validated_revision",
            "validation_artifact_id",
            "validator_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"canonical governed-state validation result requires non-empty {field_name}"
                )


class CanonicalGovernedStateValidator(Protocol):
    def validate(
        self,
        observation: CanonicalGovernedStateObservation,
    ) -> CanonicalGovernedStateValidationResult:
        ...


_VALIDATED_EVIDENCE_SEAL = object()


class CanonicalGovernedStateEvidence:
    __slots__ = (
        "_governing_issue",
        "_governed_operation",
        "_validated_revision",
        "_observed_revision",
        "_validation_artifact_id",
        "_validator_id",
        "_seal",
    )

    def __init__(
        self,
        *,
        governing_issue: str,
        governed_operation: str,
        validated_revision: str,
        observed_revision: str,
        validation_artifact_id: str,
        validator_id: str,
        _seal: object,
    ) -> None:
        if _seal is not _VALIDATED_EVIDENCE_SEAL:
            raise ValueError(
                "canonical governed-state evidence must be produced by validation"
            )
        self._governing_issue = governing_issue
        self._governed_operation = governed_operation
        self._validated_revision = validated_revision
        self._observed_revision = observed_revision
        self._validation_artifact_id = validation_artifact_id
        self._validator_id = validator_id
        self._seal = _seal

    @property
    def governing_issue(self) -> str:
        return self._governing_issue

    @property
    def governed_operation(self) -> str:
        return self._governed_operation

    @property
    def validated_revision(self) -> str:
        return self._validated_revision

    @property
    def observed_revision(self) -> str:
        return self._observed_revision

    @property
    def validation_artifact_id(self) -> str:
        return self._validation_artifact_id

    @property
    def validator_id(self) -> str:
        return self._validator_id

    @property
    def is_fresh(self) -> bool:
        return self.validated_revision == self.observed_revision

    def require_valid_for(
        self,
        *,
        governing_issue: str,
        governed_operation: str,
    ) -> None:
        if self._seal is not _VALIDATED_EVIDENCE_SEAL:
            raise ValueError(
                "canonical governed-state evidence was not produced by validation"
            )
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


def validate_canonical_governed_state(
    *,
    observation: CanonicalGovernedStateObservation,
    validator: CanonicalGovernedStateValidator,
) -> CanonicalGovernedStateEvidence:
    if not isinstance(observation, CanonicalGovernedStateObservation):
        raise ValueError("canonical governed-state observation is required")
    validate = getattr(validator, "validate", None)
    if not callable(validate):
        raise ValueError("canonical governed-state validator is required")

    result = validate(observation)
    if not isinstance(result, CanonicalGovernedStateValidationResult):
        raise ValueError(
            "canonical governed-state validator returned an invalid validation result"
        )
    if not result.canonical_structure_valid:
        raise ValueError("canonical governed-state validation failed")
    if result.governing_issue != observation.governing_issue:
        raise ValueError(
            "canonical governed-state validation result does not match governing issue"
        )
    if result.governed_operation != observation.governed_operation:
        raise ValueError(
            "canonical governed-state validation result does not match governed operation"
        )
    if result.validated_revision != observation.observed_revision:
        raise ValueError(
            "canonical governed-state validation result is stale for the observed target revision"
        )

    return CanonicalGovernedStateEvidence(
        governing_issue=result.governing_issue,
        governed_operation=result.governed_operation,
        validated_revision=result.validated_revision,
        observed_revision=observation.observed_revision,
        validation_artifact_id=result.validation_artifact_id,
        validator_id=result.validator_id,
        _seal=_VALIDATED_EVIDENCE_SEAL,
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
