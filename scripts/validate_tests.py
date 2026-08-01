#!/usr/bin/env python3

"""Mutation tests for repo-spec validation."""

from __future__ import annotations

import copy
import json
import shutil
import tempfile
from pathlib import Path

from docgen import (
    render_governing_issue,
    render_issue_form,
    render_manifest,
    render_review_proposal,
    render_review_template,
    render_validation,
)
from validate_impl import (
    ValidationFailure,
    check_acyclic_dependencies,
    check_generated_document_freshness,
    check_generated_document_write_behavior,
    ensure_schema_keywords,
    fail,
    load_repo_schemas,
    load_specs,
    resolve_repo_path,
    validate_instance,
    validate_repo,
)


def expect_failure(description: str, func, fragment: str) -> None:
    try:
        func()
    except ValidationFailure as exc:
        if fragment not in str(exc):
            fail(f"mutation test failed: {description} (expected {fragment!r}, got {exc})")
    else:
        fail(f"mutation test failed: {description} did not fail")


def expect_render_change(description: str, renderer, spec: dict, mutate) -> None:
    original = renderer(spec)
    mutated = copy.deepcopy(spec)
    mutate(mutated)
    if renderer(mutated) == original:
        fail(f"mutation test failed: {description} did not change output")


def run_mutation_tests(repo_root: Path) -> None:
    schemas = load_repo_schemas(repo_root)
    _manifest, specs, source_paths, actual_paths = load_specs(repo_root)

    expect_failure(
        "manifest root type",
        lambda: validate_instance([], schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"]),
        "must be an object",
    )

    mutated_manifest = copy.deepcopy(specs["repo.manifest"])
    mutated_manifest["extra"] = True
    expect_failure(
        "manifest additionalProperties",
        lambda: validate_instance(mutated_manifest, schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"]),
        "additionalProperties disallowed",
    )

    mutated_manifest = copy.deepcopy(specs["repo.manifest"])
    mutated_manifest.pop("authoritative_specs")
    expect_failure(
        "manifest required authoritative_specs",
        lambda: validate_instance(mutated_manifest, schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"]),
        "missing required property authoritative_specs",
    )

    mutated_manifest = copy.deepcopy(specs["repo.manifest"])
    mutated_manifest["authoritative_specs"][0]["path"] = "specs/repo/manifest.txt"
    expect_failure(
        "manifest authoritative spec path pattern",
        lambda: validate_instance(mutated_manifest, schemas["repo.manifest"], "specs/repo/manifest.json", schemas["repo.manifest"]),
        "pattern mismatch",
    )

    expect_failure(
        "repo spec root type",
        lambda: validate_instance([], schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "must be an object",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["spec_id"] = "repo.bad id"
    expect_failure(
        "repo spec id pattern",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "pattern mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["title"] = ""
    expect_failure(
        "repo title minLength",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "minLength violation",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["purpose"] = ""
    expect_failure(
        "repo purpose minLength",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "minLength violation",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["status"] = "draft"
    expect_failure(
        "repo status enum",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "enum mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["schema_version"] = "2"
    expect_failure(
        "repo schema version const",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "const mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["normative_requirements"][0].pop("text")
    expect_failure(
        "requirement required text",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "missing required property text",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["normative_requirements"][0]["extra"] = True
    expect_failure(
        "requirement additionalProperties",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "additionalProperties disallowed",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["dependencies"][0]["spec_id"] = "repo.invalid id"
    expect_failure(
        "dependency spec id pattern",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/repository-structure.json", schemas["repo.spec"]),
        "pattern mismatch",
    )

    mutated_specs = copy.deepcopy(specs)
    mutated_specs["repo.repository-structure"]["dependencies"][0]["spec_id"] = "repo.missing-spec"
    expect_failure(
        "unresolved dependency",
        lambda: check_acyclic_dependencies(mutated_specs),
        "unresolved dependency",
    )

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

        def clone_repo() -> Path:
            nonlocal clone_index
            clone_root = temp_root / f"clone-{clone_index}"
            clone_index += 1
            shutil.copytree(
                repo_root,
                clone_root,
                ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc"),
            )
            return clone_root

        def mutate_json(path: Path, transform) -> None:
            data = json.loads(path.read_text())
            path.write_text(json.dumps(transform(data), indent=2) + "\n")

        def add_lifecycle_spec(temp_repo: Path, spec_id: str, status: str, supersedes: list[str] | None = None, superseded_by: list[str] | None = None) -> None:
            mutate_json(
                temp_repo / "specs/repo/manifest.json",
                lambda manifest: (
                    manifest["authoritative_specs"].append({"spec_id": spec_id, "path": f"specs/repo/{spec_id.removeprefix('repo.')}.json"}) or manifest
                ),
            )
            lifecycle_spec = copy.deepcopy(specs["repo.validation"])
            lifecycle_spec["spec_id"] = spec_id
            lifecycle_spec["title"] = "Lifecycle Test"
            lifecycle_spec["purpose"] = "Lifecycle test specification"
            lifecycle_spec["status"] = status
            lifecycle_spec["derived_artifacts"][0]["path"] = f"derived/specs/repo/{spec_id.removeprefix('repo.')}.md"
            if supersedes is not None:
                lifecycle_spec["supersedes"] = supersedes
            if superseded_by is not None:
                lifecycle_spec["superseded_by"] = superseded_by
            (temp_repo / f"specs/repo/{spec_id.removeprefix('repo.')}.json").write_text(json.dumps(lifecycle_spec, indent=2) + "\n")

        temp_repo = clone_repo()
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "repo.unlisted"
        (temp_repo / "specs/repo/unlisted.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure(
            "unlisted json file",
            lambda: validate_repo(temp_repo),
            "manifest completeness failed",
        )

        temp_repo = clone_repo()
        (temp_repo / "specs/repo/validation.json").unlink()
        expect_failure(
            "missing manifest file",
            lambda: validate_repo(temp_repo),
            "manifest completeness failed",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: (
                manifest["authoritative_specs"][-1].__setitem__("path", "specs/repo/repository-structure.json") or manifest
            ),
        )
        expect_failure(
            "duplicate manifest paths",
            lambda: validate_repo(temp_repo),
            "manifest completeness failed",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/review-proposal.md"})
                or spec
            ),
        )
        expect_failure(
            "duplicate derived artifact paths",
            lambda: validate_repo(temp_repo),
            "duplicate derived artifact paths failed",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/validation-missing.md"}) or spec
            ),
        )
        expect_failure(
            "missing derived artifact",
            lambda: check_generated_document_freshness(temp_repo),
            "generated-document freshness failed",
        )

        temp_repo = clone_repo()
        (temp_repo / "derived/specs/repo/orphaned.md").write_text("stale\n")
        expect_failure(
            "orphaned derived markdown write",
            lambda: check_generated_document_write_behavior(temp_repo),
            "orphaned derived markdown",
        )

        temp_repo = clone_repo()
        (temp_repo / "derived/specs/repo/orphaned.md").write_text("stale\n")
        expect_failure(
            "orphaned derived markdown check",
            lambda: check_generated_document_freshness(temp_repo),
            "orphaned derived markdown",
        )

        expect_failure(
            "repository-relative path helper",
            lambda: resolve_repo_path(temp_repo, "../../etc/passwd"),
            "invalid repository-relative path",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: (
                manifest["authoritative_specs"].append({"spec_id": "repo.example", "path": "specs/repo/example.json"}) or manifest
            ),
        )
        example_spec = copy.deepcopy(specs["repo.validation"])
        example_spec["spec_id"] = "repo.example"
        example_spec["title"] = "Example"
        example_spec["purpose"] = "Example repository specification"
        example_spec["derived_artifacts"][0]["path"] = "derived/specs/repo/example.md"
        (temp_repo / "specs/repo/example.json").write_text(json.dumps(example_spec, indent=2) + "\n")
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["references"][-1].__setitem__("path", "../../etc/passwd") or spec
            ),
        )
        expect_failure(
            "artifact reference path escape",
            lambda: validate_repo(temp_repo),
            "oneOf mismatch",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["derived_artifacts"][0].__setitem__("path", "../../etc/passwd") or spec
            ),
        )
        expect_failure(
            "derived artifact path escape",
            lambda: validate_repo(temp_repo),
            "pattern mismatch",
        )

        temp_repo = clone_repo()
        add_lifecycle_spec(temp_repo, "repo.lifecycle-candidate", "candidate")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["dependencies"].append({"spec_id": "repo.lifecycle-candidate"}) or spec
            ),
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = clone_repo()
        add_lifecycle_spec(temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["dependencies"].append({"spec_id": "repo.lifecycle-retired"}) or spec
            ),
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure(
            "dependency to retired spec",
            lambda: validate_repo(temp_repo),
            "dependencies failed",
        )

        temp_repo = clone_repo()
        add_lifecycle_spec(temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["references"].append({"type": "specification", "kind": "historical", "spec_id": "repo.lifecycle-retired"}) or spec
            ),
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = clone_repo()
        add_lifecycle_spec(temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["references"].append({"type": "specification", "spec_id": "repo.lifecycle-retired"}) or spec
            ),
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure(
            "normative reference to retired spec",
            lambda: validate_repo(temp_repo),
            "resolvable references failed",
        )

        temp_repo = clone_repo()
        add_lifecycle_spec(temp_repo, "repo.lifecycle-candidate", "candidate", supersedes=["repo.validation"])
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec.setdefault("superseded_by", []).append("repo.lifecycle-candidate") or spec
            ),
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        mutated_spec = copy.deepcopy(specs["repo.validation"])
        mutated_spec["references"][0]["path"] = "docs/extra.md"
        expect_failure(
            "reference specification exclusivity",
            lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/validation.json", schemas["repo.spec"]),
            "oneOf mismatch",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/governing-issue.json",
            lambda spec: (
                spec["issue_fields"].__setitem__(1, copy.deepcopy(spec["issue_fields"][0])) or spec
            ),
        )
        expect_failure(
            "governing issue field uniqueness",
            lambda: validate_repo(temp_repo),
            "duplicate item properties id",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/review-proposal.json",
            lambda spec: (
                spec["review_fields"].__setitem__(1, copy.deepcopy(spec["review_fields"][0])) or spec
            ),
        )
        expect_failure(
            "review proposal field uniqueness",
            lambda: validate_repo(temp_repo),
            "duplicate item properties id",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["normative_requirements"].__setitem__(1, copy.deepcopy(spec["normative_requirements"][0])) or spec
            ),
        )
        expect_failure(
            "requirement id uniqueness",
            lambda: validate_repo(temp_repo),
            "duplicate item properties id",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["dependencies"].append(copy.deepcopy(spec["dependencies"][0])) or spec
            ),
        )
        expect_failure(
            "dependency uniqueness",
            lambda: validate_repo(temp_repo),
            "duplicate item properties spec_id",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["references"].append(copy.deepcopy(spec["references"][0])) or spec
            ),
        )
        expect_failure(
            "reference uniqueness",
            lambda: validate_repo(temp_repo),
            "duplicate item properties type, spec_id, path, kind",
        )

        temp_repo = clone_repo()
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: (
                spec["derived_artifacts"].append(copy.deepcopy(spec["derived_artifacts"][0])) or spec
            ),
        )
        expect_failure(
            "derived artifact uniqueness",
            lambda: validate_repo(temp_repo),
            "duplicate item properties path",
        )

        mutated_spec = copy.deepcopy(specs["repo.validation"])
        mutated_spec["derived_artifacts"][0]["type"] = "html"
        expect_failure(
            "derived artifact type enum",
            lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/validation.json", schemas["repo.spec"]),
            "enum mismatch",
        )

        mutated_spec = copy.deepcopy(specs["repo.validation"])
        mutated_spec["derived_artifacts"][0]["path"] = ""
        expect_failure(
            "derived artifact path minLength",
            lambda: validate_instance(mutated_spec, schemas["repo.spec"], "specs/repo/validation.json", schemas["repo.spec"]),
            "minLength violation",
        )

    expect_render_change(
        "manifest projected purpose",
        render_manifest,
        specs["repo.manifest"],
        lambda spec: spec.__setitem__("purpose", "Changed manifest purpose"),
    )
    expect_render_change(
        "manifest projected requirement",
        render_manifest,
        specs["repo.manifest"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed manifest requirement"),
    )
    expect_render_change(
        "manifest projected reference",
        render_manifest,
        specs["repo.manifest"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-spec"),
    )
    expect_render_change(
        "manifest projected derived artifact",
        render_manifest,
        specs["repo.manifest"],
        lambda spec: spec["derived_artifacts"][0].__setitem__("path", "derived/specs/repo/changed.md"),
    )

    expect_render_change(
        "governing issue projected requirement",
        render_governing_issue,
        specs["repo.governing-issue"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed governing-issue requirement"),
    )
    expect_render_change(
        "governing issue projected field",
        render_governing_issue,
        specs["repo.governing-issue"],
        lambda spec: spec["issue_fields"][0].__setitem__("label", "Changed change type"),
    )
    expect_render_change(
        "governing issue form projected field",
        render_issue_form,
        specs["repo.governing-issue"],
        lambda spec: spec["issue_fields"][0].__setitem__("label", "Changed change type"),
    )
    expect_render_change(
        "governing issue projected dependency",
        render_governing_issue,
        specs["repo.governing-issue"],
        lambda spec: spec["dependencies"][0].__setitem__("spec_id", "repo.changed-dependency"),
    )
    expect_render_change(
        "governing issue projected reference",
        render_governing_issue,
        specs["repo.governing-issue"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-reference"),
    )

    expect_render_change(
        "review proposal projected requirement",
        render_review_proposal,
        specs["repo.review-proposal"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed review-proposal requirement"),
    )
    expect_render_change(
        "review proposal projected field",
        render_review_proposal,
        specs["repo.review-proposal"],
        lambda spec: spec["review_fields"][0].__setitem__("label", "Changed governing issue"),
    )
    expect_render_change(
        "review proposal template projected field",
        render_review_template,
        specs["repo.review-proposal"],
        lambda spec: spec["review_fields"][0].__setitem__("label", "Changed governing issue"),
    )
    expect_render_change(
        "review proposal projected dependency",
        render_review_proposal,
        specs["repo.review-proposal"],
        lambda spec: spec["dependencies"][0].__setitem__("spec_id", "repo.changed-dependency"),
    )
    expect_render_change(
        "review proposal projected reference",
        render_review_proposal,
        specs["repo.review-proposal"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-reference"),
    )

    expect_render_change(
        "validation projected requirement",
        render_validation,
        specs["repo.validation"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed validation requirement"),
    )
    expect_render_change(
        "validation projected dependency",
        render_validation,
        specs["repo.validation"],
        lambda spec: spec["dependencies"][0].__setitem__("spec_id", "repo.changed-dependency"),
    )
    expect_render_change(
        "validation projected reference",
        render_validation,
        specs["repo.validation"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-reference"),
    )
    expect_render_change(
        "validation projected derived artifact",
        render_validation,
        specs["repo.validation"],
        lambda spec: spec["derived_artifacts"][0].__setitem__("path", "derived/specs/repo/changed.md"),
    )

    mutated_schema = copy.deepcopy(schemas["repo.spec"])
    mutated_schema["properties"]["title"]["maxLength"] = 1
    expect_failure(
        "unsupported keyword detection",
        lambda: ensure_schema_keywords(mutated_schema, "schemas/repo-spec.schema.json"),
        "unsupported schema keyword",
    )

    mutated_schema = copy.deepcopy(schemas["repo.spec"])
    mutated_schema["properties"]["normative_requirements"]["items"]["$ref"] = "#/$defs/missing"
    expect_failure(
        "unresolved ref detection",
        lambda: validate_instance(specs["repo.repository-structure"], mutated_schema, "specs/repo/repository-structure.json", mutated_schema),
        "unresolved ref",
    )

    print("ok: schema mutation tests")
