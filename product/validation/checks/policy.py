"""Domain-specific production validation policy extension point."""

from __future__ import annotations

from typing import Any

from validation.core.errors import expect, fail
from validation.core.context import ValidationContext
from validation.core.paths import resolve_repo_path


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
    def has_accepted_level0_in_closure(spec_id: str) -> bool:
        pending = [dep["spec_id"] for dep in specs[spec_id].get("dependencies", [])]
        visited: set[str] = set()

        while pending:
            target_spec_id = pending.pop()
            if target_spec_id in visited:
                continue
            visited.add(target_spec_id)

            target_spec = specs.get(target_spec_id)
            if target_spec is None:
                continue
            if target_spec["status"] == "accepted" and target_spec["level"] == 0:
                return True
            pending.extend(dep["spec_id"] for dep in target_spec.get("dependencies", []))

        return False

    for spec_id, spec in specs.items():
        if spec["status"] != "accepted" or spec["level"] not in {1, 2, 3}:
            continue
        expect(
            has_accepted_level0_in_closure(spec_id),
            f"product completeness failed: accepted spec {spec_id} has no accepted Level 0 specification in its transitive dependency closure",
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
                kind = ref["kind"]
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


# Product lifecycle and readiness policy.
from validation.core.errors import fail
from validation.core.context import ValidationContext
from validation.core.errors import expect
from .development_documents import get_development_document_records

from .development_documents import _product_development_roots


def check_product_lifecycle_readiness(context: ValidationContext) -> None:
    product_specs = context.product.specs if context.product is not None else {}
    product_entries = context.product.entries if context.product is not None else []
    records = get_development_document_records(
        context,
        development_roots=_product_development_roots(),
    )

    for plan_path, record in records.items():
        metadata = record.metadata
        if metadata["artifact_type"] != "implementation-plan":
            continue
        if metadata.get("lifecycle_status") not in {"accepted", "planning-complete"}:
            continue
        if context.product is None:
            continue

        authority_entries = metadata.get("workstream_authority", [])
        expect(authority_entries, f"lifecycle plan failed: plan {plan_path} lacks workstream authority")
        seen_ids: set[str] = set()
        for authority in authority_entries:
            workstream_id = authority["id"]
            expect(
                workstream_id not in seen_ids,
                f"lifecycle plan failed: plan {plan_path} has duplicate workstream authority identifier {workstream_id}",
            )
            seen_ids.add(workstream_id)
            for target_spec_id in authority["controlling_product_specifications"]:
                if target_spec_id not in product_specs:
                    fail(
                        f"lifecycle plan failed: plan {plan_path} references "
                        f"unknown specification {target_spec_id}"
                    )
                target_spec = product_specs[target_spec_id]
                expect(
                    target_spec["status"] == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"non-accepted specification {target_spec_id} "
                    f"(status: {target_spec['status']})",
                )
                manifest_entry = next(
                    (entry for entry in product_entries if entry["spec_id"] == target_spec_id),
                    None,
                )
                expect(
                    manifest_entry is not None and manifest_entry.get("status") == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"specification {target_spec_id} without accepted product-manifest registration",
                )

    for decomp_path, record in records.items():
        metadata = record.metadata
        if metadata["artifact_type"] != "product-decomposition":
            continue
        if metadata.get("lifecycle_status") not in {"accepted", "candidate"}:
            continue

        expected_spec_families = metadata.get("expected_specification_families", [])
        if not expected_spec_families:
            continue

        for family in expected_spec_families:
            expect(
                isinstance(family, dict),
                "lifecycle decomposition failed: expected_specification_families "
                f"entry must be an object in {decomp_path}",
            )
            expect(
                "level" in family,
                "lifecycle decomposition failed: expected_specification_families "
                f"entry missing level in {decomp_path}",
            )
            expect(
                "responsibility" in family,
                "lifecycle decomposition failed: expected_specification_families "
                f"entry missing responsibility in {decomp_path}",
            )
            expect(
                "dependency_direction" in family,
                "lifecycle decomposition failed: expected_specification_families "
                f"entry missing dependency_direction in {decomp_path}",
            )
