from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import (
    VALID_CLASSIFICATIONS,
    VALID_INVENTORY_FIELDS,
    INSTALLABLE_CLASSIFICATIONS,
    UNINSTALLABLE_CLASSIFICATIONS,
    InitializerError,
    InventoryEntry,
    ClassifiedInventory,
    SourceSelection,
)


KNOWN_ROOT_FIELDS = {"schema_version", "inventory_scope", "entries"}

RECOGNIZED_PROFILES = {"github"}


class InventoryError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


class InventoryValidationResult:
    def __init__(self) -> None:
        self._errors: list[str] = []

    def add(self, message: str) -> None:
        self._errors.append(message)

    @property
    def errors(self) -> list[str]:
        return list(self._errors)

    @property
    def is_valid(self) -> bool:
        return len(self._errors) == 0

    def raise_if_invalid(self) -> None:
        if self._errors:
            raise InventoryError(self._errors[0])


def resolve_inventory_path(repo_root: Path) -> Path:
    return repo_root / "scripts" / "initializer" / "framework-inventory.json"


def load_inventory(path: Path) -> dict[str, Any]:
    try:
        raw = json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        raise InventoryError(f"invalid JSON in inventory file: {exc.msg}") from exc
    except OSError as exc:
        raise InventoryError(f"cannot read inventory file: {exc}") from exc
    if not isinstance(raw, dict):
        raise InventoryError("inventory must be a JSON object")
    return raw


def validate_inventory(raw: dict[str, Any]) -> InventoryValidationResult:
    result = InventoryValidationResult()

    _check_inventory_unknown_root_fields(raw, result)
    _check_inventory_schema_version(raw.get("schema_version"), result)

    entries = raw.get("entries")
    if entries is None:
        result.add("missing required field: entries")
        return result
    if not isinstance(entries, list):
        result.add("entries must be a list")
        return result

    if not entries:
        result.add("inventory must contain at least one entry")
        return result

    seen_paths: dict[str, int] = {}
    for i, entry in enumerate(entries):
        _check_single_entry(entry, i, result, seen_paths)

    _check_contradictory_classifications(entries, result)
    _check_path_overlap_conflicts(entries, result)

    return result


def _check_inventory_unknown_root_fields(
    raw: dict[str, Any],
    result: InventoryValidationResult,
) -> None:
    for key in raw:
        if key not in KNOWN_ROOT_FIELDS:
            result.add(f"unknown root field: {key!r}")


def _check_inventory_schema_version(version: Any, result: InventoryValidationResult) -> None:
    if version is None:
        result.add("missing required field: schema_version")
        return
    if not isinstance(version, str):
        result.add("schema_version must be a string")
        return
    if version != "1":
        result.add(f"unsupported schema version: {version!r}")


def _check_single_entry(
    entry: Any,
    index: int,
    result: InventoryValidationResult,
    seen_paths: dict[str, int],
) -> None:
    prefix = f"entries[{index}]"

    if not isinstance(entry, dict):
        result.add(f"{prefix} must be an object")
        return

    for key in entry:
        if key not in VALID_INVENTORY_FIELDS:
            result.add(f"{prefix}: unknown field {key!r}")

    path = entry.get("path")
    if not path:
        result.add(f"{prefix}: missing required field: path")
        return
    if not isinstance(path, str):
        result.add(f"{prefix}: path must be a string")
        return
    if not path.strip():
        result.add(f"{prefix}: path must not be empty")
        return
    if path.startswith("/"):
        result.add(f"{prefix}: absolute path not allowed: {path!r}")
        return
    if ".." in path.split("/"):
        result.add(f"{prefix}: parent-directory traversal not allowed: {path!r}")
        return

    if path in seen_paths:
        prev = seen_paths[path]
        result.add(f"{prefix}: duplicate path {path!r} (also at entries[{prev}])")
    else:
        seen_paths[path] = index

    _check_entry_classification(entry, path, prefix, result)
    _check_entry_authoritative(entry, path, prefix, result)
    _check_entry_installable(entry, path, prefix, result)
    _check_entry_profile(entry, path, prefix, result)
    _check_entry_exclusion_rationale(entry, path, prefix, result)
    _check_entry_derived_from(entry, path, prefix, result)


def _check_entry_classification(
    entry: dict[str, Any],
    path: str,
    prefix: str,
    result: InventoryValidationResult,
) -> None:
    classification = entry.get("classification")
    if not classification:
        result.add(f"{prefix}: missing required field: classification")
        return
    if not isinstance(classification, str):
        result.add(f"{prefix}: classification must be a string")
        return
    if classification not in VALID_CLASSIFICATIONS:
        result.add(f"{prefix}: unsupported classification {classification!r}")


def _check_entry_authoritative(
    entry: dict[str, Any],
    path: str,
    prefix: str,
    result: InventoryValidationResult,
) -> None:
    auth = entry.get("authoritative")
    if auth is not None and not isinstance(auth, bool):
        result.add(f"{prefix}: authoritative must be a boolean")


def _check_entry_installable(
    entry: dict[str, Any],
    path: str,
    prefix: str,
    result: InventoryValidationResult,
) -> None:
    installable = entry.get("installable")
    if installable is not None and not isinstance(installable, bool):
        result.add(f"{prefix}: installable must be a boolean")
        return

    classification = entry.get("classification", "")
    if installable is True and classification in UNINSTALLABLE_CLASSIFICATIONS:
        result.add(f"{prefix}: entry marked installable but classification {classification!r} is not installable")
    if installable is False and classification in INSTALLABLE_CLASSIFICATIONS:
        result.add(f"{prefix}: entry marked not installable but classification {classification!r} requires installable")


