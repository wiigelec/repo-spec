from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repo_model import load_specs as load_repo_specs_impl, resolve_repo_path as resolve_repo_path_impl
from repo_model import RepositoryError

from .errors import expect, fail
from .generated_outputs import check_generated_document_freshness
from .schema_subset import load_repo_schemas, validate_instance


@dataclass(frozen=True)
class ValidationContext:
    repo_root: Path
    manifest: dict[str, Any]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


def load_repo_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    try:
        return load_repo_specs_impl(repo_root)
    except RepositoryError as exc:
        fail(str(exc))


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    try:
        return resolve_repo_path_impl(repo_root, value)
    except RepositoryError as exc:
        fail(str(exc))


def validate_repo_json_schema_conformance(specs: dict[str, dict[str, Any]], source_paths: dict[str, str], schemas: dict[str, dict[str, Any]]) -> None:
    validate_instance(specs["repo.manifest"], schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"])
    for spec_id, spec in specs.items():
        if spec_id == "repo.manifest":
            continue
        validate_instance(spec, schemas["repo.spec"], source_paths[spec_id], schemas["repo.spec"])


def check_manifest_completeness(specs: dict[str, dict[str, Any]], source_paths: dict[str, str], actual_paths: list[str]) -> None:
    manifest = specs["repo.manifest"]
    entries = manifest["authoritative_specs"]
    manifest_paths = [entry["path"] for entry in entries]
    expect(len(manifest_paths) == len(set(manifest_paths)), "manifest completeness failed")
    expect(set(actual_paths) == set(manifest_paths), "manifest completeness failed")
    for entry in entries:
        expect(source_paths[entry["spec_id"]] == entry["path"], "manifest completeness failed")


def check_unique_spec_ids(specs: dict[str, dict[str, Any]]) -> None:
    ids = [spec["spec_id"] for spec in specs.values()]
    expect(len(ids) == len(set(ids)), "unique specification IDs failed")


def check_unique_derived_artifact_paths(specs: dict[str, dict[str, Any]]) -> None:
    paths: list[str] = []
    for spec in specs.values():
        for artifact in spec.get("derived_artifacts", []):
            paths.append(artifact["path"])
    expect(len(paths) == len(set(paths)), "duplicate derived artifact paths failed")


def check_unique_item_properties(specs: dict[str, dict[str, Any]], spec_id: str, field: str, keys: list[str]) -> None:
    seen: set[tuple[Any, ...]] = set()
    for index, item in enumerate(specs[spec_id][field]):
        expect(isinstance(item, dict), f"{field} failed: {spec_id}[{index}] must be an object")
        identity = tuple(item.get(key) for key in keys)
        expect(identity not in seen, f"{field} failed: duplicate item properties {', '.join(keys)}")
        seen.add(identity)


def check_relation_targets(specs: dict[str, dict[str, Any]], field: str, allowed_statuses: set[str], relation_label: str) -> None:
    for spec_id, spec in specs.items():
        for index, target_spec_id in enumerate(spec.get(field, [])):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved spec {spec_id} -> {target_spec_id}")
            expect(specs[target_spec_id]["status"] in allowed_statuses, f"{relation_label} failed: {spec_id} -> {target_spec_id}")
            expect(target_spec_id != spec_id, f"{relation_label} failed: self reference {spec_id}")


def check_dependency_targets(specs: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs.items():
        for index, dep in enumerate(spec.get("dependencies", [])):
            target_spec_id = dep["spec_id"]
            expect(target_spec_id in specs, f"dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            expect(specs[target_spec_id]["status"] in {"candidate", "accepted"}, f"dependencies failed: {spec_id} -> {target_spec_id}")


def check_lineage_relations(specs: dict[str, dict[str, Any]]) -> None:
    check_relation_targets(specs, "supersedes", {"candidate", "accepted", "superseded", "retired"}, "supersedes")
    check_relation_targets(specs, "superseded_by", {"candidate", "accepted", "superseded", "retired"}, "superseded_by")


def check_resolvable_references(repo_root: Path, specs: dict[str, dict[str, Any]]) -> None:
    for spec_id, spec in specs.items():
        for ref in spec["references"]:
            if ref["type"] == "specification":
                target_spec = specs.get(ref["spec_id"])
                expect(target_spec is not None, f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
                kind = ref.get("kind", "normative")
                if kind == "historical":
                    expect(target_spec["status"] in {"superseded", "retired"}, f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
                else:
                    expect(kind == "normative", f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
                    expect(target_spec["status"] == "accepted", f"resolvable references failed: {spec_id} -> {ref['spec_id']}")
            else:
                expect(resolve_repo_path(repo_root, ref["path"]).exists(), f"resolvable references failed: missing artifact {ref['path']}")


def check_acyclic_dependencies(specs: dict[str, dict[str, Any]]) -> None:
    graph = {spec["spec_id"]: [dep["spec_id"] for dep in spec["dependencies"]] for spec in specs.values()}
    visiting: set[str] = set()
    visited: set[str] = set()

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


def load_validation_context(repo_root: Path) -> ValidationContext:
    manifest, specs, source_paths, actual_paths = load_repo_specs(repo_root)
    schemas = load_repo_schemas(repo_root)
    return ValidationContext(repo_root, manifest, specs, source_paths, actual_paths, schemas)


def check_schema_conformance(context: ValidationContext) -> None:
    validate_repo_json_schema_conformance(context.specs, context.source_paths, context.schemas)


def check_manifest_phase(context: ValidationContext) -> None:
    check_manifest_completeness(context.specs, context.source_paths, context.actual_paths)


def check_unique_spec_ids_phase(context: ValidationContext) -> None:
    check_unique_spec_ids(context.specs)


def check_unique_item_properties_phase(context: ValidationContext) -> None:
    check_unique_item_properties(context.specs, "repo.manifest", "authoritative_specs", ["spec_id"])
    for spec_id in context.specs:
        if "issue_fields" in context.specs[spec_id]:
            check_unique_item_properties(context.specs, spec_id, "issue_fields", ["id"])
        if "review_fields" in context.specs[spec_id]:
            check_unique_item_properties(context.specs, spec_id, "review_fields", ["id"])
        check_unique_item_properties(context.specs, spec_id, "normative_requirements", ["id"])
        check_unique_item_properties(context.specs, spec_id, "dependencies", ["spec_id"])
        check_unique_item_properties(context.specs, spec_id, "references", ["type", "spec_id", "path", "kind"])
        check_unique_item_properties(context.specs, spec_id, "derived_artifacts", ["path"])


def check_unique_derived_artifact_paths_phase(context: ValidationContext) -> None:
    check_unique_derived_artifact_paths(context.specs)


def check_dependency_targets_phase(context: ValidationContext) -> None:
    check_dependency_targets(context.specs)


def check_resolvable_references_phase(context: ValidationContext) -> None:
    check_resolvable_references(context.repo_root, context.specs)


def check_lineage_relations_phase(context: ValidationContext) -> None:
    check_lineage_relations(context.specs)


def check_acyclic_dependencies_phase(context: ValidationContext) -> None:
    check_acyclic_dependencies(context.specs)


def check_generated_document_freshness_phase(context: ValidationContext) -> None:
    check_generated_document_freshness(context.repo_root)


VALIDATION_PHASES: list[tuple[str, Any]] = [
    ("repository JSON Schema conformance", check_schema_conformance),
    ("manifest completeness", check_manifest_phase),
    ("unique specification IDs", check_unique_spec_ids_phase),
    ("unique item properties", check_unique_item_properties_phase),
    ("unique derived artifact paths", check_unique_derived_artifact_paths_phase),
    ("dependency target lifecycle", check_dependency_targets_phase),
    ("resolvable references", check_resolvable_references_phase),
    ("lineage relations", check_lineage_relations_phase),
    ("acyclic dependencies", check_acyclic_dependencies_phase),
    ("generated-document freshness", check_generated_document_freshness_phase),
]


def validate_repo(repo_root: Path) -> None:
    context = load_validation_context(repo_root)
    for label, check in VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")
