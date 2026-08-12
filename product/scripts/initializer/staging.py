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
    if not source.repository or not source.commit_id:
        raise StagingError("resolved executing-framework provenance is incomplete")
    if source.direction_material:
        raise StagingError("repository bootstrap must not carry product direction material")


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

# BEGIN I2 PATCH 2 GOVERNED MATERIAL REALIZATION

@dataclass(frozen=True)
class I2RealizationResult:
    workspace: StagingWorkspace
    framework_paths: tuple[str, ...]
    foundation_paths: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "i2-material-realization-complete",
            "workspace": self.workspace.to_dict(),
            "framework_paths": list(self.framework_paths),
            "foundation_paths": list(self.foundation_paths),
        }


def _i2_validate_repo_relative_output(path: str) -> None:
    if not path or path.startswith("/") or "\x00" in path:
        raise StagingError(f"invalid output path: {path!r}")
    parts = path.replace("\\", "/").split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise StagingError(f"non-canonical output path: {path!r}")
    if parts[0] == ".git":
        raise StagingError("Git administrative state is not authorized in I2")


def _i2_matches_prohibited(path: str, rules: list[dict[str, object]]) -> bool:
    normalized = path.rstrip("/")
    for rule in rules:
        kind = rule.get("rule")
        raw = rule.get("path")
        if not isinstance(raw, str):
            raise StagingError("invalid prohibited_path rule")
        target = raw.rstrip("/")
        if kind == "exact" and normalized == target:
            return True
        if kind == "prefix" and (
            normalized == target or normalized.startswith(target + "/")
        ):
            return True
        if kind not in {"exact", "prefix"}:
            raise StagingError(f"unknown prohibited_path rule: {kind!r}")
    return False


def _i2_source_blob(
    source: ResolvedSourceMaterial,
    entry: MaterialEntry,
) -> bytes:
    from .inventory import _read_commit_blob, _tree_entry

    mode, object_type = _tree_entry(
        source.repository,
        source.commit_id,
        entry.source_path,
    )
    if object_type != "blob":
        raise StagingError(
            f"material source must resolve to one Git blob: {entry.material_key}"
        )
    if entry.source_type == "blob":
        if mode not in {"100644", "100755"} or mode != entry.mode:
            raise StagingError(f"material source mode mismatch: {entry.material_key}")
    elif entry.source_type == "symlink":
        if mode != "120000" or entry.mode != "120000":
            raise StagingError(f"symlink mode mismatch: {entry.material_key}")
    else:
        raise StagingError(
            f"unsupported material source_type {entry.source_type!r}: {entry.material_key}"
        )
    return _read_commit_blob(
        source.repository,
        source.commit_id,
        entry.source_path,
    )


def _i2_prepare_framework_outputs(
    source: ResolvedSourceMaterial,
    output_inventory: dict[str, Any],
) -> list[tuple[str, MaterialEntry, bytes]]:
    material_index = output_inventory.get("material_index")
    prohibited = output_inventory.get("prohibited_paths")
    if not isinstance(material_index, list) or not material_index:
        raise StagingError("output inventory material_index must be a non-empty array")
    if not isinstance(prohibited, list):
        raise StagingError("output inventory prohibited_paths must be an array")

    manifest_by_key = {entry.material_key: entry for entry in source.manifest}
    if len(manifest_by_key) != len(source.manifest):
        raise StagingError("material manifest contains duplicate material_key values")

    index_by_key: dict[str, dict[str, Any]] = {}
    destinations: set[str] = set()
    for raw in material_index:
        if not isinstance(raw, dict):
            raise StagingError("invalid material_index entry")
        key = raw.get("material_key")
        destination = raw.get("destination_path")
        if not isinstance(key, str) or not isinstance(destination, str):
            raise StagingError("material_index key/path must be strings")
        if key in index_by_key:
            raise StagingError(f"duplicate output material_key: {key}")
        if destination in destinations:
            raise StagingError(f"duplicate framework destination_path: {destination}")
        index_by_key[key] = raw
        destinations.add(destination)

    if set(index_by_key) != set(manifest_by_key):
        raise StagingError("closed material inventory does not reconcile")

    prepared: list[tuple[str, MaterialEntry, bytes]] = []
    for entry in source.manifest:
        raw = index_by_key[entry.material_key]
        if raw.get("producer") != "framework-installation":
            raise StagingError(f"producer mismatch: {entry.material_key}")
        if raw.get("required") is not True:
            raise StagingError(f"V1 material must be required: {entry.material_key}")
        if raw.get("role") == "development-only":
            raise StagingError("development-only material is not installable")
        if raw.get("role") != entry.role:
            raise StagingError(f"role mismatch: {entry.material_key}")
        if raw.get("operation") != entry.operation:
            raise StagingError(f"operation mismatch: {entry.material_key}")
        if raw.get("mode") != entry.mode:
            raise StagingError(f"mode mismatch: {entry.material_key}")
        if entry.operation not in {"copy-verbatim", "instantiate-template"}:
            raise StagingError(
                f"accepted V1 closed framework inventory operation is unsupported: "
                f"{entry.operation!r}"
            )
        if entry.source_type == "tree":
            raise StagingError(
                f"tree-valued framework material is prohibited: {entry.material_key}"
            )

        destination = raw["destination_path"]
        _i2_validate_repo_relative_output(destination)
        if _i2_matches_prohibited(destination, prohibited):
            raise StagingError(f"framework output is prohibited: {destination}")
        prepared.append((destination, entry, _i2_source_blob(source, entry)))
    return prepared


