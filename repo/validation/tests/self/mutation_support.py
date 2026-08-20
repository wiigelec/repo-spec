"""Shared support for mutation-oriented validation self-tests."""

from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from validation.core.errors import ValidationFailure, fail
from validation.checks.development_documents import extract_document_metadata




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
    manifest = json.loads((repo_root / "repo/specs/repo/manifest.json").read_text())

    required_paths = [
        "repo/specs/repo/manifest.json",
        "repo/schemas/repo-manifest.schema.json",
        "repo/schemas/repo-artifact-taxonomy.schema.json",
        "repo/schemas/repo-platform-profiles.schema.json",
        "repo/schemas/repo-spec.schema.json",
        "repo/schemas/repo/development-document-base.schema.json",
        "repo/schemas/repo/functional-set-process.schema.json",
        "repo/schemas/repo/product-decomposition.schema.json",
        "repo/schemas/repo/implementation-plan.schema.json",
    ]

    for root_rel in (
        "repo/docs/overview/",
        "repo/docs/decompositions/",
        "repo/docs/plans/",
    ):
        docs_root = repo_root / root_rel
        if not docs_root.exists():
            continue
        for path in sorted(docs_root.glob("*.md")):
            required_paths.append(path.relative_to(repo_root).as_posix())
            if path.name == "README.md":
                continue
            text = path.read_text()
            if "## Metadata" not in text:
                continue
            metadata = extract_document_metadata(
                text,
                path.relative_to(repo_root).as_posix(),
            )
            for ref_paths in metadata.get("required_content_areas", {}).values():
                required_paths.extend(ref_paths)
            for chunk in metadata.get("subordinate_chunks", []):
                required_paths.append(chunk["path"])
            required_paths.extend(metadata.get("evidence", []))

    for entry in manifest["authoritative_specs"]:
        relative_path = entry["path"]
        required_paths.append(relative_path)
        spec = json.loads((repo_root / relative_path).read_text())

        for ref in spec.get("references", []):
            if ref.get("type") == "artifact":
                required_paths.append(ref["path"])

        for artifact in spec.get("derived_artifacts", []):
            required_paths.append(artifact["path"])

    profiles_root = repo_root / "repo/profiles"
    if profiles_root.exists():
        required_paths.extend(
            path.relative_to(repo_root).as_posix()
            for path in profiles_root.rglob("*")
            if path.is_file()
        )

    repo_only = [
        path
        for path in required_paths
        if path == "repo" or path.startswith("repo/")
    ]
    return tuple(dict.fromkeys(repo_only))


REQUIRED_FIXTURE_ROOT_FILES: tuple[str, ...] = ()
REQUIRED_FIXTURE_ROOT_DIRECTORIES = ("repo",)


def create_repo_fixture(repo_root: Path, temp_root: Path, fixture_index: int, required_paths: tuple[str, ...] | None = None) -> Path:
    fixture_root = temp_root / f"fixture-{fixture_index}"
    fixture_root.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_FIXTURE_ROOT_DIRECTORIES:
        (fixture_root / name).mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_FIXTURE_ROOT_FILES:
        shutil.copy2(repo_root / name, fixture_root / name)
    if required_paths is None:
        required_paths = declared_repo_fixture_paths(repo_root)

    # Repository validation is itself part of the exact validated structure.
    # Every mutation fixture must start with a canonical repo/validation tree.
    source_root = fixture_root / "repo/src"
    source_root.mkdir(parents=True, exist_ok=True)

    source_scripts = repo_root / "repo/scripts"
    target_scripts = fixture_root / "repo/scripts"
    if not source_scripts.is_dir():
        fail("repository mutation fixture failed: source repo/scripts is missing")
    shutil.copytree(
        source_scripts,
        target_scripts,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )

    source_validation = repo_root / "repo/validation"
    target_validation = fixture_root / "repo/validation"
    if not source_validation.is_dir():
        fail("repository mutation fixture failed: source repo/validation is missing")
    shutil.copytree(
        source_validation,
        target_validation,
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo"),
    )

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
        temp_repo / "repo/specs/repo/manifest.json",
        lambda manifest: (
            manifest["authoritative_specs"].append({"spec_id": spec_id, "path": f"repo/specs/repo/{spec_id.removeprefix('repo.')}.json"}) or manifest
        ),
    )
    lifecycle_spec = copy.deepcopy(specs["repo.validation"])
    lifecycle_spec["spec_id"] = spec_id
    lifecycle_spec["title"] = "Lifecycle Test"
    lifecycle_spec["purpose"] = "Lifecycle test specification"
    lifecycle_spec["status"] = status
    lifecycle_spec["derived_artifacts"][0]["path"] = f"repo/derived/specs/repo/{spec_id.removeprefix('repo.')}.md"
    if supersedes is not None:
        lifecycle_spec["supersedes"] = supersedes
    if superseded_by is not None:
        lifecycle_spec["superseded_by"] = superseded_by
    (temp_repo / f"repo/specs/repo/{spec_id.removeprefix('repo.')}.json").write_text(json.dumps(lifecycle_spec, indent=2) + "\n")
