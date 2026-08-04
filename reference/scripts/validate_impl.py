#!/usr/bin/env python3

from __future__ import annotations

import io
import json
import shutil
import sys
import unittest
import tempfile
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
    "scripts/generate-docs",
    "scripts/generate_docs.py",
    "specs/product/manifest.json",
    "specs/product/level-0/kernel.json",
    "specs/product/level-1/primitives.json",
    "derived/specs/product/level-0/kernel.md",
    "derived/specs/product/level-1/primitives.md",
    "schemas/product/product-manifest.schema.json",
    "schemas/product/product-spec-base.schema.json",
    "schemas/product/product-level-0.schema.json",
    "schemas/product/product-level-1.schema.json",
    "src/__init__.py",
    "src/product/__init__.py",
    "src/product/kernel.py",
    "src/product/primitives.py",
    "tests/__init__.py",
    "tests/test_kernel.py",
    "tests/test_primitives.py",
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


def render_collection(title: str, records: list[dict], key: str, path_key: str = "paths") -> list[str]:
    lines = [f"### {title}", ""]
    if not records:
        lines.extend(["- None", ""])
        return lines
    for record in records:
        lines.append(f"- `{record[key]}`")
        lines.append("  - Paths:")
        for path in record.get(path_key, []):
            lines.append(f"    - `{path}`")
        lines.append("  - Requirements:")
        for requirement in record.get("requirements", []):
            lines.append(f"    - `{requirement}`")
        lines.append("")
    return lines


def render_conformance(records: list[dict]) -> list[str]:
    lines = ["### Conformance", ""]
    if not records:
        lines.extend(["- None", ""])
        return lines
    for record in records:
        lines.append(f"- `{record['requirement_id']}`")
        lines.append(f"  - Status: `{record['status']}`")
        lines.append("  - Implementation ids:")
        for item in record.get("implementation_ids", []):
            lines.append(f"    - `{item}`")
        lines.append("  - Test ids:")
        for item in record.get("test_ids", []):
            lines.append(f"    - `{item}`")
        lines.append("")
    return lines


def render_projection(spec: dict) -> str:
    requirements = spec.get("normative_requirements", [])
    deps = spec.get("dependencies", [])
    correspondence = spec.get("correspondence", {})
    dependency_lines = ["- None"] if not deps else [f"- `{dep['spec_id']}`" for dep in deps]
    requirement_lines = ["- None"] if not requirements else [f"- `{req['id']}`: {req['text']}" for req in requirements]
    lines = [
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
        "## Correspondence",
        "",
        *render_collection("Implementations", correspondence.get("implementations", []), "id"),
        *render_collection("Tests", correspondence.get("tests", []), "id"),
        *render_conformance(correspondence.get("conformance", [])),
    ]
    return "\n".join(lines)


def validate_schema(path: Path, required_fields: list[str], const_level: int | None = None) -> None:
    schema = load_json(path)
    expect(schema.get("type") == "object", f"schema {path} must be an object schema")
    expect(schema.get("required") == required_fields, f"schema {path} has unexpected required fields")
    if const_level is not None:
        expect(schema.get("properties", {}).get("level", {}).get("const") == const_level, f"schema {path} must constrain level to {const_level}")


def validate_conformance(spec: dict) -> None:
    requirements = spec.get("normative_requirements", [])
    correspondence = spec.get("correspondence", {})
    requirement_ids = [req["id"] for req in requirements]
    implementation_ids = {item["id"]: item for item in correspondence.get("implementations", [])}
    test_ids = {item["id"]: item for item in correspondence.get("tests", [])}
    conformance_records = correspondence.get("conformance", [])
    expect(len(requirements) == 1, f"{spec['spec_id']} must have exactly one accepted requirement for this issue")
    expect(len(conformance_records) == 1, f"{spec['spec_id']} must have exactly one conformance record")
    requirement_id = requirement_ids[0]
    impl = next(iter(implementation_ids.values()))
    test = next(iter(test_ids.values()))
    expect(impl["requirements"] == [requirement_id], f"{spec['spec_id']} implementation mapping must point at the requirement")
    expect(test["requirements"] == [requirement_id], f"{spec['spec_id']} test mapping must point at the requirement")
    record = conformance_records[0]
    expect(record["requirement_id"] == requirement_id, f"{spec['spec_id']} conformance record must target the requirement")
    expect(record["implementation_ids"] == [impl["id"]], f"{spec['spec_id']} conformance record must reference the implementation mapping")
    expect(record["test_ids"] == [test["id"]], f"{spec['spec_id']} conformance record must reference the test mapping")
    expect(record["status"] == "covered", f"{spec['spec_id']} conformance record must be covered")


