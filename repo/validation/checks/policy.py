"""Domain-specific production validation policy extension point."""

from __future__ import annotations

import os
import subprocess

from pathlib import Path

from typing import Any

from ..core.context import ValidationContext
from ..core.errors import expect, fail
from .development_documents import (
    _repository_development_roots,
    get_development_document_records,
)


# validation-metadata: {"role": "helper"}
def _check_exact_validation_layout(domain_root: Path, *, require_github: bool, label: str) -> None:
    expected_top={"README.md","manifest.json","checks","core","runners","tests"}
    if require_github: expected_top.add("github")
    expect(domain_root.is_dir(), f"{label} validation layout failed: missing validation domain")
    actual={p.name:p for p in domain_root.iterdir()}
    missing=sorted(expected_top-set(actual)); extra=sorted(set(actual)-expected_top)
    expect(not missing, f"{label} validation layout failed: missing top-level entries: {', '.join(missing)}")
    expect(not extra, f"{label} validation layout failed: unexpected top-level entries: {', '.join(extra)}")
    for n in ("README.md","manifest.json"):
        expect(actual[n].is_file(), f"{label} validation layout failed: {n} must be a file")
    for n in ("checks","core","runners","tests"):
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

# validation-metadata: {"role": "helper"}
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


# validation-metadata: {"role": "task", "task_id": "repo.validation.structural-envelopes", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-039"}}
def check_repository_structural_envelopes(context: ValidationContext) -> None:
    repo_root = context.repo_root
    _check_exact_directory_envelope(
        repo_root / "repo",
        {"derived", "docs", "profiles", "schemas", "scripts", "specs", "src", "validation"},
        label="repository ownership envelope",
    )
    _check_exact_directory_envelope(repo_root / "repo/specs", {"repo"}, label="repository specifications envelope")
    _check_exact_directory_envelope(repo_root / "repo/schemas", {"repo"}, label="repository schemas envelope")
    _check_exact_directory_envelope(repo_root / "repo/derived", {"specs"}, label="repository derived envelope")
    _check_exact_directory_envelope(repo_root / "repo/derived/specs", {"repo"}, label="repository derived specifications envelope")


# validation-metadata: {"role": "task", "task_id": "repo.validation.validation-layout", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-001"}}
def check_validation_layout(context: ValidationContext) -> None:
    _check_exact_validation_layout(context.repo_root / "repo/validation", require_github=True, label="repo")


# validation-metadata: {"role": "task", "task_id": "repo.validation.repository-source-layout", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
def check_repository_source_layout(context: ValidationContext) -> None:
    repo_root = context.repo_root
    scripts_root = repo_root / "repo/scripts"
    source_root = repo_root / "repo/src"

    expect(source_root.is_dir(), "repository source layout failed: missing repo/src")
    expect(scripts_root.is_dir(), "repository source layout failed: missing repo/scripts")
    expect(
        not (source_root / "validation").exists(),
        "repository source layout failed: validation must remain under repo/validation",
    )

    for path in sorted(scripts_root.iterdir(), key=lambda item: item.name):
        expect(
            path.is_file(),
            f"repository source layout failed: repo/scripts contains non-entry-point path {path.name}",
        )
        expect(
            path.suffix != ".py",
            f"repository source layout failed: repo/scripts contains Python implementation module {path.name}",
        )
        expect(
            os.access(path, os.X_OK),
            f"repository source layout failed: repo/scripts entry point is not executable: {path.name}",
        )

# validation-metadata: {"role": "task", "task_id": "repo.validation.platform-profile-boundary", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-015"}}
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

# validation-metadata: {"role": "helper"}
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

# validation-metadata: {"role": "helper"}
def repository_reference_specs(context: ValidationContext) -> dict[str, dict[str, Any]]:
    if context.repository is not None:
        return context.repository.specs
    expect(context.external_repository is not None, "validation context missing external repository reference state")
    return context.external_repository.specs

# validation-metadata: {"role": "task", "task_id": "repo.validation.lifecycle-authority-sequence", "normative_reference": {"spec_id": "repo.validation", "requirement_id": "REPO-VAL-003"}}
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

# validation-metadata: {"role": "helper"}
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

# validation-metadata: {"role": "helper"}
def check_generate_docs_cli_contract(repo_root: Path) -> None:
    proc = subprocess.run([str(repo_root / "repo/scripts/generate-docs")], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode == 0, "generate-docs launcher failed")
    expect(proc.stdout.strip() == "", "generate-docs launcher wrote stdout")
    expect(proc.stderr.strip() == "", "generate-docs launcher wrote stderr")

    proc = subprocess.run([str(repo_root / "repo/scripts/generate-docs"), "--unknown-mode"], cwd=repo_root, capture_output=True, text=True)
    expect(proc.returncode != 0, "generate-docs unknown mode succeeded")


# validation-metadata: {"role": "helper"}
def check_validate_cli_contract(repo_root: Path) -> None:
    validate_launcher = (repo_root / "repo/scripts/validate").read_text()
    test_launcher = (repo_root / "repo/scripts/test-validation").read_text()
    expect("$root/product/scripts" not in validate_launcher, "repository validate launcher depends on product scripts")
    expect("$root/product/scripts" not in test_launcher, "repository validation-test launcher depends on product scripts")
    expect('PYTHONPATH="$root/repo/src:$root/repo${PYTHONPATH:+:$PYTHONPATH}"' in validate_launcher, "repository validate launcher runtime boundary mismatch")
    expect('PYTHONPATH="$root/repo/src:$root/repo${PYTHONPATH:+:$PYTHONPATH}"' in test_launcher, "repository validation-test launcher runtime boundary mismatch")

    expect(
        "repo_tree_sha" not in validate_launcher,
        "repository validate launcher still carries mutable repo-tree SHA state",
    )

    proc = subprocess.run(
        [str(repo_root / "repo/scripts/validate"), "--unknown-mode"],
        cwd=repo_root,
        capture_output=True,
        text=True,
    )
    expect(proc.returncode != 0, "repository validate unknown argument succeeded")
    expect(proc.stdout.strip() == "", "repository validate unknown argument wrote stdout")
    expect(
        proc.stderr.strip() == "validation error: unknown argument: --unknown-mode",
        "repository validate unknown-argument stderr mismatch",
    )
