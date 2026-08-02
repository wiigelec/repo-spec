from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from repo_model import load_json as load_repo_json, load_specs as load_repo_specs_impl, resolve_repo_path as resolve_repo_path_impl
from repo_model import RepositoryError

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
class ValidationContext:
    repo_root: Path
    repository: RepositoryValidationContext
    product: ProductValidationContext | None


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
    "intended state",
    "execution evidence",
    "rollback procedure",
    "post-change verification",
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
        for entry in context.product.entries:
            for artifact in entry.get("derived_artifacts", []):
                paths.append(artifact["path"])
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
            expect(context.product.specs[target_spec_id]["status"] in {"candidate", "accepted"}, f"product dependencies failed: {spec_id} -> {target_spec_id}")

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


def check_generated_document_freshness_phase(context: ValidationContext) -> None:
    check_generated_document_freshness(context.repo_root)


VALIDATION_PHASES: list[tuple[str, Any]] = [
    ("repository JSON Schema conformance", check_schema_conformance),
    ("manifest completeness", check_manifest_phase),
    ("unique specification IDs", check_unique_spec_ids_phase),
    ("unique item properties", check_unique_item_properties_phase),
    ("platform profile boundary", check_platform_profile_boundary),
    ("unique derived artifact paths", check_unique_derived_artifact_paths_phase),
    ("product specification root", check_product_specification_root_phase),
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
