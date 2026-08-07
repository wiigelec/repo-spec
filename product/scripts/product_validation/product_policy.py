"""Product-owned core specification validation policy."""

from __future__ import annotations

from typing import Any

from validation.errors import expect, fail
from validation.repository_checks import ValidationContext, resolve_repo_path


def check_dependency_directions(specs: dict[str, dict[str, Any]]) -> None:
    allowed_target_levels = {
        0: {0},
        1: {0, 1},
        2: {0, 1, 2},
        3: {0, 1, 2, 3},
    }
    for spec_id, spec in specs.items():
        source_level = spec["level"]
        allowed_levels = allowed_target_levels[source_level]
        for index, dep in enumerate(spec.get("dependencies", [])):
            target_spec_id = dep["spec_id"]
            target_spec = specs[target_spec_id]
            expect(
                target_spec["level"] in allowed_levels,
                f"product dependency direction failed: {spec_id} (level {source_level}) -> {target_spec_id} (level {target_spec['level']})",
            )


def check_product_completeness(specs: dict[str, dict[str, Any]]) -> None:
    accepted_level0_exists = any(spec["status"] == "accepted" and spec["level"] == 0 for spec in specs.values())
    accepted_higher_level_exists = any(spec["status"] == "accepted" and spec["level"] in {1, 2, 3} for spec in specs.values())
    if accepted_higher_level_exists:
        expect(
            accepted_level0_exists,
            "product completeness failed: accepted Level 1-3 specifications require at least one accepted Level 0 specification",
        )


def check_product_acyclic_dependencies(specs: dict[str, dict[str, Any]]) -> None:
    graph = {spec["spec_id"]: [dep["spec_id"] for dep in spec.get("dependencies", [])] for spec in specs.values()}
    visiting: list[str] = []
    visited: set[str] = set()

    def cycle_fragment(node: str) -> str:
        if node in visiting:
            start = visiting.index(node)
            cycle = visiting[start:] + [node]
            return " -> ".join(cycle)
        return node

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            fail(f"product acyclic dependencies failed: {cycle_fragment(node)}")
        visiting.append(node)
        for dep in graph[node]:
            expect(dep in graph, f"product acyclic dependencies failed: unresolved dependency {node} -> {dep}")
            visit(dep)
        visiting.pop()
        visited.add(node)

    for node in graph:
        visit(node)


def check_product_specification_root_phase(context: ValidationContext) -> None:
    if context.product is None:
        return
    for spec_id, spec in context.product.specs.items():
        for index, dep in enumerate(spec.get("dependencies", [])):
            target_spec_id = dep["spec_id"]
            expect(target_spec_id in context.product.specs, f"product dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            target_spec = context.product.specs[target_spec_id]
            if spec["status"] == "accepted":
                expect(target_spec["status"] == "accepted", f"product dependencies failed: accepted spec {spec_id} -> candidate target {target_spec_id}")
            else:
                expect(target_spec["status"] in {"candidate", "accepted"}, f"product dependencies failed: {spec_id} -> {target_spec_id}")

        for ref in spec.get("references", []):
            if ref["type"] == "specification":
                target_spec = context.product.specs.get(ref["spec_id"])
                expect(target_spec is not None, f"product references failed: unresolved spec {spec_id} -> {ref['spec_id']}")
                kind = ref.get("kind", "normative")
                if kind == "historical":
                    expect(target_spec["status"] in {"superseded", "retired"}, f"product references failed: {spec_id} -> {ref['spec_id']}")
                else:
                    expect(kind == "normative", f"product references failed: {spec_id} -> {ref['spec_id']}")
                    expect(target_spec["status"] == "accepted", f"product references failed: {spec_id} -> {ref['spec_id']}")
            else:
                expect(resolve_repo_path(context.repo_root, ref["path"]).exists(), f"product references failed: missing artifact {ref['path']}")

        for field in ("supersedes", "superseded_by"):
            for target_spec_id in spec.get(field, []):
                expect(target_spec_id in context.product.specs, f"product lineage failed: unresolved spec {spec_id} -> {target_spec_id}")
                expect(target_spec_id != spec_id, f"product lineage failed: self reference {spec_id}")


def check_dependency_directions_phase(context: ValidationContext) -> None:
    if context.product is None:
        return
    check_dependency_directions(context.product.specs)


def check_product_completeness_phase(context: ValidationContext) -> None:
    if context.product is None:
        return
    check_product_completeness(context.product.specs)


def check_product_acyclic_dependencies_phase(context: ValidationContext) -> None:
    if context.product is None:
        return
    check_product_acyclic_dependencies(context.product.specs)
