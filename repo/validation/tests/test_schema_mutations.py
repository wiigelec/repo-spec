from __future__ import annotations

import copy
from pathlib import Path

from docgen import render_issue_form, render_review_template, render_spec_projection
from repo_model import load_specs
from validation.checks.repository_checks import check_acyclic_dependencies
from validation.core.schema_subset import ensure_schema_keywords, load_repo_schemas, validate_instance

from .mutation_support import expect_failure, expect_render_change


def run_schema_mutations(repo_root: Path) -> None:
    schemas = load_repo_schemas(repo_root)
    _manifest, specs, paths, _ = load_specs(repo_root)

    expect_failure(
        "manifest root type",
        lambda: validate_instance([], schemas["repo.manifest"], "repo/specs/repo/manifest.json", schemas["repo.manifest"]),
        "must be an object",
    )

    mutated_manifest = copy.deepcopy(specs["repo.manifest"])
    mutated_manifest["extra"] = True
    expect_failure(
        "manifest additionalProperties",
        lambda: validate_instance(mutated_manifest, schemas["repo.manifest"], "repo/specs/repo/manifest.json", schemas["repo.manifest"]),
        "additionalProperties disallowed",
    )

    mutated_manifest = copy.deepcopy(specs["repo.manifest"])
    mutated_manifest.pop("authoritative_specs")
    expect_failure(
        "manifest required authoritative_specs",
        lambda: validate_instance(mutated_manifest, schemas["repo.manifest"], "repo/specs/repo/manifest.json", schemas["repo.manifest"]),
        "missing required property authoritative_specs",
    )

    mutated_manifest = copy.deepcopy(specs["repo.manifest"])
    mutated_manifest["authoritative_specs"][0]["path"] = "repo/specs/repo/manifest.txt"
    expect_failure(
        "manifest authoritative spec path pattern",
        lambda: validate_instance(mutated_manifest, schemas["repo.manifest"], "repo/specs/repo/manifest.json", schemas["repo.manifest"]),
        "pattern mismatch",
    )

    expect_failure(
        "repo spec root type",
        lambda: validate_instance([], schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "must be an object",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["spec_id"] = "repo.bad id"
    expect_failure(
        "repo spec id pattern",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "pattern mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["spec_id"] = "product.repository-structure"
    expect_failure(
        "product spec id under repo schema",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "pattern mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["title"] = ""
    expect_failure(
        "repo title minLength",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "minLength violation",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["purpose"] = ""
    expect_failure(
        "repo purpose minLength",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "minLength violation",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["status"] = "draft"
    expect_failure(
        "repo status enum",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "enum mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["schema_version"] = "2"
    expect_failure(
        "repo schema version const",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "const mismatch",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["normative_requirements"][0].pop("text")
    expect_failure(
        "requirement required text",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "missing required property text",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["normative_requirements"][0]["extra"] = True
    expect_failure(
        "requirement additionalProperties",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "additionalProperties disallowed",
    )

    mutated_spec = copy.deepcopy(specs["repo.repository-structure"])
    mutated_spec["dependencies"][0]["spec_id"] = "repo.invalid id"
    expect_failure(
        "dependency spec id pattern",
        lambda: validate_instance(mutated_spec, schemas["repo.spec"], "repo/specs/repo/repository-structure.json", schemas["repo.spec"]),
        "pattern mismatch",
    )

    taxonomy_spec = copy.deepcopy(specs["repo.artifact-taxonomy"])
    def artifact_class(spec: dict, identifier: str) -> dict:
        for item in spec["artifact_classes"]:
            if item["identifier"] == identifier:
                return item
        raise AssertionError(f"missing artifact class: {identifier}")

    expect_failure(
        "artifact taxonomy root type",
        lambda: validate_instance([], schemas["repo.artifact-taxonomy"], "repo/specs/repo/artifact-taxonomy.json", schemas["repo.artifact-taxonomy"]),
        "must be an object",
    )

    taxonomy_spec = copy.deepcopy(specs["repo.artifact-taxonomy"])
    taxonomy_spec["artifact_classes"][0]["identifier"] = "unknown-artifact"
    expect_failure(
        "unknown artifact class",
        lambda: validate_instance(taxonomy_spec, schemas["repo.artifact-taxonomy"], "repo/specs/repo/artifact-taxonomy.json", schemas["repo.artifact-taxonomy"]),
        "oneOf mismatch",
    )

    taxonomy_spec = copy.deepcopy(specs["repo.artifact-taxonomy"])
    artifact_class(taxonomy_spec, "implementation-plan")["authority_category"] = "normative"
    expect_failure(
        "plan authority category",
        lambda: validate_instance(taxonomy_spec, schemas["repo.artifact-taxonomy"], "repo/specs/repo/artifact-taxonomy.json", schemas["repo.artifact-taxonomy"]),
        "oneOf mismatch",
    )

    taxonomy_spec = copy.deepcopy(specs["repo.artifact-taxonomy"])
    artifact_class(taxonomy_spec, "derived-projection").pop("source_artifacts")
    expect_failure(
        "generated artifact without source",
        lambda: validate_instance(taxonomy_spec, schemas["repo.artifact-taxonomy"], "repo/specs/repo/artifact-taxonomy.json", schemas["repo.artifact-taxonomy"]),
        "oneOf mismatch",
    )

    taxonomy_spec = copy.deepcopy(specs["repo.artifact-taxonomy"])
    artifact_class(taxonomy_spec, "product-artifact")["authority_category"] = "normative"
    expect_failure(
        "product artifact authority",
        lambda: validate_instance(taxonomy_spec, schemas["repo.artifact-taxonomy"], "repo/specs/repo/artifact-taxonomy.json", schemas["repo.artifact-taxonomy"]),
        "oneOf mismatch",
    )

    taxonomy_spec = copy.deepcopy(specs["repo.artifact-taxonomy"])
    artifact_class(taxonomy_spec, "hosting-platform-profile")["portability_category"] = "framework-generic"
    expect_failure(
        "profile-specific portability",
        lambda: validate_instance(taxonomy_spec, schemas["repo.artifact-taxonomy"], "repo/specs/repo/artifact-taxonomy.json", schemas["repo.artifact-taxonomy"]),
        "oneOf mismatch",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    expect_failure(
        "platform profile root type",
        lambda: validate_instance([], schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "must be an object",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    profile_spec["profiles"][0]["identifier"] = "gitlab"
    expect_failure(
        "platform profile identifier",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "const mismatch",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    profile_spec["profiles"][0]["artifact_inventory"][0].pop("profile_id")
    expect_failure(
        "platform profile identity",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "missing required property profile_id",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    profile_spec["profiles"][0]["artifact_inventory"][0]["authority_category"] = "normative"
    expect_failure(
        "installed adapter authority",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "enum mismatch",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    bootstrap_entry = next(
        item
        for item in profile_spec["profiles"][0]["artifact_inventory"]
        if item["classification"] == "bootstrap-infrastructure"
    )
    bootstrap_entry["authority_category"] = "bootstrap"
    expect_failure(
        "bootstrap infrastructure authority",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "enum mismatch",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    profile_spec["profiles"][0]["authority_boundary"] = "adapter-authoritative"
    expect_failure(
        "profile authority boundary",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "enum mismatch",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    profile_spec["profiles"][0]["remote_state_kinds"][0] = "repo/derived/specs/repo/rulesets.json"
    expect_failure(
        "remote-only state as generated file",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "enum mismatch",
    )

    profile_spec = copy.deepcopy(specs["repo.platform-profiles"])
    profile_spec["profiles"][0]["deployment_state"].pop("ruleset_desired_state_format")
    expect_failure(
        "deployment-state contract",
        lambda: validate_instance(profile_spec, schemas["repo.platform-profiles"], "repo/specs/repo/platform-profiles.json", schemas["repo.platform-profiles"]),
        "missing required property ruleset_desired_state_format",
    )

    mutated_specs = copy.deepcopy(specs)
    mutated_specs["repo.repository-structure"]["dependencies"][0]["spec_id"] = "repo.missing-spec"
    expect_failure(
        "unresolved dependency",
        lambda: check_acyclic_dependencies(mutated_specs),
        "unresolved dependency",
    )

    expect_render_change(
        "artifact taxonomy projected class",
        lambda spec: render_spec_projection(specs["repo.artifact-taxonomy"]["title"], paths["repo.artifact-taxonomy"], spec),
        specs["repo.artifact-taxonomy"],
        lambda spec: spec["artifact_classes"][0].__setitem__("source_of_truth_rule", "Changed source rule"),
    )

    expect_render_change(
        "manifest projected purpose",
        lambda spec: render_spec_projection(specs["repo.manifest"]["title"], paths["repo.manifest"], spec, include_authoritative_specs=True),
        specs["repo.manifest"],
        lambda spec: spec.__setitem__("purpose", "Changed manifest purpose"),
    )
    expect_render_change(
        "manifest projected requirement",
        lambda spec: render_spec_projection(specs["repo.manifest"]["title"], paths["repo.manifest"], spec, include_authoritative_specs=True),
        specs["repo.manifest"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed manifest requirement"),
    )
    expect_render_change(
        "manifest projected reference",
        lambda spec: render_spec_projection(specs["repo.manifest"]["title"], paths["repo.manifest"], spec, include_authoritative_specs=True),
        specs["repo.manifest"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-spec"),
    )
    expect_render_change(
        "manifest projected derived artifact",
        lambda spec: render_spec_projection(specs["repo.manifest"]["title"], paths["repo.manifest"], spec, include_authoritative_specs=True),
        specs["repo.manifest"],
        lambda spec: spec["derived_artifacts"][0].__setitem__("path", "repo/derived/specs/repo/changed.md"),
    )
    expect_render_change(
        "governing issue projected requirement",
        lambda spec: render_spec_projection(specs["repo.governing-issue"]["title"], paths["repo.governing-issue"], spec),
        specs["repo.governing-issue"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed governing-issue requirement"),
    )
    expect_render_change(
        "governing issue projected field",
        lambda spec: render_spec_projection(specs["repo.governing-issue"]["title"], paths["repo.governing-issue"], spec),
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
        lambda spec: render_spec_projection(specs["repo.governing-issue"]["title"], paths["repo.governing-issue"], spec),
        specs["repo.governing-issue"],
        lambda spec: spec["dependencies"][0].__setitem__("spec_id", "repo.changed-dependency"),
    )
    expect_render_change(
        "governing issue projected reference",
        lambda spec: render_spec_projection(specs["repo.governing-issue"]["title"], paths["repo.governing-issue"], spec),
        specs["repo.governing-issue"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-reference"),
    )
    expect_render_change(
        "review proposal projected requirement",
        lambda spec: render_spec_projection(specs["repo.review-proposal"]["title"], paths["repo.review-proposal"], spec),
        specs["repo.review-proposal"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed review-proposal requirement"),
    )
    expect_render_change(
        "review proposal projected field",
        lambda spec: render_spec_projection(specs["repo.review-proposal"]["title"], paths["repo.review-proposal"], spec),
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
        lambda spec: render_spec_projection(specs["repo.review-proposal"]["title"], paths["repo.review-proposal"], spec),
        specs["repo.review-proposal"],
        lambda spec: spec["dependencies"][0].__setitem__("spec_id", "repo.changed-dependency"),
    )
    expect_render_change(
        "review proposal projected reference",
        lambda spec: render_spec_projection(specs["repo.review-proposal"]["title"], paths["repo.review-proposal"], spec),
        specs["repo.review-proposal"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-reference"),
    )
    expect_render_change(
        "validation projected requirement",
        lambda spec: render_spec_projection(specs["repo.validation"]["title"], paths["repo.validation"], spec),
        specs["repo.validation"],
        lambda spec: spec["normative_requirements"][-1].__setitem__("text", "Changed validation requirement"),
    )
    expect_render_change(
        "validation projected dependency",
        lambda spec: render_spec_projection(specs["repo.validation"]["title"], paths["repo.validation"], spec),
        specs["repo.validation"],
        lambda spec: spec["dependencies"][0].__setitem__("spec_id", "repo.changed-dependency"),
    )
    expect_render_change(
        "validation projected reference",
        lambda spec: render_spec_projection(specs["repo.validation"]["title"], paths["repo.validation"], spec),
        specs["repo.validation"],
        lambda spec: spec["references"][0].__setitem__("spec_id", "repo.changed-reference"),
    )
    expect_render_change(
        "validation projected derived artifact",
        lambda spec: render_spec_projection(specs["repo.validation"]["title"], paths["repo.validation"], spec),
        specs["repo.validation"],
        lambda spec: spec["derived_artifacts"][0].__setitem__("path", "repo/derived/specs/repo/changed.md"),
    )

    expect_render_change(
        "product manifest projected requirement",
        lambda spec: render_spec_projection(specs["repo.product-manifest"]["title"], paths["repo.product-manifest"], spec),
        specs["repo.product-manifest"],
        lambda spec: spec["normative_requirements"][0].__setitem__("text", "Changed product-manifest requirement"),
    )

    expect_render_change(
        "product spec base projected requirement",
        lambda spec: render_spec_projection(specs["repo.product-spec-base"]["title"], paths["repo.product-spec-base"], spec),
        specs["repo.product-spec-base"],
        lambda spec: spec["normative_requirements"][0].__setitem__("text", "Changed product-spec-base requirement"),
    )

    expect_render_change(
        "product levels projected requirement",
        lambda spec: render_spec_projection(specs["repo.product-levels"]["title"], paths["repo.product-levels"], spec),
        specs["repo.product-levels"],
        lambda spec: spec["normative_requirements"][0].__setitem__("text", "Changed product-levels requirement"),
    )

    mutated_schema = copy.deepcopy(schemas["repo.spec"])
    mutated_schema["properties"]["title"]["maxLength"] = 1
    expect_failure(
        "unsupported keyword detection",
        lambda: ensure_schema_keywords(mutated_schema, "repo/schemas/repo-spec.schema.json"),
        "unsupported schema keyword",
    )

    mutated_schema = copy.deepcopy(schemas["repo.spec"])
    mutated_schema["properties"]["normative_requirements"]["items"]["$ref"] = "#/$defs/missing"
    expect_failure(
        "unresolved ref detection",
        lambda: validate_instance(specs["repo.repository-structure"], mutated_schema, "repo/specs/repo/repository-structure.json", mutated_schema),
        "unresolved ref",
    )

    unique_items_schema = {"type": "array", "uniqueItems": True, "items": {"type": "string"}}
    ensure_schema_keywords(unique_items_schema, "schemas/test-unique-items.json")
    expect_failure(
        "uniqueItems duplicate detection",
        lambda: validate_instance(["a", "a"], unique_items_schema, "schemas/test-unique-items.json", unique_items_schema),
        "uniqueItems violation",
    )

    print("ok: schema mutation tests")
