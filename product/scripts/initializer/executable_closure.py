from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "1"
REPOSITORY_RELATIVE = "repository-relative"
CLOSURE_SATISFIED = "closure-satisfied"
CLOSURE_FAILED = "closure-failed"

@dataclass(frozen=True)
class InstalledCommandRequirement:
    requirement_id: str
    path: str
    classification: str = REPOSITORY_RELATIVE
    executable_required: bool = True
    portable_support: tuple[str, ...] = ()

INSTALLED_COMMAND_REQUIREMENTS = (
    InstalledCommandRequirement(
        "common-production-validation",
        "scripts/validate",
        portable_support=(
            "repo/scripts/validate",
            "repo/scripts/root_validation.py",
            "product/scripts/validate",
            "product/validation/runners/validate_impl.py",
        ),
    ),
    InstalledCommandRequirement(
        "repository-validation-self-test",
        "repo/scripts/test-validation",
        portable_support=("repo/scripts/test_validation_impl.py",),
    ),
    InstalledCommandRequirement(
        "product-validation-self-test",
        "product/scripts/test-validation",
        portable_support=("product/validation/runners/test_validation_impl.py",),
    ),
    InstalledCommandRequirement(
        "generic-product-implementation-test",
        "product/scripts/test-product",
        portable_support=("product/scripts/test_product_impl.py",),
    ),
)

class ExecutableClosureError(RuntimeError):
    pass

def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ExecutableClosureError(f"cannot load closure authority: {path}") from exc
    if not isinstance(value, dict):
        raise ExecutableClosureError(f"closure authority must be a JSON object: {path}")
    return value

def _index_output_inventory(framework_root: Path) -> dict[str, dict[str, Any]]:
    spec = _load_json(framework_root / "product/specs/product/level-1/initializer-output-inventory-v1.json")
    entries = spec.get("material_index")
    if not isinstance(entries, list):
        raise ExecutableClosureError("output inventory material_index is missing")
    by_path: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ExecutableClosureError("output inventory contains a non-object entry")
        path = entry.get("destination_path")
        if not isinstance(path, str) or not path:
            raise ExecutableClosureError("output inventory entry lacks destination_path")
        if path in by_path:
            raise ExecutableClosureError(f"duplicate output inventory path: {path}")
        by_path[path] = entry
    return by_path

