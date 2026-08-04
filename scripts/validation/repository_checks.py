from __future__ import annotations

from dataclasses import dataclass
import json
import re
from pathlib import Path
from typing import Any

from repo_model import load_json as load_repo_json, load_specs as load_repo_specs_impl, resolve_repo_path as resolve_repo_path_impl
from repo_model import RepositoryError
from github_profile import GitHubProfileError, check_profile_freshness

from .errors import expect, fail
from .generated_outputs import check_generated_document_freshness
from .schema_subset import load_product_schemas, load_repo_schemas, validate_instance


@dataclass(frozen=True)
class RepositoryValidationContext:
    manifest: dict[str, Any]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ProductValidationContext:
    manifest: dict[str, Any]
    manifest_path: Path
    entries: list[dict[str, Any]]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ProductCorrespondenceInventory:
    requirement_ids: set[str]
    implementation_index: dict[str, dict[str, Any]]
    test_index: dict[str, dict[str, Any]]
    conformance: list[dict[str, Any]]


@dataclass(frozen=True)
class ValidationContext:
    repo_root: Path
    repository: RepositoryValidationContext
    product: ProductValidationContext | None


DEVELOPMENT_DOCUMENT_ROOTS = {
    "docs/overview/": {
        "artifact_type": "product-overview",
        "schema_key": "repo.product-overview",
        "required_headings": ["Status", "Metadata", "Overview", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "filename_suffix": "-OVERVIEW.md",
        "chunk_dir_suffix": "/",
    },
    "docs/decompositions/": {
        "artifact_type": "product-decomposition",
        "schema_key": "repo.product-decomposition",
        "required_headings": ["Status", "Metadata", "Decomposition basis", "Bounded areas", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "filename_suffix": "-DECOMPOSITION.md",
        "chunk_dir_suffix": "/",
    },
    "docs/plans/": {
        "artifact_type": "implementation-plan",
        "schema_key": "repo.implementation-plan",
        "required_headings": ["Status", "Metadata", "Planning basis", "Workstreams", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "filename_suffix": "-IMPLEMENTATION-PLAN.md",
        "chunk_dir_suffix": "/",
    },
}

MAX_DEVELOPMENT_DOCUMENT_CHUNK_LINES = 180


def markdown_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for line in text.splitlines():
        if line.startswith("## "):
            headings.add(line.removeprefix("## ").strip())
    return headings


def extract_document_metadata(text: str, source: str) -> dict[str, Any]:
    match = re.search(r"## Metadata\s*\n\s*```json\s*\n(.*?)\n```", text, re.S)
    expect(match is not None, f"development document metadata failed: missing metadata block in {source}")
    try:
        metadata = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"development document metadata failed: invalid JSON in {source}: {exc.msg}")
    expect(isinstance(metadata, dict), f"development document metadata failed: {source} metadata must be an object")
    return metadata


def chunk_dir_for_metadata(metadata: dict[str, Any]) -> str:
    return f"{metadata['root_path']}{metadata['document_slug']}/"


def top_level_document_path_for_metadata(metadata: dict[str, Any]) -> str:
    return f"{metadata['root_path']}{metadata['artifact_id'].upper()}.md"


def document_chunk_paths(metadata: dict[str, Any]) -> list[str]:
    return [chunk["path"] for chunk in metadata["subordinate_chunks"]]


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
        if spec_id == "repo.artifact-taxonomy":
            schema = schemas["repo.artifact-taxonomy"]
        elif spec_id == "repo.platform-profiles":
            schema = schemas["repo.platform-profiles"]
        else:
            schema = schemas["repo.spec"]
        validate_instance(spec, schema, source_paths[spec_id], schema)


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


EXPECTED_GITHUB_ARTIFACT_INVENTORY = {
    ".github/ISSUE_TEMPLATE/governing-issue.yml": ("installed-adapter", "profile-specific"),
    ".github/PULL_REQUEST_TEMPLATE.md": ("installed-adapter", "profile-specific"),
    ".github/workflows/github-field-policy.yml": ("installed-adapter", "profile-specific"),
    ".github/workflows/validation.yml": ("installed-adapter", "profile-specific"),
    "scripts/github-field-policy": ("bootstrap-infrastructure", "bootstrap"),
    "scripts/github_field_policy.py": ("bootstrap-infrastructure", "bootstrap"),
    "scripts/github_field_policy_mutation_test.py": ("bootstrap-infrastructure", "bootstrap"),
}

EXPECTED_GITHUB_REMOTE_STATE_KINDS = {
    "branch protection",
    "repository rulesets",
    "required checks",
    "merge queues",
    "labels",
    "repository settings",
}

EXPECTED_GITHUB_MUTATION_RECORD_FIELDS = {
    "governing issue",
    "accepted repository revision",
    "target repository",
    "target remote configuration identifier",
    "previous state",
    "inspection evidence",
    "intended state",
    "execution evidence",
    "rollback procedure",
    "post-change verification",
}

EXPECTED_GITHUB_DEPLOYMENT_STATE = {
    "ruleset_desired_state_format": [
        "name",
        "target repository",
        "target remote configuration identifier",
        "target branches",
        "conditions",
        "rules",
        "bypass actors",
        "enforcement",
    ],
    "branch_protection_desired_state_format": [
        "branch pattern",
        "target repository",
        "target remote configuration identifier",
        "required status checks",
        "required reviews",
        "merge restrictions",
        "allow force pushes",
        "require linear history",
        "require signed commits",
    ],
    "inspection_procedure": [
        "Inspect the live remote state before composing a change.",
        "Record the observed state and compare it with the desired state.",
        "Capture the exact repository revision and remote configuration identifier.",
    ],
    "plan_apply_separation": [
        "Plan phase prepares desired-state and evidence records only.",
        "Apply phase performs the remote mutation only after the plan is accepted.",
    ],
    "mutation_evidence_record_fields": [
        "governing issue",
        "accepted repository revision",
        "target repository",
        "target remote configuration identifier",
        "previous state",
        "inspection evidence",
        "intended state",
        "execution evidence",
        "rollback procedure",
        "post-change verification",
    ],
    "rollback_and_post_change_verification": [
        "Rollback procedure must be declared before apply.",
        "Post-change verification must state the exact checks used after apply.",
    ],
}


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
    repository = RepositoryValidationContext(manifest, specs, source_paths, actual_paths, schemas)
    product = load_product_validation_context(repo_root)
    return ValidationContext(repo_root, repository, product)


def actual_product_paths(repo_root: Path) -> list[str]:
    product_root = repo_root / "specs/product"
    if not product_root.exists():
        return []
    return sorted(
        path.relative_to(repo_root).as_posix()
        for path in product_root.rglob("*.json")
        if path.is_file() and path.relative_to(repo_root).as_posix() != "specs/product/manifest.json"
    )


def load_product_validation_context(repo_root: Path) -> ProductValidationContext | None:
    manifest_path = repo_root / "specs/product/manifest.json"
    actual_paths = actual_product_paths(repo_root)
    if not manifest_path.exists():
        expect(
            not actual_paths,
            "product specification root failed: undeclared JSON content under specs/product/",
        )
        return None

    schemas = load_product_schemas(repo_root)
    try:
        manifest = load_repo_json(manifest_path)
    except RepositoryError as exc:
        fail(str(exc))
    validate_instance(manifest, schemas["product.manifest"], "specs/product/manifest.json", schemas["product.manifest"])
    entries = manifest["product_specifications"]
    manifest_paths = [entry["path"] for entry in entries]
    expect(len(entries) == len({entry["spec_id"] for entry in entries}), "duplicate product specification id")
    expect(len(manifest_paths) == len(set(manifest_paths)), "duplicate product specification path")
    expect(set(actual_paths) == set(manifest_paths), "product manifest completeness failed")

    specs: dict[str, dict[str, Any]] = {}
    source_paths: dict[str, str] = {}
    for entry in entries:
        path = entry["path"]
        try:
            spec = load_repo_json(repo_root / path)
        except RepositoryError as exc:
            fail(str(exc))
        validate_instance(spec, schemas["product.spec-base"], path, schemas["product.spec-base"])
        level_schema_key = f"product.level-{spec['level']}"
        expect(level_schema_key in schemas, f"product schema loading failed: missing {level_schema_key}")
        validate_instance(spec, schemas[level_schema_key], path, schemas[level_schema_key])
        expect(spec["spec_id"] == entry["spec_id"], f"product manifest correspondence failed: spec_id mismatch for {path}")
        expect(spec["status"] == entry["status"], f"product manifest correspondence failed: lifecycle mismatch for {path}")
        expect(spec["level"] == entry["level"], f"product manifest correspondence failed: level mismatch for {path}")
        if spec["spec_id"] in specs:
            raise RepositoryError(f"duplicate product specification id: {spec['spec_id']}")
        specs[spec["spec_id"]] = spec
        source_paths[spec["spec_id"]] = path

    if len(source_paths) != len(set(source_paths.values())):
        raise RepositoryError("duplicate product specification path")

    return ProductValidationContext(manifest, manifest_path, entries, specs, source_paths, actual_paths, schemas)


def check_schema_conformance(context: ValidationContext) -> None:
    validate_repo_json_schema_conformance(context.repository.specs, context.repository.source_paths, context.repository.schemas)


def check_manifest_phase(context: ValidationContext) -> None:
    check_manifest_completeness(context.repository.specs, context.repository.source_paths, context.repository.actual_paths)


def check_unique_spec_ids_phase(context: ValidationContext) -> None:
    check_unique_spec_ids(context.repository.specs)
    if context.product is not None:
        expect(
            len(context.product.specs) == len(set(context.product.specs)),
            "duplicate product specification id",
        )


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
    if context.product is not None:
        for spec_id in context.product.specs:
            check_unique_item_properties(context.product.specs, spec_id, "normative_requirements", ["id"])
            check_unique_item_properties(context.product.specs, spec_id, "dependencies", ["spec_id"])
            check_unique_item_properties(context.product.specs, spec_id, "references", ["type", "spec_id", "path", "kind"])
            check_unique_item_properties(context.product.specs, spec_id, "derived_artifacts", ["path"])


def check_unique_derived_artifact_paths_phase(context: ValidationContext) -> None:
    check_unique_derived_artifact_paths(context.repository.specs)
    if context.product is not None:
        paths: list[str] = []
        for spec in context.product.specs.values():
            for artifact in spec.get("derived_artifacts", []):
                paths.append(artifact["path"])
        expect(len(paths) == len(set(paths)), "duplicate product derived artifact paths failed")


def check_product_specification_root_phase(context: ValidationContext) -> None:
    if context.product is None:
        return
    for spec_id, spec in context.product.specs.items():
        for index, dep in enumerate(spec.get("dependencies", [])):
            target_spec_id = dep["spec_id"]
            expect(target_spec_id in context.product.specs, f"product dependencies failed: unresolved dependency {spec_id} -> {target_spec_id}")
            target_spec = context.product.specs[target_spec_id]
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


def check_dependency_targets_phase(context: ValidationContext) -> None:
    check_dependency_targets(context.repository.specs)


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


def load_product_correspondence_inventory(context: ValidationContext, spec_id: str, spec: dict[str, Any]) -> ProductCorrespondenceInventory:
    forbidden_prefixes = ("specs/", "derived/", "schemas/", "docs/", ".github/", "scripts/")
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

    for spec_id, spec in context.product.specs.items():
        if spec.get("status") != "accepted":
            continue

        inventory = load_product_correspondence_inventory(context, spec_id, spec)
        conformance_by_requirement: dict[str, list[dict[str, Any]]] = {requirement_id: [] for requirement_id in inventory.requirement_ids}
        covered_implementation_ids: set[str] = set()
        covered_test_ids: set[str] = set()

        for record in inventory.conformance:
            requirement_id = record["requirement_id"]
            conformance_by_requirement[requirement_id].append(record)
            if record["status"] == "covered":
                covered_implementation_ids.update(record["implementation_ids"])
                covered_test_ids.update(record["test_ids"])

        for requirement_id in inventory.requirement_ids:
            records = conformance_by_requirement[requirement_id]
            expect(records, f"correspondence completeness failed: {spec_id} missing conformance for {requirement_id}")
            expect(len(records) == 1, f"correspondence completeness failed: {spec_id} duplicate conformance for {requirement_id}")

        unused_implementation_ids = sorted(set(inventory.implementation_index) - covered_implementation_ids)
        expect(not unused_implementation_ids, f"correspondence completeness failed: {spec_id} unreachable implementation mappings {', '.join(unused_implementation_ids)}")
        unused_test_ids = sorted(set(inventory.test_index) - covered_test_ids)
        expect(not unused_test_ids, f"correspondence completeness failed: {spec_id} unreachable test mappings {', '.join(unused_test_ids)}")


def check_platform_profile_inventory(profile: dict[str, Any], index: int) -> None:
    identifier = profile.get("identifier")
    expect(isinstance(identifier, str) and identifier, f"platform profile boundary failed: missing profile identifier at index {index}")

    inventory = profile.get("artifact_inventory", [])
    seen_paths: set[str] = set()
    for item_index, item in enumerate(inventory):
        path = item.get("path")
        expect(isinstance(path, str), f"platform profile boundary failed: artifact inventory path missing at index {index}:{item_index}")
        expect(path not in seen_paths, f"platform profile boundary failed: duplicate artifact inventory path {path}")
        seen_paths.add(path)
        expect(item.get("profile_id") == identifier, f"platform profile boundary failed: missing profile identity for {path}")


def check_github_bootstrap_conformance(profile: dict[str, Any]) -> None:
    expect(profile.get("source_root") == "profiles/github/", "platform profile boundary failed: GitHub source root mismatch")
    expect(profile.get("installed_adapter_root") == ".github/", "platform profile boundary failed: GitHub adapter root mismatch")
    expect(profile.get("authority_boundary") == "profile-source-authoritative", "platform profile boundary failed: profile source and installed adapter authority mismatch")
    expect(profile.get("adapter_generation_policy") == "source-to-adapter", "platform profile boundary failed: adapter generation policy mismatch")

    remote_state_kinds = profile.get("remote_state_kinds", [])
    expect(set(remote_state_kinds) == EXPECTED_GITHUB_REMOTE_STATE_KINDS, "platform profile boundary failed: remote state kinds mismatch")

    mutation_record_fields = profile.get("mutation_record_fields", [])
    expect(set(mutation_record_fields) == EXPECTED_GITHUB_MUTATION_RECORD_FIELDS, "platform profile boundary failed: hosting mutation record fields mismatch")

    inventory = profile.get("artifact_inventory", [])
    expect(len(inventory) == len(EXPECTED_GITHUB_ARTIFACT_INVENTORY), "platform profile boundary failed: GitHub artifact inventory mismatch")
    seen_paths: set[str] = set()
    for index, item in enumerate(inventory):
        path = item.get("path")
        expect(isinstance(path, str), f"platform profile boundary failed: artifact inventory path missing at index {index}")
        expect(path not in seen_paths, f"platform profile boundary failed: duplicate artifact inventory path {path}")
        seen_paths.add(path)
        expected = EXPECTED_GITHUB_ARTIFACT_INVENTORY.get(path)
        expect(expected is not None, f"platform profile boundary failed: unexpected artifact inventory path {path}")
        expect(item.get("profile_id") == "github", f"platform profile boundary failed: missing GitHub profile identity for {path}")
        expect(item.get("classification") == expected[0], f"platform profile boundary failed: artifact classification mismatch for {path}")
        expect(item.get("authority_category") == expected[1], f"platform profile boundary failed: installed adapter claims independent authority for {path}")
        if item.get("classification") == "installed-adapter":
            expect(path.startswith(".github/"), f"platform profile boundary failed: installed adapter path mismatch for {path}")
        else:
            expect(path.startswith("scripts/"), f"platform profile boundary failed: bootstrap infrastructure path mismatch for {path}")

    deployment_state = profile.get("deployment_state")
    expect(isinstance(deployment_state, dict), "platform profile boundary failed: missing GitHub deployment state contract")
    ruleset_format = deployment_state.get("ruleset_desired_state_format")
    expect(isinstance(ruleset_format, dict), "platform profile boundary failed: missing ruleset desired-state format")
    expect(ruleset_format.get("required_fields") == EXPECTED_GITHUB_DEPLOYMENT_STATE["ruleset_desired_state_format"], "platform profile boundary failed: ruleset desired-state format mismatch")

    branch_protection_format = deployment_state.get("branch_protection_desired_state_format")
    expect(isinstance(branch_protection_format, dict), "platform profile boundary failed: missing branch-protection desired-state format")
    expect(branch_protection_format.get("required_fields") == EXPECTED_GITHUB_DEPLOYMENT_STATE["branch_protection_desired_state_format"], "platform profile boundary failed: branch-protection desired-state format mismatch")

    expect(deployment_state.get("inspection_procedure") == EXPECTED_GITHUB_DEPLOYMENT_STATE["inspection_procedure"], "platform profile boundary failed: inspection procedure mismatch")
    expect(deployment_state.get("plan_apply_separation") == EXPECTED_GITHUB_DEPLOYMENT_STATE["plan_apply_separation"], "platform profile boundary failed: plan/apply separation mismatch")
    expect(deployment_state.get("mutation_evidence_record_fields") == EXPECTED_GITHUB_DEPLOYMENT_STATE["mutation_evidence_record_fields"], "platform profile boundary failed: mutation evidence record mismatch")
    expect(deployment_state.get("rollback_and_post_change_verification") == EXPECTED_GITHUB_DEPLOYMENT_STATE["rollback_and_post_change_verification"], "platform profile boundary failed: rollback and post-change verification mismatch")


def check_platform_profile_boundary(context: ValidationContext) -> None:
    spec = context.repository.specs.get("repo.platform-profiles")
    expect(spec is not None, "platform profile boundary failed: missing repo.platform-profiles")
    profiles = spec.get("profiles", [])
    expect(profiles, "platform profile boundary failed: expected at least one profile")

    seen_identifiers: set[str] = set()
    github_profile: dict[str, Any] | None = None
    for index, profile in enumerate(profiles):
        identifier = profile.get("identifier")
        expect(isinstance(identifier, str) and identifier, f"platform profile boundary failed: missing profile identifier at index {index}")
        expect(identifier not in seen_identifiers, f"platform profile boundary failed: duplicate profile identifier {identifier}")
        seen_identifiers.add(identifier)

        check_platform_profile_inventory(profile, index)
        if identifier == "github":
            github_profile = profile

    expect(github_profile is not None, "platform profile boundary failed: missing GitHub profile identity")
    check_github_bootstrap_conformance(github_profile)


def check_github_profile_freshness_phase(context: ValidationContext) -> None:
    try:
        check_profile_freshness(context.repo_root)
    except GitHubProfileError as exc:
        fail(f"github profile freshness failed: {exc}")


def check_resolvable_references_phase(context: ValidationContext) -> None:
    check_resolvable_references(context.repo_root, context.repository.specs)
    if context.product is not None:
        for spec_id, spec in context.product.specs.items():
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


def check_lineage_relations_phase(context: ValidationContext) -> None:
    check_lineage_relations(context.repository.specs)
    if context.product is not None:
        for spec_id, spec in context.product.specs.items():
            for field in ("supersedes", "superseded_by"):
                for target_spec_id in spec.get(field, []):
                    expect(target_spec_id in context.product.specs, f"product lineage failed: unresolved spec {spec_id} -> {target_spec_id}")
                    expect(target_spec_id != spec_id, f"product lineage failed: self reference {spec_id}")


def check_acyclic_dependencies_phase(context: ValidationContext) -> None:
    check_acyclic_dependencies(context.repository.specs)
    if context.product is not None:
        check_acyclic_dependencies(context.product.specs)


def check_generated_document_freshness_phase(context: ValidationContext) -> None:
    check_generated_document_freshness(context.repo_root)


def check_development_documents_phase(context: ValidationContext) -> None:
    for root_rel, info in DEVELOPMENT_DOCUMENT_ROOTS.items():
        root = context.repo_root / root_rel
        expect(root.exists(), f"development document root failed: missing root {root_rel}")
        readme = root / "README.md"
        expect(readme.exists(), f"development document discovery failed: missing {root_rel}README.md")
        readme_text = readme.read_text()

        docs = []
        for path in sorted(root.glob("*.md")):
            if path.name == "README.md":
                continue
            text = path.read_text()
            if "## Metadata" not in text:
                continue
            docs.append(path)

        for path in docs:
            text = path.read_text()
            rel_path = path.relative_to(context.repo_root).as_posix()
            metadata = extract_document_metadata(text, rel_path)
            schema_key = info["schema_key"]
            validate_instance(metadata, context.repository.schemas[schema_key], rel_path, context.repository.schemas[schema_key])

            expect(metadata["artifact_type"] == info["artifact_type"], f"development document metadata failed: artifact type mismatch in {rel_path}")
            expect(metadata["root_path"] == root_rel, f"development document metadata failed: root path mismatch in {rel_path}")
            expect(metadata["artifact_id"] == metadata["document_slug"], f"development document metadata failed: slug mismatch in {rel_path}")
            expect(path.parent == root, f"development document path failed: top-level document must live directly under {root_rel}: {rel_path}")
            expect(path.name == f"{metadata['artifact_id'].upper()}.md", f"development document path failed: filename mismatch in {rel_path}")

            headings = markdown_headings(text)
            for heading in info["required_headings"]:
                expect(heading in headings, f"development document structure failed: missing heading {heading} in {rel_path}")

            chunk_dir = root / metadata["document_slug"]
            expect(chunk_dir.exists(), f"development document path failed: missing chunk directory {chunk_dir.relative_to(context.repo_root)}")
            expect(chunk_dir.is_dir(), f"development document path failed: chunk directory is not a directory {chunk_dir.relative_to(context.repo_root)}")

            actual_chunks = sorted(path for path in chunk_dir.glob("*.md") if path.is_file())
            nested_chunks = sorted(path for path in chunk_dir.rglob("*.md") if path.is_file() and path.parent != chunk_dir)
            expect(not nested_chunks, f"development document path failed: nested chunk directories are not permitted in {chunk_dir.relative_to(context.repo_root)}")

            declared_chunks = metadata["subordinate_chunks"]
            declared_paths = [chunk["path"] for chunk in declared_chunks]
            expect(len(declared_paths) == len(set(declared_paths)), f"development document chunk inventory failed: duplicate paths in {rel_path}")
            expect(len(declared_chunks) == len(actual_chunks), f"development document chunk inventory failed: chunk count mismatch in {rel_path}")
            expect(set(declared_paths) == {chunk.relative_to(context.repo_root).as_posix() for chunk in actual_chunks}, f"development document chunk inventory failed: inventory mismatch in {rel_path}")

            orders = [chunk["order"] for chunk in declared_chunks]
            expect(orders == list(range(1, len(orders) + 1)), f"development document chunk inventory failed: non-contiguous order in {rel_path}")

            for chunk in declared_chunks:
                chunk_path = context.repo_root / chunk["path"]
                expect(chunk_path.exists(), f"development document chunk inventory failed: missing chunk {chunk['path']}")
                expect(chunk_path.is_file(), f"development document chunk inventory failed: chunk path must be a file {chunk['path']}")
                expect(chunk_path.parent == chunk_dir, f"development document path failed: chunk path outside chunk directory {chunk['path']}")
                expect(re.fullmatch(r"\d\d-[a-z0-9][a-z0-9-]*\.md", chunk_path.name) is not None, f"development document path failed: malformed chunk filename {chunk['path']}")
                expect(chunk["path"] in text, f"development document navigation failed: top-level document must link to chunk {chunk['path']}")

                chunk_text = chunk_path.read_text()
                expect(len(chunk_text.splitlines()) <= MAX_DEVELOPMENT_DOCUMENT_CHUNK_LINES, f"development document size failed: chunk exceeds line limit {chunk['path']}")
                first_non_empty = next((line for line in chunk_text.splitlines() if line.strip()), "")
                expect(first_non_empty.startswith("# "), f"development document structure failed: chunk must start with a heading {chunk['path']}")

            expect(path.name in readme_text, f"development document discovery failed: README does not reference {path.name}")



VALIDATION_PHASES: list[tuple[str, Any]] = [
    ("repository JSON Schema conformance", check_schema_conformance),
    ("manifest completeness", check_manifest_phase),
    ("unique specification IDs", check_unique_spec_ids_phase),
    ("unique item properties", check_unique_item_properties_phase),
    ("platform profile boundary", check_platform_profile_boundary),
    ("GitHub profile freshness", check_github_profile_freshness_phase),
    ("unique derived artifact paths", check_unique_derived_artifact_paths_phase),
    ("product specification root", check_product_specification_root_phase),
    ("product correspondence inventory", check_product_correspondence_phase),
    ("product conformance completeness", check_product_conformance_completeness_phase),
    ("dependency target lifecycle", check_dependency_targets_phase),
    ("product dependency directions", check_dependency_directions_phase),
    ("product completeness", check_product_completeness_phase),
    ("resolvable references", check_resolvable_references_phase),
    ("lineage relations", check_lineage_relations_phase),
    ("product acyclic dependencies", check_product_acyclic_dependencies_phase),
    ("acyclic dependencies", check_acyclic_dependencies_phase),
    ("development documents", check_development_documents_phase),
    ("generated-document freshness", check_generated_document_freshness_phase),
]


def validate_repo(repo_root: Path) -> None:
    context = load_validation_context(repo_root)
    for label, check in VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")
