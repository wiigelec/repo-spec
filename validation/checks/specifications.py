"""Cross-domain validation-correspondence aggregate integrity."""
from __future__ import annotations

import json
from pathlib import Path

from .policy import RootValidationError


# validation-metadata: {"role": "helper"}
def _load_json_object(path: Path, label: str) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RootValidationError(
            f"root validation correspondence aggregate failed: unreadable {label}: {path}"
        ) from exc
    if not isinstance(value, dict):
        raise RootValidationError(
            f"root validation correspondence aggregate failed: {label} must be an object: {path}"
        )
    return value


# validation-metadata: {"role": "helper"}
def _active_requirement_refs(repo_root: Path, domain: str) -> set[tuple[str, str]]:
    if domain == "repo":
        manifest_path = repo_root / "repo/specs/repo/manifest.json"
        collection_name = "authoritative_specs"
    elif domain == "product":
        manifest_path = repo_root / "product/specs/product/manifest.json"
        collection_name = "product_specifications"
    else:
        raise RootValidationError(
            f"root validation correspondence aggregate failed: unsupported domain {domain}"
        )

    manifest = _load_json_object(manifest_path, f"{domain} manifest")
    entries = manifest.get(collection_name)
    if not isinstance(entries, list):
        raise RootValidationError(
            f"root validation correspondence aggregate failed: {domain} manifest lacks {collection_name}"
        )

    refs: set[tuple[str, str]] = set()
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise RootValidationError(
                f"root validation correspondence aggregate failed: malformed {domain} manifest entry"
            )
        spec = _load_json_object(repo_root / entry["path"], f"{domain} specification")
        if spec.get("status") != "accepted":
            continue
        spec_id = spec.get("spec_id")
        requirements = spec.get("normative_requirements")
        if not isinstance(spec_id, str) or not isinstance(requirements, list):
            raise RootValidationError(
                f"root validation correspondence aggregate failed: malformed accepted {domain} specification {entry['path']}"
            )
        for requirement in requirements:
            requirement_id = requirement.get("id") if isinstance(requirement, dict) else None
            if not isinstance(requirement_id, str):
                raise RootValidationError(
                    f"root validation correspondence aggregate failed: malformed requirement in {entry['path']}"
                )
            coordinate = (spec_id, requirement_id)
            if coordinate in refs:
                raise RootValidationError(
                    f"root validation correspondence aggregate failed: duplicate active requirement {spec_id}/{requirement_id}"
                )
            refs.add(coordinate)
    return refs


# validation-metadata: {"role": "helper"}
def _package_refs(repo_root: Path, domain: str) -> list[tuple[str, str]]:
    package_root = repo_root / domain / "validation/packages"
    if not package_root.is_dir():
        raise RootValidationError(
            f"root validation correspondence aggregate failed: missing {domain} package root"
        )
    refs: list[tuple[str, str]] = []
    for path in sorted(package_root.rglob("*.json")):
        package = _load_json_object(path, f"{domain} validation package")
        ref = package.get("normative_reference")
        if not isinstance(ref, dict) or not isinstance(ref.get("spec_id"), str) or not isinstance(ref.get("requirement_id"), str):
            raise RootValidationError(
                f"root validation correspondence aggregate failed: malformed package reference {path.relative_to(repo_root).as_posix()}"
            )
        refs.append((ref["spec_id"], ref["requirement_id"]))
    return refs


# validation-metadata: {"role": "helper"}
def validate(repo_root: Path) -> None:
    active = _active_requirement_refs(repo_root, "repo") | _active_requirement_refs(repo_root, "product")
    all_packages = _package_refs(repo_root, "repo") + _package_refs(repo_root, "product")

    seen: set[tuple[str, str]] = set()
    duplicates: set[tuple[str, str]] = set()
    for coordinate in all_packages:
        if coordinate in seen:
            duplicates.add(coordinate)
        seen.add(coordinate)
    if duplicates:
        rendered = ", ".join(f"{s}/{r}" for s, r in sorted(duplicates))
        raise RootValidationError(
            f"root validation correspondence aggregate failed: duplicate package coordinate(s): {rendered}"
        )

    package_set = set(all_packages)
    missing = sorted(active - package_set)
    unexpected = sorted(package_set - active)
    if missing:
        rendered = ", ".join(f"{s}/{r}" for s, r in missing)
        raise RootValidationError(
            f"root validation correspondence aggregate failed: missing active package(s): {rendered}"
        )
    if unexpected:
        rendered = ", ".join(f"{s}/{r}" for s, r in unexpected)
        raise RootValidationError(
            f"root validation correspondence aggregate failed: unexpected package(s): {rendered}"
        )

    print(f"ok: root validation correspondence aggregate completeness ({len(active)} active requirements)")
