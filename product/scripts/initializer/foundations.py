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
    ("01-collected-input.md", "Collected input", ["collected_input"]),
    ("02-provenance.md", "Provenance", ["provenance"]),
    ("03-unresolved-intent.md", "Unresolved intent", ["unresolved_intent"]),
]

REQUIRED_OVERVIEW_AREAS = {
    "collected_input": "Collected input",
    "provenance": "Provenance",
    "unresolved_intent": "Unresolved intent",
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
            "path": f"product/docs/overview/{slug}-whiteboard/{filename}",
            "title": title,
            "coverage": coverage,
        })

    content_areas = {}
    for area_key in REQUIRED_OVERVIEW_AREAS:
        area_paths = []
        for chunk_file, _chunk_title, chunk_coverage in OVERVIEW_CHUNK_COVERAGE:
            if area_key in chunk_coverage:
                area_paths.append(f"product/docs/overview/{slug}-whiteboard/{chunk_file}")
        content_areas[area_key] = area_paths

    metadata = {
        "artifact_id": f"{slug}-whiteboard",
        "artifact_type": "overview-whiteboard",
        "document_slug": f"{slug}-whiteboard",
        "filename_stem": f"{slug}-whiteboard",
        "root_path": "product/docs/overview/",
        "title": f"{plan.product_id} Overview Whiteboard",
        "product_id": plan.product_id,
        "authority_category": "evidentiary",
        "lifecycle_status": "active",
        "governing_issue": governing_issue,
        "controlling_documents": [],
        "predecessor_documents": [],
        "evidence": list(direction_material),
        "required_content_areas": content_areas,
        "subordinate_chunks": chunks,
        "successor_action": "Analyze the collected direction into candidate functional sets before any decomposition.",
        "schema_version": "1",
    }

    chunk_dir_rel = f"{slug}-whiteboard/"
    lines = [
        f"# {plan.product_id} Overview Whiteboard",
        "",
        "## Status",
        "",
        "Active evidentiary direction collection.",
        "",
        "This whiteboard preserves supplied direction without assigning product semantics or approving a functional set.",
        "",
        "## Metadata",
        "",
        "```json",
        json.dumps(metadata, indent=2),
        "```",
        "",
        "## Overview",
        "",
        "The whiteboard is the collected-input boundary before analysis and functional-set approval.",
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
        "Bootstrap evidence is the supplied direction material. The whiteboard has no controlling or predecessor development document.",
        "",
        "## Next authorized action",
        "",
        "Analyze this whiteboard into candidate functional sets. Decomposition remains unauthorized until a functional set is explicitly approved.",
        "",
        "## Discoverability",
        "",
        "- [Overview lifecycle root index](./README.md)",
        "",
    ])
    return "\n".join(lines)



