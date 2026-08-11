"""Product-owned correspondence and conformance validation policy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from validation.errors import expect
from validation.context import ValidationContext
from validation.repository_checks import resolve_repo_path


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
