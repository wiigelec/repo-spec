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
