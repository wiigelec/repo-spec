from __future__ import annotations

import copy
from pathlib import Path

from docgen import render_governing_issue, render_issue_form, render_manifest, render_review_proposal, render_review_template, render_validation
from repo_model import load_specs
from validation.repository_checks import check_acyclic_dependencies
from validation.schema_subset import ensure_schema_keywords, load_repo_schemas, validate_instance

from .mutation_support import expect_failure, expect_render_change


def run_schema_mutations(repo_root: Path) -> None:
    schemas = load_repo_schemas(repo_root)
    _manifest, specs, _, _ = load_specs(repo_root)

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
