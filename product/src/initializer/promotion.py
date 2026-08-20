from __future__ import annotations

import os
import shutil
from pathlib import Path

from .models import (
    InitializerError,
    DestinationState,
    TransactionPhase,
    PreflightDecision,
    PromotionPlan,
    PromotionResult,
    DestinationPreflight,
)
from .destination import (
    DestinationError,
    destination_preflight,
    build_promotion_plan,
    validate_staging_result_complete,
)


BACKUP_PREFIX = "repo-spec-backup-"


class PromotionError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def _rename(src: Path, dst: Path) -> None:
    os.rename(str(src), str(dst))


def _backup_name(dest_dir: Path, dest_name: str) -> Path:
    backup = dest_dir / f"{BACKUP_PREFIX}{dest_name}"
    suffix = 0
    while backup.exists():
        suffix += 1
        backup = dest_dir / f"{BACKUP_PREFIX}{dest_name}.{suffix}"
    return backup


def prepare_destination(
    plan: PromotionPlan,
) -> str | None:
    dest_path = Path(plan.destination_path)

    if plan.destination_state == DestinationState.absent:
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        return None

    if plan.destination_state == DestinationState.empty_directory:
        backup = _backup_name(dest_path.parent, dest_path.name)
        _rename(dest_path, backup)
        return str(backup)

    return None


def restore_destination(plan: PromotionPlan, backup_path: str | None) -> bool:
    if backup_path is None:
        return False

    dest_p = Path(plan.destination_path)
    backup_p = Path(backup_path)

    if plan.destination_state == DestinationState.empty_directory:
        if backup_p.exists() and not dest_p.exists():
            try:
                _rename(backup_p, dest_p)
                return True
            except OSError:
                pass
        elif not dest_p.exists():
            try:
                dest_p.mkdir(parents=True, exist_ok=True)
            except OSError:
                pass

    return False


def promote(
    staging_path: str,
    destination_path: str,
) -> PromotionResult:
    staging_p = Path(staging_path).resolve()
    dest_p = Path(destination_path).resolve()

    preflight = destination_preflight(staging_path, destination_path)

    if preflight.decision != PreflightDecision.allowed:
        return PromotionResult(
            status="failed",
            transaction_state=TransactionPhase.preflight,
            destination_classification=preflight.destination_classification,
            staging_path=str(staging_p),
            requested_destination=str(dest_p),
            failure_reason=preflight.rejection_reason or "preflight rejected destination",
        )

    plan = build_promotion_plan(preflight)

    backup_path: str | None = None
    try:
        backup_path = prepare_destination(plan)
    except OSError as exc:
        return PromotionResult(
            status="failed",
            transaction_state=TransactionPhase.failed,
            destination_classification=plan.destination_state,
            staging_path=str(staging_p),
            requested_destination=str(dest_p),
            failure_reason=f"prepare failed: {exc}",
        )

    try:
        _rename(staging_p, dest_p)
    except OSError as exc:
        restore_destination(plan, backup_path)
        return PromotionResult(
            status="failed",
            transaction_state=TransactionPhase.failed,
            destination_classification=plan.destination_state,
            staging_path=str(staging_p),
            requested_destination=str(dest_p),
            failure_reason=f"commit rename failed: {exc}",
            preserved_state=backup_path,
            cleanup_state="restored",
        )

    if backup_path is not None:
        try:
            _cleanup_backup(backup_path)
        except OSError:
            pass

    return PromotionResult(
        status="success",
        transaction_state=TransactionPhase.committed,
        destination_classification=plan.destination_state,
        staging_path=str(staging_p),
        requested_destination=str(dest_p),
        committed_destination=str(dest_p),
    )


def _cleanup_backup(backup_path: str) -> None:
    backup_p = Path(backup_path)
    if backup_p.is_dir():
        shutil.rmtree(backup_p, ignore_errors=True)
    elif backup_p.exists():
        backup_p.unlink()


def promote_with_validation(
    staging_path: str,
    destination_path: str,
    installed: list[dict[str, object]],
    rejected: list[dict[str, object]],
) -> PromotionResult:
    try:
        validate_staging_result_complete(installed, rejected)
    except DestinationError as exc:
        return PromotionResult(
            status="failed",
            transaction_state=TransactionPhase.preflight,
            destination_classification="unknown",
            staging_path=str(Path(staging_path).resolve()),
            requested_destination=str(Path(destination_path).resolve()),
            failure_reason=str(exc),
        )

    return promote(staging_path, destination_path)
