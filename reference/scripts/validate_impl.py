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
    "derived/specs/repo/manifest.md",
    "derived/specs/repo/governing-issue.md",
    "derived/specs/repo/review-proposal.md",
    "derived/specs/repo/repository-structure.md",
    "derived/specs/repo/artifact-taxonomy.md",
    "derived/specs/repo/platform-profiles.md",
    "derived/specs/repo/development-workflow.md",
    "derived/specs/repo/validation.md",
    ".github/README.md",
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


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    if not value:
        fail(f"invalid repository-relative path: {value}")
    if value.startswith("/") or value.startswith("./") or "/./" in value or value.endswith("/.") or "\\" in value or "//" in value:
        fail(f"invalid repository-relative path: {value}")
    relative = Path(value)
    if any(part in {".", ".."} for part in relative.parts):
        fail(f"invalid repository-relative path: {value}")
    resolved = (repo_root / relative).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        fail(f"invalid repository-relative path: {value}")
    return resolved


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


def render_spec_references(references: list[dict]) -> list[str]:
    lines: list[str] = []
    if not references:
        lines.append("- None")
        return lines
    for ref in references:
        if ref.get("type") == "specification":
            kind = ref.get("kind", "normative")
            if kind == "historical":
                lines.append(f"- historical specification: `{ref['spec_id']}`")
            else:
                lines.append(f"- specification: `{ref['spec_id']}`")
        else:
            lines.append(f"- artifact: `{ref['path']}`")
    return lines


def render_derived_artifacts(records: list[dict]) -> list[str]:
    lines: list[str] = []
    if not records:
        lines.append("- None")
        return lines
    for artifact in records:
        line = f"- `{artifact['type']}`: `{artifact['path']}`"
        if "renderer" in artifact:
            line += f" (renderer: `{artifact['renderer']}`)"
        lines.append(line)
    return lines


def render_repo_projection(spec: dict) -> str:
    lines = [
        f"# {spec['title']}",
        "",
        "## Status",
        "",
        spec["status"],
        "",
        "## Purpose",
        "",
        spec["purpose"],
        "",
    ]

    if "authoritative_specs" in spec:
        lines.extend(["## Authoritative specs", ""])
        entries = spec.get("authoritative_specs", [])
        if entries:
            for entry in entries:
                lines.append(f"- `{entry['spec_id']}` -> `{entry['path']}`")
        else:
            lines.append("- None")
        lines.append("")

    if "issue_fields" in spec:
        lines.extend(["## Issue fields", ""])
        entries = spec.get("issue_fields", [])
        if entries:
            for field in entries:
                lines.append(f"- `{field['id']}`: {field['label']}")
        else:
            lines.append("- None")
        lines.append("")

    if "review_fields" in spec:
        lines.extend(["## Review fields", ""])
        entries = spec.get("review_fields", [])
        if entries:
            for field in entries:
                lines.append(f"- `{field['id']}`: {field['label']}")
        else:
            lines.append("- None")
        lines.append("")

    if "artifact_classes" in spec:
        lines.extend(["## Artifact classes", ""])
        entries = spec.get("artifact_classes", [])
        if entries:
            for artifact in entries:
                lines.append(f"- `{artifact['identifier']}`: {artifact['label']}")
        else:
            lines.append("- None")
        lines.append("")

    if "profiles" in spec:
        lines.extend(["## Profiles", ""])
        entries = spec.get("profiles", [])
        if entries:
            for profile in entries:
                lines.append(f"- `{profile['identifier']}`: {profile['label']}")
                lines.append(f"  - Source root: `{profile['source_root']}`")
                lines.append(f"  - Installed adapter root: `{profile['installed_adapter_root']}`")
                lines.append(f"  - Authority boundary: `{profile['authority_boundary']}`")
                lines.append(f"  - Adapter generation policy: `{profile['adapter_generation_policy']}`")
                lines.append("  - Artifact inventory:")
                if profile.get("artifact_inventory"):
                    for item in profile["artifact_inventory"]:
                        lines.append(
                            f"    - `{item['path']}` -> `{item['classification']}` / `{item['authority_category']}` / `{item['profile_id']}`"
                        )
                else:
                    lines.append("    - None")
                lines.append("  - Remote state kinds:")
                if profile.get("remote_state_kinds"):
                    for kind in profile["remote_state_kinds"]:
                        lines.append(f"    - {kind}")
                else:
                    lines.append("    - None")
                lines.append("  - Hosting mutation record fields:")
                if profile.get("mutation_record_fields"):
                    for field in profile["mutation_record_fields"]:
                        lines.append(f"    - {field}")
                else:
                    lines.append("    - None")
        else:
            lines.append("- None")
        lines.append("")

    if "dependencies" in spec:
        lines.extend(["## Dependencies", ""])
        deps = spec.get("dependencies", [])
        if deps:
            for dep in deps:
                lines.append(f"- `{dep['spec_id']}`")
        else:
            lines.append("- None")
        lines.append("")

    if "references" in spec:
        lines.extend(["## References", ""])
        lines.extend(render_spec_references(spec.get("references", [])))
        lines.append("")

    if "derived_artifacts" in spec:
        lines.extend(["## Derived artifacts", ""])
        lines.extend(render_derived_artifacts(spec.get("derived_artifacts", [])))
        lines.append("")

    requirements = spec.get("normative_requirements", [])
    lines.extend(["## Normative requirements", ""])
    if requirements:
        for requirement in requirements:
            lines.append(f"- `{requirement['id']}`: {requirement['text']}")
    else:
        lines.append("- None")
    lines.append("")
    return "\n".join(lines)


