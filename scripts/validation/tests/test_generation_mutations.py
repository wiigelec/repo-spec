from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from docgen import render_issue_form, render_review_template, render_spec_projection
from repo_model import load_specs
from validation.generated_outputs import check_generated_document_freshness, check_generated_document_write_behavior
from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, expect_failure, expect_render_change, mutate_json


def run_generation_mutations(repo_root: Path) -> None:
    _manifest, specs, paths, _ = load_specs(repo_root)

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/validation-missing.md"}) or spec,
        )
        expect_failure("missing derived artifact", lambda: check_generated_document_freshness(temp_repo), "generated-document freshness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "derived/specs/repo/orphaned.md").write_text("stale\n")
        expect_failure("orphaned derived markdown write", lambda: check_generated_document_write_behavior(temp_repo), "orphaned derived markdown")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "derived/specs/repo/orphaned.md").write_text("stale\n")
        expect_failure("orphaned derived markdown check", lambda: check_generated_document_freshness(temp_repo), "orphaned derived markdown")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"].append({"spec_id": "repo.example", "path": "specs/repo/example.json"}) or manifest,
        )
        example_spec = copy.deepcopy(specs["repo.validation"])
        example_spec["spec_id"] = "repo.example"
        example_spec["title"] = "Example"
        example_spec["purpose"] = "Example repository specification"
        example_spec["derived_artifacts"][0]["path"] = "derived/specs/repo/example.md"
        (temp_repo / "specs/repo/example.json").write_text(json.dumps(example_spec, indent=2) + "\n")
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

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
        lambda spec: spec["derived_artifacts"][0].__setitem__("path", "derived/specs/repo/changed.md"),
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
        "review proposal template projected description",
        render_review_template,
        specs["repo.review-proposal"],
        lambda spec: spec["review_fields"][0].__setitem__("description", "Changed governing issue description"),
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
        lambda spec: spec["derived_artifacts"][0].__setitem__("path", "derived/specs/repo/changed.md"),
    )

    expect_render_change(
        "platform profiles projected boundary",
        lambda spec: render_spec_projection(specs["repo.platform-profiles"]["title"], paths["repo.platform-profiles"], spec),
        specs["repo.platform-profiles"],
        lambda spec: spec["profiles"][0].__setitem__("authority_boundary", "adapter-authoritative") or spec,
    )
    expect_render_change(
        "platform profiles projected inventory",
        lambda spec: render_spec_projection(specs["repo.platform-profiles"]["title"], paths["repo.platform-profiles"], spec),
        specs["repo.platform-profiles"],
        lambda spec: spec["profiles"][0]["artifact_inventory"][0].__setitem__("path", ".github/ISSUE_TEMPLATE/changed.yml"),
    )
    expect_render_change(
        "platform profiles projected remote state kinds",
        lambda spec: render_spec_projection(specs["repo.platform-profiles"]["title"], paths["repo.platform-profiles"], spec),
        specs["repo.platform-profiles"],
        lambda spec: spec["profiles"][0]["remote_state_kinds"].__setitem__(0, "repository settings") or spec,
    )
    expect_render_change(
        "platform profiles projected mutation record fields",
        lambda spec: render_spec_projection(specs["repo.platform-profiles"]["title"], paths["repo.platform-profiles"], spec),
        specs["repo.platform-profiles"],
        lambda spec: spec["profiles"][0]["mutation_record_fields"].remove("accepted repository revision") or spec,
    )

    print("ok: generation mutation tests")
