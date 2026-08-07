from __future__ import annotations

import hashlib
import json
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
    ("01-product-identity-and-purpose.md", "Product identity and purpose", ["product_identity"]),
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
            "path": f"docs/overview/{slug}-overview/{filename}",
            "title": title,
            "coverage": coverage,
        })

    content_areas = {}
    for area_key, area_label in REQUIRED_OVERVIEW_AREAS.items():
        area_paths = []
        for chunk_file, chunk_title, chunk_coverage in OVERVIEW_CHUNK_COVERAGE:
            if area_key in chunk_coverage:
                area_paths.append(f"docs/overview/{slug}-overview/{chunk_file}")
        content_areas[area_key] = area_paths

    metadata = {
        "artifact_id": f"{slug}-overview",
        "artifact_type": "product-overview",
        "document_slug": f"{slug}-overview",
        "filename_stem": f"{slug}-overview",
        "root_path": "docs/overview/",
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

    overview_path = f"docs/overview/{slug}-OVERVIEW.md"
    chunk_dir_rel = f"docs/overview/{slug}-overview/"

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
        "The next authorized action is product decomposition under docs/decompositions/.",
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
            "path": f"docs/decompositions/{slug}-decomposition/{filename}",
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
                area_paths.append(f"docs/decompositions/{slug}-decomposition/{chunk_file}")
        if area_paths:
            content_areas[area_key] = area_paths

    evidence = [f"docs/overview/{slug}-OVERVIEW.md"] + [f"docs/overview/{slug}-overview/{f}" for f, _, _ in OVERVIEW_CHUNK_COVERAGE]

    metadata = {
        "artifact_id": f"{slug}-decomposition",
        "artifact_type": "product-decomposition",
        "document_slug": f"{slug}-decomposition",
        "filename_stem": f"{slug}-decomposition",
        "root_path": "docs/decompositions/",
        "title": f"{plan.product_id} Decomposition",
        "product_id": plan.product_id,
        "authority_category": "directional",
        "lifecycle_status": "candidate",
        "governing_issue": governing_issue,
        "controlling_documents": [f"docs/overview/{slug}-OVERVIEW.md"],
        "predecessor_documents": [f"docs/overview/{slug}-OVERVIEW.md"],
        "evidence": evidence,
        "required_content_areas": content_areas,
        "subordinate_chunks": chunks,
        "successor_action": "Proceed to implementation planning once the decomposition is reviewed.",
        "schema_version": "1",
    }

    chunk_dir_rel = f"docs/decompositions/{slug}-decomposition/"

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
        "The next authorized action is an implementation plan under docs/plans/.",
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
            "path": f"docs/plans/{slug}-implementation-plan/{filename}",
            "title": title,
            "coverage": coverage,
        })

    content_areas = {}
    for area_key, area_label in REQUIRED_PLAN_AREAS.items():
        area_paths = []
        for chunk_file, chunk_title, chunk_coverage in PLAN_CHUNK_COVERAGE:
            if area_key in chunk_coverage:
                area_paths.append(f"docs/plans/{slug}-implementation-plan/{chunk_file}")
        if area_paths:
            content_areas[area_key] = area_paths

    evidence = [
        f"docs/overview/{slug}-OVERVIEW.md",
        f"docs/decompositions/{slug}-DECOMPOSITION.md",
    ]

    metadata = {
        "artifact_id": f"{slug}-implementation-plan",
        "artifact_type": "implementation-plan",
        "document_slug": f"{slug}-implementation-plan",
        "filename_stem": f"{slug}-implementation-plan",
        "root_path": "docs/plans/",
        "title": f"{plan.product_id} Implementation Plan",
        "product_id": plan.product_id,
        "authority_category": "planning",
        "lifecycle_status": "candidate",
        "governing_issue": governing_issue,
        "controlling_documents": [
            f"docs/overview/{slug}-OVERVIEW.md",
            f"docs/decompositions/{slug}-DECOMPOSITION.md",
        ],
        "predecessor_documents": [f"docs/decompositions/{slug}-DECOMPOSITION.md"],
        "evidence": evidence,
        "required_content_areas": content_areas,
        "subordinate_chunks": chunks,
        "successor_action": "Open separately governed implementation issues after this plan is reviewed.",
        "schema_version": "1",
    }

    chunk_dir_rel = f"docs/plans/{slug}-implementation-plan/"

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
        f"- [Product overview](docs/overview/{slug}-OVERVIEW.md)",
        f"- [Product decomposition](docs/decompositions/{slug}-DECOMPOSITION.md)",
        f"- [Implementation plan](docs/plans/{slug}-IMPLEMENTATION-PLAN.md)",
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
    overview_path = staging / "docs" / "overview" / f"{slug}-OVERVIEW.md"
    _safe_write(
        overview_path,
        _overview_controlling_content(plan, slug, governing_issue_ref, direction_material),
        "product-overview-controlling",
    )

    # Product overview chunks
    for filename, title, coverage in OVERVIEW_CHUNK_COVERAGE:
        chunk_path = staging / "docs" / "overview" / f"{slug}-overview" / filename
        _safe_write(
            chunk_path,
            _overview_chunk_content(title, coverage, plan),
            "product-overview-chunk",
        )

    # Product decomposition controlling document
    decomp_path = staging / "docs" / "decompositions" / f"{slug}-DECOMPOSITION.md"
    _safe_write(
        decomp_path,
        _decomposition_controlling_content(plan, slug, governing_issue_ref),
        "product-decomposition-controlling",
    )

    # Product decomposition chunks
    for filename, title, role, area_id, doc_coverage in DECOMPOSITION_CHUNK_COVERAGE:
        chunk_path = staging / "docs" / "decompositions" / f"{slug}-decomposition" / filename
        _safe_write(
            chunk_path,
            _decomposition_chunk_content(title, role, area_id, plan),
            "product-decomposition-chunk",
        )

    # Implementation plan controlling document
    plan_path = staging / "docs" / "plans" / f"{slug}-IMPLEMENTATION-PLAN.md"
    _safe_write(
        plan_path,
        _plan_controlling_content(plan, slug, governing_issue_ref),
        "implementation-plan-controlling",
    )

    # Implementation plan chunks
    for filename, title, coverage in PLAN_CHUNK_COVERAGE:
        chunk_path = staging / "docs" / "plans" / f"{slug}-implementation-plan" / filename
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
    overview_readme = staging / "docs" / "overview" / "README.md"
    if not overview_readme.exists():
        _safe_write(
            overview_readme,
            _readme_discoverability_content(slug, product_id),
            "root-index-overview",
        )

    decompositions_readme = staging / "docs" / "decompositions" / "README.md"
    if not decompositions_readme.exists():
        _safe_write(
            decompositions_readme,
            _readme_discoverability_content(slug, product_id),
            "root-index-decompositions",
        )

    plans_readme = staging / "docs" / "plans" / "README.md"
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
