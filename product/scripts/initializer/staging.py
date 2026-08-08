from __future__ import annotations

import json
import os
import secrets
import shutil
import sys
import tempfile
import stat as stat_module
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .foundations import (
    FoundationPlan,
    FoundationResult,
    FoundationError,
    build_foundation_plan,
    establish_product_foundations,
)
from .models import (
    InitializerError,
    SourceSelection,
    InventoryEntry,
    ClassifiedInventory,
    InstallationPlan,
    InstallationResult,
    InstallationEntryStatus,
    ImmutableRequest,
    I1DestinationPreflight,
)
from .inventory import ResolvedSourceMaterial


class StagingError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


STAGING_PREFIX = "repo-spec-stage-"
TRANSACTION_RECORD_NAMES = frozenset({
    "staging-state.json",
    "execution-report.json",
    "validation-report.json",
})

SUPPORTED_ENTRY_TYPES = {"file", "directory", "symlink"}


@dataclass(frozen=True)
class I2StagingInputs:
    request: ImmutableRequest
    source: ResolvedSourceMaterial
    destination: I1DestinationPreflight


@dataclass(frozen=True)
class StagingWorkspace:
    root: Path
    root_inode: int
    transaction_path: Path
    repository_path: Path
    staging_state_path: Path
    execution_report_path: Path
    validation_report_path: Path
    inputs: I2StagingInputs

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "i2-staging-established",
            "root": str(self.root),
            "root_inode": self.root_inode,
            "transaction_path": str(self.transaction_path),
            "repository_path": str(self.repository_path),
            "staging_state_path": str(self.staging_state_path),
            "execution_report_path": str(self.execution_report_path),
            "validation_report_path": str(self.validation_report_path),
            "request_fingerprint": self.inputs.request.request_fingerprint,
            "source_repository": self.inputs.source.repository,
            "source_revision": self.inputs.source.commit_id,
            "destination": self.inputs.destination.to_dict(),
        }


def validate_i2_staging_inputs(inputs: I2StagingInputs) -> None:
    request = inputs.request
    source = inputs.source
    destination = inputs.destination
    if destination.decision != "allowed":
        raise StagingError("I1 destination preflight was not allowed")
    if destination.destination_state != "absent":
        raise StagingError("I2 requires an absent destination")
    if not destination.same_filesystem:
        raise StagingError("I1 destination preflight did not establish same-filesystem staging")
    if destination.destination != request.destination:
        raise StagingError("I1 destination fact does not match the canonical request")
    if destination.destination_parent != str(Path(request.destination).parent):
        raise StagingError("I1 destination parent does not match the canonical request")
    if source.repository != request.source_repository:
        raise StagingError("resolved source repository does not match the canonical request")
    if source.commit_id != request.source_revision.object_id:
        raise StagingError("resolved source revision does not match the canonical request")
    if source.direction_material != request.product_direction_material:
        raise StagingError("resolved direction material does not match the canonical request")


def _require_absent_destination(destination: Path) -> None:
    try:
        destination.lstat()
    except FileNotFoundError:
        return
    except OSError as exc:
        raise StagingError(f"destination cannot be rechecked: {exc}") from exc
    raise StagingError("destination no longer absent")


