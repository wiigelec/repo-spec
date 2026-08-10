from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from .models import (
    InitializerError,
    FoundationPlan,
    FoundationResult,
    FoundationArtifactStatus,
    _to_slug,
)


class FoundationError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


OVERVIEW_CHUNK_COVERAGE = [
    ("01-identity-and-purpose.md", "Product identity and purpose", ["product_identity"]),
    ("02-problem-and-outcome.md", "Problem and outcome", ["problem_and_outcome"]),
    ("03-users-principles-and-boundaries.md", "Users, principles, and boundaries", ["intended_users_and_stakeholders", "scope_and_non_goals", "product_boundaries", "durable_principles"]),
    ("04-capabilities-and-success.md", "Capabilities and success", ["capabilities_and_success"]),
    ("05-unresolved-questions.md", "Unresolved questions", ["unresolved_questions"]),
    ("06-lifecycle-and-handoff.md", "Lifecycle and handoff", ["readiness_for_decomposition"]),
]

DECOMPOSITION_CHUNK_COVERAGE = [
    ("01-invocation-and-authority.md", "Invocation and authority", "product-area", "invocation-and-authority", ["decomposition_basis", "product_area_inventory", "unresolved_decisions"]),
    ("02-product-areas.md", "Product areas", "product-area", "product-areas", ["product_area_inventory", "dependency_model", "unresolved_decisions"]),
    ("03-cross-cutting-concerns.md", "Cross-cutting concerns", "product-area", "cross-cutting-concerns", ["cross_cutting_concerns", "unresolved_decisions"]),
    ("04-stopping-criteria-and-handoff.md", "Stopping criteria and handoff", "product-area", "stopping-criteria-and-handoff", ["unresolved_decisions", "stopping_criteria", "planning_handoff"]),
]

PLAN_CHUNK_COVERAGE = [
    ("01-scope-and-preconditions.md", "Scope and preconditions", ["authority_and_basis", "scope_and_exclusions"]),
    ("02-workstreams-and-dependencies.md", "Workstreams and dependencies", ["workstreams_and_dependencies"]),
    ("03-validation-and-completion.md", "Validation and completion", ["entry_and_exit_conditions", "transition_gates", "validation_strategy", "completion_and_successor_work"]),
    ("04-risks-and-unresolved-decisions.md", "Risks and unresolved decisions", ["risks_and_unresolved_decisions", "completion_and_successor_work"]),
]

REQUIRED_OVERVIEW_AREAS = {
    "product_identity": "Product identity",
    "problem_and_outcome": "Problem and outcome",
    "intended_users_and_stakeholders": "Intended users and stakeholders",
    "scope_and_non_goals": "Scope and non-goals",
    "product_boundaries": "Product boundaries",
    "durable_principles": "Durable principles",
    "capabilities_and_success": "Capabilities and success",
    "unresolved_questions": "Unresolved questions",
    "readiness_for_decomposition": "Readiness for decomposition",
}

REQUIRED_DECOMPOSITION_AREAS = {
    "decomposition_basis": "Decomposition basis",
    "product_area_inventory": "Product area inventory",
    "dependency_model": "Dependency model",
    "cross_cutting_concerns": "Cross-cutting concerns",
    "unresolved_decisions": "Unresolved decisions",
    "stopping_criteria": "Stopping criteria",
    "planning_handoff": "Planning handoff",
}

REQUIRED_PLAN_AREAS = {
    "authority_and_basis": "Authority and basis",
    "scope_and_exclusions": "Scope and exclusions",
    "workstreams_and_dependencies": "Workstreams and dependencies",
    "entry_and_exit_conditions": "Entry and exit conditions",
    "transition_gates": "Transition gates",
    "validation_strategy": "Validation strategy",
    "risks_and_unresolved_decisions": "Risks and unresolved decisions",
    "completion_and_successor_work": "Completion and successor work",
}


def build_foundation_plan(
    product_id: str,
    direction_material: list[str],
    governing_issue: str,
) -> FoundationPlan:
    if not product_id or not product_id.strip():
        raise FoundationError("product_id must be non-empty")
    if not direction_material:
        raise FoundationError("direction_material must be non-empty")
    return FoundationPlan(product_id, direction_material, governing_issue)


