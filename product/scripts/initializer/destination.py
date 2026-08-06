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