def _check_entry_profile(
    entry: dict[str, Any],
    path: str,
    prefix: str,
    result: InventoryValidationResult,
) -> None:
    profile = entry.get("profile")
    if profile is not None:
        if not isinstance(profile, str):
            result.add(f"{prefix}: profile must be a string")
            return
        if profile not in RECOGNIZED_PROFILES:
            result.add(f"{prefix}: unrecognized profile identifier {profile!r}")
        classification = entry.get("classification", "")
        if classification not in ("profile-source", "installed-adapter"):
            result.add(f"{prefix}: profile field set on non-profile classification {classification!r}")


def _check_entry_exclusion_rationale(
    entry: dict[str, Any],
    path: str,
    prefix: str,
    result: InventoryValidationResult,
) -> None:
    rationale = entry.get("exclusion_rationale")
    classification = entry.get("classification", "")

    if classification in UNINSTALLABLE_CLASSIFICATIONS or classification == "excluded":
        if not rationale:
            result.add(f"{prefix}: exclusion_rationale required for uninstallable or excluded classification")
    if rationale is not None and not isinstance(rationale, str):
        result.add(f"{prefix}: exclusion_rationale must be a string")
    if rationale is not None and classification in INSTALLABLE_CLASSIFICATIONS:
        result.add(f"{prefix}: exclusion_rationale set on installable classification {classification!r}")


def _check_entry_derived_from(
    entry: dict[str, Any],
    path: str,
    prefix: str,
    result: InventoryValidationResult,
) -> None:
    df = entry.get("derived_from")
    classification = entry.get("classification", "")

    if df is not None:
        if not isinstance(df, list):
            result.add(f"{prefix}: derived_from must be a list")
            return
        if classification != "derived":
            result.add(f"{prefix}: derived_from set on non-derived classification {classification!r}")
            return
        if not df:
            result.add(f"{prefix}: derived_from must list at least one authoritative path")
            return
        for item in df:
            if not isinstance(item, str) or not item.strip():
                result.add(f"{prefix}: derived_from items must be non-empty strings")


def _check_contradictory_classifications(
    entries: list[Any],
    result: InventoryValidationResult,
) -> None:
    installable_set: set[str] = set()
    uninstallable_set: set[str] = set()

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        path = entry.get("path", "")
        classification = entry.get("classification", "")
        if classification in INSTALLABLE_CLASSIFICATIONS:
            installable_set.add(path)
        elif classification in UNINSTALLABLE_CLASSIFICATIONS:
            uninstallable_set.add(path)

    conflicting = installable_set & uninstallable_set
    for path in sorted(conflicting):
        result.add(f"contradictory classification for {path!r}: appears in both installable and uninstallable groups")


def _check_path_overlap_conflicts(
    entries: list[Any],
    result: InventoryValidationResult,
) -> None:
    entries_with_class = []
    for entry in entries:
        if isinstance(entry, dict) and "path" in entry and "classification" in entry:
            entries_with_class.append((entry["path"], entry["classification"]))

    sorted_entries = sorted(entries_with_class, key=lambda x: x[0])
    by_prefix: list[tuple[str, str]] = []
    for path, cls in sorted_entries:
        normalized = path.rstrip("/")
        for existing_path, existing_cls in by_prefix:
            if normalized.startswith(existing_path + "/") or existing_path.startswith(normalized + "/"):
                if cls != existing_cls:
                    parent = path if len(path) < len(existing_path) else existing_path
                    child = existing_path if len(path) < len(existing_path) else path
                    result.add(
                        f"overlapping entries with contradictory classifications: "
                        f"{parent!r} ({cls if path == parent else existing_cls}) "
                        f"and {child!r} ({existing_cls if path == parent else cls})"
                    )
        by_prefix.append((normalized, cls))


def validate_and_load_inventory(
    raw: dict[str, Any],
    source_selection: SourceSelection | None = None,
) -> ClassifiedInventory:
    result = validate_inventory(raw)
    result.raise_if_invalid()

    entries = [InventoryEntry(e) for e in raw["entries"]]
    return ClassifiedInventory(entries)


def build_source_selection(
    repository: str | None,
    revision: str | None,
) -> SourceSelection | None:
    if repository is None and revision is None:
        return None
    if repository is not None and revision is None:
        raise InventoryError("source revision is required when source repository is supplied")
    if revision is not None and repository is None:
        raise InventoryError("contradictory source: revision supplied without repository identity")
    if repository is not None and revision is not None:
        return SourceSelection(repository, revision)
    return None


def resolve_source_selection_from_request(
    request_repository: str | None,
    request_revision: str | None,
) -> SourceSelection:
    if request_repository is None and request_revision is None:
        raise InventoryError("source selection requires explicit source repository and revision")
    return build_source_selection(request_repository, request_revision)


def inventory_to_ordered_dict(
    classified: ClassifiedInventory,
    source_selection: SourceSelection | None,
) -> dict[str, Any]:
    output: dict[str, Any] = {
        "source_selection": None,
        "classifications": {},
    }

    if source_selection is not None:
        output["source_selection"] = {
            "repository": source_selection.repository,
            "revision": source_selection.revision,
        }

    for cls in sorted(classified.classifications):
        entries = classified.entries_by_classification(cls)
        output["classifications"][cls] = [
            {
                "path": e.path,
                "authoritative": e.authoritative,
                "installable": e.installable,
                "profile": e.profile,
                "exclusion_rationale": e.exclusion_rationale,
                "derived_from": e.derived_from,
            }
            for e in entries
        ]

    return output