def _overview_controlling_content(
    plan: FoundationPlan,
    slug: str,
    governing_issue: str,
    direction_material: list[str],
) -> str:
    chunks = []
    for i, (filename, title, coverage) in enumerate(OVERVIEW_CHUNK_COVERAGE, 1):
        chunks.append({
            "order": i,
            "path": f"product/docs/overview/{slug}-overview/{filename}",
            "title": title,
            "coverage": coverage,
        })

    content_areas = {}
    for area_key, area_label in REQUIRED_OVERVIEW_AREAS.items():
        area_paths = []
        for chunk_file, chunk_title, chunk_coverage in OVERVIEW_CHUNK_COVERAGE:
            if area_key in chunk_coverage:
                area_paths.append(f"product/docs/overview/{slug}-overview/{chunk_file}")
        content_areas[area_key] = area_paths

    metadata = {
        "artifact_id": f"{slug}-overview",
        "artifact_type": "product-overview",
        "document_slug": f"{slug}-overview",
        "filename_stem": f"{slug}-overview",
        "root_path": "product/docs/overview/",
        "title": f"{plan.product_id} Overview",
        "product_id": plan.product_id,
        "authority_category": "directional",
        "lifecycle_status": "candidate",
        "overview_role": "initial",
        "governing_issue": governing_issue,
        "controlling_documents": [],
        "predecessor_documents": [],
        "evidence": list(direction_material),
        "required_content_areas": content_areas,
        "subordinate_chunks": chunks,
        "successor_action": "Proceed to product decomposition once the overview direction is reviewed.",
        "schema_version": "1",
    }

    overview_path = f"product/docs/overview/{slug}-OVERVIEW.md"
    chunk_dir_rel = f"product/docs/overview/{slug}-overview/"

    lines = [
        f"# {plan.product_id} Overview",
        "",
        "## Status",
        "",
        "Directional product overview.",
        "",
        "This document is the controlling entry point for the product overview composite document. It is directional and non-normative.",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2),
        "```",
        "",
        "## Overview",
        "",
        "This overview records the intended product direction. It is directional and non-normative. Product semantics are recorded only from explicit supplied direction material.",
        "",
        "## Chunk index",
        "",
    ]
    for filename, title, _ in OVERVIEW_CHUNK_COVERAGE:
        lines.append(f"- [{title}](./{chunk_dir_rel}{filename})")
    lines.extend([
        "",
        "## Relationships",
        "",
        "Bootstrap authority is recorded through the governing issue and evidence. The supplied direction material is preserved without semantic expansion.",
        "",
        "## Next authorized action",
        "",
        "The next authorized action is product decomposition under product/docs/decompositions/.",
        "",
        "## Discoverability",
        "",
        f"- [Product overview root index](./README.md)",
        f"- [Product decomposition](../decompositions/{slug}-DECOMPOSITION.md)",
        f"- [Implementation plan](../plans/{slug}-IMPLEMENTATION-PLAN.md)",
        "",
    ])
    return "\n".join(lines)


def _overview_chunk_content(title: str, area_keys: list[str], plan: FoundationPlan) -> str:
    lines = [
        f"# {title}",
        "",
        "> This chunk is a placeholder established by the initializer. Substantive content requires governed successor work.",
        "",
        "## Status",
        "",
        "Candidate placeholder content. No product semantics have been defined here.",
        "",
    ]
    if "product_identity" in area_keys:
        lines.extend([
            "## Product identity",
            "",
            f"**Product:** {plan.product_id}",
            "",
            "Supplied direction material:",
            "",
        ])
        for mat in plan.direction_material:
            lines.append(f"- {mat}")
        lines.append("")
    lines.extend([
        "<!--",
        "Required content areas covered by this chunk:",
    ])
    for key in area_keys:
        label = REQUIRED_OVERVIEW_AREAS.get(key, key)
        lines.append(f"  {key}: {label}")
    lines.extend([
        "",
        "Substantive content for each area must be added through governed successor work.",
        "-->",
        "",
    ])
    return "\n".join(lines)


