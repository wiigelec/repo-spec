from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Any
from weakref import WeakSet

from .provenance import IntakeProvenance


TRUSTED_CANONICAL_VALIDATION_PRODUCERS = {
    "repository-canonical-validator": {
        "command_env": "REPO_SPEC_CANONICAL_VALIDATOR",
        "sha256": "e33c64598dab548733ae0869bded33877c8a49b104e372928ac82d5f0cbc6dcc",
    },
}


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
    producer_id: str
    canonical_structure_valid: bool

    def __post_init__(self) -> None:
        for field_name in (
            "governing_issue",
            "governed_operation",
            "validated_revision",
            "validation_artifact_id",
            "producer_id",
        ):
            value = getattr(self, field_name)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(
                    f"canonical governed-state validation result requires non-empty {field_name}"
                )


class CanonicalGovernedStateEvidence:
    __slots__ = (
        "_governing_issue",
        "_governed_operation",
        "_validated_revision",
        "_observed_revision",
        "_validation_artifact_id",
        "_producer_id",
        "__weakref__",
    )

    def __new__(cls, *args, **kwargs):
        raise ValueError(
            "canonical governed-state evidence must be issued by trusted validation"
        )

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
    def producer_id(self) -> str:
        return self._producer_id

    @property
    def validator_id(self) -> str:
        # Compatibility alias for callers that only need producer identity.
        return self._producer_id

    @property
    def is_fresh(self) -> bool:
        return self.validated_revision == self.observed_revision


def _parse_validation_result(payload: Any) -> CanonicalGovernedStateValidationResult:
    if not isinstance(payload, dict):
        raise ValueError("trusted canonical validator returned a non-object result")
    expected = {
        "governing_issue",
        "governed_operation",
        "validated_revision",
        "validation_artifact_id",
        "producer_id",
        "canonical_structure_valid",
    }
    if set(payload) != expected:
        raise ValueError("trusted canonical validator returned invalid result fields")
    return CanonicalGovernedStateValidationResult(**payload)


def _build_promotion_boundary():
    issued: WeakSet[CanonicalGovernedStateEvidence] = WeakSet()

    def validate_canonical_governed_state(
        *,
        observation: CanonicalGovernedStateObservation,
        producer_id: str,
    ) -> CanonicalGovernedStateEvidence:
        if not isinstance(observation, CanonicalGovernedStateObservation):
            raise ValueError("canonical governed-state observation is required")
        descriptor = TRUSTED_CANONICAL_VALIDATION_PRODUCERS.get(producer_id)
        if descriptor is None:
            raise ValueError(
                f"unrecognized canonical validation producer: {producer_id}"
            )

        command_value = os.environ.get(descriptor["command_env"], "")
        if not command_value:
            raise ValueError(
                f"trusted canonical validation producer is unavailable: {producer_id}"
            )
        command = Path(command_value).resolve()
        if not command.is_file():
            raise ValueError(
                f"trusted canonical validation producer is unavailable: {producer_id}"
            )
        observed_command_sha256 = hashlib.sha256(command.read_bytes()).hexdigest()
        if observed_command_sha256 != descriptor["sha256"]:
            raise ValueError(
                "canonical validation producer artifact identity mismatch"
            )

        validation_subject = os.environ.get(
            "REPO_SPEC_CANONICAL_VALIDATION_SUBJECT", ""
        )
        if not validation_subject:
            raise ValueError("canonical validation subject is unavailable")

        request = {
            "governing_issue": observation.governing_issue,
            "governed_operation": observation.governed_operation,
            "observed_revision": observation.observed_revision,
            "producer_id": producer_id,
            "validation_subject": validation_subject,
        }
        result = subprocess.run(
            [str(command)],
            input=json.dumps(request),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise ValueError(
                f"trusted canonical validation producer failed: {detail}"
            )
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            raise ValueError(
                "trusted canonical validator returned invalid JSON"
            ) from exc

        validated = _parse_validation_result(payload)
        if validated.producer_id != producer_id:
            raise ValueError(
                "canonical validation result does not match trusted producer"
            )
        if not validated.canonical_structure_valid:
            raise ValueError("canonical governed-state validation failed")
        if validated.governing_issue != observation.governing_issue:
            raise ValueError(
                "canonical governed-state validation result does not match governing issue"
            )
        if validated.governed_operation != observation.governed_operation:
            raise ValueError(
                "canonical governed-state validation result does not match governed operation"
            )
        if validated.validated_revision != observation.observed_revision:
            raise ValueError(
                "canonical governed-state validation result is stale for the observed target revision"
            )

        evidence = object.__new__(CanonicalGovernedStateEvidence)
        evidence._governing_issue = validated.governing_issue
        evidence._governed_operation = validated.governed_operation
        evidence._validated_revision = validated.validated_revision
        evidence._observed_revision = observation.observed_revision
        evidence._validation_artifact_id = validated.validation_artifact_id
        evidence._producer_id = validated.producer_id
        issued.add(evidence)
        return evidence

    def plan_promotion(
        *,
        form: PromotionForm,
        intake_issue: str,
        governing_issue: str,
        governed_operation: str,
        provenance: IntakeProvenance,
        canonical_state_evidence: CanonicalGovernedStateEvidence,
    ) -> "PromotionPlan":
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

        if not isinstance(canonical_state_evidence, CanonicalGovernedStateEvidence):
            raise ValueError("validated canonical governed-state evidence is required")
        if canonical_state_evidence not in issued:
            raise ValueError(
                "canonical governed-state evidence was not issued by trusted validation"
            )
        if canonical_state_evidence.governing_issue != governing:
            raise ValueError(
                "canonical governed-state evidence does not match governing issue"
            )
        if canonical_state_evidence.governed_operation != operation:
            raise ValueError(
                "canonical governed-state evidence does not match governed operation"
            )
        if not canonical_state_evidence.is_fresh:
            raise ValueError(
                "canonical governed-state evidence is stale for the observed target revision"
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

    return validate_canonical_governed_state, plan_promotion


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


validate_canonical_governed_state, plan_promotion = _build_promotion_boundary()
del _build_promotion_boundary