def render_product_projection(spec: dict) -> str:
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


def render_projection(spec: dict) -> str:
    if "level" in spec:
        return render_product_projection(spec)
    return render_repo_projection(spec)


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


def validate_declared_json_files(repo_root: Path, schemas: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    repo_manifest = load_json(repo_root / "specs/repo/manifest.json")
    validate_instance(repo_manifest, schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"])

    # Repository manifest completeness is part of the reference proof.
    actual_repo_paths = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "specs/repo").glob("*.json")
        if path.is_file()
    )
    declared_repo_paths = [entry["path"] for entry in repo_manifest["authoritative_specs"]]
    expect(set(actual_repo_paths) == set(declared_repo_paths), "manifest completeness failed")

    repo_specs: dict[str, dict[str, Any]] = {"repo.manifest": repo_manifest}

    for relpath in [
        "specs/repo/governing-issue.json",
        "specs/repo/review-proposal.json",
        "specs/repo/repository-structure.json",
        "specs/repo/development-workflow.json",
        "specs/repo/validation.json",
        "specs/repo/artifact-taxonomy.json",
        "specs/repo/platform-profiles.json",
    ]:
        spec = load_json(repo_root / relpath)
        validate_instance(spec, schemas["repo.spec"], relpath, schemas["repo.spec"])
        repo_specs[spec["spec_id"]] = spec

    validate_repo_relationships(repo_root, repo_specs)
    for spec in repo_specs.values():
        for artifact in spec.get("derived_artifacts", []):
            validate_projection(repo_root, spec, artifact["path"])

    validate_profile_support(repo_root)

    product_manifest_path = repo_root / "specs/product/manifest.json"
    product_manifest = load_json(product_manifest_path)
    validate_instance(product_manifest, schemas["product.manifest"], "specs/product/manifest.json", schemas["product.manifest"])

    entries = product_manifest.get("product_specifications", [])
    declared_paths = {entry["path"] for entry in entries}
    actual_paths = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "specs/product").rglob("*.json")
        if path.is_file() and path.relative_to(repo_root).as_posix() != "specs/product/manifest.json"
    )
    expect(set(actual_paths) == declared_paths, "product manifest completeness failed")

    specs_by_id: dict[str, dict[str, Any]] = {}
    for entry in entries:
        level = entry["level"]
        level_schema_key = f"product.level-{level}"
        expect(level_schema_key in schemas, f"schema loading failed: missing {level_schema_key}")
        spec_path = repo_root / entry["path"]
        spec = load_json(spec_path)
        validate_instance(spec, schemas["product.spec-base"], entry["path"], schemas["product.spec-base"])
        validate_instance(spec, schemas[level_schema_key], entry["path"], schemas[level_schema_key])
        validate_product_spec(spec, spec_path, level)
        specs_by_id[spec["spec_id"]] = spec

    validate_product_relationships(repo_root, specs_by_id)
    for spec in specs_by_id.values():
        for artifact in spec.get("derived_artifacts", []):
            validate_projection(repo_root, spec, artifact["path"])
    return specs_by_id