def _decomposition_controlling_content(plan: FoundationPlan, slug: str, governing_issue: str) -> str:
    chunks = []
    for i, (filename, title, role, area_id, doc_coverage) in enumerate(DECOMPOSITION_CHUNK_COVERAGE, 1):
        chunks.append({
            "order": i,
            "path": f"product/docs/decompositions/{slug}-decomposition/{filename}",
            "title": title,
            "role": role,
            "area_id": area_id,
            "document_coverage": doc_coverage,
            "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"],
        })

    content_areas = {}
    for area_key, area_label in REQUIRED_DECOMPOSITION_AREAS.items():
        area_paths = []
        for chunk_file, chunk_title, chunk_role, chunk_area_id, chunk_doc_coverage in DECOMPOSITION_CHUNK_COVERAGE:
            if area_key in chunk_doc_coverage:
                area_paths.append(f"product/docs/decompositions/{slug}-decomposition/{chunk_file}")
        if area_paths:
            content_areas[area_key] = area_paths

    evidence = [f"product/docs/overview/{slug}-OVERVIEW.md"] + [f"product/docs/overview/{slug}-overview/{f}" for f, _, _ in OVERVIEW_CHUNK_COVERAGE]

    metadata = {
        "artifact_id": f"{slug}-decomposition",
        "artifact_type": "product-decomposition",
        "document_slug": f"{slug}-decomposition",
        "filename_stem": f"{slug}-decomposition",
        "root_path": "product/docs/decompositions/",
        "title": f"{plan.product_id} Decomposition",
        "product_id": plan.product_id,
        "authority_category": "directional",
        "lifecycle_status": "candidate",
        "governing_issue": governing_issue,
        "controlling_documents": [f"product/docs/overview/{slug}-OVERVIEW.md"],
        "predecessor_documents": [f"product/docs/overview/{slug}-OVERVIEW.md"],
        "evidence": evidence,
        "required_content_areas": content_areas,
        "subordinate_chunks": chunks,
        "successor_action": "Proceed to implementation planning once the decomposition is reviewed.",
        "schema_version": "1",
    }

    chunk_dir_rel = f"product/docs/decompositions/{slug}-decomposition/"

    lines = [
        f"# {plan.product_id} Decomposition",
        "",
        "## Status",
        "",
        "Directional decomposition record.",
        "",
        "This document is the controlling entry point for the product decomposition composite document. It is directional and non-normative.",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2),
        "```",
        "",
        "## Decomposition basis",
        "",
        "This decomposition translates the product overview into bounded areas and is intentionally non-normative.",
        "",
        "## Bounded areas",
        "",
        "The product is decomposed into bounded areas awaiting governed successor work.",
        "",
        "## Chunk index",
        "",
    ]
    for filename, title, _, _, _ in DECOMPOSITION_CHUNK_COVERAGE:
        lines.append(f"- [{title}](./{chunk_dir_rel}{filename})")
    lines.extend([
        "",
        "## Relationships",
        "",
        "This decomposition is grounded in the product overview. Unresolved decisions are preserved rather than decided early.",
        "",
        "## Next authorized action",
        "",
        "The next authorized action is an implementation plan under product/docs/plans/.",
        "",
        "## Discoverability",
        "",
        f"- [Decomposition root index](./README.md)",
        f"- [Product overview](../overview/{slug}-OVERVIEW.md)",
        f"- [Implementation plan](../plans/{slug}-IMPLEMENTATION-PLAN.md)",
        "",
    ])
    return "\n".join(lines)


def _decomposition_chunk_content(title: str, role: str, area_id: str, plan: FoundationPlan) -> str:
    return "\n".join([
        f"# {title}",
        "",
        "> This chunk is a placeholder established by the initializer. Substantive content requires governed successor work.",
        "",
        "## Status",
        "",
        "Candidate placeholder content.",
        "",
        f"**Area ID:** {area_id}",
        f"**Role:** {role}",
        "",
        "<!--",
        "Required content areas: purpose, responsibilities, boundaries, dependencies, exclusions, unresolved-decisions, successor-work",
        "-->",
        "",
    ])


def _plan_controlling_content(plan: FoundationPlan, slug: str, governing_issue: str) -> str:
    chunks = []
    for i, (filename, title, coverage) in enumerate(PLAN_CHUNK_COVERAGE, 1):
        chunks.append({
            "order": i,
            "path": f"product/docs/plans/{slug}-implementation-plan/{filename}",
            "title": title,
            "coverage": coverage,
        })

    content_areas = {}
    for area_key, area_label in REQUIRED_PLAN_AREAS.items():
        area_paths = []
        for chunk_file, chunk_title, chunk_coverage in PLAN_CHUNK_COVERAGE:
            if area_key in chunk_coverage:
                area_paths.append(f"product/docs/plans/{slug}-implementation-plan/{chunk_file}")
        if area_paths:
            content_areas[area_key] = area_paths

    evidence = [
        f"product/docs/overview/{slug}-OVERVIEW.md",
        f"product/docs/decompositions/{slug}-DECOMPOSITION.md",
    ]

    metadata = {
        "artifact_id": f"{slug}-implementation-plan",
        "artifact_type": "implementation-plan",
        "document_slug": f"{slug}-implementation-plan",
        "filename_stem": f"{slug}-implementation-plan",
        "root_path": "product/docs/plans/",
        "title": f"{plan.product_id} Implementation Plan",
        "product_id": plan.product_id,
        "authority_category": "planning",
        "lifecycle_status": "candidate",
        "governing_issue": governing_issue,
        "controlling_documents": [
            f"product/docs/overview/{slug}-OVERVIEW.md",
            f"product/docs/decompositions/{slug}-DECOMPOSITION.md",
        ],
        "predecessor_documents": [f"product/docs/decompositions/{slug}-DECOMPOSITION.md"],
        "evidence": evidence,
        "required_content_areas": content_areas,
        "subordinate_chunks": chunks,
        "successor_action": "Open separately governed implementation issues after this plan is reviewed.",
        "schema_version": "1",
    }

    chunk_dir_rel = f"product/docs/plans/{slug}-implementation-plan/"

    lines = [
        f"# {plan.product_id} Implementation Plan",
        "",
        "## Status",
        "",
        "Candidate implementation plan.",
        "",
        "This document is the controlling entry point for the implementation plan composite document. It has planning authority for subsequent governed implementation work, but it is non-normative with respect to product semantics.",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2),
        "```",
        "",
        "## Planning basis",
        "",
        "This plan is grounded in the accepted product overview and decomposition. It does not redefine product behavior.",
        "",
        "## Chunk index",
        "",
    ]
    for filename, title, _ in PLAN_CHUNK_COVERAGE:
        lines.append(f"- [{title}](./{chunk_dir_rel}{filename})")
    lines.extend([
        "",
        "## Relationships",
        "",
        "This plan has planning authority but does not have authority to change product semantics or accepted specifications.",
        "",
        "## Next authorized action",
        "",
        "After this plan is reviewed, the next authorized action is to create governed implementation issues.",
        "",
        "## Discoverability",
        "",
        f"- [Plan root index](./README.md)",
        f"- [Product overview](../overview/{slug}-OVERVIEW.md)",
        f"- [Product decomposition](../decompositions/{slug}-DECOMPOSITION.md)",
        "",
    ])
    return "\n".join(lines)


