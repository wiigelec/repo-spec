from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from repo_model import load_specs
from validation.generated_outputs import check_generated_document_write_behavior
from validation.errors import fail
from validation.repository_checks import VALIDATION_PHASES, resolve_repo_path, validate_repo

from .mutation_support import add_lifecycle_spec, create_repo_fixture, expect_failure, mutate_json


def run_repository_mutations(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    labels = [label for label, _check in VALIDATION_PHASES]
    expected_labels = [
        "repository JSON Schema conformance",
        "manifest completeness",
        "unique specification IDs",
        "unique item properties",
        "platform profile boundary",
        "GitHub profile freshness",
        "unique derived artifact paths",
        "product specification root",
        "product correspondence inventory",
        "product conformance completeness",
        "dependency target lifecycle",
        "product dependency directions",
        "product completeness",
        "resolvable references",
        "lineage relations",
        "product acyclic dependencies",
        "acyclic dependencies",
        "generated-document freshness",
    ]
    if labels != expected_labels:
        fail(f"validation phase order changed: {labels}")

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "repo.unlisted"
        (temp_repo / "specs/repo/unlisted.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("unlisted json file", lambda: validate_repo(temp_repo), "manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "product.repo-validation"
        (temp_repo / "specs/repo/product-validation.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"].append({"spec_id": "product.repo-validation", "path": "specs/repo/product-validation.json"}) or manifest,
        )
        expect_failure("product file in repository manifest", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        product_root = temp_repo / "specs/product"
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "repo.product-root-rogue"
        (product_root / "rogue.json").parent.mkdir(parents=True, exist_ok=True)
        (product_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("product root contamination", lambda: validate_repo(temp_repo), "undeclared JSON content under specs/product/")

        for level_name in ["level-0", "level-1", "level-2", "level-3"]:
            temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
            clone_index += 1
            product_level_root = temp_repo / "specs/product" / level_name
            extra_spec = copy.deepcopy(specs["repo.validation"])
            extra_spec["spec_id"] = f"repo.{level_name}.rogue"
            product_level_root.mkdir(parents=True, exist_ok=True)
            (product_level_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
            expect_failure(f"product root contamination in {level_name}", lambda: validate_repo(temp_repo), "undeclared JSON content under specs/product/")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "specs/repo/validation.json").unlink()
        expect_failure("missing manifest file", lambda: validate_repo(temp_repo), "manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"][-1].__setitem__("path", "specs/repo/repository-structure.json") or manifest,
        )
        expect_failure("duplicate manifest paths", lambda: validate_repo(temp_repo), "manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/review-proposal.md"}) or spec,
        )
        expect_failure("duplicate derived artifact paths", lambda: validate_repo(temp_repo), "duplicate derived artifact paths failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/validation-missing.md"}) or spec,
        )
        expect_failure("missing derived artifact", lambda: check_generated_document_write_behavior(temp_repo), "generated-document write failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"][-1].__setitem__("path", "../../etc/passwd") or spec,
        )
        expect_failure("artifact reference path escape", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec.__setitem__("spec_id", "product.validation") or spec,
        )
        expect_failure("product spec under repo root", lambda: validate_repo(temp_repo), "manifest entry repo.validation does not match specs/repo/validation.json")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"][0].__setitem__("path", "../../etc/passwd") or spec,
        )
        expect_failure("derived artifact path escape", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["dependencies"].append({"spec_id": "repo.lifecycle-candidate"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["dependencies"].append({"spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("dependency to retired spec", lambda: validate_repo(temp_repo), "dependencies failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"].append({"type": "specification", "kind": "historical", "spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"].append({"type": "specification", "spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("normative reference to retired spec", lambda: validate_repo(temp_repo), "resolvable references failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate", supersedes=["repo.validation"])
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec.setdefault("superseded_by", []).append("repo.lifecycle-candidate") or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/governing-issue.json",
            lambda spec: spec["issue_fields"].__setitem__(1, copy.deepcopy(spec["issue_fields"][0])) or spec,
        )
        expect_failure("governing issue field uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/review-proposal.json",
            lambda spec: spec["review_fields"].__setitem__(1, copy.deepcopy(spec["review_fields"][0])) or spec,
        )
        expect_failure("review proposal field uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["normative_requirements"].__setitem__(1, copy.deepcopy(spec["normative_requirements"][0])) or spec,
        )
        expect_failure("requirement id uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["dependencies"].append(copy.deepcopy(spec["dependencies"][0])) or spec,
        )
        expect_failure("dependency uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties spec_id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"].append(copy.deepcopy(spec["references"][0])) or spec,
        )
        expect_failure("reference uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties type, spec_id, path, kind")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].append(copy.deepcopy(spec["derived_artifacts"][0])) or spec,
        )
        expect_failure("derived artifact uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: (
                spec["profiles"][0]["artifact_inventory"][0].__setitem__("classification", "bootstrap-infrastructure"),
                spec["profiles"][0]["artifact_inventory"][0].__setitem__("authority_category", "bootstrap"),
                spec,
            )[-1],
        )
        expect_failure("installed adapter authority", lambda: validate_repo(temp_repo), "artifact classification mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["artifact_inventory"][0].pop("profile_id") and spec,
        )
        expect_failure("profile artifact identity", lambda: validate_repo(temp_repo), "missing required property profile_id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["remote_state_kinds"].__setitem__(0, "derived/specs/repo/rulesets.json") or spec,
        )
        expect_failure("remote state kinds", lambda: validate_repo(temp_repo), "enum mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0].__setitem__("authority_boundary", "adapter-authoritative") or spec,
        )
        expect_failure("profile authority boundary", lambda: validate_repo(temp_repo), "enum mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"].append(copy.deepcopy(spec["profiles"][0])) or spec,
        )
        expect_failure("duplicate profile identifier", lambda: validate_repo(temp_repo), "duplicate profile identifier github")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["mutation_record_fields"].remove("accepted repository revision") or spec,
        )
        expect_failure("hosting mutation record fields", lambda: validate_repo(temp_repo), "hosting mutation record fields mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["deployment_state"]["plan_apply_separation"].append("Apply requires a change ticket.") or spec,
        )
        expect_failure("deployment-state contract", lambda: validate_repo(temp_repo), "plan/apply separation mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/artifact-taxonomy.json",
            lambda spec: spec["artifact_classes"].__setitem__(1, copy.deepcopy(spec["artifact_classes"][0])) or spec,
        )
        expect_failure("artifact class uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties identifier")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        expect_failure("repository-relative path helper", lambda: resolve_repo_path(temp_repo, "../../etc/passwd"), "invalid repository-relative path")

    print("ok: repository mutation tests")