def validate_repo_relationships(repo_root: Path, specs_by_id: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs_by_id.items():
        expect(spec.get("status") == "accepted", f"repo spec lifecycle failed: {spec_id}")

        for artifact in spec.get("derived_artifacts", []):
            expect(
                artifact.get("path", "").startswith("derived/specs/repo/"),
                f"repo artifact-root separation failed: {spec_id} -> {artifact.get('path')}",
            )

        for dep in spec.get("dependencies", []):
            target_spec_id = dep.get("spec_id")
            expect(target_spec_id in specs_by_id, f"repo dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            expect(target_spec_id != spec_id, f"repo dependencies failed: self reference {spec_id}")

        for ref in spec.get("references", []):
            if ref.get("type") == "specification":
                target_spec = specs_by_id.get(ref.get("spec_id"))
                expect(target_spec is not None, f"repo references failed: unresolved spec {spec_id} -> {ref.get('spec_id')}")
                kind = ref.get("kind", "normative")
                if kind == "historical":
                    expect(target_spec["status"] in {"superseded", "retired"}, f"repo references failed: {spec_id} -> {ref.get('spec_id')}")
                else:
                    expect(kind == "normative", f"repo references failed: {spec_id} -> {ref.get('spec_id')}")
                    expect(target_spec["status"] == "accepted", f"repo references failed: {spec_id} -> {ref.get('spec_id')}")
            else:
                resolved = resolve_repo_path(repo_root, ref.get("path", ""))
                expect(resolved.exists(), f"repo references failed: missing artifact {ref.get('path')}")

        for field in ("supersedes", "superseded_by"):
            for target_spec_id in spec.get(field, []):
                expect(target_spec_id in specs_by_id, f"repo lineage failed: unresolved spec {spec_id} -> {target_spec_id}")
                expect(target_spec_id != spec_id, f"repo lineage failed: self reference {spec_id}")


def validate_profile_support(repo_root: Path) -> None:
    profile_manifest = load_json(repo_root / "profiles/github/manifest.json")
    expect(profile_manifest.get("profile_id") == "github", "profile source/adapter freshness failed: profile identity")
    expect(profile_manifest.get("source_root") == "profiles/github/", "profile source/adapter freshness failed: source root")
    expect(profile_manifest.get("installed_adapter_root") == ".github/", "profile source/adapter freshness failed: adapter root")
    expect(profile_manifest.get("status") == "placeholder", "profile source/adapter freshness failed: status")

    inventory = profile_manifest.get("artifact_inventory", [])
    expect(isinstance(inventory, list) and inventory, "profile source/adapter freshness failed: artifact inventory")
    inventory_paths: set[str] = set()
    for index, item in enumerate(inventory):
        expect(isinstance(item, dict), f"profile source/adapter freshness failed: artifact_inventory[{index}] must be an object")
        path = item.get("path")
        expect(isinstance(path, str) and path, f"profile source/adapter freshness failed: artifact_inventory[{index}] path")
        classification = item.get("classification")
        expect(classification in {"profile-source", "installed-adapter"}, f"profile source/adapter freshness failed: artifact_inventory[{index}] classification")
        authority_category = item.get("authority_category")
        expect(isinstance(authority_category, str) and authority_category, f"profile source/adapter freshness failed: artifact_inventory[{index}] authority_category")
        expect(item.get("profile_id") == "github", f"profile source/adapter freshness failed: artifact_inventory[{index}] profile_id")
        expect(path.startswith("profiles/github/") or path.startswith(".github/"), f"profile source/adapter freshness failed: artifact_inventory[{index}] path root")
        expect(resolve_repo_path(repo_root, path).exists(), f"profile source/adapter freshness failed: missing artifact {path}")
        inventory_paths.add(path)

    expect("profiles/github/README.md" in inventory_paths, "profile source/adapter freshness failed: source README missing")
    expect(".github/README.md" in inventory_paths, "profile source/adapter freshness failed: adapter README missing")

    source_readme = load_text(repo_root / "profiles/github/README.md")
    adapter_readme = load_text(repo_root / ".github/README.md")
    expect(source_readme == adapter_readme, "profile source/adapter freshness failed: README mismatch")


def validate_schema(path: Path, required_fields: list[str], const_level: int | None = None) -> None:
    schema = load_json(path)
    expect(schema.get("type") == "object", f"schema {path} must be an object schema")
    expect(schema.get("required") == required_fields, f"schema {path} has unexpected required fields")
    if const_level is not None:
        expect(schema.get("properties", {}).get("level", {}).get("const") == const_level, f"schema {path} must constrain level to {const_level}")


def validate_general_conformance(spec: dict, spec_path: Path) -> None:
    requirements = spec.get("normative_requirements", [])
    correspondence = spec.get("correspondence", {})
    expect(isinstance(requirements, list) and requirements, f"{spec_path} must declare at least one requirement")
    expect(isinstance(correspondence, dict), f"{spec_path} must declare correspondence as an object")

    requirement_ids: set[str] = set()
    for index, requirement in enumerate(requirements):
        expect(isinstance(requirement, dict), f"{spec_path} normative_requirements[{index}] must be an object")
        requirement_id = requirement.get("id")
        expect(isinstance(requirement_id, str) and requirement_id, f"{spec_path} normative_requirements[{index}] missing id")
        requirement_text = requirement.get("text")
        expect(isinstance(requirement_text, str) and requirement_text.strip(), f"{spec_path} normative_requirements[{index}] missing text")
        requirement_ids.add(requirement_id)

    implementation_index: dict[str, dict[str, Any]] = {}
    test_index: dict[str, dict[str, Any]] = {}
    declared_paths: set[str] = set()

    def validate_mapping_collection(collection_name: str, indexed: dict[str, dict[str, Any]]) -> None:
        mappings = correspondence.get(collection_name, [])
        expect(isinstance(mappings, list), f"{spec_path} {collection_name} must be an array")
        for index, mapping in enumerate(mappings):
            expect(isinstance(mapping, dict), f"{spec_path} {collection_name}[{index}] must be an object")
            mapping_id = mapping.get("id")
            expect(isinstance(mapping_id, str) and mapping_id, f"{spec_path} {collection_name}[{index}] missing id")
            expect(mapping_id not in indexed, f"{spec_path} duplicate {collection_name} id {mapping_id}")
            paths = mapping.get("paths", [])
            requirements = mapping.get("requirements", [])
            expect(isinstance(paths, list) and paths, f"{spec_path} {collection_name} {mapping_id} requires at least one path")
            expect(isinstance(requirements, list) and requirements, f"{spec_path} {collection_name} {mapping_id} requires at least one requirement")
            for path in paths:
                expect(isinstance(path, str) and path.strip(), f"{spec_path} {collection_name} {mapping_id} path must be a string")
                expect(path not in declared_paths, f"{spec_path} duplicate correspondence path {path}")
                declared_paths.add(path)
            for requirement_id in requirements:
                expect(requirement_id in requirement_ids, f"{spec_path} {collection_name} {mapping_id} unknown requirement {requirement_id}")
            indexed[mapping_id] = mapping

    validate_mapping_collection("implementations", implementation_index)
    validate_mapping_collection("tests", test_index)

    conformance_records = correspondence.get("conformance", [])
    expect(isinstance(conformance_records, list) and conformance_records, f"{spec_path} must declare at least one conformance record")

    seen_requirement_ids: set[str] = set()
    covered_implementation_ids: set[str] = set()
    covered_test_ids: set[str] = set()

    for index, record in enumerate(conformance_records):
        expect(isinstance(record, dict), f"{spec_path} conformance[{index}] must be an object")
        requirement_id = record.get("requirement_id")
        expect(isinstance(requirement_id, str) and requirement_id, f"{spec_path} conformance[{index}] missing requirement_id")
        expect(requirement_id in requirement_ids, f"{spec_path} conformance[{index}] unknown requirement {requirement_id}")
        seen_requirement_ids.add(requirement_id)

        implementation_ids = record.get("implementation_ids", [])
        test_ids = record.get("test_ids", [])
        expect(isinstance(implementation_ids, list), f"{spec_path} conformance[{index}] implementation_ids must be an array")
        expect(isinstance(test_ids, list), f"{spec_path} conformance[{index}] test_ids must be an array")

        status = record.get("status")
        if status == "covered":
            expect(implementation_ids, f"{spec_path} conformance[{index}] covered requirement {requirement_id} requires at least one implementation mapping")
            expect(test_ids, f"{spec_path} conformance[{index}] covered requirement {requirement_id} requires at least one test mapping")
        else:
            rationale = record.get("rationale")
            expect(isinstance(rationale, str) and rationale.strip(), f"{spec_path} conformance[{index}] not-applicable requirement {requirement_id} requires rationale")

        for mapping_id in implementation_ids:
            expect(mapping_id in implementation_index, f"{spec_path} conformance[{index}] unresolved implementation {mapping_id}")
            expect(requirement_id in implementation_index[mapping_id]["requirements"], f"{spec_path} conformance[{index}] implementation {mapping_id} does not own {requirement_id}")
            covered_implementation_ids.add(mapping_id)

        for mapping_id in test_ids:
            expect(mapping_id in test_index, f"{spec_path} conformance[{index}] unresolved test {mapping_id}")
            expect(requirement_id in test_index[mapping_id]["requirements"], f"{spec_path} conformance[{index}] test {mapping_id} does not own {requirement_id}")
            covered_test_ids.add(mapping_id)

    expect(seen_requirement_ids == requirement_ids, f"{spec_path} must cover every declared requirement")
    expect(not (set(implementation_index) - covered_implementation_ids), f"{spec_path} has unreachable implementation mappings")
    expect(not (set(test_index) - covered_test_ids), f"{spec_path} has unreachable test mappings")


def validate_product_spec(spec: dict, spec_path: Path, expected_level: int) -> None:
    expect(spec.get("schema_version") == "1", f"{spec_path} must use schema_version 1")
    expect(spec.get("status") == "accepted", f"{spec_path} must be accepted")
    expect(spec.get("level") == expected_level, f"{spec_path} must declare level {expected_level}")
    expect(isinstance(spec.get("supersedes", []), list), f"{spec_path} must declare supersedes as an array")
    expect(isinstance(spec.get("superseded_by", []), list), f"{spec_path} must declare superseded_by as an array")
    derived = spec.get("derived_artifacts", [])
    expect(isinstance(derived, list) and derived, f"{spec_path} must declare at least one derived artifact")
    for index, artifact in enumerate(derived):
        expect(isinstance(artifact, dict), f"{spec_path} derived_artifacts[{index}] must be an object")
        expect(artifact.get("type") == "markdown", f"{spec_path} derived_artifacts[{index}] must declare a markdown derived artifact")
        path = artifact.get("path")
        expect(isinstance(path, str) and path.strip(), f"{spec_path} derived_artifacts[{index}] must declare a path")
    validate_general_conformance(spec, spec_path)


def validate_product_relationships(repo_root: Path, specs_by_id: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs_by_id.items():
        source_level = spec.get("level")
        for dep in spec.get("dependencies", []):
            target_spec_id = dep.get("spec_id")
            expect(target_spec_id in specs_by_id, f"product dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            target_spec = specs_by_id[target_spec_id]
            expect(target_spec["level"] <= source_level, f"product dependency direction failed: {spec_id} (level {source_level}) -> {target_spec_id} (level {target_spec['level']})")

        for ref in spec.get("references", []):
            if ref.get("type") == "specification":
                target_spec = specs_by_id.get(ref.get("spec_id"))
                expect(target_spec is not None, f"product references failed: unresolved spec {spec_id} -> {ref.get('spec_id')}")
                kind = ref.get("kind", "normative")
                if kind == "historical":
                    expect(target_spec["status"] in {"superseded", "retired"}, f"product references failed: {spec_id} -> {ref.get('spec_id')}")
                else:
                    expect(kind == "normative", f"product references failed: {spec_id} -> {ref.get('spec_id')}")
                    expect(target_spec["status"] == "accepted", f"product references failed: {spec_id} -> {ref.get('spec_id')}")
            else:
                resolved = resolve_repo_path(repo_root, ref.get("path", ""))
                expect(resolved.exists(), f"product references failed: missing artifact {ref.get('path')}")

        for field in ("supersedes", "superseded_by"):
            for target_spec_id in spec.get(field, []):
                expect(target_spec_id in specs_by_id, f"product lineage failed: unresolved spec {spec_id} -> {target_spec_id}")
                expect(target_spec_id != spec_id, f"product lineage failed: self reference {spec_id}")


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

        temp_repo = temp_root / "reference"
        shutil.rmtree(temp_repo)
        shutil.copytree(repo_root, temp_repo)
        repo_projection = temp_repo / "derived/specs/repo/validation.md"
        repo_projection.write_text(repo_projection.read_text().replace("Defines the local validation boundary for the reference skeleton.", "Tampered reference validation boundary.", 1))
        expect_subprocess_failure("repository projection freshness", temp_repo, "projection freshness mismatch")


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

        print("ok: reference product layer validation")
        return 0
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