def _plan_chunk_content(title: str, coverage: list[str], plan: FoundationPlan) -> str:
    return "\n".join([
        f"# {title}",
        "",
        "> This chunk is a placeholder established by the initializer. Substantive content requires governed successor work.",
        "",
        "## Status",
        "",
        "Candidate placeholder content.",
        "",
        "<!--",
        "Required content areas covered by this chunk:",
    ] + [f"  {key}" for key in coverage] + [
        "",
        "Substantive content must be added through governed successor work.",
        "-->",
        "",
    ])


def _product_manifest_content(plan: FoundationPlan, slug: str, governing_issue: str) -> str:
    manifest = {
        "spec_id": "product.manifest",
        "title": f"{plan.product_id} Product Manifest",
        "purpose": "Registers the governed product-specification set for this product.",
        "status": "candidate",
        "schema_version": "1",
        "product_specifications": [],
        "dependencies": [
            {"spec_id": "repo.manifest"},
            {"spec_id": "repo.product-manifest"},
        ],
        "references": [
            {"type": "specification", "spec_id": "repo.manifest"},
            {"type": "specification", "spec_id": "repo.product-manifest"},
            {"type": "specification", "spec_id": "repo.repository-structure"},
        ],
        "derived_artifacts": [
            {"type": "markdown", "path": f"product/derived/specs/product/manifest.md"},
        ],
    }
    return json.dumps(manifest, indent=2) + "\n"


def _readme_discoverability_content(slug: str, product_id: str) -> str:
    return "\n".join([
        f"# {product_id}",
        "",
        "Product development workspace.",
        "",
        "## Start here",
        "",
        f"- [Product overview](product/docs/overview/{slug}-OVERVIEW.md)",
        f"- [Product decomposition](product/docs/decompositions/{slug}-DECOMPOSITION.md)",
        f"- [Implementation plan](product/docs/plans/{slug}-IMPLEMENTATION-PLAN.md)",
        f"- [Product manifest](product/specs/product/manifest.json)",
        "",
    ])


def _git_blob_id(path: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "hash-object", str(path)],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _canonical_object_id(raw_id: str) -> dict[str, str]:
    if len(raw_id) == 40 and all(c in "0123456789abcdef" for c in raw_id):
        return {"object_format": "sha1", "object_id": raw_id}
    if len(raw_id) == 64 and all(c in "0123456789abcdef" for c in raw_id):
        return {"object_format": "sha256", "object_id": raw_id}
    return {"object_format": "sha1", "object_id": raw_id}


