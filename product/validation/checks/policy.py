"""Domain-specific production validation policy extension point."""

from __future__ import annotations

import os

from pathlib import Path

from typing import Any

from validation.core.errors import expect, fail
from validation.core.context import ValidationContext
from validation.core.paths import resolve_repo_path



def _check_exact_validation_layout(domain_root: Path, *, require_github: bool, label: str) -> None:
    expected_top={"README.md","manifest.json","checks","core","runners","tests","packages"}
    if require_github: expected_top.add("github")
    expect(domain_root.is_dir(), f"{label} validation layout failed: missing validation domain")
    actual={p.name:p for p in domain_root.iterdir()}
    missing=sorted(expected_top-set(actual)); extra=sorted(set(actual)-expected_top)
    expect(not missing, f"{label} validation layout failed: missing top-level entries: {', '.join(missing)}")
    expect(not extra, f"{label} validation layout failed: unexpected top-level entries: {', '.join(extra)}")
    for n in ("README.md","manifest.json"):
        expect(actual[n].is_file(), f"{label} validation layout failed: {n} must be a file")
    for n in ("checks","core","runners","tests","packages"):
        expect(actual[n].is_dir(), f"{label} validation layout failed: {n} must be a directory")
    if require_github: expect(actual["github"].is_dir(), f"{label} validation layout failed: github must be a directory")
    fixed={
      "checks":{"development_documents.py","domain.py","generated_outputs.py","policy.py","specifications.py"},
      "core":{"context.py","errors.py","invariants.py","paths.py","schema_subset.py"},
      "runners":{"validate_impl.py","test_validation_impl.py"},
    }
    for dirname,expected in fixed.items():
        got={p.name:p for p in (domain_root/dirname).iterdir()}
        missing=sorted(expected-set(got)); extra=sorted(set(got)-expected)
        expect(not missing, f"{label} validation layout failed: missing {dirname} entries: {', '.join(missing)}")
        expect(not extra, f"{label} validation layout failed: unexpected {dirname} entries: {', '.join(extra)}")
        wrong=sorted(n for n,p in got.items() if not p.is_file())
        expect(not wrong, f"{label} validation layout failed: non-file {dirname} entries: {', '.join(wrong)}")
    tests={p.name:p for p in (domain_root/"tests").iterdir()}
    expected_tests={"unit","self","fixtures"}
    missing=sorted(expected_tests-set(tests)); extra=sorted(set(tests)-expected_tests)
    expect(not missing, f"{label} validation layout failed: missing tests entries: {', '.join(missing)}")
    expect(not extra, f"{label} validation layout failed: unexpected tests entries: {', '.join(extra)}")
    wrong=sorted(n for n,p in tests.items() if not p.is_dir())
    expect(not wrong, f"{label} validation layout failed: non-directory tests entries: {', '.join(wrong)}")

def _check_exact_directory_envelope(
    root: Path,
    expected_directories: set[str],
    *,
    label: str,
) -> None:
    expect(root.is_dir(), f"{label} failed: missing directory")
    actual = {path.name: path for path in root.iterdir()}
    missing = sorted(expected_directories - set(actual))
    extra = sorted(set(actual) - expected_directories)
    expect(not missing, f"{label} failed: missing entries: {', '.join(missing)}")
    expect(not extra, f"{label} failed: unexpected entries: {', '.join(extra)}")
    wrong = sorted(name for name, path in actual.items() if not path.is_dir())
    expect(not wrong, f"{label} failed: non-directory entries: {', '.join(wrong)}")


def check_product_structural_envelopes(context: ValidationContext) -> None:
    repo_root = context.repo_root
    _check_exact_directory_envelope(
        repo_root / "product",
        {"derived", "docs", "schemas", "scripts", "specs", "src", "validation"},
        label="product ownership envelope",
    )
    _check_exact_directory_envelope(repo_root / "product/specs", {"product"}, label="product specifications envelope")
    _check_exact_directory_envelope(repo_root / "product/schemas", {"product"}, label="product schemas envelope")
    _check_exact_directory_envelope(repo_root / "product/derived", {"specs"}, label="product derived envelope")
    _check_exact_directory_envelope(repo_root / "product/derived/specs", {"product"}, label="product derived specifications envelope")


def check_product_source_layout(context: ValidationContext) -> None:
    repo_root = context.repo_root
    scripts_root = repo_root / "product/scripts"
    source_root = repo_root / "product/src"
    expect(source_root.is_dir(), "product source layout failed: missing product/src")
    expect(scripts_root.is_dir(), "product source layout failed: missing product/scripts")
    expect(not (source_root / "validation").exists(), "product source layout failed: validation must remain under product/validation")
    for path in sorted(scripts_root.iterdir(), key=lambda item: item.name):
        expect(path.is_file(), f"product source layout failed: product/scripts contains non-entry-point path {path.name}")
        expect(path.suffix != ".py", f"product source layout failed: product/scripts contains Python implementation module {path.name}")
        expect(os.access(path, os.X_OK), f"product source layout failed: product/scripts entry point is not executable: {path.name}")


def check_validation_layout(context: ValidationContext) -> None:
    _check_exact_validation_layout(context.repo_root / "product/validation", require_github=False, label="product")

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