def _i2_expected_foundation_paths(plan: FoundationPlan) -> set[str]:
    product_id = plan.product_id
    paths = {
        "product/docs/direction/manifest.json",
        f"product/docs/overview/{product_id}-OVERVIEW.md",
        f"product/docs/decompositions/{product_id}-DECOMPOSITION.md",
        f"product/docs/plans/{product_id}-IMPLEMENTATION-PLAN.md",
        "repo/docs/overview/README.md",
        "repo/docs/decompositions/README.md",
        "repo/docs/plans/README.md",
        "product/specs/product/README.md",
        "product/specs/product/manifest.json",
        "product/specs/product/level-0/README.md",
        "product/specs/product/level-1/README.md",
        "product/specs/product/level-2/README.md",
        "product/specs/product/level-3/README.md",
    }
    for index, source_path in enumerate(plan.direction_material):
        paths.add(
            f"product/docs/direction/evidence/{index:03d}-{Path(source_path).name}"
        )
    for filename in (
        "chunk-01-identity-and-purpose.md",
        "chunk-02-problem-and-outcome.md",
        "chunk-03-users-principles-boundaries.md",
        "chunk-04-capabilities-and-success.md",
        "chunk-05-unresolved-questions.md",
        "chunk-06-lifecycle-and-handoff.md",
    ):
        paths.add(f"product/docs/overview/{product_id}-overview/{filename}")
    for filename in (
        "chunk-01-invocation-and-authority.md",
        "chunk-02-product-areas.md",
        "chunk-03-cross-cutting-concerns.md",
        "chunk-04-stopping-criteria-and-handoff.md",
    ):
        paths.add(f"product/docs/decompositions/{product_id}-decomposition/{filename}")
    for filename in (
        "chunk-01-scope-and-preconditions.md",
        "chunk-02-workstreams-and-dependencies.md",
        "chunk-03-validation-and-completion.md",
        "chunk-04-risks-and-unresolved-decisions.md",
    ):
        paths.add(f"product/docs/plans/{product_id}-implementation-plan/{filename}")
    return paths


def _i2_validate_foundation_inventory(
    plan: FoundationPlan,
    files: dict[str, bytes],
    output_inventory: dict[str, Any],
) -> None:
    expected = _i2_expected_foundation_paths(plan)
    if set(files) != expected:
        raise StagingError("foundation deterministic path set mismatch")

    prohibited = output_inventory.get("prohibited_paths")
    fixed = output_inventory.get("fixed_worktree_files")
    families = output_inventory.get("dynamic_path_families")
    if not isinstance(prohibited, list):
        raise StagingError("output inventory prohibited_paths must be an array")
    if not isinstance(fixed, list):
        raise StagingError("output inventory fixed_worktree_files must be an array")
    if not isinstance(families, list):
        raise StagingError("output inventory dynamic_path_families must be an array")

    producers = {"direction-evidence-installation", "workspace-seeding"}
    required_fixed = {
        item.get("destination_path")
        for item in fixed
        if isinstance(item, dict)
        and item.get("producer") in producers
        and item.get("required") is True
    }
    if {path for path in expected if path in required_fixed} != required_fixed:
        raise StagingError("required fixed foundation outputs do not reconcile")

    family_producers = [
        item.get("producer")
        for item in families
        if isinstance(item, dict)
        and item.get("required") is True
        and item.get("governing_spec") == "product.foundation-seeding"
    ]
    if family_producers.count("direction-evidence-installation") != 1:
        raise StagingError("direction-evidence dynamic family is not unique")
    if family_producers.count("workspace-seeding") != 4:
        raise StagingError("workspace-seeding dynamic families do not reconcile")

    for path in expected:
        _i2_validate_repo_relative_output(path)
        if _i2_matches_prohibited(path, prohibited):
            raise StagingError(f"foundation output is prohibited: {path}")