def validate_staging_workspace(workspace: StagingWorkspace) -> None:
    root = workspace.root
    try:
        root_stat = root.lstat()
    except OSError as exc:
        raise StagingError(f"staging root cannot be inspected: {exc}") from exc
    if not stat_module.S_ISDIR(root_stat.st_mode):
        raise StagingError("staging root is not a directory")
    if root_stat.st_ino != workspace.root_inode:
        raise StagingError("staging root identity changed")
    if root_stat.st_dev != workspace.inputs.destination.filesystem_device:
        raise StagingError("staging root is not on the destination filesystem")
    if root.parent != Path(workspace.inputs.destination.destination_parent):
        raise StagingError("staging root is not under the canonical destination parent")
    canonical_transaction = root / "transaction"
    canonical_repository = root / "repository"
    if (
        workspace.transaction_path != canonical_transaction
        or workspace.repository_path != canonical_repository
    ):
        raise StagingError("staging topology paths do not match the canonical layout")
    expected = {canonical_transaction, canonical_repository}
    if set(root.iterdir()) != expected:
        raise StagingError("staging root must contain exactly transaction/ and repository/")
    root_resolved = root.resolve()
    for name, path in (
        ("transaction", workspace.transaction_path),
        ("repository", workspace.repository_path),
    ):
        if path.is_symlink() or not path.is_dir() or path.resolve().parent != root_resolved:
            raise StagingError(f"{name}/ is not a contained staging directory")
    if workspace.transaction_path.resolve() == workspace.repository_path.resolve():
        raise StagingError("transaction/ and repository/ must not alias")
    transaction_entries = list(workspace.transaction_path.iterdir())
    if any(
        path.name not in TRANSACTION_RECORD_NAMES
        or path.is_symlink()
        or not path.is_file()
        for path in transaction_entries
    ):
        raise StagingError("transaction/ contains undeclared content")
    reserved = {
        workspace.staging_state_path,
        workspace.execution_report_path,
        workspace.validation_report_path,
    }
    if reserved != {workspace.transaction_path / name for name in TRANSACTION_RECORD_NAMES}:
        raise StagingError("transaction record paths do not match the canonical layout")
    _require_absent_destination(Path(workspace.inputs.destination.destination))


