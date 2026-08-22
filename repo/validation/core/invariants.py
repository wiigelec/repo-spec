"""Reusable validation invariant extension point."""

# Invariant-neutral validation mechanics shared across validation domains.

from __future__ import annotations

from typing import Any

from ..core.errors import expect, fail


# validation-metadata: {"role": "helper"}
def check_supersession_pairs(specs: dict[str, dict[str, Any]], relation_label: str) -> None:
    for spec_id, spec in specs.items():
        for target_spec_id in spec.get("supersedes", []):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved supersedes pair {spec_id} -> {target_spec_id}")
            expect(spec_id in specs[target_spec_id].get("superseded_by", []), f"{relation_label} failed: non-reciprocal supersedes pair {spec_id} -> {target_spec_id}")
        for target_spec_id in spec.get("superseded_by", []):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved superseded_by pair {spec_id} -> {target_spec_id}")
            expect(spec_id in specs[target_spec_id].get("supersedes", []), f"{relation_label} failed: non-reciprocal superseded_by pair {spec_id} -> {target_spec_id}")


# validation-metadata: {"role": "helper"}
def check_supersession_acyclicity(specs: dict[str, dict[str, Any]], relation_label: str) -> None:
    graph = {spec_id: list(spec.get("supersedes", [])) for spec_id, spec in specs.items()}
    visiting: set[str] = set()
    visited: set[str] = set()

    # validation-metadata: {"role": "helper"}
    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            fail(f"{relation_label} failed: cycle detected")
        visiting.add(node)
        for dep in graph[node]:
            expect(dep in graph, f"{relation_label} failed: unresolved supersedes relation {node} -> {dep}")
            visit(dep)
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node)


# validation-metadata: {"role": "helper"}
def check_unique_item_properties(specs: dict[str, dict[str, Any]], spec_id: str, field: str, keys: list[str]) -> None:
    seen: set[tuple[Any, ...]] = set()
    for index, item in enumerate(specs[spec_id][field]):
        expect(isinstance(item, dict), f"{field} failed: {spec_id}[{index}] must be an object")
        identity = tuple(item.get(key) for key in keys)
        expect(identity not in seen, f"{field} failed: duplicate item properties {', '.join(keys)}")
        seen.add(identity)

_FORBIDDEN_PRODUCT_TEST_MAPPING_KEYS = {
    "requirements",
    "requirement_ids",
    "normative_requirements",
    "normative_requirement_ids",
    "validation_tasks",
    "validation_task_ids",
    "task_ids",
    "package_path",
    "package_paths",
    "validation_package_path",
    "validation_package_paths",
    "validation_task_callable",
    "validation_task_callables",
    "requirement_to_validation",
    "requirement_validation_registry",
}


# validation-metadata: {"role": "helper"}
def check_product_test_mapping_validation_package_refs(
    mapping: dict[str, Any],
    relation_label: str,
) -> None:
    expect(isinstance(mapping, dict), f"{relation_label} failed: test mapping must be an object")

    forbidden = sorted(set(mapping) & _FORBIDDEN_PRODUCT_TEST_MAPPING_KEYS)
    expect(
        not forbidden,
        f"{relation_label} failed: forbidden independent validation registry field(s): {', '.join(forbidden)}",
    )

    expect(
        "validation_package_refs" in mapping,
        f"{relation_label} failed: validation_package_refs is required",
    )
    refs = mapping["validation_package_refs"]
    expect(
        isinstance(refs, list),
        f"{relation_label} failed: validation_package_refs must be an array",
    )

    for index, ref in enumerate(refs):
        expect(
            isinstance(ref, dict),
            f"{relation_label} failed: validation_package_refs[{index}] must be an object",
        )
        expect(
            set(ref) == {"spec_id", "requirement_id"},
            f"{relation_label} failed: validation_package_refs[{index}] must contain exactly spec_id and requirement_id",
        )
        expect(
            isinstance(ref.get("spec_id"), str) and bool(ref["spec_id"]),
            f"{relation_label} failed: validation_package_refs[{index}].spec_id must be a non-empty string",
        )
        expect(
            isinstance(ref.get("requirement_id"), str) and bool(ref["requirement_id"]),
            f"{relation_label} failed: validation_package_refs[{index}].requirement_id must be a non-empty string",
        )


# validation-metadata: {"role": "helper"}
def enumerate_product_validation_package_obligations(
    specs: dict[str, dict[str, Any]],
) -> list[dict[str, str]]:
    obligations: list[dict[str, str]] = []
    for spec_id in sorted(specs):
        spec = specs[spec_id]
        if spec.get("status") != "accepted":
            continue

        requirements = spec.get("normative_requirements", [])
        expect(
            isinstance(requirements, list),
            f"product validation correspondence failed: {spec_id}.normative_requirements must be an array",
        )

        for requirement in requirements:
            expect(
                isinstance(requirement, dict),
                f"product validation correspondence failed: {spec_id} requirement must be an object",
            )
            requirement_id = requirement.get("id")
            expect(
                isinstance(requirement_id, str) and bool(requirement_id),
                f"product validation correspondence failed: {spec_id} requirement id must be a non-empty string",
            )
            obligations.append(
                {
                    "spec_id": spec_id,
                    "requirement_id": requirement_id,
                    "canonical_package_path": (
                        f"product/validation/packages/{spec_id}/{requirement_id}.json"
                    ),
                }
            )

    return obligations