def _i2_clear_repository_contents(repository: Path) -> None:
    if not repository.is_dir() or repository.is_symlink():
        return
    for child in list(repository.iterdir()):
        if child.is_symlink() or child.is_file():
            child.unlink(missing_ok=True)
        else:
            shutil.rmtree(child)


def realize_i2_materials(
    workspace: StagingWorkspace,
    foundation_plan: FoundationPlan | None = None,
) -> I2RealizationResult:
    validate_staging_workspace(workspace)
    repository = workspace.repository_path
    if any(repository.iterdir()):
        raise StagingError("framework realization requires an empty repository/ workspace")
    if foundation_plan is not None:
        raise StagingError("repository bootstrap does not accept a product foundation plan")

    source = workspace.inputs.source
    from .inventory import _load_json_blob, OUTPUT_INVENTORY_SPEC_PATH

    output_inventory = _load_json_blob(
        source.repository,
        source.commit_id,
        OUTPUT_INVENTORY_SPEC_PATH,
    )
    prepared = _i2_prepare_framework_outputs(source, output_inventory)
    framework_paths = [path for path, _entry, _data in prepared]

    try:
        for destination, entry, data in prepared:
            target = repository / destination
            target.parent.mkdir(parents=True, exist_ok=True)
            if entry.source_type == "symlink":
                link_target = data.decode("utf-8")
                if not link_target or "\x00" in link_target or Path(link_target).is_absolute():
                    raise StagingError(f"unsafe symlink target: {entry.material_key}")
                candidate = (target.parent / link_target).resolve(strict=False)
                try:
                    candidate.relative_to(repository.resolve())
                except ValueError as exc:
                    raise StagingError(
                        f"symlink target escapes repository/: {entry.material_key}"
                    ) from exc
                target.symlink_to(link_target)
            else:
                target.write_bytes(data)
                os.chmod(target, 0o755 if entry.mode == "100755" else 0o644)

        if (repository / ".git").exists():
            raise StagingError("Git state appeared during framework realization")
        validate_staging_workspace(workspace)
    except BaseException:
        _i2_clear_repository_contents(repository)
        raise

    return I2RealizationResult(
        workspace=workspace,
        framework_paths=tuple(framework_paths),
        foundation_paths=(),
    )

# END I2 PATCH 2 GOVERNED MATERIAL REALIZATION
# END I2 PATCH 2 GOVERNED MATERIAL REALIZATION

# BEGIN I2 PATCH 3 DETERMINISTIC EXIT

@dataclass(frozen=True)
class I2RepositoryEntry:
    path: str
    entry_type: str
    executable: bool | None
    byte_length: int | None
    content_sha256: str | None
    symlink_target: str | None

    def to_dict(self) -> dict[str, object]:
        value: dict[str, object] = {"path": self.path, "type": self.entry_type}
        if self.executable is not None:
            value["executable"] = self.executable
        if self.byte_length is not None:
            value["byte_length"] = self.byte_length
        if self.content_sha256 is not None:
            value["content_sha256"] = self.content_sha256
        if self.symlink_target is not None:
            value["symlink_target"] = self.symlink_target
        return value


@dataclass(frozen=True)
class I2RepositoryDigest:
    algorithm: str
    digest: str
    entry_count: int
    canonical_input_byte_length: int

    def to_dict(self) -> dict[str, object]:
        return {
            "algorithm": self.algorithm,
            "digest": self.digest,
            "entry_count": self.entry_count,
            "canonical_input_byte_length": self.canonical_input_byte_length,
        }


