from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

from .upgrade_reanchoring import (
    FrameworkReanchoringError,
    reanchor_staged_repository,
    reanchoring_evidence_fingerprint,
)
from .upgrade_reconciliation import (
    StagedReconciliationError,
    stage_managed_reconciliation,
    staged_reconciliation_evidence_fingerprint,
)
from .upgrade_resolution import (
    UpgradeResolutionError,
    resolve_upgrade_set,
    upgrade_set_evidence_fingerprint,
)
from .upgrade_validation_promotion import (
    UpgradeValidationPromotionError,
    promote_validated_candidate,
    up4_evidence_fingerprint,
    validate_reanchored_candidate,
)


@dataclass(frozen=True)
class DerivedRepositoryUpgradeResult:
    terminal_result: str
    succeeded: bool
    accepted: bool
    baseline_source: str | None
    baseline_revision: str | None
    reconciliation_target_revision: str | None
    selected_material_keys: tuple[str, ...]
    reconciliation_status: str | None
    validation_status: str | None
    promotion_outcome: str | None
    failure_reason: str | None
    upgrade_set_fingerprint: str | None
    staged_reconciliation_fingerprint: str | None
    reanchoring_fingerprint: str | None
    up4_fingerprint: str | None

    def canonical_evidence_dict(self) -> dict[str, object]:
        return {
            "terminal_result": self.terminal_result,
            "succeeded": self.succeeded,
            "accepted": self.accepted,
            "baseline_source": self.baseline_source,
            "baseline_revision": self.baseline_revision,
            "reconciliation_target_revision": self.reconciliation_target_revision,
            "selected_material_keys": list(self.selected_material_keys),
            "reconciliation_status": self.reconciliation_status,
            "validation_status": self.validation_status,
            "promotion_outcome": self.promotion_outcome,
            "failure_reason": self.failure_reason,
            "upgrade_set_fingerprint": self.upgrade_set_fingerprint,
            "staged_reconciliation_fingerprint": self.staged_reconciliation_fingerprint,
            "reanchoring_fingerprint": self.reanchoring_fingerprint,
            "up4_fingerprint": self.up4_fingerprint,
        }

    def to_dict(self) -> dict[str, object]:
        return self.canonical_evidence_dict()