def _project_direction_evidence(
    direction_material: list[str],
    staging_root: Path,
    source_revision: str,
) -> list[dict[str, str]]:
    evidence_dir = staging_root / "product" / "docs" / "direction" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, Any]] = []
    created: list[dict[str, str]] = []
    rev_identity = _canonical_object_id(source_revision)

    for idx, source_path_str in enumerate(direction_material):
        source_path = Path(source_path_str)
        if not source_path.is_file():
            created.append({
                "path": f"product/docs/direction/evidence/{idx:03d}-{source_path.name}",
                "artifact": "direction-evidence-skipped",
                "reason": "source file not found",
            })
            continue

        evidence_name = f"{idx:03d}-{source_path.name}"
        evidence_path = evidence_dir / evidence_name
        raw_bytes = source_path.read_bytes()
        evidence_path.write_bytes(raw_bytes)

        blob_id_raw = _git_blob_id(source_path)
        blob_identity = _canonical_object_id(blob_id_raw) if blob_id_raw else None
        byte_len = len(raw_bytes)

        entries.append({
            "positional_index": idx,
            "original_source_path": str(source_path),
            "source_revision": rev_identity,
            "source_blob_object_id": blob_identity,
            "projected_evidence_path": f"product/docs/direction/evidence/{evidence_name}",
            "byte_length": byte_len,
            "detected_media_type": None,
        })
        created.append({
            "path": f"product/docs/direction/evidence/{evidence_name}",
            "artifact": "direction-evidence",
        })

    if entries:
        manifest_path = staging_root / "product" / "docs" / "direction" / "manifest.json"
        manifest = {
            "spec_id": "product.direction-manifest",
            "title": "Direction Evidence Manifest",
            "purpose": "Records the authoritative mapping of direction evidence files.",
            "source_revision": rev_identity,
            "entries": entries,
        }
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        created.append({"path": "product/docs/direction/manifest.json", "artifact": "direction-evidence-manifest"})

    return created


def establish_product_foundations(
    plan: FoundationPlan,
    staging_root: Path,
) -> FoundationResult:
    staging = staging_root.resolve()
    if not staging.exists():
        raise FoundationError(f"staging workspace does not exist: {staging}")

    slug = plan.product_slug
    product_id = plan.product_id
    governing_issue_ref = plan.governing_issue
    direction_material = plan.direction_material

    created: list[dict[str, str]] = []
    preserved: list[dict[str, str]] = []
    omitted: list[dict[str, str]] = []
    deferred: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []

    def _check_overwrite(path: Path) -> bool:
        if path.exists():
            rejected.append({"path": str(path.relative_to(staging)), "reason": "file already exists"})
            return True
        return False

    def _safe_write(path: Path, content: str, artifact_label: str) -> None:
        if _check_overwrite(path):
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
        created.append({"path": str(path.relative_to(staging)), "artifact": artifact_label})

    # Product overview controlling document
    overview_path = staging / "product" / "docs" / "overview" / f"{slug}-OVERVIEW.md"
    _safe_write(
        overview_path,
        _overview_controlling_content(plan, slug, governing_issue_ref, direction_material),
        "product-overview-controlling",
    )

    # Product overview chunks
    for filename, title, coverage in OVERVIEW_CHUNK_COVERAGE:
        chunk_path = staging / "product" / "docs" / "overview" / f"{slug}-overview" / filename
        _safe_write(
            chunk_path,
            _overview_chunk_content(title, coverage, plan),
            "product-overview-chunk",
        )

    # Product decomposition controlling document
    decomp_path = staging / "product" / "docs" / "decompositions" / f"{slug}-DECOMPOSITION.md"
    _safe_write(
        decomp_path,
        _decomposition_controlling_content(plan, slug, governing_issue_ref),
        "product-decomposition-controlling",
    )

    # Product decomposition chunks
    for filename, title, role, area_id, doc_coverage in DECOMPOSITION_CHUNK_COVERAGE:
        chunk_path = staging / "product" / "docs" / "decompositions" / f"{slug}-decomposition" / filename
        _safe_write(
            chunk_path,
            _decomposition_chunk_content(title, role, area_id, plan),
            "product-decomposition-chunk",
        )

    # Implementation plan controlling document
    plan_path = staging / "product" / "docs" / "plans" / f"{slug}-IMPLEMENTATION-PLAN.md"
    _safe_write(
        plan_path,
        _plan_controlling_content(plan, slug, governing_issue_ref),
        "implementation-plan-controlling",
    )

    # Implementation plan chunks
    for filename, title, coverage in PLAN_CHUNK_COVERAGE:
        chunk_path = staging / "product" / "docs" / "plans" / f"{slug}-implementation-plan" / filename
        _safe_write(
            chunk_path,
            _plan_chunk_content(title, coverage, plan),
            "implementation-plan-chunk",
        )

    # Product manifest
    manifest_path = staging / "product" / "specs" / "product" / "manifest.json"
    _safe_write(
        manifest_path,
        _product_manifest_content(plan, slug, governing_issue_ref),
        "product-manifest",
    )

    # Level root directories (created but empty)
    level_roots = [
        "product/specs/product/level-0/",
        "product/specs/product/level-1/",
        "product/specs/product/level-2/",
        "product/specs/product/level-3/",
    ]
    for lr in level_roots:
        lr_path = staging / lr
        if not lr_path.exists():
            lr_path.mkdir(parents=True, exist_ok=True)
            created.append({"path": lr, "artifact": "product-level-root"})
        else:
            preserved.append({"path": lr, "artifact": "product-level-root"})

    # Discoverability README updates
    overview_readme = staging / "product" / "docs" / "overview" / "README.md"
    if not overview_readme.exists():
        _safe_write(
            overview_readme,
            _readme_discoverability_content(slug, product_id),
            "root-index-overview",
        )

    decompositions_readme = staging / "product" / "docs" / "decompositions" / "README.md"
    if not decompositions_readme.exists():
        _safe_write(
            decompositions_readme,
            _readme_discoverability_content(slug, product_id),
            "root-index-decompositions",
        )

    plans_readme = staging / "product" / "docs" / "plans" / "README.md"
    if not plans_readme.exists():
        _safe_write(
            plans_readme,
            _readme_discoverability_content(slug, product_id),
            "root-index-plans",
        )

    # Product overview README update (products README under product/specs/product/)
    specs_product_readme = staging / "product" / "specs" / "product" / "README.md"
    if not specs_product_readme.exists():
        _safe_write(
            specs_product_readme,
            _readme_discoverability_content(slug, product_id),
            "product-spec-readme",
        )

    # Direction evidence: project source material as byte-identical evidence files
    evidence_created = _project_direction_evidence(
        direction_material,
        staging,
        "initializing",
    )
    for item in evidence_created:
        if "reason" not in item:
            created.append(item)

    return FoundationResult(
        product_id=product_id,
        product_slug=slug,
        created=created,
        preserved=preserved,
        omitted=omitted,
        deferred=deferred,
        rejected=rejected,
    )

