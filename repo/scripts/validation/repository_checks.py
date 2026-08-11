from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from pathlib import Path
from typing import Any

from repo_model import load_json as load_repo_json, load_specs as load_repo_specs_impl, resolve_repo_path as resolve_repo_path_impl
from repo_model import RepositoryError
from github_profile import GitHubProfileError, check_profile_freshness

from .errors import expect, fail
from .generated_outputs import check_generated_document_freshness
from .schema_subset import load_repo_schemas, validate_instance


@dataclass(frozen=True)
class RepositoryValidationContext:
    manifest: dict[str, Any]
    specs: dict[str, dict[str, Any]]
    source_paths: dict[str, str]
    actual_paths: list[str]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ExternalRepositoryValidationContext:
    """Repository authority read by another validation domain without certifying it."""

    specs: dict[str, dict[str, Any]]
    schemas: dict[str, dict[str, Any]]


@dataclass(frozen=True)
class ValidationContext:
    repo_root: Path
    repository: RepositoryValidationContext | None
    product: Any | None
    external_repository: ExternalRepositoryValidationContext | None = None


def repository_reference_specs(context: ValidationContext) -> dict[str, dict[str, Any]]:
    if context.repository is not None:
        return context.repository.specs
    expect(context.external_repository is not None, "validation context missing external repository reference state")
    return context.external_repository.specs


def development_document_schemas(context: ValidationContext) -> dict[str, dict[str, Any]]:
    if context.repository is not None:
        return context.repository.schemas
    expect(context.external_repository is not None, "validation context missing external repository schema state")
    return context.external_repository.schemas


@dataclass(frozen=True)
class DevelopmentDocumentRecord:
    path: str
    root_rel: str
    info: dict[str, Any]
    metadata: dict[str, Any]
    chunk_paths: list[str]