@dataclass(frozen=True)
class I2ExitState:
    realization: I2RealizationResult
    repository_entries: tuple[I2RepositoryEntry, ...]
    repository_digest: I2RepositoryDigest

    def to_dict(self) -> dict[str, object]:
        return {
            "status": "i2-exit-ready",
            "realization": self.realization.to_dict(),
            "repository_entries": [e.to_dict() for e in self.repository_entries],
            "repository_digest": self.repository_digest.to_dict(),
            "successor_increment": "I3",
            "successor_authorized": False,
        }


def _i2_frame_part(value: bytes) -> bytes:
    return len(value).to_bytes(8, "big") + value


def enumerate_i2_repository(repository: Path) -> tuple[I2RepositoryEntry, ...]:
    import hashlib

    root = repository.resolve()
    if not root.is_dir() or repository.is_symlink():
        raise StagingError("candidate repository/ is not a real directory")

    entries: list[I2RepositoryEntry] = []
    for path in sorted(
        repository.rglob("*"),
        key=lambda item: item.relative_to(repository).as_posix(),
    ):
        relative = path.relative_to(repository).as_posix()
        _i2_validate_repo_relative_output(relative)
        if relative == ".git" or relative.startswith(".git/"):
            raise StagingError("Git administrative state is not part of I2 repository content")
        try:
            st = path.lstat()
        except OSError as exc:
            raise StagingError(
                f"cannot stat candidate repository path {relative}: {exc}"
            ) from exc

        if stat_module.S_ISLNK(st.st_mode):
            target = os.readlink(path)
            target_bytes = target.encode("utf-8", "strict")
            entries.append(I2RepositoryEntry(
                path=relative,
                entry_type="symlink",
                executable=None,
                byte_length=len(target_bytes),
                content_sha256=hashlib.sha256(target_bytes).hexdigest(),
                symlink_target=target,
            ))
        elif stat_module.S_ISDIR(st.st_mode):
            entries.append(I2RepositoryEntry(
                path=relative + "/",
                entry_type="directory",
                executable=None,
                byte_length=None,
                content_sha256=None,
                symlink_target=None,
            ))
        elif stat_module.S_ISREG(st.st_mode):
            raw = path.read_bytes()
            entries.append(I2RepositoryEntry(
                path=relative,
                entry_type="regular-file",
                executable=bool(st.st_mode & 0o111),
                byte_length=len(raw),
                content_sha256=hashlib.sha256(raw).hexdigest(),
                symlink_target=None,
            ))
        else:
            raise StagingError(
                f"unsupported filesystem object in candidate repository: {relative}"
            )
    return tuple(entries)


def i2_repository_digest_input(
    repository: Path,
) -> tuple[bytes, tuple[I2RepositoryEntry, ...]]:
    entries = enumerate_i2_repository(repository)
    framed = bytearray(b"repo-spec-i2-repository-content-v1\\0")
    for entry in entries:
        framed.extend(_i2_frame_part(entry.path.encode("utf-8", "strict")))
        framed.extend(_i2_frame_part(entry.entry_type.encode("ascii")))
        actual = repository / entry.path.rstrip("/")
        if entry.entry_type == "directory":
            framed.extend(_i2_frame_part(b""))
            framed.extend(_i2_frame_part(b""))
        elif entry.entry_type == "symlink":
            target = os.readlink(actual).encode("utf-8", "strict")
            framed.extend(_i2_frame_part(b""))
            framed.extend(_i2_frame_part(target))
        else:
            mode = b"x" if entry.executable else b"-"
            framed.extend(_i2_frame_part(mode))
            framed.extend(_i2_frame_part(actual.read_bytes()))
    return bytes(framed), entries


def build_i2_exit_state(realization: I2RealizationResult) -> I2ExitState:
    import hashlib

    workspace = realization.workspace
    validate_staging_workspace(workspace)
    repository = workspace.repository_path
    digest_input, entries = i2_repository_digest_input(repository)

    observed_leaf_paths = {
        entry.path for entry in entries if entry.entry_type != "directory"
    }
    expected_leaf_paths = set(realization.framework_paths) | set(realization.foundation_paths)
    if observed_leaf_paths != expected_leaf_paths:
        missing = sorted(expected_leaf_paths - observed_leaf_paths)
        undeclared = sorted(observed_leaf_paths - expected_leaf_paths)
        raise StagingError(
            f"candidate repository inventory mismatch: missing={missing}, undeclared={undeclared}"
        )

    return I2ExitState(
        realization=realization,
        repository_entries=entries,
        repository_digest=I2RepositoryDigest(
            algorithm="sha256",
            digest=hashlib.sha256(digest_input).hexdigest(),
            entry_count=len(entries),
            canonical_input_byte_length=len(digest_input),
        ),
    )

