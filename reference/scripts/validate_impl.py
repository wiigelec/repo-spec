#!/usr/bin/env python3

from __future__ import annotations

import io
import json
import shutil
import re
import sys
import unittest
import tempfile
from pathlib import Path
from typing import Any


SUPPORTED_SCHEMA_KEYS = {
    "$schema",
    "$id",
    "title",
    "type",
    "additionalProperties",
    "unevaluatedProperties",
    "required",
    "properties",
    "items",
    "$ref",
    "$defs",
    "allOf",
    "oneOf",
    "if",
    "then",
    "else",
    "enum",
    "const",
    "minLength",
    "pattern",
}

SUPPORTED_SCHEMA_TYPES = {"object", "array", "string", "boolean", "integer"}


class ValidationFailure(Exception):
    pass


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
    raise ValidationFailure(message)


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


def schema_location(source: str, path: str) -> str:
    return source if not path else f"{source}{path}"


def instance_location(source: str, path: str) -> str:
    return source if not path else f"{source} {path}"


def resolve_ref(root_schema: dict[str, Any], ref: str, source: str) -> Any:
    expect(ref.startswith("#/$defs/"), f"schema loading failed: {source} unsupported ref {ref}")
    parts = ref.removeprefix("#/").split("/")
    node: Any = root_schema
    for part in parts:
        expect(isinstance(node, dict) and part in node, f"schema loading failed: {source} unresolved ref {ref}")
        node = node[part]
    return node


def ensure_schema_keywords(schema: Any, source: str, path: str = "", root_schema: Any | None = None) -> None:
    expect(isinstance(schema, dict), f"schema loading failed: {schema_location(source, path)} must be an object")
    if root_schema is None:
        root_schema = schema
    for key in schema:
        if key not in SUPPORTED_SCHEMA_KEYS:
            fail(f"unsupported schema keyword: {schema_location(source, path)} {key}")

    if "type" in schema:
        expect(isinstance(schema["type"], str), f"schema loading failed: {schema_location(source, path)} type must be a string")
        expect(schema["type"] in SUPPORTED_SCHEMA_TYPES, f"schema loading failed: {schema_location(source, path)} unsupported type {schema['type']}")

    if "additionalProperties" in schema:
        expect(isinstance(schema["additionalProperties"], bool), f"schema loading failed: {schema_location(source, path)} additionalProperties must be a boolean")

    if "unevaluatedProperties" in schema:
        expect(isinstance(schema["unevaluatedProperties"], bool), f"schema loading failed: {schema_location(source, path)} unevaluatedProperties must be a boolean")

    if "required" in schema:
        expect(isinstance(schema["required"], list), f"schema loading failed: {schema_location(source, path)} required must be an array")
        for index, item in enumerate(schema["required"]):
            expect(isinstance(item, str), f"schema loading failed: {schema_location(source, path)} required[{index}] must be a string")

    if "properties" in schema:
        expect(isinstance(schema["properties"], dict), f"schema loading failed: {schema_location(source, path)} properties must be an object")
        for name, subschema in schema["properties"].items():
            ensure_schema_keywords(subschema, source, f"{path}/properties/{name}", root_schema)

    if "items" in schema:
        ensure_schema_keywords(schema["items"], source, f"{path}/items", root_schema)

    if "$defs" in schema:
        expect(isinstance(schema["$defs"], dict), f"schema loading failed: {schema_location(source, path)} $defs must be an object")
        for name, subschema in schema["$defs"].items():
            ensure_schema_keywords(subschema, source, f"{path}/$defs/{name}", root_schema)

    if "allOf" in schema:
        expect(isinstance(schema["allOf"], list), f"schema loading failed: {schema_location(source, path)} allOf must be an array")
        for index, subschema in enumerate(schema["allOf"]):
            ensure_schema_keywords(subschema, source, f"{path}/allOf/{index}", root_schema)

    if "oneOf" in schema:
        expect(isinstance(schema["oneOf"], list), f"schema loading failed: {schema_location(source, path)} oneOf must be an array")
        for index, subschema in enumerate(schema["oneOf"]):
            ensure_schema_keywords(subschema, source, f"{path}/oneOf/{index}", root_schema)

    for branch in ("if", "then", "else"):
        if branch in schema:
            ensure_schema_keywords(schema[branch], source, f"{path}/{branch}", root_schema)

    if "enum" in schema:
        expect(isinstance(schema["enum"], list), f"schema loading failed: {schema_location(source, path)} enum must be an array")

    if "minLength" in schema:
        expect(isinstance(schema["minLength"], int) and schema["minLength"] >= 0, f"schema loading failed: {schema_location(source, path)} minLength must be a non-negative integer")

    if "pattern" in schema:
        expect(isinstance(schema["pattern"], str), f"schema loading failed: {schema_location(source, path)} pattern must be a string")
        re.compile(schema["pattern"])

    if "$ref" in schema:
        expect(isinstance(schema["$ref"], str), f"schema loading failed: {schema_location(source, path)} $ref must be a string")
        resolve_ref(root_schema, schema["$ref"], source)


