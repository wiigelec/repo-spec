from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
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
)


class StagingError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


STAGING_PREFIX = "repo-spec-stage-"

SUPPORTED_ENTRY_TYPES = {"file", "directory", "symlink"}


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
