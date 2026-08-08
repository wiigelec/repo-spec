from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .models import InitializerError, SourceSelection

MANIFEST_PATH = "product/scripts/initializer/framework-inventory.json"
OUTPUT_INVENTORY_SPEC_PATH = "product/specs/product/level-1/initializer-output-inventory-v1.json"
ROOT_FIELDS = frozenset({"schema_version", "entries"})
ENTRY_FIELDS = frozenset({
    "material_key", "source_path", "role", "operation", "source_type", "mode",
    "profile", "exclusion_rationale",
})
REQUIRED_ENTRY_FIELDS = (
    "material_key", "source_path", "role", "operation", "source_type", "mode"
)
OPERATIONS = frozenset({"copy-verbatim", "instantiate-template", "generate-record"})
SOURCE_TYPES = frozenset({"blob", "symlink"})
MATERIAL_ROLES = frozenset({
    "runtime-framework",
    "governing-specification",
    "validation-utility",
    "documentation-support",
    "generated-reference",
    "initializer-framework",
})


class InventoryError(InitializerError):
    pass


@dataclass(frozen=True)
class MaterialEntry:
    material_key: str
    source_path: str
    role: str
    operation: str
    source_type: str
    mode: str
    profile: str | None = None
    exclusion_rationale: str | None = None


@dataclass(frozen=True)
class ResolvedSourceMaterial:
    repository: str
    commit_id: str
    manifest: tuple[MaterialEntry, ...]
    direction_material: tuple[str, ...]


def _git(repo: str, *args: str) -> subprocess.CompletedProcess[bytes]:
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git", "-C", repo, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )


def _git_text(repo: str, *args: str) -> str:
    p = _git(repo, *args)
    if p.returncode:
        raise InventoryError(
            f"git {' '.join(args)} failed: {p.stderr.decode('utf-8', 'replace').strip()}"
        )
    return p.stdout.decode("utf-8")


def _validate_repo_relative(path: str, context: str) -> None:
    if not path or path.startswith("/") or "\x00" in path:
        raise InventoryError(f"{context} must be a non-empty repository-relative path")
    depth = 0
    for part in path.split("/"):
        if not part or part == ".":
            continue
        if part == "..":
            if depth == 0:
                raise InventoryError(f"{context} escapes the repository root")
            depth -= 1
        else:
            depth += 1


def _read_commit_blob(repository: str, commit_id: str, path: str) -> bytes:
    _validate_repo_relative(path, "commit path")
    p = _git(repository, "cat-file", "blob", f"{commit_id}:{path}")
    if p.returncode:
        raise InventoryError(f"required source blob is unavailable: {path}")
    return p.stdout


def _tree_entry(repository: str, commit_id: str, path: str) -> tuple[str, str]:
    _validate_repo_relative(path, "source path")
    p = _git(repository, "ls-tree", "-z", commit_id, "--", path)
    if p.returncode:
        raise InventoryError(f"cannot inspect source path: {path}")
    records = [r for r in p.stdout.split(b"\x00") if r]
    if len(records) != 1:
        raise InventoryError(f"source path does not resolve to exactly one commit-tree entry: {path}")
    meta, _, found = records[0].partition(b"\t")
    if found.decode("utf-8", "strict") != path:
        raise InventoryError(f"source path resolution mismatch: {path}")
    mode, obj_type, _oid = meta.decode("ascii").split(" ", 2)
    return mode, obj_type


