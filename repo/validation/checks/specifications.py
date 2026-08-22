"""Specification-system validation extension point."""

from __future__ import annotations

import ast
import json

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


_VALIDATION_METADATA_PREFIX = "# validation-metadata: "


# validation-metadata: {"role": "helper"}
def _active_repository_requirement_refs(
    specs: dict[str, dict[str, Any]],
) -> set[tuple[str, str]]:
    refs: set[tuple[str, str]] = set()
    for spec_id, spec in specs.items():
        if spec.get("status") != "accepted":
            continue
        requirements = spec.get("normative_requirements", [])
        expect(
            isinstance(requirements, list),
            f"validation correspondence failed: {spec_id}.normative_requirements must be an array",
        )
        for requirement in requirements:
            expect(
                isinstance(requirement, dict),
                f"validation correspondence failed: {spec_id} requirement must be an object",
            )
            requirement_id = requirement.get("id")
            expect(
                isinstance(requirement_id, str) and bool(requirement_id),
                f"validation correspondence failed: {spec_id} requirement id must be a non-empty string",
            )
            ref = (spec_id, requirement_id)
            expect(
                ref not in refs,
                f"validation correspondence failed: duplicate active requirement {spec_id}/{requirement_id}",
            )
            refs.add(ref)
    return refs


# validation-metadata: {"role": "helper"}
def _is_python_validation_source(path: Path) -> bool:
    if not path.is_file():
        return False
    if path.suffix == ".py":
        return True
    try:
        first_line = path.read_text(encoding="utf-8").splitlines()[0]
    except (OSError, UnicodeDecodeError, IndexError):
        return False
    return first_line.startswith("#!") and "python" in first_line.lower()


# validation-metadata: {"role": "helper"}
def _collect_validation_callable_metadata(
    repo_root: Path,
) -> tuple[dict[str, dict[str, Any]], set[tuple[str, str]]]:
    task_records: dict[str, dict[str, Any]] = {}
    helper_coordinates: set[tuple[str, str]] = set()

    for validation_root in (repo_root / "repo/validation",):
        if not validation_root.is_dir():
            continue
        for path in sorted(validation_root.rglob("*")):
            if not _is_python_validation_source(path):
                continue

            source = path.relative_to(repo_root).as_posix()
            text = path.read_text(encoding="utf-8")
            lines = text.splitlines()
            try:
                tree = ast.parse(text, filename=source)
            except SyntaxError as exc:
                fail(
                    f"validation correspondence failed: cannot parse validation source {source}: {exc}"
                )

            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                declaration_line = min(
                    [node.lineno] + [decorator.lineno for decorator in node.decorator_list]
                )
                expect(
                    declaration_line > 1,
                    f"validation correspondence failed: missing source metadata for {source}:{node.name}",
                )
                declaration_text = lines[declaration_line - 1]
                indent = declaration_text[
                    : len(declaration_text) - len(declaration_text.lstrip())
                ]
                metadata_line = lines[declaration_line - 2]
                prefix = indent + _VALIDATION_METADATA_PREFIX
                expect(
                    metadata_line.startswith(prefix),
                    f"validation correspondence failed: unclassified callable {source}:{node.name}",
                )

                try:
                    metadata = json.loads(metadata_line[len(prefix) :])
                except json.JSONDecodeError as exc:
                    fail(
                        f"validation correspondence failed: invalid metadata for {source}:{node.name}: {exc}"
                    )

                role = metadata.get("role")
                if role == "helper":
                    expect(
                        set(metadata) == {"role"},
                        f"validation correspondence failed: helper metadata must be non-owning at {source}:{node.name}",
                    )
                    helper_coordinates.add((source, node.name))
                    continue

                expect(
                    role == "task",
                    f"validation correspondence failed: invalid callable role at {source}:{node.name}",
                )
                expect(
                    set(metadata) == {"role", "task_id", "normative_reference"},
                    f"validation correspondence failed: task metadata shape mismatch at {source}:{node.name}",
                )

                task_id = metadata.get("task_id")
                normative_reference = metadata.get("normative_reference")
                expect(
                    isinstance(task_id, str) and bool(task_id),
                    f"validation correspondence failed: invalid task id at {source}:{node.name}",
                )
                expect(
                    isinstance(normative_reference, dict)
                    and set(normative_reference) == {"spec_id", "requirement_id"}
                    and isinstance(normative_reference.get("spec_id"), str)
                    and bool(normative_reference["spec_id"])
                    and isinstance(normative_reference.get("requirement_id"), str)
                    and bool(normative_reference["requirement_id"]),
                    f"validation correspondence failed: invalid normative reference for task {task_id}",
                )
                expect(
                    task_id not in task_records,
                    f"validation correspondence failed: duplicate source task id {task_id}",
                )
                task_records[task_id] = {
                    "task_id": task_id,
                    "source": source,
                    "callable": node.name,
                    "normative_reference": normative_reference,
                }

    return task_records, helper_coordinates


