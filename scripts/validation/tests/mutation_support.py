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


def clone_repo(repo_root: Path, temp_root: Path, clone_index: int) -> Path:
    clone_root = temp_root / f"clone-{clone_index}"
    shutil.copytree(
        repo_root,
        clone_root,
        ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
    )
    return clone_root


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