def _load_json_blob(repository: str, commit_id: str, path: str) -> dict[str, Any]:
    raw = _read_commit_blob(repository, commit_id, path)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InventoryError(f"{path} is not UTF-8") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise InventoryError(f"invalid JSON in {path}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise InventoryError(f"{path} must contain one JSON object")
    return value


def validate_material_manifest(
    raw: dict[str, Any],
    output_inventory: dict[str, Any],
) -> tuple[MaterialEntry, ...]:
    unknown_root = set(raw) - ROOT_FIELDS
    if unknown_root:
        raise InventoryError(f"unknown material-manifest root field(s): {sorted(unknown_root)}")
    if raw.get("schema_version") != "1":
        raise InventoryError("material manifest schema_version must be '1'")
    entries = raw.get("entries")
    if not isinstance(entries, list) or not entries:
        raise InventoryError("material manifest entries must be a non-empty array")

    output_entries = output_inventory.get("material_index")
    if not isinstance(output_entries, list):
        raise InventoryError("output inventory material_index must be an array")
    by_key = {}
    for item in output_entries:
        if not isinstance(item, dict) or not isinstance(item.get("material_key"), str):
            raise InventoryError("invalid output inventory material_index entry")
        role = item.get("role")
        if role == "development-only":
            raise InventoryError("output inventory must not contain development-only material")
        if role not in MATERIAL_ROLES:
            raise InventoryError(f"unknown output inventory material role: {role!r}")
        key = item["material_key"]
        if key in by_key:
            raise InventoryError(f"duplicate output material_key: {key}")
        by_key[key] = item

    parsed: list[MaterialEntry] = []
    seen = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise InventoryError(f"entries[{index}] must be an object")
        unknown = set(item) - ENTRY_FIELDS
        if unknown:
            raise InventoryError(f"entries[{index}] unknown field(s): {sorted(unknown)}")
        missing = [field for field in REQUIRED_ENTRY_FIELDS if field not in item]
        if missing:
            raise InventoryError(f"entries[{index}] missing required field(s): {missing}")
        for field in REQUIRED_ENTRY_FIELDS:
            if not isinstance(item[field], str) or not item[field]:
                raise InventoryError(f"entries[{index}].{field} must be a non-empty string")
        key = item["material_key"]
        if key in seen:
            raise InventoryError(f"duplicate material_key: {key}")
        seen.add(key)
        _validate_repo_relative(item["source_path"], f"entries[{index}].source_path")
        if item["operation"] not in OPERATIONS:
            raise InventoryError(f"unknown operation: {item['operation']}")
        if item["role"] == "development-only":
            raise InventoryError("material manifest must not contain development-only material")
        if item["role"] not in MATERIAL_ROLES:
            raise InventoryError(f"unknown material role: {item['role']!r}")
        if item["source_type"] not in SOURCE_TYPES:
            raise InventoryError(f"unsupported source_type: {item['source_type']}")
        if item["source_type"] == "symlink" and item["mode"] != "120000":
            raise InventoryError("symlink source_type requires mode 120000")
        if item["source_type"] == "blob" and item["mode"] not in {"100644", "100755"}:
            raise InventoryError("blob source_type requires mode 100644 or 100755")
        target = by_key.get(key)
        if target is None:
            raise InventoryError(f"unused material_key absent from output inventory: {key}")
        for field in ("operation", "mode", "role"):
            if target.get(field) != item[field]:
                raise InventoryError(f"material_key {key!r} disagrees with output inventory field {field}")
        parsed.append(MaterialEntry(
            material_key=key,
            source_path=item["source_path"],
            role=item["role"],
            operation=item["operation"],
            source_type=item["source_type"],
            mode=item["mode"],
            profile=item.get("profile"),
            exclusion_rationale=item.get("exclusion_rationale"),
        ))

    if seen != set(by_key):
        missing = sorted(set(by_key) - seen)
        raise InventoryError(f"output material_index key(s) missing from material manifest: {missing}")
    return tuple(parsed)


def resolve_source_material(
    repository: str,
    revision_object_id: str,
    direction_material: tuple[str, ...] | list[str],
) -> ResolvedSourceMaterial:
    if not Path(repository).is_absolute():
        raise InventoryError("source repository must be the intake-resolved absolute path")
    if len(revision_object_id) != 40 or any(c not in "0123456789abcdef" for c in revision_object_id):
        raise InventoryError("source revision must be an exact lowercase SHA-1 object ID")

    if _git(repository, "rev-parse", "--git-dir").returncode:
        raise InventoryError("source repository is not a local Git repository")
    object_format = _git_text(repository, "rev-parse", "--show-object-format").strip()
    if object_format != "sha1":
        raise InventoryError(f"unsupported source repository object format: {object_format}")

    resolved = _git_text(
        repository, "rev-parse", "--verify", f"{revision_object_id}^{{commit}}"
    ).strip()
    if resolved != revision_object_id:
        raise InventoryError("source revision did not resolve directly to the exact commit object")

    p = _git(repository, "fsck", "--connectivity-only", "--no-dangling", revision_object_id)
    if p.returncode:
        raise InventoryError("source commit tree is not fully available locally")

    manifest_raw = _load_json_blob(repository, revision_object_id, MANIFEST_PATH)
    output_raw = _load_json_blob(repository, revision_object_id, OUTPUT_INVENTORY_SPEC_PATH)
    manifest = validate_material_manifest(manifest_raw, output_raw)

    for entry in manifest:
        mode, obj_type = _tree_entry(repository, revision_object_id, entry.source_path)
        if obj_type != "blob":
            raise InventoryError(f"source_path resolves to a Git tree/non-blob object: {entry.source_path}")
        actual_type = "symlink" if mode == "120000" else "blob"
        if actual_type != entry.source_type:
            raise InventoryError(
                f"source_type mismatch for {entry.source_path}: expected {entry.source_type}, observed {actual_type}"
            )
        if mode != entry.mode:
            raise InventoryError(
                f"mode mismatch for {entry.source_path}: expected {entry.mode}, observed {mode}"
            )

    validated_direction: list[str] = []
    for item in direction_material:
        _validate_repo_relative(item, "direction_material")
        mode, obj_type = _tree_entry(repository, revision_object_id, item)
        if obj_type != "blob" or mode == "120000":
            raise InventoryError(f"direction_material must resolve to an existing regular file: {item}")
        validated_direction.append(item)

    return ResolvedSourceMaterial(
        repository=repository,
        commit_id=revision_object_id,
        manifest=manifest,
        direction_material=tuple(validated_direction),
    )


def resolve_source_selection_from_request(
    request_repository: str | None,
    request_revision: str | None,
) -> SourceSelection:
    if request_repository is None or request_revision is None:
        raise InventoryError("source selection requires explicit source repository and revision")
    return SourceSelection(request_repository, request_revision)


def build_source_selection(repository: str | None, revision: str | None) -> SourceSelection | None:
    if repository is None and revision is None:
        return None
    return resolve_source_selection_from_request(repository, revision)
