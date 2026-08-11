from __future__ import annotations

import copy
import json
import shutil
from pathlib import Path

from validation.errors import ValidationFailure, fail
from validation.repository_checks import extract_document_metadata


def deactivate_product_plans(repo_root: Path) -> None:
    """Make copied product plans non-active for fixtures that replace the product registry."""
    plans_root = repo_root / "product/docs/plans"
    if not plans_root.is_dir():
        return
    for plan_path in sorted(plans_root.glob("*.md")):
        text = plan_path.read_text()
        accepted = '"lifecycle_status": "accepted"'
        if accepted in text:
            plan_path.write_text(
                text.replace(accepted, '"lifecycle_status": "candidate"', 1)
            )


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
        "repo/schemas/repo/product-overview.schema.json",
        "repo/schemas/repo/product-decomposition.schema.json",
        "repo/schemas/repo/implementation-plan.schema.json",
        "repo/schemas/repo/architecture-plan.schema.json",
        "product/schemas/product/product-manifest.schema.json",
        "product/schemas/product/product-spec-base.schema.json",
        "product/schemas/product/product-level-0.schema.json",
        "product/schemas/product/product-level-1.schema.json",
        "product/schemas/product/product-level-2.schema.json",
        "product/schemas/product/product-level-3.schema.json",
    ]
    for root_rel in ("repo/docs/overview/", "repo/docs/decompositions/", "repo/docs/plans/", "repo/docs/architecture/"):
        root = repo_root / root_rel
        for path in sorted(root.glob("*.md")):
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
                for ref_path in ref_paths:
                    required_paths.append(ref_path)
            for chunk in metadata.get("subordinate_chunks", []):
                required_paths.append(chunk["path"])
            required_paths.extend(metadata.get("evidence", []))
    for entry in manifest["authoritative_specs"]:
        path = entry["path"]
        required_paths.append(path)
        spec = json.loads((repo_root / path).read_text())
        for ref in spec.get("references", []):
            if ref.get("type") == "artifact":
                required_paths.append(ref["path"])
        for artifact in spec.get("derived_artifacts", []):
            required_paths.append(artifact["path"])

    for root_name in ("product/src", "product/tests"):
        root = repo_root / root_name
        if root.exists():
            required_paths.extend(
                path.relative_to(repo_root).as_posix()
                for path in root.rglob("*")
                if path.is_file()
            )

    product_docs_root = repo_root / "product/docs"
    if product_docs_root.exists():
        product_doc_paths = [
            path for path in product_docs_root.rglob("*") if path.is_file()
        ]
        required_paths.extend(
            path.relative_to(repo_root).as_posix() for path in product_doc_paths
        )
        for path in product_doc_paths:
            if path.suffix != ".md":
                continue
            document_text = path.read_text()
            if "## Metadata" not in document_text:
                continue
            document_metadata = extract_document_metadata(
                document_text,
                path.relative_to(repo_root).as_posix(),
            )
            required_paths.extend(document_metadata.get("evidence", []))

    for root_name in ("repo/profiles", ".github"):
        root = repo_root / root_name
        if root.exists():
            required_paths.extend(
                path.relative_to(repo_root).as_posix()
                for path in root.rglob("*")
                if path.is_file()
            )

    product_manifest_path = repo_root / "product/specs/product/manifest.json"
    if product_manifest_path.exists():
        product_manifest = json.loads(product_manifest_path.read_text())
        for entry in product_manifest.get("product_specifications", []):
            spec = json.loads((repo_root / entry["path"]).read_text())
            correspondence = spec.get("correspondence", {})
            for collection_name in ("implementations", "tests"):
                for mapping in correspondence.get(collection_name, []):
                    required_paths.extend(mapping.get("paths", []))
    return tuple(dict.fromkeys(required_paths))


REQUIRED_FIXTURE_ROOT_FILES = (".gitignore", "AGENTS.md", "LICENSE", "README.md")
REQUIRED_FIXTURE_ROOT_DIRECTORIES = (".github", "product", "reference", "repo", "scripts", "user")


def create_repo_fixture(repo_root: Path, temp_root: Path, fixture_index: int, required_paths: tuple[str, ...] | None = None) -> Path:
    fixture_root = temp_root / f"fixture-{fixture_index}"
    fixture_root.mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_FIXTURE_ROOT_DIRECTORIES:
        (fixture_root / name).mkdir(parents=True, exist_ok=True)
    for name in REQUIRED_FIXTURE_ROOT_FILES:
        shutil.copy2(repo_root / name, fixture_root / name)
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
