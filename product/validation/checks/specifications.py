"""Specification-system validation extension point."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from validation.core.errors import expect
from validation.core.context import ValidationContext
from validation.core.paths import resolve_repo_path


@dataclass(frozen=True)
class ProductCorrespondenceInventory:
    requirement_ids: set[str]
    implementation_index: dict[str, dict[str, Any]]
    test_index: dict[str, dict[str, Any]]
    conformance: list[dict[str, Any]]


def load_product_correspondence_inventory(context: ValidationContext, spec_id: str, spec: dict[str, Any]) -> ProductCorrespondenceInventory:
    forbidden_prefixes = ("specs/", "derived/", "schemas/", "docs/", ".github/", "repo/scripts/")
    forbidden_exact = {"README.md", "AGENTS.md", "LICENSE"}

    correspondence = spec.get("correspondence")
    expect(isinstance(correspondence, dict), f"correspondence validation failed: {spec_id} correspondence must be an object")

    requirement_ids = {req["id"] for req in spec.get("normative_requirements", [])}
    declared_paths: set[str] = set()

    def validate_mapping_collection(collection_name: str, id_field: str) -> dict[str, dict[str, Any]]:
        mappings = correspondence.get(collection_name, [])
        expect(isinstance(mappings, list), f"correspondence validation failed: {spec_id} {collection_name} must be an array")
        seen_ids: set[str] = set()
        indexed: dict[str, dict[str, Any]] = {}
        for index, mapping in enumerate(mappings):
            expect(isinstance(mapping, dict), f"correspondence validation failed: {spec_id} {collection_name}[{index}] must be an object")
            mapping_id = mapping.get(id_field)
            expect(isinstance(mapping_id, str) and mapping_id, f"correspondence validation failed: {spec_id} {collection_name}[{index}] missing {id_field}")
            expect(mapping_id not in seen_ids, f"correspondence validation failed: {spec_id} duplicate {collection_name} id {mapping_id}")
            seen_ids.add(mapping_id)
            indexed[mapping_id] = mapping

            paths = mapping.get("paths")
            expect(isinstance(paths, list), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} paths must be an array")
            expect(paths, f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} requires at least one path")
            expect(len(paths) == len(set(paths)), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} duplicate paths")

            requirements = mapping.get("requirements")
            expect(isinstance(requirements, list), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} requirements must be an array")
            expect(requirements, f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} requires at least one requirement")
            expect(len(requirements) == len(set(requirements)), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} duplicate requirements")
            for requirement_id in requirements:
                expect(requirement_id in requirement_ids, f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} unknown requirement {requirement_id}")

            for path in paths:
                expect(path not in forbidden_exact, f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} invalid path {path}")
                expect(not path.startswith(forbidden_prefixes), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} invalid path {path}")
                expect(path not in declared_paths, f"correspondence validation failed: {spec_id} duplicate correspondence path {path}")
                declared_paths.add(path)
                resolved = resolve_repo_path(context.repo_root, path)
                expect(resolved.exists(), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} missing path {path}")
                expect(resolved.is_file(), f"correspondence validation failed: {spec_id} {collection_name} {mapping_id} path {path} must be a file")

        return indexed

    implementation_index = validate_mapping_collection("implementations", "id")
    test_index = validate_mapping_collection("tests", "id")

    conformance = correspondence.get("conformance", [])
    expect(isinstance(conformance, list), f"correspondence validation failed: {spec_id} conformance must be an array")
    seen_requirement_ids: set[str] = set()
    for index, record in enumerate(conformance):
        expect(isinstance(record, dict), f"correspondence validation failed: {spec_id} conformance[{index}] must be an object")
        requirement_id = record.get("requirement_id")
        expect(isinstance(requirement_id, str) and requirement_id, f"correspondence validation failed: {spec_id} conformance[{index}] missing requirement_id")
        expect(requirement_id in requirement_ids, f"correspondence validation failed: {spec_id} conformance[{index}] unknown requirement {requirement_id}")
        expect(requirement_id not in seen_requirement_ids, f"correspondence validation failed: {spec_id} duplicate conformance requirement {requirement_id}")
        seen_requirement_ids.add(requirement_id)

        implementation_ids = record.get("implementation_ids", [])
        test_ids = record.get("test_ids", [])
        expect(isinstance(implementation_ids, list), f"correspondence validation failed: {spec_id} conformance[{index}] implementation_ids must be an array")
        expect(isinstance(test_ids, list), f"correspondence validation failed: {spec_id} conformance[{index}] test_ids must be an array")

        status = record.get("status")
        if status == "covered":
            expect(implementation_ids, f"correspondence validation failed: {spec_id} conformance[{index}] covered requirement {requirement_id} requires at least one implementation mapping")
            expect(test_ids, f"correspondence validation failed: {spec_id} conformance[{index}] covered requirement {requirement_id} requires at least one test mapping")
        else:
            rationale = record.get("rationale")
            expect(isinstance(rationale, str) and rationale.strip(), f"correspondence validation failed: {spec_id} conformance[{index}] not-applicable requirement {requirement_id} requires rationale")
            expect(not implementation_ids, f"correspondence validation failed: {spec_id} conformance[{index}] not-applicable requirement {requirement_id} must not reference implementation mappings")
            expect(not test_ids, f"correspondence validation failed: {spec_id} conformance[{index}] not-applicable requirement {requirement_id} must not reference test mappings")

        for mapping_id in implementation_ids:
            expect(mapping_id in implementation_index, f"correspondence validation failed: {spec_id} conformance[{index}] unresolved implementation {mapping_id}")
            expect(requirement_id in implementation_index[mapping_id]["requirements"], f"correspondence validation failed: {spec_id} conformance[{index}] implementation {mapping_id} does not own {requirement_id}")

        for mapping_id in test_ids:
            expect(mapping_id in test_index, f"correspondence validation failed: {spec_id} conformance[{index}] unresolved test {mapping_id}")
            expect(requirement_id in test_index[mapping_id]["requirements"], f"correspondence validation failed: {spec_id} conformance[{index}] test {mapping_id} does not own {requirement_id}")

    return ProductCorrespondenceInventory(requirement_ids, implementation_index, test_index, conformance)


def check_product_validation_correspondence_packages_phase(
    context: ValidationContext,
) -> None:
    if context.product is None:
        return
    expect(context.external_repository is not None, "product validation correspondence failed: repository authority context missing")
    schema = context.external_repository.schemas.get("validation-correspondence-package")
    expect(isinstance(schema, dict), "product validation correspondence failed: package schema missing")
    package_root = context.repo_root / "product/validation/packages"
    expect(package_root.is_dir(), "product validation correspondence failed: missing product/validation/packages")

    active_refs: set[tuple[str, str]] = set()
    source_records: dict[tuple[str, str], dict[str, Any]] = {}
    for spec_id, spec in context.product.specs.items():
        if spec.get("status") != "accepted":
            continue
        inventory = load_product_correspondence_inventory(context, spec_id, spec)
        records = {record["requirement_id"]: record for record in inventory.conformance}
        for req in spec.get("normative_requirements", []):
            requirement_id = req.get("id") if isinstance(req, dict) else None
            if not isinstance(requirement_id, str):
                continue
            ref = (spec_id, requirement_id)
            active_refs.add(ref)
            expect(requirement_id in records, f"product validation correspondence failed: missing conformance source {spec_id}/{requirement_id}")
            source_records[ref] = records[requirement_id]

    package_refs: set[tuple[str, str]] = set()
    for path in sorted(package_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package_root)
        expect(path.suffix == ".json" and len(relative.parts) == 2, f"product validation correspondence failed: noncanonical package path {path.relative_to(context.repo_root).as_posix()}")
        ref = (relative.parts[0], path.stem)
        expect(ref not in package_refs, f"product validation correspondence failed: duplicate package owner {ref[0]}/{ref[1]}")
        package = load_json(path)
        validate_instance(package, schema, path.relative_to(context.repo_root).as_posix(), schema)
        expect(package["normative_reference"] == {"spec_id": ref[0], "requirement_id": ref[1]}, f"product validation correspondence failed: package/path binding mismatch {ref[0]}/{ref[1]}")
        expect(ref in active_refs, f"product validation correspondence failed: inactive or unknown package {ref[0]}/{ref[1]}")
        source = source_records[ref]
        expect(source.get("status") == "not-applicable", f"product validation correspondence failed: unsupported migration state {ref[0]}/{ref[1]}")
        expect(package["validation_disposition"] == "not-applicable", f"product validation correspondence failed: disposition mismatch {ref[0]}/{ref[1]}")
        expect(package.get("validation_rationale") == source.get("rationale"), f"product validation correspondence failed: rationale mismatch {ref[0]}/{ref[1]}")
        expect(package["tasks"] == [], f"product validation correspondence failed: not-applicable package invented task ownership {ref[0]}/{ref[1]}")
        package_refs.add(ref)

    missing = sorted(active_refs - package_refs)
    unexpected = sorted(package_refs - active_refs)
    expect(not missing, "product validation correspondence failed: missing active package(s): " + ", ".join(f"{s}/{r}" for s, r in missing))
    expect(not unexpected, "product validation correspondence failed: unexpected package(s): " + ", ".join(f"{s}/{r}" for s, r in unexpected))


def check_product_correspondence_phase(context: ValidationContext) -> None:
    if context.product is None:
        return

    for spec_id, spec in context.product.specs.items():
        load_product_correspondence_inventory(context, spec_id, spec)


def check_product_conformance_completeness_phase(context: ValidationContext) -> None:
    if context.product is None:
        return

    # Product specifications may become accepted before implementation and tests
    # exist. Validate reachability for correspondence that has actually been
    # declared, but do not require conformance solely because a specification
    # has entered the accepted lifecycle state.
    for spec_id, spec in context.product.specs.items():
        inventory = load_product_correspondence_inventory(context, spec_id, spec)
        referenced_implementation_ids: set[str] = set()
        referenced_test_ids: set[str] = set()

        for record in inventory.conformance:
            referenced_implementation_ids.update(record["implementation_ids"])
            referenced_test_ids.update(record["test_ids"])

        unused_implementation_ids = sorted(set(inventory.implementation_index) - referenced_implementation_ids)
        expect(not unused_implementation_ids, f"correspondence validation failed: {spec_id} unreachable implementation mappings {', '.join(unused_implementation_ids)}")
        unused_test_ids = sorted(set(inventory.test_index) - referenced_test_ids)
        expect(not unused_test_ids, f"correspondence validation failed: {spec_id} unreachable test mappings {', '.join(unused_test_ids)}")


# Product validation state and schema loading.
from dataclasses import dataclass
import copy
from pathlib import Path
from typing import Any

from validation.core.errors import expect, fail
from validation.core.schema_subset import ensure_schema_keywords, load_json, validate_instance


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