DEVELOPMENT_DOCUMENT_ROOTS = {
    "repo/docs/overview/": {
        "artifact_type": "product-overview",
        "schema_key": "repo.product-overview",
        "required_headings": ["Status", "Metadata", "Overview", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys": ["product_identity", "problem_and_outcome", "intended_users_and_stakeholders", "scope_and_non_goals", "product_boundaries", "durable_principles", "capabilities_and_success", "unresolved_questions", "readiness_for_decomposition"],
        "filename_suffix": "-OVERVIEW.md",
        "chunk_dir_suffix": "/",
    },
    "repo/docs/decompositions/": {
        "artifact_type": "product-decomposition",
        "schema_key": "repo.product-decomposition",
        "required_headings": ["Status", "Metadata", "Decomposition basis", "Bounded areas", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys": ["decomposition_basis", "product_area_inventory", "dependency_model", "cross_cutting_concerns", "unresolved_decisions", "stopping_criteria", "planning_handoff"],
        "required_chunk_coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"],
        "allowed_chunk_roles": ["product-area", "decomposition-basis", "cross-cutting-concerns", "dependency-model", "unresolved-decisions", "stopping-and-handoff"],
        "filename_suffix": "-DECOMPOSITION.md",
        "chunk_dir_suffix": "/",
    },
    "repo/docs/plans/": {
        "artifact_type": "implementation-plan",
        "schema_key": "repo.implementation-plan",
        "required_headings": ["Status", "Metadata", "Planning basis", "Workstreams", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys": ["authority_and_basis", "scope_and_exclusions", "workstreams_and_dependencies", "entry_and_exit_conditions", "transition_gates", "validation_strategy", "risks_and_unresolved_decisions", "completion_and_successor_work"],
        "filename_suffix": "-IMPLEMENTATION-PLAN.md",
        "chunk_dir_suffix": "/",
    },
}

for product_root, framework_root in (
    ("product/docs/overview/", "repo/docs/overview/"),
    ("product/docs/decompositions/", "repo/docs/decompositions/"),
    ("product/docs/plans/", "repo/docs/plans/"),
):
    DEVELOPMENT_DOCUMENT_ROOTS[product_root] = DEVELOPMENT_DOCUMENT_ROOTS[framework_root]

OVERVIEW_AND_PLAN_ROOTS = {"repo/docs/overview/", "repo/docs/plans/", "product/docs/overview/", "product/docs/plans/"}
DECOMPOSITION_ROOTS = {"repo/docs/decompositions/", "product/docs/decompositions/"}

DEVELOPMENT_DOCUMENT_COMPATIBILITY_REGISTRY_PATH = "repo/docs/development-document-compatibility.json"
DEVELOPMENT_DOCUMENT_LEGACY_COMPOSITE_PREFIX_OWNERS = {
    "repo/docs/overview/product-overview/": "repo/docs/overview/PRODUCT-OVERVIEW.md",
    "product/docs/decompositions/initializer-decomposition/": "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md",
    "product/docs/plans/initializer-implementation-plan/": "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md",
}

MAX_DEVELOPMENT_DOCUMENT_CHUNK_LINES = 180
MAX_DEVELOPMENT_DOCUMENT_CHUNK_BYTES = 24_576

REQUIRED_REPOSITORY_ROOT_ENTRY_KINDS = {
    '.github': 'directory',
    '.gitignore': 'file',
    'AGENTS.md': 'file',
    'LICENSE': 'file',
    'README.md': 'file',
    'product': 'directory',
    'reference': 'directory',
    'repo': 'directory',
    'scripts': 'directory',
    'user': 'directory',
}
IGNORED_REPOSITORY_ROOT_ENTRIES = {".git"}


def check_repository_root_boundary(context: ValidationContext) -> None:
    actual = {path.name: path for path in context.repo_root.iterdir() if path.name not in IGNORED_REPOSITORY_ROOT_ENTRIES}
    expected = set(REQUIRED_REPOSITORY_ROOT_ENTRY_KINDS)
    unexpected = sorted(set(actual) - expected)
    expect(not unexpected, "repository root boundary failed: undeclared top-level entries: " + ", ".join(unexpected))
    missing = sorted(expected - set(actual))
    expect(not missing, "repository root boundary failed: missing required top-level entries: " + ", ".join(missing))
    wrong_kind: list[str] = []
    for name, kind in REQUIRED_REPOSITORY_ROOT_ENTRY_KINDS.items():
        path = actual[name]
        matches = path.is_file() if kind == "file" else path.is_dir()
        if not matches:
            wrong_kind.append(f"{name} (expected {kind})")
    expect(not wrong_kind, "repository root boundary failed: wrong-kind top-level entries: " + ", ".join(sorted(wrong_kind)))



def markdown_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for line in text.splitlines():
        if line.startswith("## "):
            headings.add(line.removeprefix("## ").strip())
    return headings


def markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def resolve_markdown_link_target(source_path: str, target: str) -> str:
    target = target.split("#", 1)[0]
    if not target:
        return target
    return os.path.normpath((Path(source_path).parent / target).as_posix())


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line == f"## {heading}":
            start = index + 1
            break
    expect(start is not None, f"development document navigation failed: missing section {heading}")

    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


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


def document_chunk_paths(metadata: dict[str, Any]) -> list[str]:
    return [chunk["path"] for chunk in metadata["subordinate_chunks"]]


def load_development_document_compatibility_registry(
    repo_root: Path,
    *,
    development_roots: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    if development_roots is None:
        development_roots = DEVELOPMENT_DOCUMENT_ROOTS
    registry_path = repo_root / DEVELOPMENT_DOCUMENT_COMPATIBILITY_REGISTRY_PATH
    expect(
        registry_path.exists(),
        f"development document classification failed: missing compatibility registry {DEVELOPMENT_DOCUMENT_COMPATIBILITY_REGISTRY_PATH}",
    )
    try:
        data = json.loads(registry_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"development document classification failed: invalid compatibility registry JSON: {exc.msg}")

    expect(isinstance(data, dict), "development document classification failed: compatibility registry must be an object")
    expect(data.get("registry_version") == "1", "development document classification failed: unsupported compatibility registry version")
    entries = data.get("entries")
    expect(isinstance(entries, list), "development document classification failed: compatibility registry entries must be an array")

    registry: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        expect(isinstance(entry, dict), f"development document classification failed: compatibility registry entry at index {index} must be an object")
        path = entry.get("path")
        kind = entry.get("kind")
        reason = entry.get("reason")
        expect(isinstance(path, str) and path, f"development document classification failed: compatibility registry entry at index {index} must include a path")
        expect(isinstance(kind, str) and kind in {"compatibility", "exemption"}, f"development document classification failed: compatibility registry entry at index {index} must declare compatibility or exemption")
        expect(isinstance(reason, str) and reason.strip(), f"development document classification failed: compatibility registry entry at index {index} must include a reason")
        expect(path not in registry, f"development document classification failed: duplicate compatibility registry path {path}")
        path_obj = Path(path)
        expect(path_obj.name != "README.md", f"development document classification failed: compatibility registry may not include README.md {path}")
        expect(path_obj.suffix == ".md", f"development document classification failed: compatibility registry path must be Markdown {path}")
        expect(f"{path_obj.parent.as_posix()}/" in development_roots, f"development document classification failed: compatibility registry path must be under a canonical root {path}")
        registry[path] = entry

    return registry


def resolve_development_document_artifact(
    path: str,
    records: dict[str, DevelopmentDocumentRecord],
    compatibility_registry: dict[str, dict[str, Any]],
    chunk_owner_paths: dict[str, str],
) -> tuple[str, DevelopmentDocumentRecord | None]:
    if path in records:
        return path, records[path]
    if path in compatibility_registry:
        return path, None
    owner_path = chunk_owner_paths.get(path)
    if owner_path is not None:
        return owner_path, records[owner_path]
    for prefix, owner_path in DEVELOPMENT_DOCUMENT_LEGACY_COMPOSITE_PREFIX_OWNERS.items():
        if path.startswith(prefix):
            expect(owner_path in compatibility_registry, f"development document relationship failed: unresolved legacy composite owner for {path}")
            return owner_path, None
    raise KeyError(path)


def check_supersession_pairs(specs: dict[str, dict[str, Any]], relation_label: str) -> None:
    for spec_id, spec in specs.items():
        for target_spec_id in spec.get("supersedes", []):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved supersedes pair {spec_id} -> {target_spec_id}")
            expect(spec_id in specs[target_spec_id].get("superseded_by", []), f"{relation_label} failed: non-reciprocal supersedes pair {spec_id} -> {target_spec_id}")
        for target_spec_id in spec.get("superseded_by", []):
            expect(target_spec_id in specs, f"{relation_label} failed: unresolved superseded_by pair {spec_id} -> {target_spec_id}")
            expect(spec_id in specs[target_spec_id].get("supersedes", []), f"{relation_label} failed: non-reciprocal superseded_by pair {spec_id} -> {target_spec_id}")


def check_supersession_acyclicity(specs: dict[str, dict[str, Any]], relation_label: str) -> None:
    graph = {spec_id: list(spec.get("supersedes", [])) for spec_id, spec in specs.items()}
    visiting: set[str] = set()
    visited: set[str] = set()

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


def check_development_document_relationships(
    repo_root: Path,
    records: dict[str, DevelopmentDocumentRecord],
    compatibility_registry: dict[str, dict[str, Any]],
    chunk_owner_paths: dict[str, str],
) -> None:
    artifact_ids: dict[str, str] = {}
    basis_graph: dict[str, list[str]] = {path: [] for path in records}

    for path, record in records.items():
        metadata = record.metadata
        artifact_id = metadata["artifact_id"]
        expect(artifact_id not in artifact_ids, f"development document identity failed: duplicate artifact_id {artifact_id}")
        artifact_ids[artifact_id] = path

    for path, record in records.items():
        metadata = record.metadata
        source_type = metadata["artifact_type"]
        source_product = metadata["product_id"]
        source_status = metadata["lifecycle_status"]
        allowed_types = {
            "product-overview": {"product-overview"},
            "product-decomposition": {"product-overview"},
            "implementation-plan": {"product-overview", "product-decomposition", "implementation-plan"},
        }[source_type]

        controlling_documents = metadata["controlling_documents"]
        predecessor_documents = metadata["predecessor_documents"]
        evidence = metadata["evidence"]
        overview_role = metadata.get("overview_role")

        expect(len(controlling_documents) == len(set(controlling_documents)), f"development document relationship failed: duplicate controlling documents for {path}")
        expect(len(predecessor_documents) == len(set(predecessor_documents)), f"development document relationship failed: duplicate predecessor documents for {path}")
        expect(len(evidence) == len(set(evidence)), f"development document relationship failed: duplicate evidence entries for {path}")

        saw_overview = False
        saw_decomposition = False
        saw_overview_predecessor = False

        for target_path in controlling_documents:
            try:
                resolved_path, resolved_record = resolve_development_document_artifact(target_path, records, compatibility_registry, chunk_owner_paths)
            except KeyError:
                fail(f"development document relationship failed: unresolved controlling document path {path} -> {target_path}")

            expect(resolved_path == target_path or resolved_path in compatibility_registry, f"development document relationship failed: controlling document must reference a governed document {path} -> {target_path}")
            if resolved_record is None:
                if resolved_path == "repo/docs/overview/PRODUCT-OVERVIEW.md":
                    saw_overview = True
                continue

            target_metadata = resolved_record.metadata
            expect(resolved_path != path, f"development document relationship failed: self reference {path}")
            expect(target_metadata["product_id"] == source_product, f"development document relationship failed: product mismatch {path} -> {target_path}")
            expect(
                source_status in {"superseded", "retired"} or target_metadata["lifecycle_status"] in {"candidate", "accepted"},
                f"development document relationship failed: controlling lifecycle mismatch {path} -> {target_path}",
            )
            expect(target_metadata["artifact_type"] in allowed_types, f"development document relationship failed: artifact-type transition mismatch {path} -> {target_path}")
            basis_graph[path].append(resolved_path)
            if source_type in {"product-decomposition", "implementation-plan"} and target_metadata["artifact_type"] == "product-overview":
                saw_overview = True
            if source_type == "implementation-plan" and target_metadata["artifact_type"] == "product-decomposition":
                saw_decomposition = True

        for target_path in predecessor_documents:
            try:
                resolved_path, resolved_record = resolve_development_document_artifact(target_path, records, compatibility_registry, chunk_owner_paths)
            except KeyError:
                fail(f"development document relationship failed: unresolved predecessor path {path} -> {target_path}")

            expect(resolved_path == target_path, f"development document relationship failed: predecessor document must reference a governing document {path} -> {target_path}")
            if resolved_record is None:
                if resolved_path == "repo/docs/overview/PRODUCT-OVERVIEW.md":
                    saw_overview = True
                continue

            target_metadata = resolved_record.metadata
            expect(resolved_path != path, f"development document relationship failed: self reference {path}")
            expect(target_metadata["product_id"] == source_product, f"development document relationship failed: product mismatch {path} -> {target_path}")
            expect(
                source_status in {"superseded", "retired"} or target_metadata["lifecycle_status"] in {"candidate", "accepted"},
                f"development document relationship failed: predecessor lifecycle mismatch {path} -> {target_path}",
            )
            expect(target_metadata["artifact_type"] in allowed_types, f"development document relationship failed: artifact-type transition mismatch {path} -> {target_path}")

            basis_graph[path].append(resolved_path)
            if target_metadata["artifact_type"] == "product-overview":
                saw_overview = True
                if source_type == "product-overview":
                    saw_overview_predecessor = True
            if source_type == "implementation-plan" and target_metadata["artifact_type"] == "product-decomposition":
                saw_decomposition = True

        if source_type == "product-overview":
            if not predecessor_documents:
                expect(overview_role == "initial", f"development document relationship failed: missing initial overview role for {path}")
            else:
                expect(saw_overview_predecessor, f"development document relationship failed: missing predecessor overview for {path}")
        elif source_type == "product-decomposition":
            expect(saw_overview, f"development document relationship failed: missing controlling overview for {path}")
        elif source_type == "implementation-plan":
            expect(saw_overview, f"development document relationship failed: missing controlling overview for {path}")
            expect(saw_decomposition, f"development document relationship failed: missing controlling decomposition for {path}")

        for target_path in evidence:
            try:
                resolved_path, resolved_record = resolve_development_document_artifact(target_path, records, compatibility_registry, chunk_owner_paths)
            except KeyError:
                evidence_path = repo_root / target_path
                expect(evidence_path.exists(), f"development document evidence failed: missing evidence path {path} -> {target_path}")
                continue

            if resolved_record is not None:
                continue

            evidence_path = repo_root / resolved_path
            expect(evidence_path.exists(), f"development document evidence failed: missing evidence path {path} -> {target_path}")

    visiting: list[str] = []
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            start = visiting.index(node)
            cycle = visiting[start:] + [node]
            fail(f"development document relationship failed: cycle detected {' -> '.join(cycle)}")
        visiting.append(node)
        for dep in basis_graph[node]:
            visit(dep)
        visiting.pop()
        visited.add(node)

    for node in basis_graph:
        visit(node)


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
    "repo/scripts/github-field-policy": ("bootstrap-infrastructure", "implementation"),
    "repo/scripts/github_field_policy.py": ("bootstrap-infrastructure", "implementation"),
    "repo/scripts/github_field_policy_mutation_test.py": ("bootstrap-infrastructure", "implementation"),
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


def check_lineage_relations(specs: dict[str, dict[str, Any]]) -> None:
    check_relation_targets(specs, "supersedes", {"candidate", "accepted", "superseded", "retired"}, "supersedes")
    check_relation_targets(specs, "superseded_by", {"candidate", "accepted", "superseded", "retired"}, "superseded_by")
    check_supersession_pairs(specs, "supersession relations")
    check_supersession_acyclicity(specs, "supersession relations")


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


def check_schema_conformance(context: ValidationContext) -> None:
    validate_repo_json_schema_conformance(context.repository.specs, context.repository.source_paths, context.repository.schemas)


def check_manifest_phase(context: ValidationContext) -> None:
    check_manifest_completeness(context.repository.specs, context.repository.source_paths, context.repository.actual_paths)


def check_unique_spec_ids_phase(context: ValidationContext) -> None:
    check_unique_spec_ids(context.repository.specs)


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


def check_unique_derived_artifact_paths_phase(context: ValidationContext) -> None:
    check_unique_derived_artifact_paths(context.repository.specs)


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
    expect(profile.get("source_root") == "repo/profiles/github/", "platform profile boundary failed: GitHub source root mismatch")
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
        expect(item.get("authority_category") == expected[1], f"platform profile boundary failed: artifact authority category mismatch for {path}")
        if item.get("classification") == "installed-adapter":
            expect(path.startswith(".github/"), f"platform profile boundary failed: installed adapter path mismatch for {path}")
        else:
            expect(path.startswith("repo/scripts/"), f"platform profile boundary failed: bootstrap infrastructure path mismatch for {path}")

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


def check_lineage_relations_phase(context: ValidationContext) -> None:
    check_lineage_relations(context.repository.specs)


def check_acyclic_dependencies_phase(context: ValidationContext) -> None:
    check_acyclic_dependencies(context.repository.specs)


def check_generated_document_freshness_phase(context: ValidationContext) -> None:
    check_generated_document_freshness(context.repo_root)


def check_development_documents_phase(
    context: ValidationContext,
    *,
    development_roots: dict[str, dict[str, Any]] | None = None,
    compatibility_registry: dict[str, dict[str, Any]] | None = None,
    owned_compatibility_paths: set[str] | None = None,
) -> None:
    if development_roots is None:
        development_roots = DEVELOPMENT_DOCUMENT_ROOTS
    if compatibility_registry is None:
        compatibility_registry = load_development_document_compatibility_registry(
            context.repo_root,
            development_roots=DEVELOPMENT_DOCUMENT_ROOTS,
        )
    if owned_compatibility_paths is None:
        prefixes = tuple(development_roots)
        owned_compatibility_paths = {
            path for path in compatibility_registry if path.startswith(prefixes)
        }
    unmarked_docs: set[str] = set()
    records: dict[str, DevelopmentDocumentRecord] = {}
    chunk_owner_paths: dict[str, str] = {}

    for root_rel, info in development_roots.items():
        root = context.repo_root / root_rel
        expect(root.exists(), f"development document root failed: missing root {root_rel}")
        readme = root / "README.md"
        expect(readme.exists(), f"development document discovery failed: missing {root_rel}README.md")
        readme_text = readme.read_text()

        docs = []
        for path in sorted(root.glob("*.md")):
            if path.name == "README.md":
                continue
            docs.append(path)

        for path in docs:
            text = path.read_text()
            rel_path = path.relative_to(context.repo_root).as_posix()
            if "## Metadata" not in text:
                unmarked_docs.add(rel_path)
                continue

            metadata = extract_document_metadata(text, rel_path)
            schema_key = info["schema_key"]
            schemas = development_document_schemas(context)
            validate_instance(metadata, schemas[schema_key], rel_path, schemas[schema_key])

            if metadata["artifact_type"] != "implementation-plan":
                expect(
                    "workstream_authority" not in metadata,
                    f"development document authority failed: workstream authority outside implementation plan in {rel_path}",
                )
            elif metadata.get("lifecycle_status") == "accepted":
                authority_ids = [entry["id"] for entry in metadata["workstream_authority"]]
                duplicate_authority_ids = sorted({authority_id for authority_id in authority_ids if authority_ids.count(authority_id) > 1})
                expect(
                    not duplicate_authority_ids,
                    f"development document authority failed: duplicate workstream authority identifier "
                    f"{', '.join(duplicate_authority_ids)} in {rel_path}",
                )

            expect(metadata["artifact_type"] == info["artifact_type"], f"development document metadata failed: artifact type mismatch in {rel_path}")
            expect(metadata["root_path"] == root_rel, f"development document metadata failed: root path mismatch in {rel_path}")
            expect(path.parent == root, f"development document path failed: top-level document must live directly under {root_rel}: {rel_path}")
            expect(path.name == f"{metadata['filename_stem'].upper()}.md", f"development document path failed: filename mismatch in {rel_path}")

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

            required_content_areas = metadata.get("required_content_areas")
            expect(isinstance(required_content_areas, dict), f"development document content inventory failed: required content areas must be an object in {rel_path}")
            expected_area_keys = info.get("required_content_area_keys", [])
            expect(set(required_content_areas) == set(expected_area_keys), f"development document content inventory failed: required content area key mismatch in {rel_path}")
            covered_paths: set[str] = set()
            for area_id in expected_area_keys:
                area_paths = required_content_areas[area_id]
                expect(isinstance(area_paths, list), f"development document content inventory failed: required content area {area_id} must be an array in {rel_path}")
                expect(area_paths, f"development document content inventory failed: required content area {area_id} must not be empty in {rel_path}")
                expect(len(area_paths) == len(set(area_paths)), f"development document content inventory failed: duplicate paths in required content area {area_id} in {rel_path}")
                for area_path in area_paths:
                    expect(area_path in declared_paths, f"development document content inventory failed: required content area {area_id} references unknown chunk {area_path} in {rel_path}")
                    covered_paths.add(area_path)
            expect(covered_paths == set(declared_paths), f"development document content inventory failed: required content area coverage mismatch in {rel_path}")

            if root_rel in OVERVIEW_AND_PLAN_ROOTS:
                for chunk in declared_chunks:
                    coverage = chunk.get("coverage")
                    expect(isinstance(coverage, list), f"development document content inventory failed: required coverage must be an array in {rel_path}")
                    expect(coverage, f"development document content inventory failed: required coverage must not be empty in {rel_path}")
                    expect(len(coverage) == len(set(coverage)), f"development document content inventory failed: duplicate coverage entries in {rel_path}")
                    expected_coverage = sorted(area_id for area_id, area_paths in required_content_areas.items() if chunk["path"] in area_paths)
                    expect(set(coverage) == set(expected_coverage), f"development document content inventory failed: chunk coverage mismatch in {rel_path}")

            if root_rel in DECOMPOSITION_ROOTS:
                product_area_paths = {
                    chunk["path"]
                    for chunk in declared_chunks
                    if chunk["role"] == "product-area"
                }
                expect(
                    set(required_content_areas["product_area_inventory"]) == product_area_paths,
                    f"development document content inventory failed: product-area inventory mismatch in {rel_path}",
                )

            records[rel_path] = DevelopmentDocumentRecord(rel_path, root_rel, info, metadata, declared_paths)
            for chunk_path in declared_paths:
                expect(chunk_path not in chunk_owner_paths, f"development document chunk inventory failed: duplicate chunk path {chunk_path}")
                chunk_owner_paths[chunk_path] = rel_path

            if root_rel in DECOMPOSITION_ROOTS:
                seen_area_ids: set[str] = set()
                for chunk in declared_chunks:
                    role = chunk.get("role")
                    expect(role in info["allowed_chunk_roles"], f"development document chunk inventory failed: unsupported decomposition chunk role in {rel_path}")
                    document_coverage = chunk.get("document_coverage")
                    expect(isinstance(document_coverage, list), f"development document content inventory failed: missing document coverage in {rel_path}")
                    expect(document_coverage, f"development document content inventory failed: document coverage must not be empty in {rel_path}")
                    expect(len(document_coverage) == len(set(document_coverage)), f"development document content inventory failed: duplicate document coverage entries in {rel_path}")
                    expected_document_coverage = sorted(area_id for area_id, area_paths in required_content_areas.items() if chunk["path"] in area_paths)
                    expect(set(document_coverage) == set(expected_document_coverage), f"development document content inventory failed: document coverage mismatch in {rel_path}")
                    area_id = chunk.get("area_id")
                    if role == "product-area":
                        expect(isinstance(area_id, str) and area_id, f"development document chunk inventory failed: missing area_id in {rel_path}")
                        expect(area_id not in seen_area_ids, f"development document chunk inventory failed: duplicate area_id in {rel_path}")
                        seen_area_ids.add(area_id)
                        coverage = chunk.get("coverage")
                        expect(isinstance(coverage, list), f"development document chunk inventory failed: missing coverage in {rel_path}")
                        expect(len(coverage) == len(set(coverage)), f"development document chunk inventory failed: duplicate coverage entries in {rel_path}")
                        expect(set(coverage) == set(info["required_chunk_coverage"]), f"development document chunk inventory failed: coverage mismatch in {rel_path}")
                    else:
                        expect(area_id is None, f"development document chunk inventory failed: non-area chunk must not declare area_id in {rel_path}")
                        expect(chunk.get("coverage") is None, f"development document chunk inventory failed: non-area chunk must not declare coverage in {rel_path}")

            orders = [chunk["order"] for chunk in declared_chunks]
            expect(orders == list(range(1, len(orders) + 1)), f"development document chunk inventory failed: non-contiguous order in {rel_path}")

            chunk_index_section = markdown_section(text, "Chunk index")
            chunk_index_links = {resolve_markdown_link_target(rel_path, target) for _label, target in markdown_links(chunk_index_section)}
            expect(chunk_index_links == set(declared_paths), f"development document navigation failed: chunk index link mismatch in {rel_path}")

            for chunk in declared_chunks:
                chunk_path = context.repo_root / chunk["path"]
                expect(chunk_path.exists(), f"development document chunk inventory failed: missing chunk {chunk['path']}")
                expect(chunk_path.is_file(), f"development document chunk inventory failed: chunk path must be a file {chunk['path']}")
                expect(chunk_path.parent == chunk_dir, f"development document path failed: chunk path outside chunk directory {chunk['path']}")
                expect(re.fullmatch(r"\d\d-[a-z0-9][a-z0-9-]*\.md", chunk_path.name) is not None, f"development document path failed: malformed chunk filename {chunk['path']}")

                chunk_text = chunk_path.read_text()
                expect(len(chunk_text.splitlines()) <= MAX_DEVELOPMENT_DOCUMENT_CHUNK_LINES, f"development document size failed: chunk exceeds line limit {chunk['path']}")
                expect(len(chunk_text.encode("utf-8")) <= MAX_DEVELOPMENT_DOCUMENT_CHUNK_BYTES, f"development document size failed: chunk exceeds byte limit {chunk['path']}")
                first_non_empty = next((line for line in chunk_text.splitlines() if line.strip()), "")
                expect(first_non_empty.startswith("# "), f"development document structure failed: chunk must start with a heading {chunk['path']}")
                if root_rel in DECOMPOSITION_ROOTS and chunk.get("role") == "product-area":
                    chunk_headings = markdown_headings(chunk_text)
                    for heading in ["Status", "Purpose", "Responsibilities", "Boundaries", "Dependencies", "Exclusions", "Unresolved decisions", "Successor work"]:
                        expect(heading in chunk_headings, f"development document structure failed: missing product-area heading {heading} in {chunk['path']}")

            canonical_links = {resolve_markdown_link_target(f"{root_rel}README.md", target) for _label, target in markdown_links(markdown_section(readme_text, "Canonical documents"))}
            expect(rel_path in canonical_links, f"development document discovery failed: README does not link to {rel_path}")

    expect(unmarked_docs == owned_compatibility_paths, f"development document classification failed: compatibility registry mismatch; unmarked={sorted(unmarked_docs)}; registered={sorted(owned_compatibility_paths)}")
    check_development_document_relationships(context.repo_root, records, compatibility_registry, chunk_owner_paths)


def _check_repository_lifecycle(
    context: ValidationContext,
) -> None:
    repository_specs = repository_reference_specs(context)
    records = get_development_document_records(
        context,
        development_roots=_repository_development_roots(),
    )

    for plan_path, record in records.items():
        metadata = record.metadata
        if metadata["artifact_type"] != "implementation-plan":
            continue
        if metadata.get("lifecycle_status") not in {"accepted", "planning-complete"}:
            continue

        required_specs = metadata.get("applicable_accepted_specifications", [])
        if not required_specs:
            continue

        for spec_ref in required_specs:
            target_spec_id = (
                spec_ref.get("spec_id") if isinstance(spec_ref, dict) else spec_ref
            )
            if target_spec_id in repository_specs:
                target_spec = repository_specs[target_spec_id]
                expect(
                    target_spec["status"] == "accepted",
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"non-accepted repository specification {target_spec_id} "
                    f"(status: {target_spec['status']})",
                )
            else:
                fail(
                    f"lifecycle plan failed: plan {plan_path} references "
                    f"unknown specification {target_spec_id}"
                )




def get_development_document_records(
    context: ValidationContext,
    *,
    development_roots: dict[str, dict[str, Any]] | None = None,
) -> dict[str, DevelopmentDocumentRecord]:
    if development_roots is None:
        development_roots = DEVELOPMENT_DOCUMENT_ROOTS
    records: dict[str, DevelopmentDocumentRecord] = {}
    chunk_owner_paths: dict[str, str] = {}

    for root_rel, info in development_roots.items():
        root = context.repo_root / root_rel
        if not root.exists():
            continue
        readme = root / "README.md"
        if not readme.exists():
            continue

        docs = sorted(path for path in root.glob("*.md") if path.name != "README.md")
        for path in docs:
            text = path.read_text()
            rel_path = path.relative_to(context.repo_root).as_posix()
            if "## Metadata" not in text:
                continue

            metadata = extract_document_metadata(text, rel_path)
            metadata["artifact_type"] = info["artifact_type"]
            metadata["root_path"] = root_rel
            declared_chunks = metadata["subordinate_chunks"]
            declared_paths = [chunk["path"] for chunk in declared_chunks]

            records[rel_path] = DevelopmentDocumentRecord(rel_path, root_rel, info, metadata, declared_paths)
            for chunk_path in declared_paths:
                chunk_owner_paths[chunk_path] = rel_path

    return records



def _load_repository_only_context(repo_root: Path) -> ValidationContext:
    manifest, specs, source_paths, actual_paths = load_repo_specs(repo_root)
    schemas = load_repo_schemas(repo_root)
    repository = RepositoryValidationContext(
        manifest,
        specs,
        source_paths,
        actual_paths,
        schemas,
    )
    return ValidationContext(repo_root, repository, None, None)


def _repository_development_roots() -> dict[str, dict[str, Any]]:
    return {
        root_rel: info
        for root_rel, info in DEVELOPMENT_DOCUMENT_ROOTS.items()
        if not root_rel.startswith("product/")
    }


def _check_repository_development_documents(
    context: ValidationContext,
) -> None:
    selected_roots = _repository_development_roots()
    full_registry = load_development_document_compatibility_registry(
        context.repo_root,
        development_roots=DEVELOPMENT_DOCUMENT_ROOTS,
    )
    prefixes = tuple(selected_roots)
    owned_compatibility_paths = {
        path for path in full_registry if path.startswith(prefixes)
    }
    check_development_documents_phase(
        context,
        development_roots=selected_roots,
        compatibility_registry=full_registry,
        owned_compatibility_paths=owned_compatibility_paths,
    )






def _check_repository_generated_freshness(
    context: ValidationContext,
) -> None:
    from docgen import SPECIAL_RENDERERS, render_spec_projection

    specs = context.repository.specs
    source_paths = context.repository.source_paths
    derived_root = context.repo_root / "repo/derived/specs/repo"
    expected_markdown_paths: set[str] = set()

    for spec_id in sorted(specs, key=lambda item: source_paths[item]):
        spec = specs[spec_id]
        source_path = source_paths[spec_id]

        for artifact in spec.get("derived_artifacts", []):
            relative_path = artifact["path"]
            path = resolve_repo_path(context.repo_root, relative_path)
            renderer_id = artifact.get("renderer")

            if renderer_id is None:
                expect(
                    artifact["type"] == "markdown",
                    "generated-document freshness failed: "
                    f"unsupported derived artifact type without renderer: "
                    f"{artifact['type']}",
                )
                content = render_spec_projection(
                    spec["title"],
                    source_path,
                    spec,
                    include_authoritative_specs=(spec_id == "repo.manifest"),
                )
            else:
                renderer = SPECIAL_RENDERERS.get(renderer_id)
                expect(
                    renderer is not None,
                    "generated-document freshness failed: "
                    f"unsupported renderer: {renderer_id}",
                )
                content = renderer(spec)

            if (
                relative_path.endswith(".md")
                and relative_path.startswith(
                    derived_root.relative_to(context.repo_root).as_posix() + "/"
                )
            ):
                expected_markdown_paths.add(relative_path)

            if not path.exists() or path.read_text() != content:
                fail(
                    "generated-document freshness failed: "
                    f"source {source_path} -> output {relative_path}"
                )

    actual_markdown_paths: set[str] = set()
    if derived_root.exists():
        actual_markdown_paths = {
            path.relative_to(context.repo_root).as_posix()
            for path in derived_root.rglob("*.md")
            if path.is_file()
        }

    missing = sorted(expected_markdown_paths - actual_markdown_paths)
    extra = sorted(actual_markdown_paths - expected_markdown_paths)
    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing derived markdown: {', '.join(missing)}")
        if extra:
            parts.append(f"orphaned derived markdown: {', '.join(extra)}")
        fail("generated-document freshness failed: " + "; ".join(parts))


REPOSITORY_LEAF_VALIDATION_PHASES: list[tuple[str, Any]] = [
    ("repository root boundary", check_repository_root_boundary),
    ("repository JSON Schema conformance", check_schema_conformance),
    ("manifest completeness", check_manifest_phase),
    ("unique specification IDs", check_unique_spec_ids_phase),
    ("unique item properties", check_unique_item_properties_phase),
    ("platform profile boundary", check_platform_profile_boundary),
    ("GitHub profile freshness", check_github_profile_freshness_phase),
    ("unique derived artifact paths", check_unique_derived_artifact_paths_phase),
    ("dependency target lifecycle", check_dependency_targets_phase),
    ("resolvable references", check_resolvable_references_phase),
    ("lineage relations", check_lineage_relations_phase),
    ("acyclic dependencies", check_acyclic_dependencies_phase),
]


def validate_repo(repo_root: Path) -> None:
    context = _load_repository_only_context(repo_root)
    for label, check in REPOSITORY_LEAF_VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")
    _check_repository_development_documents(context)
    print("ok: repository development documents")
    _check_repository_lifecycle(context)
    print("ok: repository lifecycle authority sequence")
    _check_repository_generated_freshness(context)
    print("ok: repository generated-document freshness")