def serialize_upgrade_evidence(result: DerivedRepositoryUpgradeResult) -> bytes:
    return (
        json.dumps(
            result.canonical_evidence_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def upgrade_evidence_fingerprint(result: DerivedRepositoryUpgradeResult) -> str:
    return hashlib.sha256(serialize_upgrade_evidence(result)).hexdigest()


def _resolution_fields(resolution) -> dict[str, object]:
    return {
        "baseline_source": resolution.baseline.baseline_source,
        "baseline_revision": resolution.baseline.active_baseline.framework_revision.object_id,
        "reconciliation_target_revision": resolution.reconciliation_target.commit_id,
        "selected_material_keys": tuple(resolution.selected_material_keys),
        "upgrade_set_fingerprint": upgrade_set_evidence_fingerprint(resolution),
    }


def _failure(
    terminal_result: str,
    reason: str,
    *,
    resolution=None,
    staged=None,
    reanchoring=None,
    validation=None,
    promotion=None,
) -> DerivedRepositoryUpgradeResult:
    fields = {
        "baseline_source": None,
        "baseline_revision": None,
        "reconciliation_target_revision": None,
        "selected_material_keys": (),
        "upgrade_set_fingerprint": None,
    }
    if resolution is not None:
        fields.update(_resolution_fields(resolution))

    return DerivedRepositoryUpgradeResult(
        terminal_result=terminal_result,
        succeeded=False,
        accepted=bool(promotion and promotion.accepted),
        baseline_source=fields["baseline_source"],
        baseline_revision=fields["baseline_revision"],
        reconciliation_target_revision=fields["reconciliation_target_revision"],
        selected_material_keys=fields["selected_material_keys"],
        reconciliation_status=staged.status if staged is not None else None,
        validation_status=validation.status if validation is not None else None,
        promotion_outcome=promotion.promotion_outcome if promotion is not None else None,
        failure_reason=reason,
        upgrade_set_fingerprint=fields["upgrade_set_fingerprint"],
        staged_reconciliation_fingerprint=(
            staged_reconciliation_evidence_fingerprint(staged)
            if staged is not None
            else None
        ),
        reanchoring_fingerprint=(
            reanchoring_evidence_fingerprint(reanchoring)
            if reanchoring is not None
            else None
        ),
        up4_fingerprint=(
            up4_evidence_fingerprint(validation, promotion)
            if validation is not None
            else None
        ),
    )


def execute_repository_upgrade(
    target_repository: str,
    executing_framework_repository: str,
) -> DerivedRepositoryUpgradeResult:
    try:
        resolution = resolve_upgrade_set(
            target_repository,
            executing_framework_repository,
        )
    except UpgradeResolutionError as exc:
        return _failure("pre-promotion-failure", str(exc))

    try:
        staged = stage_managed_reconciliation(resolution)
    except StagedReconciliationError as exc:
        return _failure("pre-promotion-failure", str(exc), resolution=resolution)

    if staged.conflicts:
        return _failure(
            "rejected",
            "managed reconciliation conflict",
            resolution=resolution,
            staged=staged,
        )

    try:
        reanchoring = reanchor_staged_repository(resolution, staged)
    except FrameworkReanchoringError as exc:
        return _failure(
            "pre-promotion-failure",
            str(exc),
            resolution=resolution,
            staged=staged,
        )

    try:
        validation = validate_reanchored_candidate(
            staged,
            reanchoring,
            resolution.baseline.request.target_repository,
        )
    except UpgradeValidationPromotionError as exc:
        return _failure(
            "pre-promotion-failure",
            str(exc),
            resolution=resolution,
            staged=staged,
            reanchoring=reanchoring,
        )

    if not validation.promotion_eligible:
        return _failure(
            "pre-promotion-failure",
            validation.failure_reason or "staged repository validation failed",
            resolution=resolution,
            staged=staged,
            reanchoring=reanchoring,
            validation=validation,
        )

    try:
        promotion = promote_validated_candidate(
            staged,
            reanchoring,
            validation,
            resolution.baseline.request.target_repository,
        )
    except UpgradeValidationPromotionError as exc:
        return _failure(
            "non-promoted",
            str(exc),
            resolution=resolution,
            staged=staged,
            reanchoring=reanchoring,
            validation=validation,
        )

    if promotion.promotion_outcome == "indeterminate":
        terminal = "indeterminate"
    elif not promotion.accepted:
        terminal = "non-promoted"
    elif promotion.completion_status == "promoted-with-finalization-error":
        terminal = "promoted-with-finalization-error"
    else:
        terminal = "promoted-success"

    if terminal != "promoted-success":
        return _failure(
            terminal,
            promotion.failure_reason or promotion.completion_status,
            resolution=resolution,
            staged=staged,
            reanchoring=reanchoring,
            validation=validation,
            promotion=promotion,
        )

    fields = _resolution_fields(resolution)
    return DerivedRepositoryUpgradeResult(
        terminal_result="promoted-success",
        succeeded=True,
        accepted=True,
        baseline_source=fields["baseline_source"],
        baseline_revision=fields["baseline_revision"],
        reconciliation_target_revision=fields["reconciliation_target_revision"],
        selected_material_keys=fields["selected_material_keys"],
        reconciliation_status=staged.status,
        validation_status=validation.status,
        promotion_outcome=promotion.promotion_outcome,
        failure_reason=None,
        upgrade_set_fingerprint=fields["upgrade_set_fingerprint"],
        staged_reconciliation_fingerprint=staged_reconciliation_evidence_fingerprint(staged),
        reanchoring_fingerprint=reanchoring_evidence_fingerprint(reanchoring),
        up4_fingerprint=up4_evidence_fingerprint(validation, promotion),
    )