# END I2 PATCH 3 DETERMINISTIC EXIT

# I4 PATCH 2: REPORT FINALIZATION
#
# Implements staging-state/execution-report contracts and ordered
# validation-report/staging-state finalization. Promotion remains Patch 3.

import os as _i4_os
from collections.abc import Callable as _I4Callable
from dataclasses import dataclass as _i4_dataclass

# Patch 1 validation imports staging, so Patch 2 must not import validation
# at module initialization time. Validation helpers are resolved lazily below.

_I4_STAGING_STATE_FIELDS = (
    "schema_version", "request_fingerprint", "source_revision",
    "source_repository", "initializer_version", "expected_destination",
    "current_stage", "completed_stages", "failed_stage",
    "repository_content_digest", "git_created", "validation_completed",
    "validation_overall_status", "promotion_entered", "promotion_outcome",
    "cleanup_failure",
)
_I4_EXECUTION_REPORT_FIELDS = (
    "schema_version", "request_fingerprint", "staging_root",
    "expected_destination", "promotion_outcome", "completion_status", "stages",
)
_I4_EXECUTION_STAGE_FIELDS = ("id", "status", "warnings", "errors")
_I4_STAGE_STATUSES = frozenset({"completed", "skipped", "deferred", "failed"})
_I4_PROMOTION_OUTCOMES = frozenset({"not-promoted", "promoted", "indeterminate"})
_I4_COMPLETION_STATUSES = frozenset({"failed", "promoted-with-finalization-error"})
_I4_CANONICAL_STAGES = (
    "request-intake", "source-resolution", "destination-preflight",
    "staging-establishment", "framework-installation",
    "direction-evidence-installation", "workspace-seeding",
    "provenance-recording", "handoff-assembly", "git-initialization",
    "repository-validation", "promotion", "success-finalization",
)

class ReportFinalizationError(StagingError):
    def __init__(self, failure_code: str, message: str) -> None:
        self.failure_code = failure_code
        super().__init__(message)

@_i4_dataclass(frozen=True)
class FinalizedValidationPair:
    validation_report: dict[str, object]
    staging_state: dict[str, object]

    def promotion_gate_open(self) -> bool:
        return (
            self.validation_report.get("overall_status") == "pass"
            and self.staging_state.get("validation_completed") is True
            and self.staging_state.get("validation_overall_status") == "pass"
            and self.staging_state.get("promotion_entered") is False
            and self.staging_state.get("promotion_outcome") is None
            and self.validation_report.get("request_fingerprint")
                == self.staging_state.get("request_fingerprint")
            and self.validation_report.get("repository_content_digest")
                == self.staging_state.get("repository_content_digest")
        )

def _i4_atomic_write(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    fd = -1
    try:
        fd = _i4_os.open(
            temp,
            _i4_os.O_WRONLY | _i4_os.O_CREAT | _i4_os.O_EXCL,
            0o600,
        )
        offset = 0
        while offset < len(payload):
            count = _i4_os.write(fd, payload[offset:])
            if count <= 0:
                raise OSError("short write")
            offset += count
        _i4_os.fsync(fd)
        _i4_os.close(fd)
        fd = -1
        _i4_os.replace(temp, path)
        dir_fd = _i4_os.open(
            path.parent,
            _i4_os.O_RDONLY | getattr(_i4_os, "O_DIRECTORY", 0),
        )
        try:
            _i4_os.fsync(dir_fd)
        finally:
            _i4_os.close(dir_fd)
    finally:
        if fd >= 0:
            _i4_os.close(fd)
        try:
            temp.unlink()
        except FileNotFoundError:
            pass

def _i4_json_bytes(value: dict[str, object]) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

def _i4_validate_sha256(value: object, context: str) -> None:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(ch not in "0123456789abcdef" for ch in value)
    ):
        raise ReportFinalizationError(
            "staging-state-invalid-schema",
            f"{context} must be 64 lowercase hex characters",
        )