# validation-metadata: {"role": "helper"}
def _check_repository_validation_correspondence(
    repo_root: Path,
    specs: dict[str, dict[str, Any]],
    schemas: dict[str, dict[str, Any]],
) -> None:
    package_root = repo_root / "repo/validation/packages"
    expect(
        package_root.is_dir(),
        "validation correspondence failed: missing repo/validation/packages",
    )

    schema = schemas.get("validation-correspondence-package")
    expect(
        isinstance(schema, dict),
        "validation correspondence failed: missing validation correspondence package schema",
    )

    active_refs = _active_repository_requirement_refs(specs)
    package_refs: set[tuple[str, str]] = set()
    packaged_tasks: dict[str, dict[str, Any]] = {}

    for path in sorted(package_root.rglob("*")):
        if not path.is_file():
            continue
        relative = path.relative_to(package_root)
        expect(
            path.suffix == ".json" and len(relative.parts) == 2,
            f"validation correspondence failed: noncanonical package path {path.relative_to(repo_root).as_posix()}",
        )

        spec_id = relative.parts[0]
        requirement_id = path.stem
        ref = (spec_id, requirement_id)
        expect(
            ref not in package_refs,
            f"validation correspondence failed: duplicate package owner {spec_id}/{requirement_id}",
        )

        try:
            package = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            fail(
                f"validation correspondence failed: invalid JSON {path.relative_to(repo_root).as_posix()}: {exc}"
            )

        validate_instance(
            package,
            schema,
            path.relative_to(repo_root).as_posix(),
            schema,
        )
        expect(
            package["normative_reference"]
            == {"spec_id": spec_id, "requirement_id": requirement_id},
            f"validation correspondence failed: package/path binding mismatch for {spec_id}/{requirement_id}",
        )
        expect(
            ref in active_refs,
            f"validation correspondence failed: package targets inactive or unknown requirement {spec_id}/{requirement_id}",
        )

        package_refs.add(ref)
        for task in package["tasks"]:
            task_id = task["task_id"]
            expect(
                task_id not in packaged_tasks,
                f"validation correspondence failed: task {task_id} is owned by multiple packages",
            )
            packaged_tasks[task_id] = {
                "task_id": task_id,
                "source": task["source"],
                "callable": task["callable"],
                "normative_reference": {
                    "spec_id": spec_id,
                    "requirement_id": requirement_id,
                },
            }

    missing = sorted(active_refs - package_refs)
    unexpected = sorted(package_refs - active_refs)
    expect(
        not missing,
        "validation correspondence failed: missing active package(s): "
        + ", ".join(f"{spec_id}/{requirement_id}" for spec_id, requirement_id in missing),
    )
    expect(
        not unexpected,
        "validation correspondence failed: unexpected active package(s): "
        + ", ".join(
            f"{spec_id}/{requirement_id}" for spec_id, requirement_id in unexpected
        ),
    )

    source_tasks, _ = _collect_validation_callable_metadata(repo_root)
    repo_packaged_tasks = {
        task_id: record
        for task_id, record in packaged_tasks.items()
        if record["source"].startswith("repo/validation/")
    }
    source_ids = set(source_tasks)
    package_ids = set(repo_packaged_tasks)

    missing_task_packages = sorted(source_ids - package_ids)
    unexpected_package_tasks = sorted(package_ids - source_ids)
    expect(
        not missing_task_packages,
        "validation correspondence failed: repo validation source task(s) missing package ownership: "
        + ", ".join(missing_task_packages),
    )
    expect(
        not unexpected_package_tasks,
        "validation correspondence failed: repo validation package task(s) missing source metadata: "
        + ", ".join(unexpected_package_tasks),
    )

    for task_id in sorted(source_ids):
        source_record = source_tasks[task_id]
        package_record = repo_packaged_tasks[task_id]
        expect(
            source_record == package_record,
            f"validation correspondence failed: package/source disagreement for task {task_id}",
        )

        source_path = repo_root / source_record["source"]
        expect(
            source_path.is_file(),
            f"validation correspondence failed: task source missing for {task_id}: {source_record['source']}",
        )
        source_tree = ast.parse(
            source_path.read_text(encoding="utf-8"),
            filename=source_record["source"],
        )
        callable_names = {
            node.name
            for node in ast.walk(source_tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        expect(
            source_record["callable"] in callable_names,
            f"validation correspondence failed: task callable missing for {task_id}: "
            f"{source_record['source']}:{source_record['callable']}",
        )



# validation-metadata: {"role": "task", "task_id": "repo.validation.validation-correspondence-integrity", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-043"}}
def check_validation_correspondence_integrity_phase(
    context: ValidationContext,
) -> None:
    expect(
        context.repository is not None,
        "validation correspondence failed: repository validation context is required",
    )
    _check_repository_validation_correspondence(
        context.repo_root,
        context.repository.specs,
        context.repository.schemas,
    )

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
