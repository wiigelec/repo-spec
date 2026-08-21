"""Specification-system validation extension point."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.context import ValidationContext
from ..core.errors import expect, fail
from ..core.invariants import (
    check_supersession_acyclicity,
    check_supersession_pairs,
    check_unique_item_properties,
)
from ..core.paths import resolve_repo_path
from ..core.schema_subset import validate_instance

# validation-metadata: {"role": "helper"}
def check_unique_derived_artifact_paths(specs: dict[str, dict[str, Any]]) -> None:
    paths: list[str] = []
    for spec in specs.values():
        for artifact in spec.get("derived_artifacts", []):
            paths.append(artifact["path"])
    expect(len(paths) == len(set(paths)), "duplicate derived artifact paths failed")

# validation-metadata: {"role": "task", "task_id": "repo.validation.unique-derived-artifact-paths", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_unique_derived_artifact_paths_phase(context: ValidationContext) -> None:
    check_unique_derived_artifact_paths(context.repository.specs)

# validation-metadata: {"role": "task", "task_id": "repo.validation.resolvable-references", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_resolvable_references_phase(context: ValidationContext) -> None:
    check_resolvable_references(context.repo_root, context.repository.specs)

# validation-metadata: {"role": "task", "task_id": "repo.validation.lineage-relations", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-012"}}
def check_lineage_relations_phase(context: ValidationContext) -> None:
    check_lineage_relations(context.repository.specs)

# validation-metadata: {"role": "helper"}
def check_relation_targets(specs: dict[str, dict[str, Any]], field: str, allowed_statuses: set[str], relation_label: str) -> None:
    for spec_id, spec in specs.items():
        for index, target_spec_id in enumerate(spec.get(field, [])):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved spec {spec_id} -> {target_spec_id}")
            expect(specs[target_spec_id]["status"] in allowed_statuses, f"{relation_label} failed: {spec_id} -> {target_spec_id}")
            expect(target_spec_id != spec_id, f"{relation_label} failed: self reference {spec_id}")

# validation-metadata: {"role": "task", "task_id": "repo.validation.schema-conformance", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_schema_conformance(context: ValidationContext) -> None:
    validate_repo_json_schema_conformance(context.repository.specs, context.repository.source_paths, context.repository.schemas)

# validation-metadata: {"role": "helper"}
def check_dependency_targets(specs: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs.items():
        for index, dep in enumerate(spec.get("dependencies", [])):
            target_spec_id = dep["spec_id"]
            expect(target_spec_id in specs, f"dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            expect(specs[target_spec_id]["status"] in {"candidate", "accepted"}, f"dependencies failed: {spec_id} -> {target_spec_id}")

# validation-metadata: {"role": "task", "task_id": "repo.validation.manifest-completeness", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_manifest_phase(context: ValidationContext) -> None:
    check_manifest_completeness(context.repository.specs, context.repository.source_paths, context.repository.actual_paths)

# validation-metadata: {"role": "task", "task_id": "repo.validation.dependency-target-lifecycle", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_dependency_targets_phase(context: ValidationContext) -> None:
    check_dependency_targets(context.repository.specs)

# validation-metadata: {"role": "helper"}
def check_unique_spec_ids(specs: dict[str, dict[str, Any]]) -> None:
    ids = [spec["spec_id"] for spec in specs.values()]
    expect(len(ids) == len(set(ids)), "unique specification IDs failed")

# validation-metadata: {"role": "helper"}
def check_lineage_relations(specs: dict[str, dict[str, Any]]) -> None:
    check_relation_targets(specs, "supersedes", {"candidate", "accepted", "superseded", "retired"}, "supersedes")
    check_relation_targets(specs, "superseded_by", {"candidate", "accepted", "superseded", "retired"}, "superseded_by")
    check_supersession_pairs(specs, "supersession relations")
    check_supersession_acyclicity(specs, "supersession relations")

# validation-metadata: {"role": "task", "task_id": "repo.validation.unique-specification-ids", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_unique_spec_ids_phase(context: ValidationContext) -> None:
    check_unique_spec_ids(context.repository.specs)

# validation-metadata: {"role": "helper"}
def check_acyclic_dependencies(specs: dict[str, dict[str, Any]]) -> None:
    graph = {spec["spec_id"]: [dep["spec_id"] for dep in spec["dependencies"]] for spec in specs.values()}
    visiting: set[str] = set()
    visited: set[str] = set()

    # validation-metadata: {"role": "helper"}
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

# validation-metadata: {"role": "task", "task_id": "repo.validation.acyclic-dependencies", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_acyclic_dependencies_phase(context: ValidationContext) -> None:
    check_acyclic_dependencies(context.repository.specs)

# validation-metadata: {"role": "helper"}
def check_manifest_completeness(specs: dict[str, dict[str, Any]], source_paths: dict[str, str], actual_paths: list[str]) -> None:
    manifest = specs["repo.manifest"]
    entries = manifest["authoritative_specs"]
    manifest_paths = [entry["path"] for entry in entries]
    expect(len(manifest_paths) == len(set(manifest_paths)), "manifest completeness failed")
    expect(set(actual_paths) == set(manifest_paths), "manifest completeness failed")
    for entry in entries:
        expect(source_paths[entry["spec_id"]] == entry["path"], "manifest completeness failed")

# validation-metadata: {"role": "helper"}
def check_resolvable_references(
    repo_root: Path,
    specs: dict[str, dict[str, Any]],
) -> None:
    for spec_id, spec in specs.items():
        for ref in spec["references"]:
            if ref["type"] == "specification":
                target_spec = specs.get(ref["spec_id"])
                expect(
                    target_spec is not None,
                    f"resolvable references failed: {spec_id} -> {ref['spec_id']}",
                )
                kind = ref.get("kind", "normative")
                if kind == "historical":
                    expect(
                        target_spec["status"] in {"superseded", "retired"},
                        f"resolvable references failed: {spec_id} -> {ref['spec_id']}",
                    )
                else:
                    expect(
                        kind == "normative",
                        f"resolvable references failed: {spec_id} -> {ref['spec_id']}",
                    )
                    expect(
                        target_spec["status"] == "accepted",
                        f"resolvable references failed: {spec_id} -> {ref['spec_id']}",
                    )
                continue

            relative_path = ref["path"]
            if relative_path == "repo" or relative_path.startswith("repo/"):
                expect(
                    resolve_repo_path(repo_root, relative_path).exists(),
                    f"resolvable references failed: missing artifact {relative_path}",
                )

# validation-metadata: {"role": "helper"}
def validate_repo_json_schema_conformance(specs: dict[str, dict[str, Any]], source_paths: dict[str, str], schemas: dict[str, dict[str, Any]]) -> None:
    validate_instance(specs["repo.manifest"], schemas["repo.manifest"], "repo/specs/repo/manifest.json", schemas["repo.manifest"])
    for spec_id, spec in specs.items():
        if spec_id == "repo.manifest":
            continue
        if spec_id == "repo.artifact-taxonomy":
            schema = schemas["repo.artifact-taxonomy"]
        elif spec_id == "repo.platform-profiles":
            schema = schemas["repo.platform-profiles"]
        else:
            schema = schemas["repo.spec"]
        validate_instance(spec, schema, source_paths[spec_id], schema)

# validation-metadata: {"role": "task", "task_id": "repo.validation.unique-item-properties", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_unique_item_properties_phase(context: ValidationContext) -> None:
    check_unique_item_properties(context.repository.specs, "repo.manifest", "authoritative_specs", ["spec_id"])
    for spec_id in context.repository.specs:
        if "issue_fields" in context.repository.specs[spec_id]:
            check_unique_item_properties(context.repository.specs, spec_id, "issue_fields", ["id"])
        if "review_fields" in context.repository.specs[spec_id]:
            check_unique_item_properties(context.repository.specs, spec_id, "review_fields", ["id"])
        if "artifact_classes" in context.repository.specs[spec_id]:
            check_unique_item_properties(context.repository.specs, spec_id, "artifact_classes", ["identifier"])
            for index, artifact_class in enumerate(context.repository.specs[spec_id]["artifact_classes"]):
                if artifact_class["generation_mode"] == "deterministic":
                    source_artifacts = artifact_class.get("source_artifacts", [])
                    expect(source_artifacts, f"artifact taxonomy failed: {spec_id}[{index}] requires source_artifacts")
        check_unique_item_properties(context.repository.specs, spec_id, "normative_requirements", ["id"])
        check_unique_item_properties(context.repository.specs, spec_id, "dependencies", ["spec_id"])
        check_unique_item_properties(context.repository.specs, spec_id, "references", ["type", "spec_id", "path", "kind"])
        check_unique_item_properties(context.repository.specs, spec_id, "derived_artifacts", ["path"])