def validate_staging_state_v1(state: dict[str, object]) -> None:
    if tuple(state) != _I4_STAGING_STATE_FIELDS:
        raise ReportFinalizationError(
            "staging-state-invalid-schema",
            "staging-state field closure/order is invalid",
        )
    if state["schema_version"] != "1":
        raise ReportFinalizationError(
            "staging-state-invalid-schema",
            "staging-state schema_version must be 1",
        )
    _i4_validate_sha256(state["request_fingerprint"], "request_fingerprint")
    revision = state["source_revision"]
    if (
        not isinstance(revision, dict)
        or tuple(revision) != ("object_format", "object_id")
        or revision.get("object_format") != "sha1"
        or not isinstance(revision.get("object_id"), str)
        or len(revision["object_id"]) != 40
    ):
        raise ReportFinalizationError(
            "staging-state-invalid-schema", "source_revision is invalid"
        )
    for key in (
        "source_repository", "initializer_version", "expected_destination",
        "current_stage", "repository_content_digest",
    ):
        if not isinstance(state[key], str) or not state[key]:
            raise ReportFinalizationError(
                "staging-state-invalid-schema", f"{key} must be non-empty"
            )
    _i4_validate_sha256(state["repository_content_digest"], "repository_content_digest")
    if state["current_stage"] not in _I4_CANONICAL_STAGES:
        raise ReportFinalizationError(
            "staging-state-invalid-schema", "current_stage is not canonical"
        )
    completed = state["completed_stages"]
    if not isinstance(completed, dict):
        raise ReportFinalizationError(
            "staging-state-invalid-schema", "completed_stages must be an object"
        )
    for stage, status in completed.items():
        if stage not in _I4_CANONICAL_STAGES or status != "completed":
            raise ReportFinalizationError(
                "staging-state-invalid-schema",
                "completed_stages contains an invalid entry",
            )
    failed = state["failed_stage"]
    if failed is not None and failed not in _I4_CANONICAL_STAGES:
        raise ReportFinalizationError(
            "staging-state-invalid-schema", "failed_stage is invalid"
        )
    for key in ("git_created", "validation_completed", "promotion_entered"):
        if not isinstance(state[key], bool):
            raise ReportFinalizationError(
                "staging-state-invalid-schema", f"{key} must be boolean"
            )
    if state["validation_overall_status"] not in {None, "pass", "fail"}:
        raise ReportFinalizationError(
            "staging-state-invalid-schema",
            "validation_overall_status is invalid",
        )
    if state["promotion_outcome"] not in {
        None, "not-promoted", "promoted", "indeterminate"
    }:
        raise ReportFinalizationError(
            "staging-state-invalid-schema", "promotion_outcome is invalid"
        )
    cleanup = state["cleanup_failure"]
    if cleanup is not None and (not isinstance(cleanup, str) or not cleanup):
        raise ReportFinalizationError(
            "staging-state-invalid-schema", "cleanup_failure is invalid"
        )

def staging_state_bytes_v1(state: dict[str, object]) -> bytes:
    validate_staging_state_v1(state)
    return _i4_json_bytes(state)

def build_validated_staging_state(
    workspace: StagingWorkspace,
    validation_run: object,
    *,
    initializer_version: str,
    completed_stages: tuple[str, ...],
) -> dict[str, object]:
    completed = {
        stage: "completed"
        for stage in _I4_CANONICAL_STAGES
        if stage in completed_stages
    }
    state: dict[str, object] = {
        "schema_version": "1",
        "request_fingerprint": workspace.inputs.request.request_fingerprint,
        "source_revision": {"object_format": "sha1", "object_id": workspace.inputs.source.commit_id},
        "source_repository": workspace.inputs.source.repository,
        "initializer_version": initializer_version,
        "expected_destination": workspace.inputs.request.destination,
        "current_stage": "repository-validation",
        "completed_stages": completed,
        "failed_stage": None,
        "repository_content_digest": validation_run.repository_content_digest,
        "git_created": True,
        "validation_completed": True,
        "validation_overall_status": validation_run.overall_status,
        "promotion_entered": False,
        "promotion_outcome": None,
        "cleanup_failure": None,
    }
    validate_staging_state_v1(state)
    if state["request_fingerprint"] != validation_run.request_fingerprint:
        raise ReportFinalizationError(
            "staging-state-fingerprint-mismatch",
            "staging-state/request fingerprint mismatch",
        )
    if state["repository_content_digest"] != validation_run.repository_content_digest:
        raise ReportFinalizationError(
            "staging-state-digest-mismatch",
            "staging-state/report digest mismatch",
        )
    return state

def _i4_fault(
    fault_injector: _I4Callable[[str], None] | None,
    point: str,
) -> None:
    if fault_injector is not None:
        fault_injector(point)