def _overview_chunk_content(title: str, area_keys: list[str], plan: FoundationPlan) -> str:
    lines = [
        f"# {title}",
        "",
        "> This chunk is evidentiary scaffolding established by the initializer. It does not synthesize product semantics.",
        "",
        "## Status",
        "",
        "Active whiteboard evidence.",
        "",
    ]
    if "collected_input" in area_keys:
        lines.extend([
            "## Collected input",
            "",
            "Supplied direction material:",
            "",
        ])
        for mat in plan.direction_material:
            lines.append(f"- {mat}")
        lines.append("")
    if "provenance" in area_keys:
        lines.extend([
            "## Provenance",
            "",
            "Source provenance is preserved through the direction evidence projection and governing issue.",
            "",
        ])
    if "unresolved_intent" in area_keys:
        lines.extend([
            "## Unresolved intent",
            "",
            "Intent not explicit in supplied direction material remains unresolved for governed analysis.",
            "",
        ])
    return "\n".join(lines)



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
        f"- [Overview whiteboard](product/docs/overview/{slug}-WHITEBOARD.md)",
        "- Next lifecycle step: governed overview analysis",
        "- Decomposition requires an explicitly approved functional set",
        "- Implementation planning follows decomposition",
        "- [Product manifest](product/specs/product/manifest.json)",
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

    whiteboard_path = staging / "product" / "docs" / "overview" / f"{slug}-WHITEBOARD.md"
    _safe_write(
        whiteboard_path,
        _overview_controlling_content(plan, slug, governing_issue_ref, direction_material),
        "overview-whiteboard-controlling",
    )

    for filename, title, coverage in OVERVIEW_CHUNK_COVERAGE:
        chunk_path = staging / "product" / "docs" / "overview" / f"{slug}-whiteboard" / filename
        _safe_write(
            chunk_path,
            _overview_chunk_content(title, coverage, plan),
            "overview-whiteboard-chunk",
        )

    manifest_path = staging / "product" / "specs" / "product" / "manifest.json"
    _safe_write(
        manifest_path,
        _product_manifest_content(plan, slug, governing_issue_ref),
        "product-manifest",
    )

    for lr in [
        "product/specs/product/level-0/",
        "product/specs/product/level-1/",
        "product/specs/product/level-2/",
        "product/specs/product/level-3/",
    ]:
        lr_path = staging / lr
        if not lr_path.exists():
            lr_path.mkdir(parents=True, exist_ok=True)
            created.append({"path": lr, "artifact": "product-level-root"})
        else:
            preserved.append({"path": lr, "artifact": "product-level-root"})

    overview_readme = staging / "product" / "docs" / "overview" / "README.md"
    if not overview_readme.exists():
        _safe_write(
            overview_readme,
            _readme_discoverability_content(slug, product_id),
            "root-index-overview",
        )

    specs_product_readme = staging / "product" / "specs" / "product" / "README.md"
    if not specs_product_readme.exists():
        _safe_write(
            specs_product_readme,
            _readme_discoverability_content(slug, product_id),
            "product-spec-readme",
        )

    evidence_created = _project_direction_evidence(
        direction_material,
        staging,
        "initializing",
    )
    for item in evidence_created:
        if "reason" not in item:
            created.append(item)

    deferred.extend([
        {
            "path": f"product/docs/overview/{slug}-ANALYSIS.md",
            "artifact": "overview-analysis",
            "reason": "requires governed analysis of the active whiteboard",
        },
        {
            "path": f"product/docs/overview/{slug}-FUNCTIONAL-SET.md",
            "artifact": "functional-set",
            "reason": "requires explicit approval after analysis",
        },
        {
            "path": f"product/docs/decompositions/{slug}-DECOMPOSITION.md",
            "artifact": "product-decomposition",
            "reason": "requires an approved functional set",
        },
        {
            "path": f"product/docs/plans/{slug}-IMPLEMENTATION-PLAN.md",
            "artifact": "implementation-plan",
            "reason": "requires decomposition",
        },
    ])

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
    lines = [
        _i2_front_matter(
            lifecycle_status="active",
            authority_category="evidentiary",
        ).rstrip(),
        f"# {product_id} Overview Whiteboard",
        "",
        "## Collected Input",
        "",
        "Direction material is projected byte-for-byte under product/docs/direction/evidence/. No product semantics are synthesized by the initializer.",
        "",
        "## Provenance",
        "",
        "The direction manifest records source revision, source object identity, positional index, and projected evidence path.",
        "",
        "## Unresolved Intent",
        "",
        "Any intent not explicit in supplied direction material remains unresolved for governed overview analysis.",
        "",
        "## Next Authorized Action",
        "",
        "Analyze the whiteboard into candidate functional sets. Decomposition remains unauthorized until a functional set is explicitly approved.",
        "",
    ]
    return "\n".join(lines).encode("utf-8")



def _i2_chunk(title: str, paragraph: str) -> bytes:
    return (
        _i2_front_matter(lifecycle_status="candidate")
        + f"# {title}\n\n{paragraph}\n"
    ).encode("utf-8")


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
        + f"- [Overview Whiteboard](../../../docs/overview/{product_id}-WHITEBOARD.md)\n"
        + "- Next lifecycle step: governed overview analysis\n"
        + "- Decomposition requires an explicitly approved functional set\n"
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
        projected = f"product/docs/direction/evidence/{index:03d}-{Path(source_path).name}"
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

    add(f"product/docs/overview/{product_id}-WHITEBOARD.md", _i2_overview(product_id))
    for filename, title, coverage in OVERVIEW_CHUNK_COVERAGE:
        paragraph = (
            "This whiteboard chunk is mechanically generated evidentiary scaffolding. "
            "Direction material is preserved without synthesized product semantics."
        )
        add(
            f"product/docs/overview/{product_id}-whiteboard/{filename}",
            _i2_chunk(title, paragraph),
        )

    add(
        "product/docs/overview/README.md",
        _i2_discoverability_readme(
            "Overview Whiteboard",
            f"{product_id} Overview Whiteboard",
            f"./{product_id}-WHITEBOARD.md",
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
