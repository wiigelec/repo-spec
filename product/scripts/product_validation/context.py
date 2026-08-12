# Product-owned validation context and external repository-authority loading.

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from validation.errors import expect
from .schema_subset import load_json


@dataclass(frozen=True)
class RepositoryValidationContext:
    manifest: dict[str, Any]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ExternalRepositoryValidationContext:
    specs: dict[str, dict[str, Any]]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ValidationContext:
    repo_root: Path
    repository: RepositoryValidationContext | None
    product: Any | None
    external_repository: ExternalRepositoryValidationContext | None = None


def load_repo_specs(
    repo_root: Path,
) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    manifest_path = repo_root / "repo/specs/repo/manifest.json"
    manifest = load_json(manifest_path)
    expect(isinstance(manifest, dict), "repository authority loading failed: manifest must be an object")

    entries = manifest.get("authoritative_specs")
    expect(
        isinstance(entries, list),
        "repository authority loading failed: authoritative_specs must be an array",
    )

    actual_paths = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "repo/specs/repo").glob("*.json")
        if path.is_file()
    )
    manifest_paths = [entry["path"] for entry in entries]
    expect(
        len(manifest_paths) == len(set(manifest_paths)),
        "repository authority loading failed: duplicate authoritative path",
    )
    expect(
        set(actual_paths) == set(manifest_paths),
        "repository authority loading failed: manifest completeness failed",
    )

    path_to_spec_id: dict[str, str] = {}
    spec_id_to_path: dict[str, str] = {}
    for entry in entries:
        expect(isinstance(entry, dict), "repository authority loading failed: invalid manifest entry")
        spec_id = entry.get("spec_id")
        path = entry.get("path")
        expect(
            isinstance(spec_id, str) and isinstance(path, str),
            "repository authority loading failed: invalid manifest correspondence",
        )
        expect(path not in path_to_spec_id, f"repository authority loading failed: duplicate path {path}")
        expect(spec_id not in spec_id_to_path, f"repository authority loading failed: duplicate spec_id {spec_id}")
        path_to_spec_id[path] = spec_id
        spec_id_to_path[spec_id] = path

    specs: dict[str, dict[str, Any]] = {}
    source_paths: dict[str, str] = {}
    for path in actual_paths:
        spec = manifest if path == "repo/specs/repo/manifest.json" else load_json(repo_root / path)
        expect(isinstance(spec, dict), f"repository authority loading failed: {path} must contain an object")
        expected_spec_id = path_to_spec_id[path]
        spec_id = spec.get("spec_id")
        expect(
            spec_id == expected_spec_id,
            f"repository authority loading failed: manifest entry {expected_spec_id} does not match {path}",
        )
        expect(spec_id not in specs, f"repository authority loading failed: duplicate authoritative spec_id {spec_id}")
        specs[spec_id] = spec
        source_paths[spec_id] = path

    expect(
        set(source_paths) == set(spec_id_to_path),
        "repository authority loading failed: manifest completeness failed",
    )
    return manifest, specs, source_paths, actual_paths
