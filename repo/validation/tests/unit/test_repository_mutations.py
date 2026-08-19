from __future__ import annotations

import copy
import json
import sys
import tempfile
from pathlib import Path

from repo_model import load_specs
from validation.checks.development_documents import DevelopmentDocumentRecord, check_development_document_relationships
from validation.checks.generated_outputs import check_generated_document_write_behavior
from validation.core.errors import fail
from validation.core.paths import resolve_repo_path
from validation.checks.domain import (
    REPOSITORY_LEAF_VALIDATION_PHASES,
    validate_repo,
    validate_repository_phase,
)

from ..self.mutation_support import add_lifecycle_spec, create_repo_fixture, expect_failure, mutate_json

def run_repository_validation_phase_contract_tests(repo_root: Path) -> None:
    labels = [label for label, _check in REPOSITORY_LEAF_VALIDATION_PHASES]
    expected_labels = [
        "repository JSON Schema conformance",
        "manifest completeness",
        "unique specification IDs",
        "unique item properties",
        "platform profile boundary",
        "unique derived artifact paths",
        "dependency target lifecycle",
        "resolvable references",
        "lineage relations",
        "acyclic dependencies",
    ]
    if labels != expected_labels:
        fail(f"repository validation phase order changed: {labels}")
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        validate_repo(temp_repo)

    print("ok: repository validation phase contract")