def validate_product_spec(spec_path: Path, expected_level: int) -> dict:
    spec = load_json(spec_path)
    expect(spec.get("schema_version") == "1", f"{spec_path} must use schema_version 1")
    expect(spec.get("status") == "accepted", f"{spec_path} must be accepted")
    expect(spec.get("level") == expected_level, f"{spec_path} must declare level {expected_level}")
    expect(len(spec.get("normative_requirements", [])) == 1, f"{spec_path} must declare exactly one requirement")
    expect(spec.get("supersedes") == [], f"{spec_path} must have empty supersedes")
    expect(spec.get("superseded_by") == [], f"{spec_path} must have empty superseded_by")
    correspondence = spec.get("correspondence")
    expect(isinstance(correspondence, dict), f"{spec_path} must declare correspondence as an object")
    expect(len(correspondence.get("implementations", [])) == 1, f"{spec_path} must declare exactly one implementation mapping")
    expect(len(correspondence.get("tests", [])) == 1, f"{spec_path} must declare exactly one test mapping")
    expect(len(correspondence.get("conformance", [])) == 1, f"{spec_path} must declare exactly one conformance record")
    derived = spec.get("derived_artifacts", [])
    expect(len(derived) == 1, f"{spec_path} must declare exactly one derived artifact")
    expect(derived[0].get("type") == "markdown", f"{spec_path} must declare a markdown derived artifact")
    validate_conformance(spec)
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


def write_generated_docs(repo_root: Path) -> None:
    import importlib.util

    script_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("reference_generate_docs", script_dir / "generate_docs.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.write_generated_docs(repo_root)


def expect_subprocess_failure(description: str, repo_root: Path, fragment: str, extra_args: list[str] | None = None) -> None:
    import subprocess

    args = [str(repo_root / "scripts/validate")]
    if extra_args:
        args.extend(extra_args)
    result = subprocess.run(args, capture_output=True, text=True)
    expect(result.returncode != 0, f"mutation test failed: {description} did not fail")
    expect(fragment in result.stderr, f"mutation test failed: {description} (expected {fragment!r}, got {result.stderr!r})")


def run_mutation_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="reference-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        temp_repo = temp_root / "reference"
        shutil.copytree(repo_root, temp_repo)

        kernel_source = temp_repo / "src/product/kernel.py"
        kernel_source.write_text(kernel_source.read_text().replace('return "reference-kernel"', 'return "broken-kernel"', 1))
        expect_subprocess_failure("kernel source behavior", temp_repo, "kernel source behavior")

        temp_repo = temp_root / "reference"
        shutil.rmtree(temp_repo)
        shutil.copytree(repo_root, temp_repo)
        mutate = load_json(temp_repo / "specs/product/manifest.json")
        mutate["product_specifications"][1]["level"] = 0
        (temp_repo / "specs/product/manifest.json").write_text(json.dumps(mutate, indent=2) + "\n")
        expect_subprocess_failure("product manifest level mismatch", temp_repo, "level")

        temp_repo = temp_root / "reference"
        shutil.rmtree(temp_repo)
        shutil.copytree(repo_root, temp_repo)
        projection = temp_repo / "derived/specs/product/level-1/primitives.md"
        projection.write_text(projection.read_text().replace("reference-kernel-primitives", "tampered-reference", 1))
        expect_subprocess_failure("projection freshness", temp_repo, "projection freshness mismatch")


def run_tests(root: Path) -> None:
    sys.path.insert(0, str(root / "src"))
    suite = unittest.defaultTestLoader.discover(str(root / "tests"), pattern="test_*.py")
    buffer = io.StringIO()
    result = unittest.TextTestRunner(stream=buffer, verbosity=0).run(suite)
    if not result.wasSuccessful():
        print(buffer.getvalue(), file=sys.stderr)
        fail("reference product tests failed")


def validate_source(root: Path) -> None:
    sys.path.insert(0, str(root / "src"))
    from product.kernel import kernel_identity
    from product.primitives import primitive_identity

    expect(kernel_identity() == "reference-kernel", "kernel source behavior must return the kernel identity")
    expect(primitive_identity() == "reference-kernel-primitives", "primitive source behavior must return the primitive identity")


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    mode = argv[2] if len(argv) > 2 else "--write"

    if mode == "--mutation-tests":
        run_mutation_tests(root)
        print("ok: reference mutation tests")
        return 0

    check_required_paths(root)
    validate_repo_support(root)
    validate_source(root)
    run_tests(root)

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