def establish_staging_workspace(inputs: I2StagingInputs) -> StagingWorkspace:
    validate_i2_staging_inputs(inputs)
    destination = Path(inputs.destination.destination)
    parent = Path(inputs.destination.destination_parent)
    _require_absent_destination(destination)
    try:
        parent_stat = parent.stat()
    except OSError as exc:
        raise StagingError(f"destination parent cannot be inspected: {exc}") from exc
    if not stat_module.S_ISDIR(parent_stat.st_mode):
        raise StagingError("destination parent is not a directory")
    if parent_stat.st_dev != inputs.destination.filesystem_device:
        raise StagingError("destination parent filesystem changed after I1 preflight")

    open_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    try:
        parent_fd = os.open(parent, open_flags)
    except OSError as exc:
        raise StagingError(f"destination parent cannot be opened: {exc}") from exc
    root_fd = -1
    root_name = ""
    root_identity_valid = False
    try:
        opened_parent_stat = os.fstat(parent_fd)
        if (
            opened_parent_stat.st_dev != parent_stat.st_dev
            or opened_parent_stat.st_ino != parent_stat.st_ino
        ):
            raise StagingError("destination parent identity changed after inspection")
        for _attempt in range(100):
            candidate = f"{STAGING_PREFIX}{secrets.token_hex(8)}"
            try:
                os.mkdir(candidate, mode=0o700, dir_fd=parent_fd)
            except FileExistsError:
                continue
            root_name = candidate
            break
        else:
            raise StagingError("unable to allocate a unique staging root")
        root = parent / root_name
        created_root_stat = os.stat(
            root_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        root_fd = os.open(
            root_name,
            open_flags | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        root_stat = os.fstat(root_fd)
        if (
            root_stat.st_dev != created_root_stat.st_dev
            or root_stat.st_ino != created_root_stat.st_ino
        ):
            raise StagingError("staging root identity changed during creation")
        root_identity_valid = True
        if root_stat.st_dev != inputs.destination.filesystem_device:
            raise StagingError("staging root is not on the destination filesystem")
        if os.listdir(root_fd):
            raise StagingError("new staging root was not empty")
        transaction_path = root / "transaction"
        repository_path = root / "repository"
        os.mkdir("transaction", dir_fd=root_fd)
        os.mkdir("repository", dir_fd=root_fd)
        if set(os.listdir(root_fd)) != {"transaction", "repository"}:
            raise StagingError("staging root topology changed during establishment")
        current_parent_stat = parent.stat()
        if (
            current_parent_stat.st_dev != opened_parent_stat.st_dev
            or current_parent_stat.st_ino != opened_parent_stat.st_ino
        ):
            raise StagingError("destination parent identity changed during establishment")
        workspace = StagingWorkspace(
            root=root,
            root_inode=root_stat.st_ino,
            transaction_path=transaction_path,
            repository_path=repository_path,
            staging_state_path=transaction_path / "staging-state.json",
            execution_report_path=transaction_path / "execution-report.json",
            validation_report_path=transaction_path / "validation-report.json",
            inputs=inputs,
        )
        validate_staging_workspace(workspace)
        return workspace
    except BaseException:
        if root_identity_valid:
            for child in ("transaction", "repository"):
                try:
                    os.rmdir(child, dir_fd=root_fd)
                except OSError:
                    pass
            try:
                os.rmdir(root_name, dir_fd=parent_fd)
            except OSError:
                pass
        raise
    finally:
        if root_fd >= 0:
            os.close(root_fd)
        os.close(parent_fd)


def resolve_source_root(source_revision: str, inventory_repo_root: Path) -> Path:
    return inventory_repo_root.resolve()


def build_installation_plan(
    classified: ClassifiedInventory,
) -> InstallationPlan:
    return InstallationPlan(classified)


def validate_source_path(
    source_root: Path,
    entry_path: str,
    entry: InventoryEntry,
) -> None:
    if not entry_path.strip():
        raise StagingError(f"empty path for inventory entry: {entry.path!r}")

    if entry_path.startswith("/"):
        raise StagingError(
            f"absolute source path not allowed: {entry_path!r} (entry: {entry.path!r})"
        )

    norm_parts = entry_path.replace("\\", "/").split("/")
    if ".." in norm_parts:
        raise StagingError(
            f"parent-directory traversal in source path: {entry_path!r} (entry: {entry.path!r})"
        )

    resolved = (source_root / entry_path).resolve()

    try:
        resolved.relative_to(source_root)
    except ValueError:
        raise StagingError(
            f"source path escapes source root: {entry_path!r} (entry: {entry.path!r})"
        )

    if not resolved.exists():
        raise StagingError(
            f"source path does not exist: {entry_path!r} (entry: {entry.path!r})"
        )


def resolve_entry_type(source_root: Path, entry_path: str) -> str:
    full_path = source_root / entry_path
    if full_path.is_symlink():
        return "symlink"
    resolved = full_path.resolve()
    if resolved.is_file():
        return "file"
    if resolved.is_dir():
        return "directory"
    return "unknown"


def check_symlink_safety(source_root: Path, entry_path: str) -> str:
    full_path = source_root / entry_path
    if not full_path.is_symlink():
        return ""
    link_target = os.readlink(str(full_path))
    if link_target.startswith("/"):
        raise StagingError(
            f"absolute symlink target rejects portability: {entry_path!r} -> {link_target!r}"
        )
    linked_resolved = (full_path.parent / link_target).resolve()
    try:
        linked_resolved.relative_to(source_root)
    except ValueError:
        raise StagingError(
            f"symlink escapes source root: {entry_path!r} -> {link_target!r}"
        )
    return link_target


def check_destination_conflicts(
    staging_root: Path,
    entries: list[InventoryEntry],
) -> None:
    seen: dict[str, str] = {}
    for entry in entries:
        dest_path = staging_root / entry.path
        dest_str = str(dest_path)
        if dest_str in seen:
            raise StagingError(
                f"conflicting destination path: {entry.path!r} "
                f"(conflicts with entry at path {seen[dest_str]!r})"
            )
        seen[dest_str] = entry.path

        for other_path, other_entry_path in list(seen.items()):
            if other_path == dest_str:
                continue
            other_key = other_path.rstrip("/")
            dest_key = dest_str.rstrip("/")
            if dest_key.startswith(other_key + "/"):
                raise StagingError(
                    f"destination path overlap: {entry.path!r} "
                    f"nests within {other_entry_path!r}"
                )
            if other_key.startswith(dest_key + "/"):
                raise StagingError(
                    f"destination path overlap: {entry.path!r} "
                    f"is ancestor of {other_entry_path!r}"
                )


def check_preexisting_workspace(staging_root: Path) -> None:
    if staging_root.exists():
        contents = list(staging_root.iterdir())
        if contents:
            raise StagingError(
                f"preexisting nonempty staging workspace: {staging_root}"
            )


def create_staging_workspace(
    parent_dir: Path | None = None,
) -> Path:
    if parent_dir is not None:
        parent_dir.mkdir(parents=True, exist_ok=True)
        return Path(tempfile.mkdtemp(prefix=STAGING_PREFIX, dir=str(parent_dir)))
    return Path(tempfile.mkdtemp(prefix=STAGING_PREFIX))


def copy_entry(
    source_root: Path,
    entry: InventoryEntry,
    staging_root: Path,
) -> None:
    src_path = source_root / entry.path
    dst_path = staging_root / entry.path
    dst_path.parent.mkdir(parents=True, exist_ok=True)

    if src_path.is_symlink():
        link_target = os.readlink(str(src_path))
        dst_path.symlink_to(link_target)
    elif src_path.is_file():
        shutil.copy2(str(src_path), str(dst_path))
    elif src_path.is_dir():
        dst_path.mkdir(parents=True, exist_ok=True)
        for item in src_path.iterdir():
            _copy_recursive(item, dst_path / item.name, source_root, staging_root)
    else:
        raise StagingError(
            f"unsupported source entry type: {entry.path!r}"
        )


def _copy_recursive(
    src: Path,
    dst: Path,
    source_root: Path,
    staging_root: Path,
) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_symlink():
        try:
            resolved = src.resolve()
            resolved.relative_to(source_root)
        except ValueError:
            raise StagingError(
                f"symlink escapes source root during recursive copy: {str(src)}"
            )
        link_target = os.readlink(str(src))
        dst.symlink_to(link_target)
    elif src.is_file():
        shutil.copy2(str(src), str(dst))
    elif src.is_dir():
        dst.mkdir(parents=True, exist_ok=True)
        for item in src.iterdir():
            _copy_recursive(item, dst / item.name, source_root, staging_root)


def stage_framework(
    classified: ClassifiedInventory,
    source_selection: SourceSelection | None,
    source_root: Path,
    staging_parent: Path | None = None,
) -> InstallationResult:
    plan = build_installation_plan(classified)
    entries = list(plan.entries)

    installed: list[dict[str, Any]] = []
    skipped: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    staging_root = create_staging_workspace(staging_parent)
    staging_root_str = str(staging_root)

    try:
        check_destination_conflicts(staging_root, entries)

        for entry in entries:
            entry_path = entry.path
            rejection = None

            if not entry.installable:
                rejection = "entry not installable per inventory classification"
            else:
                try:
                    validate_source_path(source_root, entry_path, entry)
                except StagingError as exc:
                    rejection = str(exc)

            if rejection is not None:
                rejected.append({
                    "path": entry.path,
                    "classification": entry.classification,
                    "reason": rejection,
                })
                continue

            entry_type = resolve_entry_type(source_root, entry_path)

            if entry_type not in SUPPORTED_ENTRY_TYPES:
                rejected.append({
                    "path": entry.path,
                    "classification": entry.classification,
                    "reason": f"unsupported source entry type: {entry_type}",
                })
                continue

            if entry_type == "symlink":
                try:
                    check_symlink_safety(source_root, entry_path)
                except StagingError as exc:
                    rejected.append({
                        "path": entry.path,
                        "classification": entry.classification,
                        "reason": str(exc),
                    })
                    continue

            try:
                copy_entry(source_root, entry, staging_root)
                installed.append({
                    "path": entry.path,
                    "classification": entry.classification,
                    "type": entry_type,
                })
            except StagingError as exc:
                rejected.append({
                    "path": entry.path,
                    "classification": entry.classification,
                    "reason": str(exc),
                })

    except BaseException:
        _cleanup_staging(staging_root)
        raise

    return InstallationResult(
        source_selection=source_selection,
        staging_workspace=staging_root_str,
        installed=installed,
        skipped=skipped,
        rejected=rejected,
    )


def stage_framework_and_foundations(
    classified: ClassifiedInventory,
    source_selection: SourceSelection | None,
    source_root: Path,
    foundation_plan: FoundationPlan | None = None,
    staging_parent: Path | None = None,
) -> tuple[InstallationResult, FoundationResult | None]:
    staging_result = stage_framework(
        classified=classified,
        source_selection=source_selection,
        source_root=source_root,
        staging_parent=staging_parent,
    )

    if foundation_plan is None:
        return staging_result, None

    staging_root = Path(staging_result.staging_workspace).resolve()
    try:
        foundation_result = establish_product_foundations(
            plan=foundation_plan,
            staging_root=staging_root,
        )
    except FoundationError:
        _cleanup_staging(staging_root)
        raise

    return staging_result, foundation_result


def _cleanup_staging(staging_root: Path) -> None:
    try:
        if staging_root.exists():
            shutil.rmtree(staging_root)
    except OSError:
        pass