def _i4_validate_report(
    report: dict[str, object],
    *,
    expected_request_fingerprint: str,
    expected_repository_content_digest: str,
) -> None:
    from .validation import (
        ValidationError as _I4ValidationError,
        validate_validation_report_v1 as _validate_validation_report_v1,
    )
    try:
        _validate_validation_report_v1(
            report,
            expected_request_fingerprint=expected_request_fingerprint,
            expected_repository_content_digest=expected_repository_content_digest,
        )
    except _I4ValidationError as exc:
        raise ReportFinalizationError(
            "validation-report-invalid-schema",
            str(exc),
        ) from exc

def finalize_validation_records(
    workspace: StagingWorkspace,
    validation_run: object,
    *,
    initializer_version: str,
    completed_stages: tuple[str, ...],
    fault_injector: _I4Callable[[str], None] | None = None,
) -> FinalizedValidationPair:
    report = validation_run.report_dict()
    state = build_validated_staging_state(
        workspace,
        validation_run,
        initializer_version=initializer_version,
        completed_stages=completed_stages,
    )
    _i4_fault(fault_injector, "after-in-memory-construction")
    validate_staging_state_v1(state)
    _i4_fault(fault_injector, "after-staging-state-validation")
    _i4_validate_report(
        report,
        expected_request_fingerprint=workspace.inputs.request.request_fingerprint,
        expected_repository_content_digest=validation_run.repository_content_digest,
    )
    _i4_fault(fault_injector, "after-validation-report-validation")
    _i4_fault(fault_injector, "before-validation-report-write")
    _i4_atomic_write(workspace.validation_report_path, validation_run.report_bytes())
    _i4_fault(fault_injector, "after-validation-report-write")
    _i4_fault(fault_injector, "before-staging-state-write")
    _i4_atomic_write(workspace.staging_state_path, staging_state_bytes_v1(state))
    _i4_fault(fault_injector, "after-staging-state-write")

    durable_report = json.loads(
        workspace.validation_report_path.read_text(encoding="utf-8")
    )
    durable_state = json.loads(
        workspace.staging_state_path.read_text(encoding="utf-8")
    )
    _i4_validate_report(
        durable_report,
        expected_request_fingerprint=workspace.inputs.request.request_fingerprint,
        expected_repository_content_digest=validation_run.repository_content_digest,
    )
    validate_staging_state_v1(durable_state)
    if durable_report["request_fingerprint"] != durable_state["request_fingerprint"]:
        raise ReportFinalizationError(
            "staging-state-fingerprint-mismatch",
            "durable records disagree on request fingerprint",
        )
    if (
        durable_report["repository_content_digest"]
        != durable_state["repository_content_digest"]
    ):
        raise ReportFinalizationError(
            "staging-state-digest-mismatch",
            "durable records disagree on repository digest",
        )
    if (
        durable_state["validation_completed"] is not True
        or durable_state["validation_overall_status"]
        != durable_report["overall_status"]
    ):
        raise ReportFinalizationError(
            "staging-state-validation-status-mismatch",
            "durable records disagree on validation result",
        )
    _i4_fault(fault_injector, "after-durable-consistency-verification")
    return FinalizedValidationPair(durable_report, durable_state)

def build_execution_report_v1(
    workspace: StagingWorkspace,
    *,
    promotion_outcome: str,
    completion_status: str,
    stage_status: dict[str, str],
    stage_errors: dict[str, list[str]] | None = None,
    stage_warnings: dict[str, list[str]] | None = None,
) -> dict[str, object]:
    if promotion_outcome not in _I4_PROMOTION_OUTCOMES:
        raise StagingError("invalid execution-report promotion_outcome")
    if completion_status not in _I4_COMPLETION_STATUSES:
        raise StagingError("invalid execution-report completion_status")
    if promotion_outcome == "promoted" and completion_status != "promoted-with-finalization-error":
        raise StagingError("promoted failure report requires promoted-with-finalization-error")
    if promotion_outcome in {"not-promoted", "indeterminate"} and completion_status != "failed":
        raise StagingError("non-promoted/indeterminate report requires failed completion_status")

    errors = stage_errors or {}
    warnings = stage_warnings or {}
    stages: list[dict[str, object]] = []
    for stage_id in _I4_CANONICAL_STAGES:
        if stage_id not in stage_status:
            continue
        status = stage_status[stage_id]
        if status not in _I4_STAGE_STATUSES:
            raise StagingError(f"invalid stage status for {stage_id}")
        stage_errors_value = list(errors.get(stage_id, []))
        if status == "failed" and not stage_errors_value:
            raise StagingError(f"failed stage {stage_id} requires an error")
        stages.append({
            "id": stage_id,
            "status": status,
            "warnings": list(warnings.get(stage_id, [])),
            "errors": stage_errors_value,
        })
    report: dict[str, object] = {
        "schema_version": "1",
        "request_fingerprint": workspace.inputs.request.request_fingerprint,
        "staging_root": str(workspace.root),
        "expected_destination": workspace.inputs.request.destination,
        "promotion_outcome": promotion_outcome,
        "completion_status": completion_status,
        "stages": stages,
    }
    validate_execution_report_v1(report)
    return report

