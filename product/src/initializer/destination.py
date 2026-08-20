from __future__ import annotations

import os
import stat as stat_module
from pathlib import Path

from .models import (
    DestinationState,
    DestinationPreflight,
    PreflightDecision,
    PromotionPlan,
    InitializerError,
    I1DestinationPreflight,
)


class DestinationError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def resolve_and_normalize(path: str) -> Path:
    return Path(path).resolve()


def paths_are_same(resolved_a: Path, resolved_b: Path) -> bool:
    return resolved_a == resolved_b


def path_contains_other(parent: Path, child: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def paths_are_aliased(
    staging_path: Path, destination_path: Path,
) -> bool:
    res_staging = staging_path.resolve()
    res_dest = destination_path.resolve()
    if res_staging == res_dest:
        return True
    return False


def check_path_conflicts(
    staging_path: Path, destination_path: Path,
) -> tuple[bool, bool, bool]:
    res_staging = staging_path.resolve()
    res_dest = destination_path.resolve()

    aliased = res_staging == res_dest

    staging_inside_dest = False
    dest_inside_staging = False

    if not aliased:
        try:
            res_staging.relative_to(res_dest)
            staging_inside_dest = True
        except ValueError:
            pass

        try:
            res_dest.relative_to(res_staging)
            dest_inside_staging = True
        except ValueError:
            pass

    return aliased, staging_inside_dest, dest_inside_staging


def classify_destination(destination: Path) -> str:
    if not destination.exists():
        parent = destination.parent
        if not parent.exists():
            return DestinationState.inaccessible
        try:
            if not os.access(str(parent), os.R_OK | os.X_OK):
                return DestinationState.inaccessible
        except OSError:
            return DestinationState.inaccessible
        return DestinationState.absent

    try:
        dest_stat = destination.lstat()
    except (PermissionError, OSError):
        return DestinationState.inaccessible

    mode = dest_stat.st_mode

    if stat_module.S_ISLNK(mode):
        return DestinationState.symlink
    if stat_module.S_ISREG(mode):
        return DestinationState.regular_file
    if stat_module.S_ISDIR(mode):
        try:
            contents = list(destination.iterdir())
            if contents:
                return DestinationState.nonempty_directory
            return DestinationState.empty_directory
        except (PermissionError, OSError):
            return DestinationState.inaccessible
    if stat_module.S_ISCHR(mode) or stat_module.S_ISBLK(mode):
        return DestinationState.unsupported
    if stat_module.S_ISFIFO(mode):
        return DestinationState.unsupported
    if stat_module.S_ISSOCK(mode):
        return DestinationState.unsupported

    return DestinationState.unsupported


def check_same_filesystem(path_a: Path, path_b: Path) -> bool:
    try:
        return path_a.stat().st_dev == path_b.stat().st_dev
    except OSError:
        return False


def destination_preflight(
    staging_path: str,
    destination_path: str,
) -> DestinationPreflight:
    staging_p = Path(staging_path)
    dest_p = Path(destination_path)

    if not staging_p.exists():
        return DestinationPreflight(
            staging_path=str(staging_p.resolve()),
            destination_path=str(dest_p.resolve()),
            destination_state=DestinationState.inaccessible,
            same_filesystem=False,
            aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.rejected,
            rejection_reason="staging workspace does not exist",
        )

    if not staging_p.is_dir():
        return DestinationPreflight(
            staging_path=str(staging_p.resolve()),
            destination_path=str(dest_p.resolve()),
            destination_state=DestinationState.inaccessible,
            same_filesystem=False,
            aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.rejected,
            rejection_reason="staging workspace is not a directory",
        )

    aliased, staging_inside_dest, dest_inside_staging = check_path_conflicts(
        staging_p, dest_p,
    )

    if aliased:
        return DestinationPreflight(
            staging_path=str(staging_p.resolve()),
            destination_path=str(dest_p.resolve()),
            destination_state=DestinationState.inaccessible,
            same_filesystem=True,
            aliased=True,
            staging_inside_destination=staging_inside_dest,
            destination_inside_staging=dest_inside_staging,
            decision=PreflightDecision.rejected,
            rejection_reason="staging workspace and destination are the same path",
        )

    if staging_inside_dest:
        return DestinationPreflight(
            staging_path=str(staging_p.resolve()),
            destination_path=str(dest_p.resolve()),
            destination_state=DestinationState.inaccessible,
            same_filesystem=False,
            aliased=False,
            staging_inside_destination=True,
            destination_inside_staging=dest_inside_staging,
            decision=PreflightDecision.rejected,
            rejection_reason="staging workspace is inside the requested destination",
        )

    if dest_inside_staging:
        return DestinationPreflight(
            staging_path=str(staging_p.resolve()),
            destination_path=str(dest_p.resolve()),
            destination_state=DestinationState.inaccessible,
            same_filesystem=False,
            aliased=False,
            staging_inside_destination=staging_inside_dest,
            destination_inside_staging=True,
            decision=PreflightDecision.rejected,
            rejection_reason="requested destination is inside the staging workspace",
        )

    dest_state = classify_destination(dest_p)

    same_fs = False
    if dest_p.exists():
        same_fs = check_same_filesystem(staging_p, dest_p)
    else:
        dest_parent = dest_p.parent
        if dest_parent.exists():
            same_fs = check_same_filesystem(staging_p, dest_parent)

    allowed_states = {DestinationState.absent, DestinationState.empty_directory}

    if dest_state in allowed_states:
        if dest_state == DestinationState.absent:
            parent = dest_p.parent
            if not parent.exists():
                return DestinationPreflight(
                    staging_path=str(staging_p.resolve()),
                    destination_path=str(dest_p.resolve()),
                    destination_state=dest_state,
                    same_filesystem=same_fs,
                    aliased=False,
                    staging_inside_destination=False,
                    destination_inside_staging=False,
                    decision=PreflightDecision.rejected,
                    rejection_reason="destination parent directory does not exist",
                )

        if not same_fs:
            return DestinationPreflight(
                staging_path=str(staging_p.resolve()),
                destination_path=str(dest_p.resolve()),
                destination_state=dest_state,
                same_filesystem=False,
                aliased=False,
                staging_inside_destination=False,
                destination_inside_staging=False,
                decision=PreflightDecision.rejected,
                rejection_reason="cross-device promotion not supported: staging and destination are on different filesystems",
            )

        return DestinationPreflight(
            staging_path=str(staging_p.resolve()),
            destination_path=str(dest_p.resolve()),
            destination_state=dest_state,
            same_filesystem=True,
            aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.allowed,
        )

    rejection_reasons = {
        DestinationState.nonempty_directory: "destination is a nonempty directory",
        DestinationState.regular_file: "destination is a regular file",
        DestinationState.symlink: "destination is a symbolic link",
        DestinationState.unsupported: "destination is an unsupported filesystem entry type",
        DestinationState.inaccessible: "destination is not accessible",
    }

    reason = rejection_reasons.get(
        dest_state,
        f"unsupported destination state: {dest_state}",
    )

    return DestinationPreflight(
        staging_path=str(staging_p.resolve()),
        destination_path=str(dest_p.resolve()),
        destination_state=dest_state,
        same_filesystem=same_fs,
        aliased=False,
        staging_inside_destination=False,
        destination_inside_staging=False,
        decision=PreflightDecision.rejected,
        rejection_reason=reason,
    )


def build_promotion_plan(preflight: DestinationPreflight) -> PromotionPlan:
    if preflight.decision != PreflightDecision.allowed:
        raise DestinationError(
            f"cannot build promotion plan from rejected preflight: {preflight.rejection_reason}"
        )

    requires_preparation = preflight.destination_state == DestinationState.empty_directory
    backup_path: str | None = None

    return PromotionPlan(
        staging_path=preflight.staging_path,
        destination_path=preflight.destination_path,
        destination_state=preflight.destination_state,
        requires_preparation=requires_preparation,
        same_filesystem=preflight.same_filesystem,
        backup_path=backup_path,
    )


def validate_staging_result_complete(
    installed: list[dict[str, object]],
    rejected: list[dict[str, object]],
) -> None:
    if rejected:
        raise DestinationError(
            f"cannot promote staging result with {len(rejected)} rejected artifacts"
        )


def i1_destination_preflight(destination_path: str) -> I1DestinationPreflight:
    destination = Path(destination_path)
    if not destination.is_absolute():
        raise DestinationError("destination must be the intake-resolved absolute path")
    try:
        destination.lstat()
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise DestinationError(f"destination cannot be inspected: {exc}") from exc
    else:
        raise DestinationError("destination already exists")
    parent = destination.parent
    try:
        st = parent.stat()
    except OSError as exc:
        raise DestinationError(f"destination parent is inaccessible: {exc}") from exc
    if not stat_module.S_ISDIR(st.st_mode):
        raise DestinationError("destination parent is not a directory")
    if not os.access(parent, os.R_OK | os.W_OK | os.X_OK):
        raise DestinationError("destination parent is inaccessible")
    return I1DestinationPreflight(
        destination=str(destination),
        destination_state="absent",
        destination_parent=str(parent),
        filesystem_device=st.st_dev,
        same_filesystem=True,
        decision="allowed",
    )


# I4 PATCH 3: TRANSACTIONAL PROMOTION
#
# Implements the absent-only destination recheck, one same-filesystem atomic
# rename, terminal promotion outcomes, and success-finalization cleanup.

import shutil as _i4_shutil
from dataclasses import dataclass as _i4_dataclass
from collections.abc import Callable as _I4Callable


@_i4_dataclass(frozen=True)
class I4PromotionResult:
    promotion_outcome: str
    completion_status: str
    destination: str
    staging_root: str
    error: str | None = None

    @property
    def promoted(self) -> bool:
        return self.promotion_outcome == "promoted"


def i4_recheck_destination_absent(destination: Path) -> None:
    if not destination.is_absolute():
        raise DestinationError("destination must remain the intake-resolved absolute path")
    try:
        destination.lstat()
    except FileNotFoundError:
        pass
    except OSError as exc:
        raise DestinationError(f"destination cannot be rechecked safely: {exc}") from exc
    else:
        raise DestinationError("destination exists at promotion recheck")

    try:
        parent_stat = destination.parent.stat()
    except OSError as exc:
        raise DestinationError(f"destination parent is inaccessible at promotion: {exc}") from exc
    if not stat_module.S_ISDIR(parent_stat.st_mode):
        raise DestinationError("destination parent is not a directory at promotion")
    if not os.access(destination.parent, os.R_OK | os.W_OK | os.X_OK):
        raise DestinationError("destination parent is inaccessible at promotion")


def _i4_same_filesystem_for_rename(repository: Path, destination: Path) -> bool:
    try:
        return repository.stat().st_dev == destination.parent.stat().st_dev
    except OSError:
        return False


def _i4_load_staging_helpers():
    from .staging import (
        _i4_atomic_write,
        build_execution_report_v1,
        execution_report_bytes_v1,
        staging_state_bytes_v1,
        validate_staging_state_v1,
    )
    return (
        _i4_atomic_write,
        build_execution_report_v1,
        execution_report_bytes_v1,
        staging_state_bytes_v1,
        validate_staging_state_v1,
    )


def _i4_state_copy(pair) -> dict[str, object]:
    state = dict(pair.staging_state)
    state["completed_stages"] = dict(state["completed_stages"])
    return state


def _i4_write_state(workspace, state: dict[str, object]) -> None:
    (
        atomic_write,
        _build_execution_report,
        _execution_report_bytes,
        staging_state_bytes,
        validate_staging_state,
    ) = _i4_load_staging_helpers()
    validate_staging_state(state)
    atomic_write(workspace.staging_state_path, staging_state_bytes(state))


def _i4_write_execution_report(
    workspace,
    *,
    promotion_outcome: str,
    completion_status: str,
    failed_stage: str,
    reason: str,
    completed_stages: tuple[str, ...],
) -> None:
    (
        atomic_write,
        build_execution_report,
        execution_report_bytes,
        _staging_state_bytes,
        _validate_staging_state,
    ) = _i4_load_staging_helpers()
    canonical = (
        "request-intake",
        "source-resolution",
        "destination-preflight",
        "staging-establishment",
        "framework-installation",
        "direction-evidence-installation",
        "workspace-seeding",
        "provenance-recording",
        "handoff-assembly",
        "git-initialization",
        "repository-validation",
        "promotion",
        "success-finalization",
    )
    failed_index = canonical.index(failed_stage)
    statuses: dict[str, str] = {}
    for stage in canonical:
        if stage in completed_stages:
            statuses[stage] = "completed"
        elif stage == failed_stage:
            statuses[stage] = "failed"
        elif canonical.index(stage) > failed_index:
            statuses[stage] = "deferred"

    report = build_execution_report(
        workspace,
        promotion_outcome=promotion_outcome,
        completion_status=completion_status,
        stage_status=statuses,
        stage_errors={failed_stage: [reason]},
    )
    atomic_write(workspace.execution_report_path, execution_report_bytes(report))


def _i4_completed_with(
    state: dict[str, object],
    *stages: str,
) -> tuple[str, ...]:
    completed = dict(state["completed_stages"])
    for stage in stages:
        completed[stage] = "completed"
    canonical = (
        "request-intake",
        "source-resolution",
        "destination-preflight",
        "staging-establishment",
        "framework-installation",
        "direction-evidence-installation",
        "workspace-seeding",
        "provenance-recording",
        "handoff-assembly",
        "git-initialization",
        "repository-validation",
        "promotion",
        "success-finalization",
    )
    return tuple(stage for stage in canonical if stage in completed)


def _i4_record_not_promoted(
    workspace,
    pair,
    *,
    reason: str,
) -> I4PromotionResult:
    state = _i4_state_copy(pair)
    state["current_stage"] = "promotion"
    state["failed_stage"] = "promotion"
    state["promotion_entered"] = True
    state["promotion_outcome"] = "not-promoted"
    state["cleanup_failure"] = None
    _i4_write_state(workspace, state)
    completed = _i4_completed_with(state, "repository-validation")
    _i4_write_execution_report(
        workspace,
        promotion_outcome="not-promoted",
        completion_status="failed",
        failed_stage="promotion",
        reason=reason,
        completed_stages=completed,
    )
    return I4PromotionResult(
        "not-promoted",
        "failed",
        workspace.inputs.request.destination,
        str(workspace.root),
        reason,
    )


def _i4_record_indeterminate(
    workspace,
    pair,
    *,
    reason: str,
) -> I4PromotionResult:
    state = _i4_state_copy(pair)
    state["current_stage"] = "promotion"
    state["failed_stage"] = "promotion"
    state["promotion_entered"] = True
    state["promotion_outcome"] = "indeterminate"
    state["cleanup_failure"] = None
    _i4_write_state(workspace, state)
    completed = _i4_completed_with(state, "repository-validation")
    _i4_write_execution_report(
        workspace,
        promotion_outcome="indeterminate",
        completion_status="failed",
        failed_stage="promotion",
        reason=reason,
        completed_stages=completed,
    )
    return I4PromotionResult(
        "indeterminate",
        "failed",
        workspace.inputs.request.destination,
        str(workspace.root),
        reason,
    )


def _i4_record_cleanup_failure(
    workspace,
    pair,
    *,
    reason: str,
) -> I4PromotionResult:
    state = _i4_state_copy(pair)
    state["current_stage"] = "success-finalization"
    state["failed_stage"] = "success-finalization"
    state["completed_stages"] = dict(state["completed_stages"])
    state["completed_stages"]["repository-validation"] = "completed"
    state["completed_stages"]["promotion"] = "completed"
    state["completed_stages"].pop("success-finalization", None)
    state["promotion_entered"] = True
    state["promotion_outcome"] = "promoted"
    state["cleanup_failure"] = reason
    _i4_write_state(workspace, state)
    completed = _i4_completed_with(state, "repository-validation", "promotion")
    _i4_write_execution_report(
        workspace,
        promotion_outcome="promoted",
        completion_status="promoted-with-finalization-error",
        failed_stage="success-finalization",
        reason=reason,
        completed_stages=completed,
    )
    return I4PromotionResult(
        "promoted",
        "promoted-with-finalization-error",
        workspace.inputs.request.destination,
        str(workspace.root),
        reason,
    )


def promote_finalized_repository(
    workspace,
    finalized_pair,
    *,
    rename: _I4Callable[[Path, Path], None] | None = None,
    cleanup: _I4Callable[[Path], None] | None = None,
) -> I4PromotionResult:
    if not finalized_pair.promotion_gate_open():
        raise DestinationError("promotion gate is closed")

    repository = workspace.repository_path
    destination = Path(workspace.inputs.request.destination)

    if not repository.is_dir():
        raise DestinationError("staged repository is missing before promotion")

    try:
        i4_recheck_destination_absent(destination)
    except DestinationError as exc:
        return _i4_record_not_promoted(
            workspace,
            finalized_pair,
            reason=str(exc),
        )

    if not _i4_same_filesystem_for_rename(repository, destination):
        return _i4_record_not_promoted(
            workspace,
            finalized_pair,
            reason="cross-device promotion is not supported",
        )

    entered_state = _i4_state_copy(finalized_pair)
    entered_state["current_stage"] = "promotion"
    entered_state["failed_stage"] = None
    entered_state["completed_stages"]["repository-validation"] = "completed"
    entered_state["promotion_entered"] = True
    entered_state["promotion_outcome"] = None
    entered_state["cleanup_failure"] = None
    _i4_write_state(workspace, entered_state)

    # Required immediate absent-only recheck after promotion entry and directly
    # before the single rename operation.
    try:
        i4_recheck_destination_absent(destination)
    except DestinationError as exc:
        return _i4_record_not_promoted(
            workspace,
            finalized_pair,
            reason=str(exc),
        )

    rename_call = rename if rename is not None else os.rename
    try:
        rename_call(repository, destination)
    except BaseException as exc:
        return _i4_record_indeterminate(
            workspace,
            finalized_pair,
            reason=f"atomic rename outcome indeterminate: {type(exc).__name__}: {exc}",
        )

    # A successful rename call is the promotion commit. Confirm the destination
    # is now the repository before reporting success to the caller.
    try:
        destination_stat = destination.stat()
    except OSError as exc:
        return _i4_record_indeterminate(
            workspace,
            finalized_pair,
            reason=f"post-rename destination confirmation failed: {exc}",
        )
    if not stat_module.S_ISDIR(destination_stat.st_mode):
        return _i4_record_indeterminate(
            workspace,
            finalized_pair,
            reason="post-rename destination is not a directory",
        )

    promoted_state = _i4_state_copy(finalized_pair)
    promoted_state["current_stage"] = "success-finalization"
    promoted_state["failed_stage"] = None
    promoted_state["completed_stages"]["repository-validation"] = "completed"
    promoted_state["completed_stages"]["promotion"] = "completed"
    promoted_state["promotion_entered"] = True
    promoted_state["promotion_outcome"] = "promoted"
    promoted_state["cleanup_failure"] = None
    _i4_write_state(workspace, promoted_state)

    cleanup_call = cleanup if cleanup is not None else _i4_shutil.rmtree
    try:
        cleanup_call(workspace.root)
    except BaseException as exc:
        reason = f"post-promotion cleanup failed: {type(exc).__name__}: {exc}"
        return _i4_record_cleanup_failure(
            workspace,
            finalized_pair,
            reason=reason,
        )

    return I4PromotionResult(
        "promoted",
        "success",
        str(destination),
        str(workspace.root),
        None,
    )