def validate_instance(
    instance: Any,
    schema: dict[str, Any],
    source: str,
    root_schema: dict[str, Any],
    path: str = "",
    ref_stack: tuple[str, ...] = (),
) -> None:
    if "$ref" in schema:
        ref = schema["$ref"]
        expect(ref not in ref_stack, f"reference validation failed: {instance_location(source, path)} circular ref {ref}")
        validate_instance(instance, resolve_ref(root_schema, ref, source), source, root_schema, path, ref_stack + (ref,))
        return

    evaluated_keys: set[str] = set()

    schema_type = schema.get("type")
    if schema_type == "object":
        expect(isinstance(instance, dict), f"reference validation failed: {instance_location(source, path)} must be an object")
    elif schema_type == "array":
        expect(isinstance(instance, list), f"reference validation failed: {instance_location(source, path)} must be an array")
    elif schema_type == "string":
        expect(isinstance(instance, str), f"reference validation failed: {instance_location(source, path)} must be a string")
    elif schema_type == "boolean":
        expect(isinstance(instance, bool), f"reference validation failed: {instance_location(source, path)} must be a boolean")
    elif schema_type == "integer":
        expect(isinstance(instance, int) and not isinstance(instance, bool), f"reference validation failed: {instance_location(source, path)} must be an integer")

    if "enum" in schema:
        expect(instance in schema["enum"], f"reference validation failed: {instance_location(source, path)} enum mismatch")

    if "const" in schema:
        expect(instance == schema["const"], f"reference validation failed: {instance_location(source, path)} const mismatch")

    if "minLength" in schema:
        expect(isinstance(instance, str), f"reference validation failed: {instance_location(source, path)} must be a string")
        expect(len(instance) >= schema["minLength"], f"reference validation failed: {instance_location(source, path)} minLength violation")

    if "pattern" in schema:
        expect(isinstance(instance, str), f"reference validation failed: {instance_location(source, path)} must be a string")
        expect(re.fullmatch(schema["pattern"], instance) is not None, f"reference validation failed: {instance_location(source, path)} pattern mismatch")

    if "required" in schema:
        expect(isinstance(instance, dict), f"reference validation failed: {instance_location(source, path)} must be an object")
        for required_key in schema["required"]:
            expect(required_key in instance, f"reference validation failed: {instance_location(source, path)} missing required property {required_key}")

    if "properties" in schema:
        expect(isinstance(instance, dict), f"reference validation failed: {instance_location(source, path)} must be an object")
        for key, subschema in schema["properties"].items():
            if key in instance:
                validate_instance(instance[key], subschema, source, root_schema, f"{path}.{key}" if path else key, ref_stack)
                evaluated_keys.add(key)

    if "additionalProperties" in schema and schema["additionalProperties"] is False:
        expect(isinstance(instance, dict), f"reference validation failed: {instance_location(source, path)} must be an object")
        allowed = set(schema.get("properties", {}))
        extra = [key for key in instance if key not in allowed]
        expect(not extra, f"reference validation failed: {instance_location(source, path)} additionalProperties disallowed: {', '.join(extra)}")

    if "items" in schema:
        expect(isinstance(instance, list), f"reference validation failed: {instance_location(source, path)} must be an array")
        for index, item in enumerate(instance):
            validate_instance(item, schema["items"], source, root_schema, f"{path}[{index}]" if path else f"[{index}]", ref_stack)

    if "allOf" in schema:
        for subschema in schema["allOf"]:
            validate_instance(instance, subschema, source, root_schema, path, ref_stack)

    if "oneOf" in schema:
        matches = 0
        for subschema in schema["oneOf"]:
            try:
                validate_instance(instance, subschema, source, root_schema, path, ref_stack)
            except ValidationFailure:
                continue
            matches += 1
        expect(matches == 1, f"reference validation failed: {instance_location(source, path)} oneOf mismatch")

    if "if" in schema:
        branch = schema.get("then") if schema_matches(instance, schema["if"], source, root_schema, path, ref_stack) else schema.get("else")
        if branch is not None:
            validate_instance(instance, branch, source, root_schema, path, ref_stack)


