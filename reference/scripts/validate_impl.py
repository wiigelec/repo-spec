#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


REPO_REQUIRED_PATHS = [
    "README.md",
    "AGENTS.md",
    "docs/overview/REFERENCE-OVERVIEW.md",
    "docs/plans/01-reference-repository-plan.md",
    "specs/repo/manifest.json",
    "specs/repo/governing-issue.json",
    "specs/repo/review-proposal.json",
    "specs/repo/repository-structure.json",
    "specs/repo/artifact-taxonomy.json",
    "specs/repo/platform-profiles.json",
    "specs/repo/development-workflow.json",
    "specs/repo/validation.json",
    "schemas/repo-manifest.schema.json",
    "schemas/repo-spec.schema.json",
    "schemas/repo-artifact-taxonomy.schema.json",
    "schemas/repo-platform-profiles.schema.json",
    "schemas/repo-validation.schema.json",
    "profiles/github/README.md",
    "profiles/github/manifest.json",
    "scripts/validate",
    "specs/product/manifest.json",
    "specs/product/level-0/kernel.json",
    "specs/product/level-1/primitives.json",
    "derived/specs/product/level-0/kernel.md",
    "derived/specs/product/level-1/primitives.md",
    "schemas/product/product-manifest.schema.json",
    "schemas/product/product-spec-base.schema.json",
    "schemas/product/product-level-0.schema.json",
    "schemas/product/product-level-1.schema.json",
]


