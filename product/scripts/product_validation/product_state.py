"""Product-owned validation state and schema loading."""

from __future__ import annotations

from dataclasses import dataclass
import copy
from pathlib import Path
from typing import Any

from validation.errors import expect, fail
from validation.schema_subset import ensure_schema_keywords, load_json, validate_instance


@dataclass(frozen=True)
class ProductValidationContext:
    manifest: dict[str, Any]
    manifest_path: Path
    entries: list[dict[str, Any]]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


def load_product_schemas(repo_root: Path) -> dict[str, dict[str, Any]]:
    schemas = {
        "product.manifest": load_json(repo_root / "product/schemas/product/product-manifest.schema.json"),
        "product.spec-base": load_json(repo_root / "product/schemas/product/product-spec-base.schema.json"),
    }
    base_schema = schemas["product.spec-base"]
    base_defs = copy.deepcopy(base_schema.get("$defs", {}))

    def materialize_level_schema(schema: dict[str, Any]) -> dict[str, Any]:
        schema = copy.deepcopy(schema)
        defs = schema.setdefault("$defs", {})
        for name, subschema in base_defs.items():
            defs.setdefault(name, copy.deepcopy(subschema))
        all_of = schema.get("allOf")
        if isinstance(all_of, list):
            for index, subschema in enumerate(all_of):
                if isinstance(subschema, dict) and subschema.get("$ref") in {"./product-spec-base.schema.json", "product-spec-base.schema.json"}:
                    inline_base = copy.deepcopy(base_schema)
                    inline_base.pop("$defs", None)
                    all_of[index] = inline_base
        return schema

    schemas["product.level-0"] = materialize_level_schema(load_json(repo_root / "product/schemas/product/product-level-0.schema.json"))
    schemas["product.level-1"] = materialize_level_schema(load_json(repo_root / "product/schemas/product/product-level-1.schema.json"))
    schemas["product.level-2"] = materialize_level_schema(load_json(repo_root / "product/schemas/product/product-level-2.schema.json"))
    schemas["product.level-3"] = materialize_level_schema(load_json(repo_root / "product/schemas/product/product-level-3.schema.json"))
    ensure_schema_keywords(schemas["product.manifest"], "product/schemas/product/product-manifest.schema.json")
    ensure_schema_keywords(schemas["product.spec-base"], "product/schemas/product/product-spec-base.schema.json")
    ensure_schema_keywords(schemas["product.level-0"], "product/schemas/product/product-level-0.schema.json")
    ensure_schema_keywords(schemas["product.level-1"], "product/schemas/product/product-level-1.schema.json")
    ensure_schema_keywords(schemas["product.level-2"], "product/schemas/product/product-level-2.schema.json")
    ensure_schema_keywords(schemas["product.level-3"], "product/schemas/product/product-level-3.schema.json")
    return schemas
def actual_product_paths(repo_root: Path) -> list[str]:
    product_root = repo_root / "product/specs/product"
    if not product_root.exists():
        return []
    return sorted(
        path.relative_to(repo_root).as_posix()
        for path in product_root.rglob("*.json")
        if path.is_file() and path.relative_to(repo_root).as_posix() != "product/specs/product/manifest.json"
    )


def load_product_validation_context(repo_root: Path) -> ProductValidationContext | None:
    manifest_path = repo_root / "product/specs/product/manifest.json"
    actual_paths = actual_product_paths(repo_root)
    if not manifest_path.exists():
        expect(
            not actual_paths,
            "product specification root failed: undeclared JSON content under product/specs/product/",
        )
        return None

    schemas = load_product_schemas(repo_root)
    manifest = load_json(manifest_path)
    validate_instance(manifest, schemas["product.manifest"], "product/specs/product/manifest.json", schemas["product.manifest"])
    entries = manifest["product_specifications"]
    manifest_paths = [entry["path"] for entry in entries]
    expect(len(entries) == len({entry["spec_id"] for entry in entries}), "duplicate product specification id")
    expect(len(manifest_paths) == len(set(manifest_paths)), "duplicate product specification path")
    expect(set(actual_paths) == set(manifest_paths), "product manifest completeness failed")

    specs: dict[str, dict[str, Any]] = {}
    source_paths: dict[str, str] = {}
    for entry in entries:
        path = entry["path"]
        spec = load_json(repo_root / path)
        validate_instance(spec, schemas["product.spec-base"], path, schemas["product.spec-base"])
        level_schema_key = f"product.level-{spec['level']}"
        expect(level_schema_key in schemas, f"product schema loading failed: missing {level_schema_key}")
        validate_instance(spec, schemas[level_schema_key], path, schemas[level_schema_key])
        expect(spec["spec_id"] == entry["spec_id"], f"product manifest correspondence failed: spec_id mismatch for {path}")
        expect(spec["status"] == entry["status"], f"product manifest correspondence failed: lifecycle mismatch for {path}")
        expect(spec["level"] == entry["level"], f"product manifest correspondence failed: level mismatch for {path}")
        if spec["spec_id"] in specs:
            fail(f"duplicate product specification id: {spec['spec_id']}")
        specs[spec["spec_id"]] = spec
        source_paths[spec["spec_id"]] = path

    if len(source_paths) != len(set(source_paths.values())):
        fail("duplicate product specification path")

    return ProductValidationContext(manifest, manifest_path, entries, specs, source_paths, actual_paths, schemas)
