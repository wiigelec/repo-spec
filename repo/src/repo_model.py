#!/usr/bin/env python3

"""Neutral repository-model loading helpers shared by generators and validators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class RepositoryError(Exception):
    pass


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except OSError as exc:
        raise RepositoryError(f"missing required file: {path}") from exc
    except json.JSONDecodeError as exc:
        raise RepositoryError(f"invalid JSON: {path}: {exc.msg}") from exc


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    if not value:
        raise RepositoryError(f"invalid repository-relative path: {value}")
    if value.startswith("/") or value.startswith("./") or "/./" in value or value.endswith("/.") or "\\" in value or "//" in value:
        raise RepositoryError(f"invalid repository-relative path: {value}")
    relative = Path(value)
    if any(part in {".", ".."} for part in relative.parts):
        raise RepositoryError(f"invalid repository-relative path: {value}")
    resolved = (repo_root / relative).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise RepositoryError(f"invalid repository-relative path: {value}") from exc
    return resolved


def load_manifest(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / "repo/specs/repo/manifest.json")


def index_manifest_paths(manifest: dict[str, Any], entry_key: str = "authoritative_specs") -> tuple[dict[str, str], dict[str, str]]:
    path_to_spec_id: dict[str, str] = {}
    spec_id_to_path: dict[str, str] = {}
    for entry in manifest[entry_key]:
        spec_id = entry["spec_id"]
        path = entry["path"]
        if path in path_to_spec_id:
            raise RepositoryError(f"duplicate authoritative spec path: {path}")
        if spec_id in spec_id_to_path:
            raise RepositoryError(f"duplicate authoritative spec_id: {spec_id}")
        path_to_spec_id[path] = spec_id
        spec_id_to_path[spec_id] = path
    return path_to_spec_id, spec_id_to_path


def load_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    manifest = load_manifest(repo_root)
    actual_paths = sorted(path.relative_to(repo_root).as_posix() for path in (repo_root / "repo/specs/repo").glob("*.json"))
    manifest_paths = [entry["path"] for entry in manifest["authoritative_specs"]]
    if len(manifest_paths) != len(set(manifest_paths)):
        raise RepositoryError("manifest completeness failed")
    if set(actual_paths) != set(manifest_paths):
        raise RepositoryError("manifest completeness failed")

    path_to_spec_id, spec_id_to_path = index_manifest_paths(manifest)
    specs = {"repo.manifest": manifest}
    paths = {"repo.manifest": "repo/specs/repo/manifest.json"}

    for path in actual_paths:
        expected_spec_id = path_to_spec_id[path]
        if path == "repo/specs/repo/manifest.json":
            if manifest["spec_id"] != expected_spec_id:
                raise RepositoryError(f"manifest entry {expected_spec_id} does not match {path}")
            paths[expected_spec_id] = path
            continue
        spec = load_json(repo_root / path)
        spec_id = spec["spec_id"]
        if spec_id != expected_spec_id:
            raise RepositoryError(f"manifest entry {expected_spec_id} does not match {path}")
        if spec_id in specs:
            raise RepositoryError(f"duplicate authoritative spec_id: {spec_id}")
        specs[spec_id] = spec
        paths[spec_id] = path

    if set(paths) != set(spec_id_to_path):
        raise RepositoryError("manifest completeness failed")
    return manifest, specs, paths, actual_paths


def load_product_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    manifest_path = repo_root / "product/specs/product/manifest.json"
    if not manifest_path.exists():
        return {}, {}, {}, []

    manifest = load_json(manifest_path)
    actual_paths = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "product/specs/product").rglob("*.json")
        if path.is_file() and path.relative_to(repo_root).as_posix() != "product/specs/product/manifest.json"
    )
    manifest_paths = [entry["path"] for entry in manifest["product_specifications"]]
    if len(manifest_paths) != len(set(manifest_paths)):
        raise RepositoryError("product manifest completeness failed")
    if set(actual_paths) != set(manifest_paths):
        raise RepositoryError("product manifest completeness failed")

    path_to_spec_id, spec_id_to_path = index_manifest_paths(manifest, "product_specifications")
    specs: dict[str, dict[str, Any]] = {}
    paths: dict[str, str] = {}

    for path in actual_paths:
        expected_spec_id = path_to_spec_id[path]
        spec = load_json(repo_root / path)
        spec_id = spec["spec_id"]
        if spec_id != expected_spec_id:
            raise RepositoryError(f"product manifest entry {expected_spec_id} does not match {path}")
        if spec_id in specs:
            raise RepositoryError(f"duplicate product specification id: {spec_id}")
        specs[spec_id] = spec
        paths[spec_id] = path

    if set(paths) != set(spec_id_to_path):
        raise RepositoryError("product manifest completeness failed")
    return manifest, specs, paths, actual_paths


def declared_derived_artifact_paths(*spec_sets: dict[str, dict[str, Any]]) -> set[str]:
    paths: list[str] = []
    for specs in spec_sets:
        for spec in specs.values():
            for artifact in spec.get("derived_artifacts", []):
                if artifact.get("type") not in {"markdown", "yaml"}:
                    raise RepositoryError(f"unsupported derived artifact type: {artifact.get('type')}")
                paths.append(artifact["path"])
    if len(paths) != len(set(paths)):
        raise RepositoryError("duplicate derived artifact paths failed")
    return set(paths)