def fail(message: str) -> None:
    print(f"validation error: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except FileNotFoundError:
        fail(f"missing required file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON in {path}: {exc}")


def load_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        fail(f"missing required file: {path}")


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def check_required_paths(root: Path) -> None:
    missing = [path for path in REPO_REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        fail("missing required reference paths: " + ", ".join(missing))


def render_projection(spec: dict) -> str:
    requirements = spec.get("normative_requirements", [])
    deps = spec.get("dependencies", [])
    dependency_lines = ["- None"] if not deps else [f"- `{dep['spec_id']}`" for dep in deps]
    requirement_lines = ["- None"] if not requirements else [f"- `{req['id']}`: {req['text']}" for req in requirements]
    return "\n".join(
        [
            f"# {spec['title']}",
            "",
            "## Status",
            "",
            spec["status"],
            "",
            "## Level",
            "",
            str(spec["level"]),
            "",
            "## Purpose",
            "",
            spec["purpose"],
            "",
            "## Normative requirements",
            "",
            *requirement_lines,
            "",
            "## Dependencies",
            "",
            *dependency_lines,
            "",
        ]
    )


def validate_schema(path: Path, required_fields: list[str], const_level: int | None = None) -> None:
    schema = load_json(path)
    expect(schema.get("type") == "object", f"schema {path} must be an object schema")
    expect(schema.get("required") == required_fields, f"schema {path} has unexpected required fields")
    if const_level is not None:
        expect(schema.get("properties", {}).get("level", {}).get("const") == const_level, f"schema {path} must constrain level to {const_level}")


def validate_product_spec(spec_path: Path, expected_level: int) -> dict:
    spec = load_json(spec_path)
    expect(spec.get("schema_version") == "1", f"{spec_path} must use schema_version 1")
    expect(spec.get("status") == "accepted", f"{spec_path} must be accepted")
    expect(spec.get("level") == expected_level, f"{spec_path} must declare level {expected_level}")
    expect(spec.get("normative_requirements") == [], f"{spec_path} must keep normative requirements empty for this issue")
    expect(spec.get("supersedes") == [], f"{spec_path} must have empty supersedes")
    expect(spec.get("superseded_by") == [], f"{spec_path} must have empty superseded_by")
    correspondence = spec.get("correspondence")
    expect(isinstance(correspondence, dict), f"{spec_path} must declare correspondence as an object")
    expect(correspondence.get("implementations") == [], f"{spec_path} must keep implementation correspondence empty")
    expect(correspondence.get("tests") == [], f"{spec_path} must keep test correspondence empty")
    expect(correspondence.get("conformance") == [], f"{spec_path} must keep conformance correspondence empty")
    derived = spec.get("derived_artifacts", [])
    expect(len(derived) == 1, f"{spec_path} must declare exactly one derived artifact")
    expect(derived[0].get("type") == "markdown", f"{spec_path} must declare a markdown derived artifact")
    return spec


def validate_level_0(spec: dict) -> None:
    expect(spec.get("dependencies") == [], "Level 0 spec must not depend on higher-level product specs")
    references = spec.get("references", [])
    expect(any(ref.get("type") == "artifact" and ref.get("path") == "docs/overview/REFERENCE-OVERVIEW.md" for ref in references), "Level 0 spec must reference the reference overview")


def validate_level_1(spec: dict) -> None:
    deps = spec.get("dependencies", [])
    expect([dep.get("spec_id") for dep in deps] == ["product.kernel"], "Level 1 spec must depend on the Level 0 kernel")
    references = spec.get("references", [])
    expect(any(ref.get("type") == "specification" and ref.get("spec_id") == "product.kernel" for ref in references), "Level 1 spec must reference the Level 0 kernel")


def validate_manifest(root: Path) -> dict[str, dict]:
    manifest = load_json(root / "specs/product/manifest.json")
    expect(manifest.get("spec_id") == "product.manifest", "product manifest must use the `product.manifest` identity")
    expect(manifest.get("status") == "accepted", "product manifest must be accepted")
    expect(manifest.get("schema_version") == "1", "product manifest must use schema_version 1")
    entries = manifest.get("product_specifications")
    expect(isinstance(entries, list), "product manifest must declare product_specifications as a list")
    expect(len(entries) == 2, "product manifest must register exactly two product specifications")

    specs_by_id: dict[str, dict] = {}
    for entry in entries:
        spec_id = entry.get("spec_id")
        path_text = entry.get("path")
        status = entry.get("status")
        level = entry.get("level")
        expect(spec_id in {"product.kernel", "product.primitives"}, f"unexpected product spec identity: {spec_id}")
        expect(status == "accepted", f"manifest entry {spec_id} must be accepted")
        expect(level in {0, 1}, f"manifest entry {spec_id} must declare level 0 or 1")
        expect(path_text in {"specs/product/level-0/kernel.json", "specs/product/level-1/primitives.json"}, f"unexpected product path: {path_text}")
        spec_path = root / path_text
        expect(spec_path.exists(), f"manifest entry path must exist: {path_text}")
        spec = validate_product_spec(spec_path, level)
        expect(spec.get("spec_id") == spec_id, f"manifest entry {spec_id} must match the product spec identity")
        expect(spec.get("status") == status, f"manifest entry {spec_id} status must match the product spec")
        specs_by_id[spec_id] = spec

    discovered = sorted(str(path.relative_to(root)) for path in root.glob("specs/product/level-*/*.json"))
    expect(discovered == ["specs/product/level-0/kernel.json", "specs/product/level-1/primitives.json"], "product manifest must enumerate every product specification present under the reserved roots")
    return specs_by_id


def validate_product_schemas(root: Path) -> None:
    validate_schema(
        root / "schemas/product/product-manifest.schema.json",
        ["spec_id", "title", "purpose", "status", "schema_version", "product_specifications"],
    )
    validate_schema(
        root / "schemas/product/product-spec-base.schema.json",
        [
            "spec_id",
            "title",
            "purpose",
            "status",
            "schema_version",
            "level",
            "normative_requirements",
            "dependencies",
            "references",
            "supersedes",
            "superseded_by",
            "derived_artifacts",
            "correspondence",
        ],
    )
    validate_schema(root / "schemas/product/product-level-0.schema.json", [], 0)
    validate_schema(root / "schemas/product/product-level-1.schema.json", [], 1)


def validate_projection(root: Path, spec: dict, relpath: str) -> None:
    projection_path = root / relpath
    actual = load_text(projection_path)
    expected = render_projection(spec)
    expect(actual == expected, f"projection freshness mismatch for {relpath}")


def validate_repo_support(root: Path) -> None:
    for relpath in [
        "specs/repo/manifest.json",
        "specs/repo/governing-issue.json",
        "specs/repo/review-proposal.json",
        "specs/repo/repository-structure.json",
        "specs/repo/artifact-taxonomy.json",
        "specs/repo/platform-profiles.json",
        "specs/repo/development-workflow.json",
        "specs/repo/validation.json",
        "profiles/github/manifest.json",
    ]:
        load_json(root / relpath)


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()

    check_required_paths(root)
    validate_repo_support(root)

    specs_by_id = validate_manifest(root)
    validate_level_0(specs_by_id["product.kernel"])
    validate_level_1(specs_by_id["product.primitives"])
    validate_product_schemas(root)
    expect(specs_by_id["product.kernel"]["derived_artifacts"][0]["path"] == "derived/specs/product/level-0/kernel.md", "Level 0 derived artifact path must match the projection path")
    expect(specs_by_id["product.primitives"]["derived_artifacts"][0]["path"] == "derived/specs/product/level-1/primitives.md", "Level 1 derived artifact path must match the projection path")
    validate_projection(root, specs_by_id["product.kernel"], "derived/specs/product/level-0/kernel.md")
    validate_projection(root, specs_by_id["product.primitives"], "derived/specs/product/level-1/primitives.md")

    print("ok: reference product layer validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
