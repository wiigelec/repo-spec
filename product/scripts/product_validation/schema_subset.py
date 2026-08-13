from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any

from validation.errors import ValidationFailure, expect, fail

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
    "minItems",
    "uniqueItems",
    "minimum",
    "pattern",
}

SUPPORTED_SCHEMA_TYPES = {"object", "array", "string", "boolean", "integer"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        fail(f"missing required file: {path}")
    except json.JSONDecodeError as exc:
        fail(f"invalid JSON: {path}: {exc.msg}")


def instance_location(source: str, path: str) -> str:
    return source if not path else f"{source} {path}"


def schema_location(source: str, path: str) -> str:
    return source if not path else f"{source}{path}"


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

    if "minItems" in schema:
        expect(isinstance(schema["minItems"], int) and schema["minItems"] >= 0, f"schema loading failed: {schema_location(source, path)} minItems must be a non-negative integer")

    if "uniqueItems" in schema:
        expect(isinstance(schema["uniqueItems"], bool), f"schema loading failed: {schema_location(source, path)} uniqueItems must be a boolean")

    if "minimum" in schema:
        expect(isinstance(schema["minimum"], int), f"schema loading failed: {schema_location(source, path)} minimum must be an integer")

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
    validate_instance_with_evaluation(instance, schema, source, root_schema, path, ref_stack)


def validate_instance_with_evaluation(
    instance: Any,
    schema: dict[str, Any],
    source: str,
    root_schema: dict[str, Any],
    path: str = "",
    ref_stack: tuple[str, ...] = (),
) -> set[str]:
    if "$ref" in schema:
        ref = schema["$ref"]
        expect(ref not in ref_stack, f"repository JSON Schema conformance failed: {instance_location(source, path)} circular ref {ref}")
        return validate_instance_with_evaluation(instance, resolve_ref(root_schema, ref, source), source, root_schema, path, ref_stack + (ref,))

    evaluated_keys: set[str] = set()

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

    if "minItems" in schema:
        expect(isinstance(instance, list), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an array")
        expect(len(instance) >= schema["minItems"], f"repository JSON Schema conformance failed: {instance_location(source, path)} minItems violation")

    if schema.get("uniqueItems") is True:
        expect(isinstance(instance, list), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an array")
        normalized_items = [json.dumps(item, sort_keys=True, separators=(",", ":")) for item in instance]
        expect(len(normalized_items) == len(set(normalized_items)), f"repository JSON Schema conformance failed: {instance_location(source, path)} uniqueItems violation")

    if "minimum" in schema:
        expect(isinstance(instance, int) and not isinstance(instance, bool), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an integer")
        expect(instance >= schema["minimum"], f"repository JSON Schema conformance failed: {instance_location(source, path)} minimum violation")

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
                validate_instance_with_evaluation(instance[key], subschema, source, root_schema, f"{path}.{key}" if path else key, ref_stack)
                evaluated_keys.add(key)

    if "additionalProperties" in schema and schema["additionalProperties"] is False:
        expect(isinstance(instance, dict), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an object")
        allowed = set(schema.get("properties", {}))
        extra = [key for key in instance if key not in allowed]
        expect(not extra, f"repository JSON Schema conformance failed: {instance_location(source, path)} additionalProperties disallowed: {', '.join(extra)}")

    if "items" in schema:
        expect(isinstance(instance, list), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an array")
        for index, item in enumerate(instance):
            validate_instance_with_evaluation(item, schema["items"], source, root_schema, f"{path}[{index}]" if path else f"[{index}]", ref_stack)

    if "allOf" in schema:
        for subschema in schema["allOf"]:
            evaluated_keys |= validate_instance_with_evaluation(instance, subschema, source, root_schema, path, ref_stack)

    if "oneOf" in schema:
        matches = 0
        matched_keys: set[str] = set()
        for subschema in schema["oneOf"]:
            if schema_matches(instance, subschema, source, root_schema, path, ref_stack):
                matches += 1
                matched_keys |= validate_instance_with_evaluation(instance, subschema, source, root_schema, path, ref_stack)
        expect(matches == 1, f"repository JSON Schema conformance failed: {instance_location(source, path)} oneOf mismatch")
        evaluated_keys |= matched_keys

    if "if" in schema:
        branch = schema.get("then") if schema_matches(instance, schema["if"], source, root_schema, path, ref_stack) else schema.get("else")
        if branch is not None:
            evaluated_keys |= validate_instance_with_evaluation(instance, branch, source, root_schema, path, ref_stack)

    if "unevaluatedProperties" in schema:
        expect(isinstance(instance, dict), f"repository JSON Schema conformance failed: {instance_location(source, path)} must be an object")
        unevaluated = [key for key in instance if key not in evaluated_keys]
        if schema["unevaluatedProperties"] is False:
            expect(not unevaluated, f"repository JSON Schema conformance failed: {instance_location(source, path)} unevaluatedProperties disallowed: {', '.join(unevaluated)}")
        else:
            for key in unevaluated:
                validate_instance_with_evaluation(instance[key], schema["unevaluatedProperties"], source, root_schema, f"{path}.{key}" if path else key, ref_stack)

    return evaluated_keys


def schema_matches(instance: Any, schema: dict[str, Any], source: str, root_schema: dict[str, Any], path: str, ref_stack: tuple[str, ...]) -> bool:
    try:
        validate_instance(instance, schema, source, root_schema, path, ref_stack)
        return True
    except ValidationFailure:
        return False


def load_repo_schemas(repo_root: Path) -> dict[str, dict[str, Any]]:
    base_document_schema = load_json(repo_root / "repo/schemas/repo/development-document-base.schema.json")

    def materialize_document_schema(schema: dict[str, Any]) -> dict[str, Any]:
        schema = copy.deepcopy(schema)
        defs = schema.setdefault("$defs", {})
        for name, subschema in base_document_schema.get("$defs", {}).items():
            defs.setdefault(name, copy.deepcopy(subschema))
        all_of = schema.get("allOf")
        if isinstance(all_of, list):
            for index, subschema in enumerate(all_of):
                if isinstance(subschema, dict) and subschema.get("$ref") == "./development-document-base.schema.json":
                    inline_base = copy.deepcopy(base_document_schema)
                    inline_base.pop("$defs", None)
                    all_of[index] = inline_base
        return schema

    schemas = {
        "repo.manifest": load_json(repo_root / "repo/schemas/repo-manifest.schema.json"),
        "repo.artifact-taxonomy": load_json(repo_root / "repo/schemas/repo-artifact-taxonomy.schema.json"),
        "repo.platform-profiles": load_json(repo_root / "repo/schemas/repo-platform-profiles.schema.json"),
        "repo.spec": load_json(repo_root / "repo/schemas/repo-spec.schema.json"),
        "repo.development-document-base": copy.deepcopy(base_document_schema),
        "repo.functional-set-process": materialize_document_schema(load_json(repo_root / "repo/schemas/repo/functional-set-process.schema.json")),
        "repo.product-decomposition": materialize_document_schema(load_json(repo_root / "repo/schemas/repo/product-decomposition.schema.json")),
        "repo.implementation-plan": materialize_document_schema(load_json(repo_root / "repo/schemas/repo/implementation-plan.schema.json")),
        "repo.architecture-plan": materialize_document_schema(load_json(repo_root / "repo/schemas/repo/architecture-plan.schema.json")),
    }
    ensure_schema_keywords(schemas["repo.manifest"], "repo/schemas/repo-manifest.schema.json")
    ensure_schema_keywords(schemas["repo.artifact-taxonomy"], "repo/schemas/repo-artifact-taxonomy.schema.json")
    ensure_schema_keywords(schemas["repo.platform-profiles"], "repo/schemas/repo-platform-profiles.schema.json")
    ensure_schema_keywords(schemas["repo.spec"], "repo/schemas/repo-spec.schema.json")
    ensure_schema_keywords(schemas["repo.development-document-base"], "repo/schemas/repo/development-document-base.schema.json")
    ensure_schema_keywords(schemas["repo.functional-set-process"], "repo/schemas/repo/functional-set-process.schema.json")
    ensure_schema_keywords(schemas["repo.product-decomposition"], "repo/schemas/repo/product-decomposition.schema.json")
    ensure_schema_keywords(schemas["repo.implementation-plan"], "repo/schemas/repo/implementation-plan.schema.json")
    ensure_schema_keywords(schemas["repo.architecture-plan"], "repo/schemas/repo/architecture-plan.schema.json")
    return schemas