# BEGIN I2 PATCH 2 GOVERNED FOUNDATION REALIZATION

def _i2_front_matter(**fields: str) -> str:
    lines = ["---"]
    lines.extend(f"{key}: {value}" for key, value in fields.items())
    lines.extend(["---", ""])
    return "\n".join(lines)


def _i2_git_blob(
    repository: str,
    revision: str,
    source_path: str,
) -> tuple[str, bytes]:
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise FoundationError("I2 foundation source revision must be a full SHA-1 object id")
    parts = source_path.replace("\\", "/").split("/")
    if (
        not source_path
        or source_path.startswith("/")
        or "\x00" in source_path
        or ".." in parts
    ):
        raise FoundationError(f"invalid direction_material source path: {source_path!r}")

    env = dict(os.environ)
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    tree = subprocess.run(
        ["git", "-C", repository, "ls-tree", "-z", revision, "--", source_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if tree.returncode:
        raise FoundationError(
            f"cannot inspect direction material {source_path}: "
            f"{tree.stderr.decode('utf-8', 'replace').strip()}"
        )
    records = [r for r in tree.stdout.split(b"\x00") if r]
    if len(records) != 1:
        raise FoundationError(
            f"direction material does not resolve to exactly one source entry: {source_path}"
        )
    meta, sep, found = records[0].partition(b"\t")
    if not sep or found.decode("utf-8", "strict") != source_path:
        raise FoundationError(f"direction material source resolution mismatch: {source_path}")
    mode, obj_type, oid = meta.decode("ascii").split(" ", 2)
    if obj_type != "blob" or mode == "120000":
        raise FoundationError(f"direction material must be a regular Git blob: {source_path}")

    blob = subprocess.run(
        ["git", "-C", repository, "cat-file", "blob", oid],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if blob.returncode:
        raise FoundationError(f"direction material blob is unavailable: {source_path}")
    return oid, blob.stdout


def _i2_json_bytes(value: dict[str, Any]) -> bytes:
    return (json.dumps(value, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def _i2_overview(product_id: str) -> bytes:
    placeholder = (
        "Direction material for this section is available at the positional index "
        "identified by the chunk document. Content is not synthesized by the initializer."
    )
    headings = (
        "1. Identity and Purpose",
        "2. Problem and Outcome",
        "3. Users, Principles, and Boundaries",
        "4. Capabilities and Success",
        "5. Unresolved Questions",
        "6. Lifecycle and Handoff",
    )
    lines = [
        _i2_front_matter(
            lifecycle_status="candidate",
            authority_category="directional",
            overview_role="initial",
        ).rstrip(),
        f"# {product_id} Overview",
        "",
        "## Purpose",
        "",
        f"This overview establishes the product direction, scope, and boundaries for {product_id}. It is a candidate directional document and is not normative.",
        "",
        "## Scope",
        "",
        "Overview scope is determined by the accepted decomposition and governing product specifications. This document records the directional boundary for the product.",
        "",
    ]
    for heading in headings:
        lines.extend([f"### {heading}", "", placeholder, ""])
    lines.extend([
        "## Open Questions",
        "",
        "Unresolved questions are recorded in the unresolved-questions chunk document. No questions are synthesized by the initializer.",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def _i2_chunk(title: str, paragraph: str) -> bytes:
    return (
        _i2_front_matter(lifecycle_status="candidate")
        + f"# {title}\n\n{paragraph}\n"
    ).encode("utf-8")


def _i2_decomposition(product_id: str) -> bytes:
    placeholder = (
        "Decomposition area content is not synthesized by the initializer. "
        "Direction material for this area may be available in product/docs/direction/."
    )
    lines = [
        _i2_front_matter(
            lifecycle_status="candidate",
            authority_category="directional",
        ).rstrip(),
        f"# {product_id} Decomposition",
        "",
        "## Scope",
        "",
        f"This decomposition identifies product areas and cross-cutting concerns for {product_id}. It is a candidate directional document and is not normative.",
        "",
        "## Product Areas",
        "",
    ]
    for heading in (
        "invocation-and-authority",
        "product-areas",
        "cross-cutting-concerns",
        "stopping-criteria-and-handoff",
    ):
        lines.extend([f"### {heading}", "", placeholder, ""])
    lines.extend([
        "## Cross-cutting Concerns",
        "",
        "Cross-cutting concerns are identified in the decomposition chunk documents. No concerns are synthesized by the initializer.",
        "",
    ])
    return "\n".join(lines).encode("utf-8")


def _i2_plan(product_id: str) -> bytes:
    lines = [
        _i2_front_matter(
            lifecycle_status="candidate",
            authority_category="planning",
        ).rstrip(),
        f"# {product_id} Implementation Plan",
        "",
        "## Scope and Preconditions",
        "",
        "Implementation scope is defined by the governing product specifications and decomposition. This plan is a candidate planning document and is not normative.",
        "",
        "## Workstreams and Dependencies",
        "",
        "Workstreams are identified in the implementation plan chunk documents. No workstream content is synthesized by the initializer.",
        "",
        "## Validation and Completion",
        "",
        "Validation criteria are defined by the governing product specifications. No validation content is synthesized by the initializer.",
        "",
        "## Risks and Unresolved Decisions",
        "",
        "Risks and unresolved decisions are recorded in the implementation plan chunk documents. No risk content is synthesized by the initializer.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")


def _i2_discoverability_readme(
    heading: str,
    title: str,
    relative_path: str,
) -> bytes:
    return (
        _i2_front_matter(lifecycle_status="candidate")
        + f"# {heading}\n\n"
        + f"See the [{title}]({relative_path}) controlling document.\n"
    ).encode("utf-8")


def _i2_level_readme(level: int) -> bytes:
    return (
        _i2_front_matter(lifecycle_status="candidate")
        + f"# Level {level}\n\n"
        + f"The Level {level} product-specification workspace is activated.\n\n"
        + f"No product specifications currently exist at Level {level}.\n\n"
        + "Generated content remains candidate and non-normative.\n\n"
        + f"The governed next action is to add Level {level} specifications only through separately authorized specification work.\n"
    ).encode("utf-8")


def _i2_product_readme(product_id: str) -> bytes:
    return (
        _i2_front_matter(lifecycle_status="candidate")
        + f"# {product_id}\n\n"
        + f"This directory contains the activated but empty product-specification workspace for {product_id}.\n\n"
        + f"- [Overview](../../../docs/overview/{product_id}-OVERVIEW.md)\n"
        + f"- [Decomposition](../../../docs/decompositions/{product_id}-DECOMPOSITION.md)\n"
        + f"- [Implementation Plan](../../../docs/plans/{product_id}-IMPLEMENTATION-PLAN.md)\n"
    ).encode("utf-8")


def build_i2_foundation_files(
    plan: FoundationPlan,
    source_repository: str,
    source_revision: str,
) -> dict[str, bytes]:
    product_id = plan.product_id
    if (
        not product_id
        or product_id in {".", ".."}
        or "/" in product_id
        or "\\" in product_id
        or "\x00" in product_id
    ):
        raise FoundationError("product_id is not safe for governed foundation paths")

    files: dict[str, bytes] = {}

    def add(path: str, content: bytes) -> None:
        if path in files:
            raise FoundationError(f"foundation output path collision: {path}")
        files[path] = content

    manifest_entries: list[dict[str, Any]] = []
    for index, source_path in enumerate(plan.direction_material):
        oid, raw = _i2_git_blob(source_repository, source_revision, source_path)
        projected = (
            f"product/docs/direction/evidence/{index:03d}-{Path(source_path).name}"
        )
        add(projected, raw)
        manifest_entries.append({
            "positional_index": index,
            "original_source_path": source_path,
            "source_revision": {
                "object_format": "sha1",
                "object_id": source_revision,
            },
            "source_blob_object_id": {
                "object_format": "sha1",
                "object_id": oid,
            },
            "projected_evidence_path": projected,
            "byte_length": len(raw),
        })

    add(
        "product/docs/direction/manifest.json",
        _i2_json_bytes({"entries": manifest_entries}),
    )

    overview_chunks = (
        ("chunk-01-identity-and-purpose.md", "Product Identity and Purpose"),
        ("chunk-02-problem-and-outcome.md", "Problem and Outcome"),
        ("chunk-03-users-principles-boundaries.md", "Users, Principles, and Boundaries"),
        ("chunk-04-capabilities-and-success.md", "Capabilities and Success"),
        ("chunk-05-unresolved-questions.md", "Unresolved Questions"),
        ("chunk-06-lifecycle-and-handoff.md", "Lifecycle and Handoff"),
    )
    overview_paragraph = (
        "Direction material entries with positional indices relevant to this section "
        "are projected to product/docs/direction/. This chunk is a mechanically "
        "generated skeleton and does not contain synthesized product semantics."
    )
    add(f"product/docs/overview/{product_id}-OVERVIEW.md", _i2_overview(product_id))
    for filename, title in overview_chunks:
        add(
            f"product/docs/overview/{product_id}-overview/{filename}",
            _i2_chunk(title, overview_paragraph),
        )

    decomposition_chunks = (
        ("chunk-01-invocation-and-authority.md", "Invocation and Authority"),
        ("chunk-02-product-areas.md", "Product Areas"),
        ("chunk-03-cross-cutting-concerns.md", "Cross-cutting Concerns"),
        ("chunk-04-stopping-criteria-and-handoff.md", "Stopping Criteria and Handoff"),
    )
    decomposition_paragraph = (
        "This decomposition chunk is a mechanically generated skeleton. "
        "Decomposition content is not synthesized by the initializer."
    )
    add(
        f"product/docs/decompositions/{product_id}-DECOMPOSITION.md",
        _i2_decomposition(product_id),
    )
    for filename, title in decomposition_chunks:
        add(
            f"product/docs/decompositions/{product_id}-decomposition/{filename}",
            _i2_chunk(title, decomposition_paragraph),
        )

    plan_chunks = (
        ("chunk-01-scope-and-preconditions.md", "Scope and Preconditions"),
        ("chunk-02-workstreams-and-dependencies.md", "Workstreams and Dependencies"),
        ("chunk-03-validation-and-completion.md", "Validation and Completion"),
        ("chunk-04-risks-and-unresolved-decisions.md", "Risks and Unresolved Decisions"),
    )
    plan_paragraph = (
        "This implementation plan chunk is a mechanically generated skeleton. "
        "Plan content is not synthesized by the initializer."
    )
    add(
        f"product/docs/plans/{product_id}-IMPLEMENTATION-PLAN.md",
        _i2_plan(product_id),
    )
    for filename, title in plan_chunks:
        add(
            f"product/docs/plans/{product_id}-implementation-plan/{filename}",
            _i2_chunk(title, plan_paragraph),
        )

    add(
        "repo/docs/overview/README.md",
        _i2_discoverability_readme(
            "Overview", f"{product_id} Overview", f"./{product_id}-OVERVIEW.md"
        ),
    )
    add(
        "repo/docs/decompositions/README.md",
        _i2_discoverability_readme(
            "Decompositions",
            f"{product_id} Decomposition",
            f"./{product_id}-DECOMPOSITION.md",
        ),
    )
    add(
        "repo/docs/plans/README.md",
        _i2_discoverability_readme(
            "Plans",
            f"{product_id} Implementation Plan",
            f"./{product_id}-IMPLEMENTATION-PLAN.md",
        ),
    )
    for level in range(4):
        add(f"product/specs/product/level-{level}/README.md", _i2_level_readme(level))

    add(
        "product/specs/product/manifest.json",
        _i2_json_bytes({
            "spec_id": "product.manifest",
            "title": f"{product_id} Product Specification Manifest",
            "purpose": f"Registers the product specifications for {product_id}.",
            "status": "candidate",
            "schema_version": "1",
            "product_specifications": [],
            "dependencies": [
                {"spec_id": "repo.manifest"},
                {"spec_id": "repo.product-manifest"},
            ],
        }),
    )
    add("product/specs/product/README.md", _i2_product_readme(product_id))
    return files

# END I2 PATCH 2 GOVERNED FOUNDATION REALIZATION
