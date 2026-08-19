from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from pathlib import Path
from typing import Any

from repo_model import load_json as load_repo_json
from repo_model import RepositoryError
from github_profile import GitHubProfileError, check_profile_freshness

from ..core.errors import expect, fail
from ..core.context import RepositoryValidationContext, ValidationContext, load_repo_specs
from ..checks.development_documents import DEVELOPMENT_DOCUMENT_ROOTS, check_development_documents_phase, get_development_document_records, load_development_document_compatibility_registry
from ..checks.generated_outputs import check_generated_document_freshness
from ..core.invariants import check_supersession_acyclicity, check_supersession_pairs, check_unique_item_properties
from ..core.paths import resolve_repo_path
from ..core.schema_subset import load_repo_schemas, validate_instance


def repository_reference_specs(context: ValidationContext) -> dict[str, dict[str, Any]]:
    if context.repository is not None:
        return context.repository.specs
    expect(context.external_repository is not None, "validation context missing external repository reference state")
    return context.external_repository.specs


def chunk_dir_for_metadata(metadata: dict[str, Any]) -> str:
    return f"{metadata['root_path']}{metadata['document_slug']}/"


def document_chunk_paths(metadata: dict[str, Any]) -> list[str]:
    return [chunk["path"] for chunk in metadata["subordinate_chunks"]]


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


EXPECTED_GITHUB_ARTIFACT_INVENTORY = {
    ".github/ISSUE_TEMPLATE/governing-issue.yml": ("installed-adapter", "profile-specific"),
    ".github/PULL_REQUEST_TEMPLATE.md": ("installed-adapter", "profile-specific"),
    ".github/workflows/github-field-policy.yml": ("installed-adapter", "profile-specific"),
    ".github/workflows/validation.yml": ("installed-adapter", "profile-specific"),
    "repo/validation/github/github-field-policy": ("bootstrap-infrastructure", "implementation"),
    "repo/validation/github/github_field_policy.py": ("bootstrap-infrastructure", "implementation"),
    "repo/validation/tests/github_field_policy_mutation_test.py": ("bootstrap-infrastructure", "implementation"),
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
            expect(path.startswith("repo/validation/"), f"platform profile boundary failed: bootstrap infrastructure path mismatch for {path}")

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




def check_resolvable_references_phase(context: ValidationContext) -> None:
    check_resolvable_references(context.repo_root, context.repository.specs)


def check_lineage_relations_phase(context: ValidationContext) -> None:
    check_lineage_relations(context.repository.specs)


def check_acyclic_dependencies_phase(context: ValidationContext) -> None:
    check_acyclic_dependencies(context.repository.specs)


def check_generated_document_freshness_phase(context: ValidationContext) -> None:
    check_generated_document_freshness(context.repo_root)


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

            # Repository validation owns only generated outputs under repo/.
            # Cross-domain adapters remain declared and are validated later by
            # root/aggregate validation.
            if not (
                relative_path == "repo"
                or relative_path.startswith("repo/")
            ):
                continue

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
    ("repository JSON Schema conformance", check_schema_conformance),
    ("manifest completeness", check_manifest_phase),
    ("unique specification IDs", check_unique_spec_ids_phase),
    ("unique item properties", check_unique_item_properties_phase),
    ("platform profile boundary", check_platform_profile_boundary),
    ("unique derived artifact paths", check_unique_derived_artifact_paths_phase),
    ("dependency target lifecycle", check_dependency_targets_phase),
    ("resolvable references", check_resolvable_references_phase),
    ("lineage relations", check_lineage_relations_phase),
    ("acyclic dependencies", check_acyclic_dependencies_phase),
]


REPOSITORY_VALIDATION_PHASES: list[tuple[str, Any]] = [
    *REPOSITORY_LEAF_VALIDATION_PHASES,
    ("repository development documents", _check_repository_development_documents),
    ("repository lifecycle authority sequence", _check_repository_lifecycle),
    ("repository generated-document freshness", _check_repository_generated_freshness),
]


def validate_repository_phase(repo_root: Path, phase_label: str) -> None:
    context = _load_repository_only_context(repo_root)
    for label, check in REPOSITORY_VALIDATION_PHASES:
        if label == phase_label:
            check(context)
            return
    fail(f"unknown repository validation phase: {phase_label}")


def validate_repo(repo_root: Path) -> None:
    context = _load_repository_only_context(repo_root)
    for label, check in REPOSITORY_VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")