def validate_execution_report_v1(report: dict[str, object]) -> None:
    if tuple(report) != _I4_EXECUTION_REPORT_FIELDS:
        raise StagingError("execution-report field closure/order is invalid")
    if report["schema_version"] != "1":
        raise StagingError("execution-report schema_version must be 1")
    _i4_validate_sha256(
        report["request_fingerprint"], "execution-report request_fingerprint"
    )
    if not isinstance(report["staging_root"], str) or not report["staging_root"]:
        raise StagingError("execution-report staging_root must be non-empty")
    if (
        not isinstance(report["expected_destination"], str)
        or not report["expected_destination"]
    ):
        raise StagingError("execution-report expected_destination must be non-empty")
    if report["promotion_outcome"] not in _I4_PROMOTION_OUTCOMES:
        raise StagingError("execution-report promotion_outcome is invalid")
    if report["completion_status"] not in _I4_COMPLETION_STATUSES:
        raise StagingError("execution-report completion_status is invalid")
    stages = report["stages"]
    if not isinstance(stages, list):
        raise StagingError("execution-report stages must be an array")
    seen: set[str] = set()
    last_index = -1
    for entry in stages:
        if not isinstance(entry, dict) or tuple(entry) != _I4_EXECUTION_STAGE_FIELDS:
            raise StagingError("execution-report stage field closure/order is invalid")
        stage_id = entry["id"]
        if stage_id not in _I4_CANONICAL_STAGES or stage_id in seen:
            raise StagingError("execution-report stage id is invalid or duplicate")
        idx = _I4_CANONICAL_STAGES.index(stage_id)
        if idx <= last_index:
            raise StagingError("execution-report stages are not canonical-order")
        last_index = idx
        seen.add(stage_id)
        if entry["status"] not in _I4_STAGE_STATUSES:
            raise StagingError("execution-report stage status is invalid")
        if (
            not isinstance(entry["warnings"], list)
            or any(not isinstance(v, str) for v in entry["warnings"])
        ):
            raise StagingError("execution-report warnings must be strings")
        if (
            not isinstance(entry["errors"], list)
            or any(not isinstance(v, str) for v in entry["errors"])
        ):
            raise StagingError("execution-report errors must be strings")
        if entry["status"] == "failed" and not entry["errors"]:
            raise StagingError("failed execution-report stage requires an error")

def execution_report_bytes_v1(report: dict[str, object]) -> bytes:
    validate_execution_report_v1(report)
    return _i4_json_bytes(report)



def cleanup_failed_staging_for_destination(
    destination: str,
    stage_names_before: tuple[str, ...],
) -> tuple[str, ...]:
    dest = Path(destination).expanduser().resolve()
    parent = dest.parent
    if not parent.exists() or not parent.is_dir():
        return ()

    before = set(stage_names_before)
    removed: list[str] = []
    for candidate in parent.iterdir():
        if candidate.name in before or not candidate.name.startswith("repo-spec-stage-"):
            continue
        if candidate.is_symlink() or not candidate.is_dir():
            continue

        transaction = candidate / "transaction"
        repository = candidate / "repository"
        state_path = transaction / "staging-state.json"
        if not transaction.is_dir() or not repository.is_dir() or not state_path.is_file():
            continue

        try:
            raw = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            continue

        recorded_destination = raw.get("destination")
        if not isinstance(recorded_destination, str):
            continue
        if Path(recorded_destination).expanduser().resolve() != dest:
            continue

        shutil.rmtree(candidate)
        removed.append(candidate.name)

    return tuple(sorted(removed))

