#!/usr/bin/env python3

"""Neutral repository-model loading helpers shared by generators and validators."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    return json.loads(path.read_text())


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    if not value:
        raise ValueError(f"invalid repository-relative path: {value}")
    if value.startswith("/") or value.startswith("./") or "/./" in value or value.endswith("/.") or "\\" in value or "//" in value:
        raise ValueError(f"invalid repository-relative path: {value}")
    relative = Path(value)
    if any(part in {".", ".."} for part in relative.parts):
        raise ValueError(f"invalid repository-relative path: {value}")
    resolved = (repo_root / relative).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"invalid repository-relative path: {value}") from exc
    return resolved


def load_manifest(repo_root: Path) -> dict[str, Any]:
    return load_json(repo_root / "specs/repo/manifest.json")


def index_manifest_paths(manifest: dict[str, Any]) -> tuple[dict[str, str], dict[str, str]]:
    path_to_spec_id: dict[str, str] = {}
    spec_id_to_path: dict[str, str] = {}
    for entry in manifest["authoritative_specs"]:
        spec_id = entry["spec_id"]
        path = entry["path"]
        if path in path_to_spec_id:
            raise ValueError(f"duplicate authoritative spec path: {path}")
        if spec_id in spec_id_to_path:
            raise ValueError(f"duplicate authoritative spec_id: {spec_id}")
        path_to_spec_id[path] = spec_id
        spec_id_to_path[spec_id] = path
    return path_to_spec_id, spec_id_to_path


def load_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    manifest = load_manifest(repo_root)
    actual_paths = sorted(path.relative_to(repo_root).as_posix() for path in (repo_root / "specs/repo").glob("*.json"))
    manifest_paths = [entry["path"] for entry in manifest["authoritative_specs"]]
    if len(manifest_paths) != len(set(manifest_paths)):
        raise ValueError("manifest completeness failed")
    if set(actual_paths) != set(manifest_paths):
        raise ValueError("manifest completeness failed")

    path_to_spec_id, spec_id_to_path = index_manifest_paths(manifest)
    specs = {"repo.manifest": manifest}
    paths = {"repo.manifest": "specs/repo/manifest.json"}

    for path in actual_paths:
        expected_spec_id = path_to_spec_id[path]
        if path == "specs/repo/manifest.json":
            if manifest["spec_id"] != expected_spec_id:
                raise ValueError(f"manifest entry {expected_spec_id} does not match {path}")
            paths[expected_spec_id] = path
            continue
        spec = load_json(repo_root / path)
        spec_id = spec["spec_id"]
        if spec_id != expected_spec_id:
            raise ValueError(f"manifest entry {expected_spec_id} does not match {path}")
        if spec_id in specs:
            raise ValueError(f"duplicate authoritative spec_id: {spec_id}")
        specs[spec_id] = spec
        paths[spec_id] = path

    if set(paths) != set(spec_id_to_path):
        raise ValueError("manifest completeness failed")
    return manifest, specs, paths, actual_paths


def declared_derived_artifact_paths(specs: dict[str, dict[str, Any]]) -> set[str]:
    paths: list[str] = []
    for spec in specs.values():
        for artifact in spec.get("derived_artifacts", []):
            if artifact.get("type") not in {"markdown", "yaml"}:
                raise ValueError(f"unsupported derived artifact type: {artifact.get('type')}")
            paths.append(artifact["path"])
    if len(paths) != len(set(paths)):
        raise ValueError("duplicate derived artifact paths failed")
    return set(paths)
