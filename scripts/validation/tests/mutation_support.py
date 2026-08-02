from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from validation.errors import ValidationFailure, fail


def expect_failure(description: str, func, fragment: str) -> None:
    try:
        func()
    except ValidationFailure as exc:
        if fragment not in str(exc):
            fail(f"mutation test failed: {description} (expected {fragment!r}, got {exc})")
    else:
        fail(f"mutation test failed: {description} did not fail")


def expect_render_change(description: str, renderer, spec: dict, mutate) -> None:
    original = renderer(spec)
    mutated = copy.deepcopy(spec)
    mutate(mutated)
    if renderer(mutated) == original:
        fail(f"mutation test failed: {description} did not change output")


def declared_repo_fixture_paths(repo_root: Path) -> tuple[str, ...]:
    manifest = json.loads((repo_root / "specs/repo/manifest.json").read_text())
    required_paths = [
        "specs/repo/manifest.json",
        "schemas/repo-manifest.schema.json",
        "schemas/repo-artifact-taxonomy.schema.json",
        "schemas/repo-platform-profiles.schema.json",
        "schemas/repo-spec.schema.json",
        "schemas/product/product-manifest.schema.json",
        "schemas/product/product-spec-base.schema.json",
    ]
    for entry in manifest["authoritative_specs"]:
        path = entry["path"]
        required_paths.append(path)
        spec = json.loads((repo_root / path).read_text())
        for ref in spec.get("references", []):
            if ref.get("type") == "artifact":
                required_paths.append(ref["path"])
        for artifact in spec.get("derived_artifacts", []):
            required_paths.append(artifact["path"])
    return tuple(dict.fromkeys(required_paths))


def create_repo_fixture(repo_root: Path, temp_root: Path, fixture_index: int, required_paths: tuple[str, ...] | None = None) -> Path:
    fixture_root = temp_root / f"fixture-{fixture_index}"
    fixture_root.mkdir(parents=True, exist_ok=True)
    if required_paths is None:
        required_paths = declared_repo_fixture_paths(repo_root)
    for relative_path in required_paths:
        source = repo_root / relative_path
        target = fixture_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    return fixture_root


def mutate_json(path: Path, transform) -> None:
    data = json.loads(path.read_text())
    path.write_text(json.dumps(transform(data), indent=2) + "\n")


def add_lifecycle_spec(specs: dict, temp_repo: Path, spec_id: str, status: str, supersedes: list[str] | None = None, superseded_by: list[str] | None = None) -> None:
    mutate_json(
        temp_repo / "specs/repo/manifest.json",
        lambda manifest: (
            manifest["authoritative_specs"].append({"spec_id": spec_id, "path": f"specs/repo/{spec_id.removeprefix('repo.')}.json"}) or manifest
        ),
    )
    lifecycle_spec = copy.deepcopy(specs["repo.validation"])
    lifecycle_spec["spec_id"] = spec_id
    lifecycle_spec["title"] = "Lifecycle Test"
    lifecycle_spec["purpose"] = "Lifecycle test specification"
    lifecycle_spec["status"] = status
    lifecycle_spec["derived_artifacts"][0]["path"] = f"derived/specs/repo/{spec_id.removeprefix('repo.')}.md"
    if supersedes is not None:
        lifecycle_spec["supersedes"] = supersedes
    if superseded_by is not None:
        lifecycle_spec["superseded_by"] = superseded_by
    (temp_repo / f"specs/repo/{spec_id.removeprefix('repo.')}.json").write_text(json.dumps(lifecycle_spec, indent=2) + "\n")
