#!/usr/bin/env python3

"""Validation entry point for repo-spec.

This validator enforces conformance to the repository's JSON Schemas using a
small in-repo interpreter for the schema subset currently in use.
"""

from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from docgen import (
    load_specs as load_repo_specs,
    render_governing_issue,
    render_issue_form,
    render_manifest,
    render_review_proposal,
    render_review_template,
    render_validation,
    resolve_repo_path as resolve_repo_path_impl,
)

SUPPORTED_SCHEMA_KEYS = {
    "$schema",
    "$id",
    "title",
    "type",
    "additionalProperties",
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


def fail(message: str) -> None:
    raise ValidationFailure(message)


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    try:
        return resolve_repo_path_impl(repo_root, value)
    except ValueError as exc:
        fail(str(exc))


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        fail(f"missing required file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {path}: {exc.msg}")


def load_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    try:
        return load_repo_specs(repo_root)
    except Exception as exc:
        fail(str(exc))


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def instance_location(source: str, path: str) -> str:
    return source if not path else f"{source} {path}"


def schema_location(source: str, path: str) -> str:
    return source if not path else f"{source}{path}"


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

    if "const" in schema:
        pass

    if "minLength" in schema:
        expect(isinstance(schema["minLength"], int) and schema["minLength"] >= 0, f"schema loading failed: {schema_location(source, path)} minLength must be a non-negative integer")

    if "pattern" in schema:
        expect(isinstance(schema["pattern"], str), f"schema loading failed: {schema_location(source, path)} pattern must be a string")
        re.compile(schema["pattern"])

    if "$ref" in schema:
        expect(isinstance(schema["$ref"], str), f"schema loading failed: {schema_location(source, path)} $ref must be a string")
        resolve_ref(root_schema, schema["$ref"], source)


def resolve_ref(root_schema: dict[str, Any], ref: str, source: str) -> Any:
    expect(ref.startswith("#/$defs/"), f"schema loading failed: {source} unsupported ref {ref}")
    parts = ref.removeprefix("#/").split("/")
    node: Any = root_schema
    for part in parts:
        expect(isinstance(node, dict) and part in node, f"schema loading failed: {source} unresolved ref {ref}")
        node = node[part]
    return node


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
        expect(ref not in ref_stack, f"repository JSON Schema conformance failed: {instance_location(source, path)} circular ref {ref}")
        validate_instance(instance, resolve_ref(root_schema, ref, source), source, root_schema, path, ref_stack + (ref,))

    schema_type = schema.get("type")
    if schema_type == "object":
        expect(isinstance(instance, dict), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an object")
    elif schema_type == "array":
        expect(isinstance(instance, list), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an array")
    elif schema_type == "string":
        expect(isinstance(instance, str), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be a string")
    elif schema_type == "boolean":
        expect(isinstance(instance, bool), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be a boolean")
    elif schema_type == "integer":
        expect(isinstance(instance, int) and not isinstance(instance, bool), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an integer")

    if "enum" in schema:
        expect(instance in schema["enum"], f"repository JSON Schema conformance failed: {instance_location(source, path)} enum mismatch")

    if "const" in schema:
        expect(instance == schema["const"], f"repository JSON Schema conformance failed: {instance_location(source, path)} const mismatch")

    if "minLength" in schema:
        expect(isinstance(instance, str), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be a string")
        expect(len(instance) >= schema["minLength"], f"repository JSON Schema conformance failed: {instance_location(source, path)} minLength violation")

    if "pattern" in schema:
        expect(isinstance(instance, str), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be a string")
        expect(re.fullmatch(schema["pattern"], instance) is not None, f"repository JSON Schema conformance failed: {instance_location(source, path)} pattern mismatch")

    if "required" in schema:
        expect(isinstance(instance, dict), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an object")
        for required_key in schema["required"]:
            expect(required_key in instance, f"repository JSON Schema conformance failed: {instance_location(source, path)} missing required property {required_key}")

    if "properties" in schema:
        expect(isinstance(instance, dict), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an object")
        for key, subschema in schema["properties"].items():
            if key in instance:
                validate_instance(instance[key], subschema, source, root_schema, f"{path}.{key}" if path else key, ref_stack)

    if "additionalProperties" in schema and schema["additionalProperties"] is False:
        expect(isinstance(instance, dict), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an object")
        allowed = set(schema.get("properties", {}))
        extra = [key for key in instance if key not in allowed]
        expect(not extra, f"repository JSON Schema conformance failed: {instance_location(source, path)} additionalProperties disallowed: {', '.join(extra)}")

    if "items" in schema:
        expect(isinstance(instance, list), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an array")
        for index, item in enumerate(instance):
            validate_instance(item, schema["items"], source, root_schema, f"{path}[{index}]" if path else f"[{index}]", ref_stack)

    if "allOf" in schema:
        for subschema in schema["allOf"]:
            validate_instance(instance, subschema, source, root_schema, path, ref_stack)

    if "oneOf" in schema:
        matches = 0
        for subschema in schema["oneOf"]:
            if schema_matches(instance, subschema, source, root_schema, path, ref_stack):
                matches += 1
        expect(matches == 1, f"repository JSON Schema conformance failed: {instance_location(source, path)} oneOf mismatch")

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


def load_repo_schemas(repo_root: Path) -> dict[str, dict[str, Any]]:
    schemas = {
        "repo.manifest": load_json(repo_root / "schemas/repo-manifest.schema.json"),
        "repo.spec": load_json(repo_root / "schemas/repo-spec.schema.json"),
    }
    ensure_schema_keywords(schemas["repo.manifest"], "schemas/repo-manifest.schema.json")
    ensure_schema_keywords(schemas["repo.spec"], "schemas/repo-spec.schema.json")
    return schemas


def validate_repo_json_schema_conformance(specs: dict[str, dict[str, Any]], source_paths: dict[str, str], schemas: dict[str, dict[str, Any]]) -> None:
    validate_instance(specs["repo.manifest"], schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"])
    for spec_id, spec in specs.items():
        if spec_id == "repo.manifest":
            continue
        validate_instance(spec, schemas["repo.spec"], source_paths[spec_id], schemas["repo.spec"])


def check_manifest_completeness(specs: dict[str, dict[str, Any]], source_paths: dict[str, str], actual_paths: list[str]) -> None:
    manifest = specs["repo.manifest"]
    entries = manifest["authoritative_specs"]
    manifest_paths = [entry["path"] for entry in entries]
    expect(len(manifest_paths) == len(set(manifest_paths)), "manifest completeness failed")
    expect(set(actual_paths) == set(manifest_paths), "manifest completeness failed")
    for entry in entries:
        expect(source_paths[entry["spec_id"]] == entry["path"], "manifest completeness failed")


def check_unique_spec_ids(specs: dict[str, dict[str, Any]]) -> None:
    ids = [spec["spec_id"] for spec in specs.values()]
    expect(len(ids) == len(set(ids)), "unique specification IDs failed")


def check_unique_derived_artifact_paths(specs: dict[str, dict[str, Any]]) -> None:
    paths: list[str] = []
    for spec in specs.values():
        for artifact in spec.get("derived_artifacts", []):
            paths.append(artifact["path"])
    expect(len(paths) == len(set(paths)), "duplicate derived artifact paths failed")


def check_unique_item_properties(specs: dict[str, dict[str, Any]], spec_id: str, field: str, keys: list[str]) -> None:
    seen: set[tuple[Any, ...]] = set()
    for index, item in enumerate(specs[spec_id][field]):
        expect(isinstance(item, dict), f"{field} failed: {spec_id}[{index}] must be an object")
        identity = tuple(item.get(key) for key in keys)
        expect(identity not in seen, f"{field} failed: duplicate item properties {', '.join(keys)}")
        seen.add(identity)


def check_relation_targets(specs: dict[str, dict[str, Any]], field: str, allowed_statuses: set[str], relation_label: str) -> None:
    for spec_id, spec in specs.items():
        for index, target_spec_id in enumerate(spec.get(field, [])):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved spec {spec_id} -> {target_spec_id}")
            expect(specs[target_spec_id]["status"] in allowed_statuses, f"{relation_label} failed: {spec_id} -> {target_spec_id}")
            expect(target_spec_id != spec_id, f"{relation_label} failed: self reference {spec_id}")


def check_dependency_targets(specs: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs.items():
        for index, dep in enumerate(spec.get("dependencies", [])):
            target_spec_id = dep["spec_id"]
            expect(target_spec_id in specs, f"dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            expect(specs[target_spec_id]["status"] in {"candidate", "accepted"}, f"dependencies failed: {spec_id} -> {target_spec_id}")


def check_lineage_relations(specs: dict[str, dict[str, Any]]) -> None:
    check_relation_targets(specs, "supersedes", {"candidate", "accepted", "superseded", "retired"}, "supersedes")
    check_relation_targets(specs, "superseded_by", {"candidate", "accepted", "superseded", "retired"}, "superseded_by")


def check_resolvable_references(repo_root: Path, specs: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs.items():
        for ref in spec["references"]:
            if ref["type"] == "specification":
                target_spec = specs.get(ref["spec_id"])
                expect(target_spec is not None, f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
                kind = ref.get("kind", "normative")
                if kind == "historical":
                    expect(target_spec["status"] in {"superseded", "retired"}, f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
                else:
                    expect(kind == "normative", f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
                    expect(target_spec["status"] == "accepted", f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
            else:
                expect(resolve_repo_path(repo_root, ref["path"]).exists(), f"resolvable references failed: missing artifact {ref['path']}")


def check_acyclic_dependencies(specs: dict[str, dict[str, Any]]) -> None:
    graph = {spec["spec_id"]: [dep["spec_id"] for dep in spec["dependencies"]] for spec in specs.values()}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            fail("acyclic dependencies failed")
        visiting.add(node)
        for dep in graph[node]:
            expect(dep in graph, f"acyclic dependencies failed: unresolved dependency {node} -> {dep}")
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


def check_generated_document_freshness(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "scripts/generate-docs"), "--check"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, f"generated-document freshness failed: {proc.stderr.strip() or proc.stdout.strip() or 'check failed'}")


def check_generated_document_write_behavior(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "scripts/generate-docs")], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, f"generated-document write failed: {proc.stderr.strip() or proc.stdout.strip() or 'write failed'}")


def check_clean_failure_behavior(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "scripts/validate"), "--self-test-failure"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode != 0, "clean failure behavior failed")
    expect(proc.stdout.strip() == "", "clean failure behavior failed")
    expect(proc.stderr.strip() == "forced failure for behavior test", "clean failure behavior failed")


def validate_repo(repo_root: Path) -> None:
    _manifest, specs, source_paths, actual_paths = load_specs(repo_root)
    schemas = load_repo_schemas(repo_root)
    validate_repo_json_schema_conformance(specs, source_paths, schemas)
    print("ok: conformance to the repository's JSON Schemas")
    check_manifest_completeness(specs, source_paths, actual_paths)
    print("ok: manifest completeness")
    check_unique_spec_ids(specs)
    print("ok: unique specification IDs")
    check_unique_item_properties(specs, "repo.manifest", "authoritative_specs", ["spec_id"])
    print("ok: unique manifest authoritative spec IDs")
    for spec_id in specs:
        if "issue_fields" in specs[spec_id]:
            check_unique_item_properties(specs, spec_id, "issue_fields", ["id"])
            print(f"ok: unique issue fields for {spec_id}")
        if "review_fields" in specs[spec_id]:
            check_unique_item_properties(specs, spec_id, "review_fields", ["id"])
            print(f"ok: unique review fields for {spec_id}")
        check_unique_item_properties(specs, spec_id, "normative_requirements", ["id"])
        check_unique_item_properties(specs, spec_id, "dependencies", ["spec_id"])
        check_unique_item_properties(specs, spec_id, "references", ["type", "spec_id", "path", "kind"])
        check_unique_item_properties(specs, spec_id, "derived_artifacts", ["path"])
    print("ok: unique item properties")
    check_unique_derived_artifact_paths(specs)
    print("ok: unique derived artifact paths")
    check_dependency_targets(specs)
    print("ok: dependency target lifecycle")
    check_resolvable_references(repo_root, specs)
    print("ok: resolvable references")
    check_lineage_relations(specs)
    print("ok: lineage relations")
    check_acyclic_dependencies(specs)
    print("ok: acyclic dependencies")
    check_generated_document_freshness(repo_root)
    print("ok: generated-document freshness")
    check_clean_failure_behavior(repo_root)
    print("ok: clean failure behavior")


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    mode = argv[2] if len(argv) > 2 else "--write"

    if mode == "--self-test-failure":
        print("forced failure for behavior test", file=sys.stderr)
        return 1

    try:
        if mode == "--write":
            validate_repo(repo_root)
            return 0
        if mode == "--mutation-tests":
            from validate_tests import run_mutation_tests

            run_mutation_tests(repo_root)
            return 0
        fail(f"unknown mode: {mode}")
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