def _index_material_manifest(framework_root: Path) -> dict[str, dict[str, Any]]:
    manifest = _load_json(framework_root / "product/scripts/initializer/framework-inventory.json")
    entries = manifest.get("entries")
    if not isinstance(entries, list):
        raise ExecutableClosureError("framework inventory entries are missing")
    by_key: dict[str, dict[str, Any]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ExecutableClosureError("framework inventory contains a non-object entry")
        key = entry.get("material_key")
        if not isinstance(key, str) or not key:
            raise ExecutableClosureError("framework inventory entry lacks material_key")
        if key in by_key:
            raise ExecutableClosureError(f"duplicate framework material key: {key}")
        by_key[key] = entry
    return by_key

def installed_command_requirements() -> list[dict[str, Any]]:
    return [
        {
            "requirement_id": item.requirement_id,
            "path": item.path,
            "classification": item.classification,
            "executable_required": item.executable_required,
            "portable_support": list(item.portable_support),
        }
        for item in INSTALLED_COMMAND_REQUIREMENTS
    ]

def _resolve_installed_path(
    path: str,
    *,
    output_by_path: dict[str, dict[str, Any]],
    material_by_key: dict[str, dict[str, Any]],
    staged_repository: Path,
    executable_required: bool,
) -> dict[str, Any]:
    item: dict[str, Any] = {"path": path}
    inventory = output_by_path.get(path)
    item["output_inventory_authorized"] = inventory is not None
    material = None
    if inventory is not None:
        key = inventory.get("material_key")
        item["material_key"] = key
        if isinstance(key, str):
            material = material_by_key.get(key)
    item["material_authorized"] = material is not None
    if material is not None:
        item["source_path"] = material.get("source_path")
        item["declared_mode"] = material.get("mode")
        item["source_type"] = material.get("source_type")
        item["operation"] = material.get("operation")
    staged_path = staged_repository / path
    item["staged_path_present"] = staged_path.is_file()
    item["staged_executable"] = os.access(staged_path, os.X_OK) if staged_path.is_file() else False
    if executable_required:
        authority_mode_ok = (
            inventory is not None and inventory.get("mode") == "100755"
            and material is not None and material.get("mode") == "100755"
        )
    else:
        authority_mode_ok = inventory is not None and material is not None
    item["executable_authority"] = authority_mode_ok if executable_required else None
    resolved = (
        item["output_inventory_authorized"]
        and item["material_authorized"]
        and item["staged_path_present"]
        and (not executable_required or (item["staged_executable"] and authority_mode_ok))
    )
    item["resolution"] = "resolved" if resolved else "unresolved"
    return item

def evaluate_executable_reference_closure(framework_root: Path, staged_repository: Path) -> dict[str, Any]:
    framework_root = framework_root.resolve()
    staged_repository = staged_repository.resolve()
    output_by_path = _index_output_inventory(framework_root)
    material_by_key = _index_material_manifest(framework_root)
    evidence: list[dict[str, Any]] = []
    overall_ok = True
    for requirement in INSTALLED_COMMAND_REQUIREMENTS:
        item: dict[str, Any] = {
            "requirement_id": requirement.requirement_id,
            "classification": requirement.classification,
            "path": requirement.path,
            "executable_required": requirement.executable_required,
        }
        if requirement.classification != REPOSITORY_RELATIVE:
            item["resolution"] = "unresolved"
            item["classification_valid"] = False
            item["portable_support"] = []
            overall_ok = False
            evidence.append(item)
            continue
        item["classification_valid"] = True
        command = _resolve_installed_path(
            requirement.path,
            output_by_path=output_by_path,
            material_by_key=material_by_key,
            staged_repository=staged_repository,
            executable_required=requirement.executable_required,
        )
        item.update(command)
        support = [
            _resolve_installed_path(
                support_path,
                output_by_path=output_by_path,
                material_by_key=material_by_key,
                staged_repository=staged_repository,
                executable_required=False,
            )
            for support_path in requirement.portable_support
        ]
        item["portable_support"] = support
        item["portable_support_closed"] = all(x["resolution"] == "resolved" for x in support)
        resolved = (
            item["classification_valid"]
            and command["resolution"] == "resolved"
            and item["portable_support_closed"]
        )
        item["resolution"] = "resolved" if resolved else "unresolved"
        if not resolved:
            overall_ok = False
        evidence.append(item)
    return {
        "schema_version": SCHEMA_VERSION,
        "classification": CLOSURE_SATISFIED if overall_ok else CLOSURE_FAILED,
        "requirements": evidence,
    }

def closure_failure_code(result: dict[str, Any]) -> str | None:
    if result.get("classification") == CLOSURE_SATISFIED:
        return None
    requirements = result.get("requirements")
    if not isinstance(requirements, list):
        return "installed-authority-missing"
    for item in requirements:
        if not isinstance(item, dict):
            return "installed-authority-missing"
        if item.get("classification_valid") is False:
            return "dependency-classification-invalid"
        if not item.get("output_inventory_authorized") or not item.get("material_authorized"):
            return "installed-authority-missing"
        if not item.get("staged_path_present"):
            return "installed-path-missing"
        if item.get("executable_required") and (
            not item.get("staged_executable") or not item.get("executable_authority")
        ):
            return "executable-capability-missing"
        support = item.get("portable_support")
        if isinstance(support, list):
            for support_item in support:
                if not isinstance(support_item, dict):
                    return "portable-support-missing"
                if (
                    not support_item.get("output_inventory_authorized")
                    or not support_item.get("material_authorized")
                    or not support_item.get("staged_path_present")
                ):
                    return "portable-support-missing"
        if item.get("portable_support_closed") is False:
            return "portable-support-missing"
    return "installed-authority-missing"