def run_repository_root_boundary_tests(repo_root: Path) -> None:
    def expect_root_failure(description: str, func, fragment: str) -> None:
        try:
            func()
        except RootValidationError as exc:
            if fragment not in str(exc):
                fail(
                    f"mutation test failed: {description} "
                    f"(expected {fragment!r}, got {exc})"
                )
        else:
            fail(f"mutation test failed: {description} did not fail")

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "undeclared-root-file.txt").write_text("mutation\n")
        expect_root_failure(
            "undeclared root file",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: undeclared top-level entries: undeclared-root-file.txt",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "undeclared-root-directory").mkdir()
        expect_root_failure(
            "undeclared root directory",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: undeclared top-level entries: undeclared-root-directory",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "docs").mkdir()
        expect_root_failure(
            "legacy root docs reintroduction",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: undeclared top-level entries: docs",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "README.md").unlink()
        expect_root_failure(
            "missing required root",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: missing required top-level entries: README.md",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "README.md").unlink()
        (temp_repo / "README.md").mkdir()
        expect_root_failure(
            "wrong-kind required root file",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: wrong-kind top-level entries: README.md (expected file)",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        import shutil
        shutil.rmtree(temp_repo / "user")
        (temp_repo / "user").write_text("mutation\n")
        expect_root_failure(
            "wrong-kind required root directory",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: wrong-kind top-level entries: user (expected directory)",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / ".pytest_cache").mkdir()
        expect_root_failure(
            "pytest cache at repository root",
            lambda: validate_root_boundary(temp_repo, initialized=False),
            "repository root boundary failed: undeclared top-level entries: .pytest_cache",
        )

    print("ok: repository root boundary")


def _git_for_root_integrity(repo: Path, *args: str) -> str:
    import subprocess

    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout.strip()




def _make_integrity_framework(root: Path) -> tuple[Path, str, str]:
    framework = root / "framework"
    framework.mkdir()
    _git_for_root_integrity(framework, "init", "-q")
    _git_for_root_integrity(framework, "config", "user.email", "validation@example.invalid")
    _git_for_root_integrity(framework, "config", "user.name", "Validation")

    _write_integrity_inventory(framework, content="baseline\n")
    _git_for_root_integrity(framework, "add", "-A")
    _git_for_root_integrity(framework, "commit", "-qm", "baseline")
    baseline = _git_for_root_integrity(framework, "rev-parse", "HEAD")

    _write_integrity_inventory(framework, content="current\n")
    _git_for_root_integrity(framework, "add", "-A")
    _git_for_root_integrity(framework, "commit", "-qm", "current")
    current = _git_for_root_integrity(framework, "rev-parse", "HEAD")
    return framework, baseline, current


def _materialize_integrity_authority_bundle(
    repo: Path,
    framework: Path,
    revision: str,
) -> None:
    product_scripts = Path(__file__).resolve().parents[4] / "product/scripts"
    if str(product_scripts) not in sys.path:
        sys.path.insert(0, str(product_scripts))
    from initializer.framework_authority import build_framework_authority_bundle

    bundle_dir = (
        repo
        / "repo/initializer/framework-authority"
        / revision
    )
    build_framework_authority_bundle(
        str(framework),
        revision,
        bundle_dir,
    )


def _make_initialized_integrity_fixture(
    root: Path,
    name: str,
    framework: Path,
    baseline: str,
    current: str,
    *,
    add_unmanaged_drift: bool = False,
) -> Path:
    repo = root / name
    repo.mkdir()
    _git_for_root_integrity(repo, "init", "-q")
    _git_for_root_integrity(repo, "config", "user.email", "target@example.invalid")
    _git_for_root_integrity(repo, "config", "user.name", "Target")

    tool = repo / "repo/scripts/tool.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("baseline\n", encoding="utf-8")
    _git_for_root_integrity(repo, "add", "-A")
    _git_for_root_integrity(repo, "commit", "-qm", "initialized baseline")

    tool.write_text("current\n", encoding="utf-8")
    lineage = repo / "repo/initializer/framework-lineage.json"
    lineage.parent.mkdir(parents=True, exist_ok=True)
    lineage.write_text(
        json.dumps(
            {
                "schema_version": "1",
                "entries": [
                    {
                        "framework_repository": str(framework.resolve()),
                        "framework_revision": {
                            "object_format": "sha1",
                            "object_id": baseline,
                        },
                    },
                    {
                        "framework_repository": str(framework.resolve()),
                        "framework_revision": {
                            "object_format": "sha1",
                            "object_id": current,
                        },
                    },
                ],
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    _materialize_integrity_authority_bundle(repo, framework, baseline)
    _materialize_integrity_authority_bundle(repo, framework, current)
    if add_unmanaged_drift:
        (repo / "repo/unmanaged.txt").write_text("unauthorized\n", encoding="utf-8")
    _git_for_root_integrity(repo, "add", "-A")
    _git_for_root_integrity(repo, "commit", "-qm", "framework reconciliation")
    return repo


def run_repository_initialized_tree_integrity_tests(repo_root: Path) -> None:
    del repo_root

    def expect_integrity_failure(description: str, func, fragment: str) -> None:
        try:
            func()
        except RootValidationError as exc:
            if fragment not in str(exc):
                fail(
                    f"mutation test failed: {description} "
                    f"(expected {fragment!r}, got {exc})"
                )
        else:
            fail(f"mutation test failed: {description} did not fail")

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_name:
        temp_root = Path(temp_name)
        framework, baseline, current = _make_integrity_framework(temp_root)

        legal = _make_initialized_integrity_fixture(
            temp_root,
            "legal-managed-transition",
            framework,
            baseline,
            current,
        )
        validate_repo_tree_integrity(legal)

        drift = _make_initialized_integrity_fixture(
            temp_root,
            "unmanaged-drift",
            framework,
            baseline,
            current,
            add_unmanaged_drift=True,
        )
        expect_integrity_failure(
            "committed repo drift outside initializer-managed authority",
            lambda: validate_repo_tree_integrity(drift),
            "outside initializer-managed authority",
        )

        tampered = _make_initialized_integrity_fixture(
            temp_root,
            "tampered-managed-content",
            framework,
            baseline,
            current,
        )
        (tampered / "repo/scripts/tool.py").write_text(
            "tampered\n",
            encoding="utf-8",
        )
        _git_for_root_integrity(tampered, "add", "-A")
        _git_for_root_integrity(tampered, "commit", "-qm", "tamper managed material")
        expect_integrity_failure(
            "managed repo bytes outside accepted framework authority",
            lambda: validate_repo_tree_integrity(tampered),
            "does not match accepted framework authority",
        )

    print("ok: initialized repository tree integrity")


def run_repository_development_document_compatibility_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/docs/development-document-compatibility.json",
            lambda registry: registry["entries"].__delitem__(0) or registry,
        )
        expect_failure("legacy development document without registry entry", lambda: validate_repository_phase(temp_repo, "repository development documents"), "compatibility registry mismatch")

    print("ok: repository development document compatibility")


def run_repository_manifest_completeness_tests(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "repo.unlisted"
        (temp_repo / "repo/specs/repo/unlisted.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("unlisted json file", lambda: validate_repository_phase(temp_repo, "manifest completeness"), "manifest completeness failed")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "repo/specs/repo/validation.json").unlink()
        expect_failure("missing manifest file", lambda: validate_repository_phase(temp_repo, "manifest completeness"), "manifest completeness failed")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"][-1].__setitem__("path", "repo/specs/repo/repository-structure.json") or manifest,
        )
        expect_failure("duplicate manifest paths", lambda: validate_repository_phase(temp_repo, "manifest completeness"), "manifest completeness failed")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec.__setitem__("spec_id", "product.validation") or spec,
        )
        expect_failure("product spec under repo root", lambda: validate_repository_phase(temp_repo, "manifest completeness"), "manifest entry repo.validation does not match repo/specs/repo/validation.json")

    print("ok: repository manifest completeness")


def run_repository_schema_conformance_tests(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "product.repo-validation"
        (temp_repo / "repo/specs/repo/product-validation.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        mutate_json(
            temp_repo / "repo/specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"].append({"spec_id": "product.repo-validation", "path": "repo/specs/repo/product-validation.json"}) or manifest,
        )
        expect_failure("product file in repository manifest", lambda: validate_repository_phase(temp_repo, "repository JSON Schema conformance"), "pattern mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"][0].__setitem__("path", "../../etc/passwd") or spec,
        )
        expect_failure("derived artifact path escape", lambda: validate_repository_phase(temp_repo, "repository JSON Schema conformance"), "pattern mismatch")

    print("ok: repository schema conformance")


def run_repository_derived_artifact_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "repo/derived/specs/repo/review-proposal.md"}) or spec,
        )
        expect_failure("duplicate derived artifact paths", lambda: validate_repository_phase(temp_repo, "unique derived artifact paths"), "duplicate derived artifact paths failed")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "repo/derived/specs/repo/validation-missing.md"}) or spec,
        )
        expect_failure("missing derived artifact", lambda: check_generated_document_write_behavior(temp_repo), "generated-document write failed")

    print("ok: repository derived artifact")


def run_repository_dependency_lifecycle_tests(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate")
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["dependencies"].append({"spec_id": "repo.lifecycle-candidate"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repository_phase(temp_repo, "dependency target lifecycle")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["dependencies"].append({"spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("dependency to retired spec", lambda: validate_repository_phase(temp_repo, "dependency target lifecycle"), "dependencies failed")

    print("ok: repository dependency lifecycle")




def run_repository_reference_tests(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["references"][-1].__setitem__("path", "../../etc/passwd") or spec,
        )
        expect_failure("artifact reference path escape", lambda: validate_repository_phase(temp_repo, "repository JSON Schema conformance"), "oneOf mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["references"].append({"type": "specification", "kind": "historical", "spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repository_phase(temp_repo, "resolvable references")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["references"].append({"type": "specification", "spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("normative reference to retired spec", lambda: validate_repository_phase(temp_repo, "resolvable references"), "resolvable references failed")

    print("ok: repository reference")


def run_repository_lineage_tests(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate", supersedes=["repo.validation"])
        expect_failure("non-reciprocal supersession pair", lambda: validate_repository_phase(temp_repo, "lineage relations"), "non-reciprocal supersedes pair")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate", supersedes=["repo.validation"])
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec.setdefault("superseded_by", []).append("repo.lifecycle-candidate") or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repository_phase(temp_repo, "lineage relations")

    print("ok: repository lineage")


def run_repository_unique_item_property_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/governing-issue.json",
            lambda spec: spec["issue_fields"].__setitem__(1, copy.deepcopy(spec["issue_fields"][0])) or spec,
        )
        expect_failure("governing issue field uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/review-proposal.json",
            lambda spec: spec["review_fields"].__setitem__(1, copy.deepcopy(spec["review_fields"][0])) or spec,
        )
        expect_failure("review proposal field uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["normative_requirements"].__setitem__(1, copy.deepcopy(spec["normative_requirements"][0])) or spec,
        )
        expect_failure("requirement id uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["dependencies"].append(copy.deepcopy(spec["dependencies"][0])) or spec,
        )
        expect_failure("dependency uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties spec_id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["references"].append(copy.deepcopy(spec["references"][0])) or spec,
        )
        expect_failure("reference uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties type, spec_id, path, kind")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].append(copy.deepcopy(spec["derived_artifacts"][0])) or spec,
        )
        expect_failure("derived artifact uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties path")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/artifact-taxonomy.json",
            lambda spec: spec["artifact_classes"].__setitem__(1, copy.deepcopy(spec["artifact_classes"][0])) or spec,
        )
        expect_failure("artifact class uniqueness", lambda: validate_repository_phase(temp_repo, "unique item properties"), "duplicate item properties identifier")

    print("ok: repository unique item property")


def run_repository_platform_profile_boundary_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: (
                spec["profiles"][0]["artifact_inventory"][0].__setitem__("classification", "bootstrap-infrastructure"),
                spec["profiles"][0]["artifact_inventory"][0].__setitem__("authority_category", "implementation"),
                spec,
            )[-1],
        )
        expect_failure("installed adapter authority", lambda: validate_repository_phase(temp_repo, "platform profile boundary"), "artifact classification mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["artifact_inventory"][0].pop("profile_id") and spec,
        )
        expect_failure("profile artifact identity", lambda: validate_repository_phase(temp_repo, "repository JSON Schema conformance"), "missing required property profile_id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["remote_state_kinds"].__setitem__(0, "repo/derived/specs/repo/rulesets.json") or spec,
        )
        expect_failure("remote state kinds", lambda: validate_repository_phase(temp_repo, "repository JSON Schema conformance"), "enum mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0].__setitem__("authority_boundary", "adapter-authoritative") or spec,
        )
        expect_failure("profile authority boundary", lambda: validate_repository_phase(temp_repo, "repository JSON Schema conformance"), "enum mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"].append(copy.deepcopy(spec["profiles"][0])) or spec,
        )
        expect_failure("duplicate profile identifier", lambda: validate_repository_phase(temp_repo, "platform profile boundary"), "duplicate profile identifier github")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["mutation_record_fields"].remove("accepted repository revision") or spec,
        )
        expect_failure("hosting mutation record fields", lambda: validate_repository_phase(temp_repo, "platform profile boundary"), "hosting mutation record fields mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "repo/specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["deployment_state"]["plan_apply_separation"].append("Apply requires a change ticket.") or spec,
        )
        expect_failure("deployment-state contract", lambda: validate_repository_phase(temp_repo, "platform profile boundary"), "plan/apply separation mismatch")

    print("ok: repository platform profile boundary")


def run_repository_path_helper_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        expect_failure("repository-relative path helper", lambda: resolve_repo_path(temp_repo, "../../etc/passwd"), "invalid repository-relative path")

    print("ok: repository path helper")