def schema_matches(instance: Any, schema: dict[str, Any], source: str, root_schema: dict[str, Any], path: str, ref_stack: tuple[str, ...]) -> bool:
    try:
        validate_instance(instance, schema, source, root_schema, path, ref_stack)
        return True
    except ValidationFailure:
        return False


def load_schema(path: Path) -> dict[str, Any]:
    return load_json(path)


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


def load_reference_schemas(repo_root: Path) -> dict[str, dict[str, Any]]:
    schemas = {
        "repo.manifest": load_schema(repo_root / "schemas/repo-manifest.schema.json"),
        "repo.spec": load_schema(repo_root / "schemas/repo-spec.schema.json"),
        "repo.artifact-taxonomy": load_schema(repo_root / "schemas/repo-artifact-taxonomy.schema.json"),
        "repo.platform-profiles": load_schema(repo_root / "schemas/repo-platform-profiles.schema.json"),
        "repo.validation": load_schema(repo_root / "schemas/repo-validation.schema.json"),
        "product.manifest": load_schema(repo_root / "schemas/product/product-manifest.schema.json"),
        "product.spec-base": load_schema(repo_root / "schemas/product/product-spec-base.schema.json"),
        "product.level-0": load_schema(repo_root / "schemas/product/product-level-0.schema.json"),
        "product.level-1": load_schema(repo_root / "schemas/product/product-level-1.schema.json"),
    }
    for schema_name, schema in schemas.items():
        ensure_schema_keywords(schema, f"schemas/{schema_name}.schema.json")
    return schemas


def validate_declared_json_files(repo_root: Path, schemas: dict[str, dict[str, Any]]) -> None:
    validate_instance(load_json(repo_root / "specs/repo/manifest.json"), schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"])

    for relpath in [
        "specs/repo/governing-issue.json",
        "specs/repo/review-proposal.json",
        "specs/repo/repository-structure.json",
        "specs/repo/development-workflow.json",
        "specs/repo/validation.json",
        "specs/repo/artifact-taxonomy.json",
        "specs/repo/platform-profiles.json",
    ]:
        validate_instance(load_json(repo_root / relpath), schemas["repo.spec"], relpath, schemas["repo.spec"])

    validate_instance(load_json(repo_root / "specs/product/manifest.json"), schemas["product.manifest"], "specs/product/manifest.json", schemas["product.manifest"])
    validate_instance(load_json(repo_root / "specs/product/level-0/kernel.json"), schemas["product.level-0"], "specs/product/level-0/kernel.json", schemas["product.level-0"])
    validate_instance(load_json(repo_root / "specs/product/level-1/primitives.json"), schemas["product.level-1"], "specs/product/level-1/primitives.json", schemas["product.level-1"])


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
        expect_subprocess_failure("product manifest level mismatch", temp_repo, "oneOf mismatch")

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
    try:
        root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
        mode = argv[2] if len(argv) > 2 else "--write"

        if mode == "--mutation-tests":
            run_mutation_tests(root)
            print("ok: reference mutation tests")
            return 0

        check_required_paths(root)
        schemas = load_reference_schemas(root)
        validate_declared_json_files(root, schemas)
        validate_repo_support(root)
        validate_source(root)
        run_tests(root)

        specs_by_id = validate_manifest(root)
        validate_level_0(specs_by_id["product.kernel"])
        validate_level_1(specs_by_id["product.primitives"])
        expect(specs_by_id["product.kernel"]["derived_artifacts"][0]["path"] == "derived/specs/product/level-0/kernel.md", "Level 0 derived artifact path must match the projection path")
        expect(specs_by_id["product.primitives"]["derived_artifacts"][0]["path"] == "derived/specs/product/level-1/primitives.md", "Level 1 derived artifact path must match the projection path")
        validate_projection(root, specs_by_id["product.kernel"], "derived/specs/product/level-0/kernel.md")
        validate_projection(root, specs_by_id["product.primitives"], "derived/specs/product/level-1/primitives.md")

        print("ok: reference product layer validation")
        return 0
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
