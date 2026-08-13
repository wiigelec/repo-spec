"""Shared development-document validation mechanics."""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
from pathlib import Path
from typing import Any

from .context import ValidationContext
from validation.errors import expect, fail
from .schema_subset import validate_instance


DEVELOPMENT_DOCUMENT_ROOTS = {
    "repo/docs/overview/": {
        "artifact_types": ["overview-whiteboard", "overview-analysis", "functional-set"],
        "schema_key": "repo.functional-set-process",
        "required_headings": ["Status", "Metadata", "Overview", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys_by_type": {
            "overview-whiteboard": ["collected_input", "provenance", "unresolved_intent"],
            "overview-analysis": ["source_evidence", "candidate_groupings", "dependencies", "ambiguities", "candidate_functional_sets"],
            "functional-set": ["capability_boundary", "included_intent", "exclusions", "dependencies", "integration_foundation", "end_to_end_usability", "decomposition_handoff"],
        },
        "filename_suffix": "-OVERVIEW.md",
        "chunk_dir_suffix": "/",
    },
    "repo/docs/decompositions/": {
        "artifact_type": "product-decomposition",
        "schema_key": "repo.product-decomposition",
        "required_headings": ["Status", "Metadata", "Decomposition basis", "Bounded areas", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys": ["decomposition_basis", "product_area_inventory", "dependency_model", "cross_cutting_concerns", "unresolved_decisions", "stopping_criteria", "planning_handoff"],
        "required_chunk_coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"],
        "allowed_chunk_roles": ["product-area", "decomposition-basis", "cross-cutting-concerns", "dependency-model", "unresolved-decisions", "stopping-and-handoff"],
        "filename_suffix": "-DECOMPOSITION.md",
        "chunk_dir_suffix": "/",
    },
    "repo/docs/plans/": {
        "artifact_type": "implementation-plan",
        "schema_key": "repo.implementation-plan",
        "required_headings": ["Status", "Metadata", "Planning basis", "Workstreams", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys": ["authority_and_basis", "scope_and_exclusions", "workstreams_and_dependencies", "entry_and_exit_conditions", "transition_gates", "validation_strategy", "risks_and_unresolved_decisions", "completion_and_successor_work"],
        "filename_suffix": "-IMPLEMENTATION-PLAN.md",
        "chunk_dir_suffix": "/",
    },
    "repo/docs/architecture/": {
        "artifact_type": "architecture-plan",
        "schema_key": "repo.architecture-plan",
        "required_headings": ["Status", "Metadata", "Architecture basis", "Desired state", "Chunk index", "Relationships", "Next authorized action", "Discoverability"],
        "required_content_area_keys": ["authority_and_basis", "scope_and_boundaries", "target_architecture", "portability_and_ownership", "validation_strategy", "risks_and_unresolved_decisions", "audit_and_successor_work"],
        "filename_suffix": "-ARCHITECTURE.md",
        "chunk_dir_suffix": "/",
    },
}

for product_root, framework_root in (
    ("product/docs/overview/", "repo/docs/overview/"),
    ("product/docs/decompositions/", "repo/docs/decompositions/"),
    ("product/docs/plans/", "repo/docs/plans/"),
):
    DEVELOPMENT_DOCUMENT_ROOTS[product_root] = DEVELOPMENT_DOCUMENT_ROOTS[framework_root]

COVERAGE_DOCUMENT_ROOTS = {"repo/docs/overview/", "repo/docs/plans/", "repo/docs/architecture/", "product/docs/overview/", "product/docs/plans/"}
DECOMPOSITION_ROOTS = {"repo/docs/decompositions/", "product/docs/decompositions/"}

DEVELOPMENT_DOCUMENT_COMPATIBILITY_REGISTRY_PATH = "repo/docs/development-document-compatibility.json"
DEVELOPMENT_DOCUMENT_LEGACY_COMPOSITE_PREFIX_OWNERS = {
    "product/docs/decompositions/initializer-decomposition/": "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md",
    "product/docs/plans/initializer-implementation-plan/": "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md",
}

MAX_DEVELOPMENT_DOCUMENT_CHUNK_LINES = 180
MAX_DEVELOPMENT_DOCUMENT_CHUNK_BYTES = 24_576


@dataclass(frozen=True)
class DevelopmentDocumentRecord:
    path: str
    root_rel: str
    info: dict[str, Any]
    metadata: dict[str, Any]
    chunk_paths: list[str]


def development_document_schemas(context: ValidationContext) -> dict[str, dict[str, Any]]:
    if context.repository is not None:
        return context.repository.schemas
    expect(context.external_repository is not None, "validation context missing external repository schema state")
    return context.external_repository.schemas


def markdown_headings(text: str) -> set[str]:
    headings: set[str] = set()
    for line in text.splitlines():
        if line.startswith("## "):
            headings.add(line.removeprefix("## ").strip())
    return headings


def markdown_links(text: str) -> list[tuple[str, str]]:
    return re.findall(r"\[([^\]]+)\]\(([^)]+)\)", text)


def resolve_markdown_link_target(source_path: str, target: str) -> str:
    target = target.split("#", 1)[0]
    if not target:
        return target
    return os.path.normpath((Path(source_path).parent / target).as_posix())


def markdown_section(text: str, heading: str) -> str:
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line == f"## {heading}":
            start = index + 1
            break
    expect(start is not None, f"development document navigation failed: missing section {heading}")

    end = len(lines)
    for index in range(start, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def extract_document_metadata(text: str, source: str) -> dict[str, Any]:
    match = re.search(r"## Metadata\s*\n\s*```json\s*\n(.*?)\n```", text, re.S)
    expect(match is not None, f"development document metadata failed: missing metadata block in {source}")
    try:
        metadata = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        fail(f"development document metadata failed: invalid JSON in {source}: {exc.msg}")
    expect(isinstance(metadata, dict), f"development document metadata failed: {source} metadata must be an object")
    return metadata


def load_development_document_compatibility_registry(
    repo_root: Path,
    *,
    development_roots: dict[str, dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    if development_roots is None:
        development_roots = DEVELOPMENT_DOCUMENT_ROOTS
    registry_path = repo_root / DEVELOPMENT_DOCUMENT_COMPATIBILITY_REGISTRY_PATH
    expect(
        registry_path.exists(),
        f"development document classification failed: missing compatibility registry {DEVELOPMENT_DOCUMENT_COMPATIBILITY_REGISTRY_PATH}",
    )
    try:
        data = json.loads(registry_path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"development document classification failed: invalid compatibility registry JSON: {exc.msg}")

    expect(isinstance(data, dict), "development document classification failed: compatibility registry must be an object")
    expect(data.get("registry_version") == "1", "development document classification failed: unsupported compatibility registry version")
    entries = data.get("entries")
    expect(isinstance(entries, list), "development document classification failed: compatibility registry entries must be an array")

    registry: dict[str, dict[str, Any]] = {}
    for index, entry in enumerate(entries):
        expect(isinstance(entry, dict), f"development document classification failed: compatibility registry entry at index {index} must be an object")
        path = entry.get("path")
        kind = entry.get("kind")
        reason = entry.get("reason")
        expect(isinstance(path, str) and path, f"development document classification failed: compatibility registry entry at index {index} must include a path")
        expect(isinstance(kind, str) and kind in {"compatibility", "exemption"}, f"development document classification failed: compatibility registry entry at index {index} must declare compatibility or exemption")
        expect(isinstance(reason, str) and reason.strip(), f"development document classification failed: compatibility registry entry at index {index} must include a reason")
        expect(path not in registry, f"development document classification failed: duplicate compatibility registry path {path}")
        path_obj = Path(path)
        expect(path_obj.name != "README.md", f"development document classification failed: compatibility registry may not include README.md {path}")
        expect(path_obj.suffix == ".md", f"development document classification failed: compatibility registry path must be Markdown {path}")
        expect(f"{path_obj.parent.as_posix()}/" in development_roots, f"development document classification failed: compatibility registry path must be under a canonical root {path}")
        registry[path] = entry

    return registry


def resolve_development_document_artifact(
    path: str,
    records: dict[str, DevelopmentDocumentRecord],
    compatibility_registry: dict[str, dict[str, Any]],
    chunk_owner_paths: dict[str, str],
) -> tuple[str, DevelopmentDocumentRecord | None]:
    if path in records:
        return path, records[path]
    if path in compatibility_registry:
        return path, None
    owner_path = chunk_owner_paths.get(path)
    if owner_path is not None:
        return owner_path, records[owner_path]
    for prefix, owner_path in DEVELOPMENT_DOCUMENT_LEGACY_COMPOSITE_PREFIX_OWNERS.items():
        if path.startswith(prefix):
            expect(owner_path in compatibility_registry, f"development document relationship failed: unresolved legacy composite owner for {path}")
            return owner_path, None
    raise KeyError(path)


def check_development_document_relationships(
    repo_root: Path,
    records: dict[str, DevelopmentDocumentRecord],
    compatibility_registry: dict[str, dict[str, Any]],
    chunk_owner_paths: dict[str, str],
) -> None:
    artifact_ids: dict[str, str] = {}
    basis_graph: dict[str, list[str]] = {path: [] for path in records}

    for path, record in records.items():
        metadata = record.metadata
        artifact_id = metadata["artifact_id"]
        expect(artifact_id not in artifact_ids, f"development document identity failed: duplicate artifact_id {artifact_id}")
        artifact_ids[artifact_id] = path

    for path, record in records.items():
        metadata = record.metadata
        source_type = metadata["artifact_type"]
        source_product = metadata["product_id"]
        source_status = metadata["lifecycle_status"]
        allowed_types = {
            "overview-whiteboard": {"overview-whiteboard"},
            "overview-analysis": {"overview-whiteboard", "overview-analysis"},
            "functional-set": {"overview-whiteboard", "overview-analysis", "functional-set"},
            "product-decomposition": {"functional-set"},
            "implementation-plan": {"functional-set", "product-decomposition", "implementation-plan"},
            "architecture-plan": {"functional-set", "architecture-plan"},
        }[source_type]

        controlling_documents = metadata["controlling_documents"]
        predecessor_documents = metadata["predecessor_documents"]
        evidence = metadata["evidence"]

        expect(len(controlling_documents) == len(set(controlling_documents)), f"development document relationship failed: duplicate controlling documents for {path}")
        expect(len(predecessor_documents) == len(set(predecessor_documents)), f"development document relationship failed: duplicate predecessor documents for {path}")
        expect(len(evidence) == len(set(evidence)), f"development document relationship failed: duplicate evidence entries for {path}")

        saw_whiteboard = False
        saw_analysis = False
        saw_functional_set = False
        saw_approved_functional_set = False
        saw_decomposition = False

        def classify_target(target_metadata: dict[str, Any]) -> None:
            nonlocal saw_whiteboard
            nonlocal saw_analysis
            nonlocal saw_functional_set
            nonlocal saw_approved_functional_set
            nonlocal saw_decomposition

            target_type = target_metadata["artifact_type"]
            if target_type == "overview-whiteboard":
                saw_whiteboard = True
            elif target_type == "overview-analysis":
                saw_analysis = True
            elif target_type == "functional-set":
                saw_functional_set = True
                if target_metadata["lifecycle_status"] == "approved":
                    saw_approved_functional_set = True
            elif target_type == "product-decomposition":
                saw_decomposition = True

        for target_path in controlling_documents:
            try:
                resolved_path, resolved_record = resolve_development_document_artifact(
                    target_path, records, compatibility_registry, chunk_owner_paths
                )
            except KeyError:
                fail(f"development document relationship failed: unresolved controlling document path {path} -> {target_path}")

            expect(
                resolved_path == target_path or resolved_path in compatibility_registry,
                f"development document relationship failed: controlling document must reference a governed document {path} -> {target_path}",
            )
            if resolved_record is None:
                continue

            target_metadata = resolved_record.metadata
            expect(resolved_path != path, f"development document relationship failed: self reference {path}")
            expect(
                target_metadata["product_id"] == source_product,
                f"development document relationship failed: product mismatch {path} -> {target_path}",
            )
            expect(
                source_status in {"superseded", "retired"}
                or target_metadata["lifecycle_status"] in {"active", "candidate", "approved", "accepted"},
                f"development document relationship failed: controlling lifecycle mismatch {path} -> {target_path}",
            )
            expect(
                target_metadata["artifact_type"] in allowed_types,
                f"development document relationship failed: artifact-type transition mismatch {path} -> {target_path}",
            )
            basis_graph[path].append(resolved_path)
            classify_target(target_metadata)

        for target_path in predecessor_documents:
            try:
                resolved_path, resolved_record = resolve_development_document_artifact(
                    target_path, records, compatibility_registry, chunk_owner_paths
                )
            except KeyError:
                fail(f"development document relationship failed: unresolved predecessor path {path} -> {target_path}")

            expect(
                resolved_path == target_path,
                f"development document relationship failed: predecessor document must reference a governing document {path} -> {target_path}",
            )
            if resolved_record is None:
                continue

            target_metadata = resolved_record.metadata
            expect(resolved_path != path, f"development document relationship failed: self reference {path}")
            expect(
                target_metadata["product_id"] == source_product,
                f"development document relationship failed: product mismatch {path} -> {target_path}",
            )
            expect(
                source_status in {"superseded", "retired"}
                or target_metadata["lifecycle_status"] in {"active", "candidate", "approved", "accepted"},
                f"development document relationship failed: predecessor lifecycle mismatch {path} -> {target_path}",
            )
            expect(
                target_metadata["artifact_type"] in allowed_types,
                f"development document relationship failed: artifact-type transition mismatch {path} -> {target_path}",
            )
            basis_graph[path].append(resolved_path)
            classify_target(target_metadata)

        if source_type == "overview-whiteboard":
            expect(
                source_status in {"active", "superseded", "retired"},
                f"development document relationship failed: invalid whiteboard lifecycle status for {path}",
            )
            expect(
                not controlling_documents and not predecessor_documents,
                f"development document relationship failed: whiteboard must bootstrap from evidence for {path}",
            )
        elif source_type == "overview-analysis":
            expect(
                source_status in {"candidate", "superseded", "retired"},
                f"development document relationship failed: invalid analysis lifecycle status for {path}",
            )
            expect(
                saw_whiteboard,
                f"development document relationship failed: analysis missing whiteboard evidence predecessor for {path}",
            )
        elif source_type == "functional-set":
            expect(
                source_status in {"candidate", "approved", "superseded", "retired"},
                f"development document relationship failed: invalid functional-set lifecycle status for {path}",
            )
            expect(
                saw_analysis,
                f"development document relationship failed: functional set missing analysis predecessor for {path}",
            )
        elif source_type == "product-decomposition":
            expect(
                saw_functional_set,
                f"development document relationship failed: decomposition missing controlling functional set for {path}",
            )
            expect(
                saw_approved_functional_set,
                f"development document relationship failed: candidate functional set cannot govern decomposition for {path}",
            )
        elif source_type == "implementation-plan":
            expect(
                saw_functional_set,
                f"development document relationship failed: missing controlling functional set for {path}",
            )
            expect(
                saw_decomposition,
                f"development document relationship failed: missing controlling decomposition for {path}",
            )

        for target_path in evidence:
            try:
                resolved_path, resolved_record = resolve_development_document_artifact(
                    target_path, records, compatibility_registry, chunk_owner_paths
                )
            except KeyError:
                evidence_path = repo_root / target_path
                expect(
                    evidence_path.exists(),
                    f"development document evidence failed: missing evidence path {path} -> {target_path}",
                )
                continue

            if resolved_record is not None:
                continue

            evidence_path = repo_root / resolved_path
            expect(
                evidence_path.exists(),
                f"development document evidence failed: missing evidence path {path} -> {target_path}",
            )

    visiting: list[str] = []
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            start = visiting.index(node)
            cycle = visiting[start:] + [node]
            fail(f"development document relationship failed: cycle detected {' -> '.join(cycle)}")
        visiting.append(node)
        for dep in basis_graph[node]:
            visit(dep)
        visiting.pop()
        visited.add(node)

    for node in basis_graph:
        visit(node)


def check_development_documents_phase(
    context: ValidationContext,
    *,
    development_roots: dict[str, dict[str, Any]] | None = None,
    compatibility_registry: dict[str, dict[str, Any]] | None = None,
    owned_compatibility_paths: set[str] | None = None,
) -> None:
    if development_roots is None:
        development_roots = DEVELOPMENT_DOCUMENT_ROOTS
    if compatibility_registry is None:
        compatibility_registry = load_development_document_compatibility_registry(
            context.repo_root,
            development_roots=DEVELOPMENT_DOCUMENT_ROOTS,
        )
    if owned_compatibility_paths is None:
        prefixes = tuple(development_roots)
        owned_compatibility_paths = {
            path for path in compatibility_registry if path.startswith(prefixes)
        }
    unmarked_docs: set[str] = set()
    records: dict[str, DevelopmentDocumentRecord] = {}
    chunk_owner_paths: dict[str, str] = {}

    for root_rel, info in development_roots.items():
        root = context.repo_root / root_rel
        expect(root.exists(), f"development document root failed: missing root {root_rel}")
        readme = root / "README.md"
        expect(readme.exists(), f"development document discovery failed: missing {root_rel}README.md")
        readme_text = readme.read_text()

        docs = []
        for path in sorted(root.glob("*.md")):
            if path.name == "README.md":
                continue
            docs.append(path)

        for path in docs:
            text = path.read_text()
            rel_path = path.relative_to(context.repo_root).as_posix()
            if "## Metadata" not in text:
                unmarked_docs.add(rel_path)
                continue

            metadata = extract_document_metadata(text, rel_path)
            schema_key = info["schema_key"]
            schemas = development_document_schemas(context)
            validate_instance(metadata, schemas[schema_key], rel_path, schemas[schema_key])

            if metadata["artifact_type"] != "implementation-plan":
                expect(
                    "workstream_authority" not in metadata,
                    f"development document authority failed: workstream authority outside implementation plan in {rel_path}",
                )
            elif metadata.get("lifecycle_status") == "accepted":
                authority_ids = [entry["id"] for entry in metadata["workstream_authority"]]
                duplicate_authority_ids = sorted({authority_id for authority_id in authority_ids if authority_ids.count(authority_id) > 1})
                expect(
                    not duplicate_authority_ids,
                    f"development document authority failed: duplicate workstream authority identifier "
                    f"{', '.join(duplicate_authority_ids)} in {rel_path}",
                )

            allowed_artifact_types = info.get("artifact_types", [info.get("artifact_type")])
            expect(metadata["artifact_type"] in allowed_artifact_types, f"development document metadata failed: artifact type mismatch in {rel_path}")
            expect(metadata["root_path"] == root_rel, f"development document metadata failed: root path mismatch in {rel_path}")
            expect(path.parent == root, f"development document path failed: top-level document must live directly under {root_rel}: {rel_path}")
            expect(path.name == f"{metadata['filename_stem'].upper()}.md", f"development document path failed: filename mismatch in {rel_path}")

            headings = markdown_headings(text)
            for heading in info["required_headings"]:
                expect(heading in headings, f"development document structure failed: missing heading {heading} in {rel_path}")

            chunk_dir = root / metadata["document_slug"]
            expect(chunk_dir.exists(), f"development document path failed: missing chunk directory {chunk_dir.relative_to(context.repo_root)}")
            expect(chunk_dir.is_dir(), f"development document path failed: chunk directory is not a directory {chunk_dir.relative_to(context.repo_root)}")

            actual_chunks = sorted(path for path in chunk_dir.glob("*.md") if path.is_file())
            nested_chunks = sorted(path for path in chunk_dir.rglob("*.md") if path.is_file() and path.parent != chunk_dir)
            expect(not nested_chunks, f"development document path failed: nested chunk directories are not permitted in {chunk_dir.relative_to(context.repo_root)}")

            declared_chunks = metadata["subordinate_chunks"]
            declared_paths = [chunk["path"] for chunk in declared_chunks]
            expect(len(declared_paths) == len(set(declared_paths)), f"development document chunk inventory failed: duplicate paths in {rel_path}")
            expect(len(declared_chunks) == len(actual_chunks), f"development document chunk inventory failed: chunk count mismatch in {rel_path}")
            expect(set(declared_paths) == {chunk.relative_to(context.repo_root).as_posix() for chunk in actual_chunks}, f"development document chunk inventory failed: inventory mismatch in {rel_path}")

            required_content_areas = metadata.get("required_content_areas")
            expect(isinstance(required_content_areas, dict), f"development document content inventory failed: required content areas must be an object in {rel_path}")
            by_type = info.get("required_content_area_keys_by_type", {})
            expected_area_keys = by_type.get(metadata["artifact_type"], info.get("required_content_area_keys", []))
            expect(set(required_content_areas) == set(expected_area_keys), f"development document content inventory failed: required content area key mismatch in {rel_path}")
            covered_paths: set[str] = set()
            for area_id in expected_area_keys:
                area_paths = required_content_areas[area_id]
                expect(isinstance(area_paths, list), f"development document content inventory failed: required content area {area_id} must be an array in {rel_path}")
                expect(area_paths, f"development document content inventory failed: required content area {area_id} must not be empty in {rel_path}")
                expect(len(area_paths) == len(set(area_paths)), f"development document content inventory failed: duplicate paths in required content area {area_id} in {rel_path}")
                for area_path in area_paths:
                    expect(area_path in declared_paths, f"development document content inventory failed: required content area {area_id} references unknown chunk {area_path} in {rel_path}")
                    covered_paths.add(area_path)
            expect(covered_paths == set(declared_paths), f"development document content inventory failed: required content area coverage mismatch in {rel_path}")

            if root_rel in COVERAGE_DOCUMENT_ROOTS:
                for chunk in declared_chunks:
                    coverage = chunk.get("coverage")
                    expect(isinstance(coverage, list), f"development document content inventory failed: required coverage must be an array in {rel_path}")
                    expect(coverage, f"development document content inventory failed: required coverage must not be empty in {rel_path}")
                    expect(len(coverage) == len(set(coverage)), f"development document content inventory failed: duplicate coverage entries in {rel_path}")
                    expected_coverage = sorted(area_id for area_id, area_paths in required_content_areas.items() if chunk["path"] in area_paths)
                    expect(set(coverage) == set(expected_coverage), f"development document content inventory failed: chunk coverage mismatch in {rel_path}")

            if root_rel in DECOMPOSITION_ROOTS:
                product_area_paths = {
                    chunk["path"]
                    for chunk in declared_chunks
                    if chunk["role"] == "product-area"
                }
                expect(
                    set(required_content_areas["product_area_inventory"]) == product_area_paths,
                    f"development document content inventory failed: product-area inventory mismatch in {rel_path}",
                )

            records[rel_path] = DevelopmentDocumentRecord(rel_path, root_rel, info, metadata, declared_paths)
            for chunk_path in declared_paths:
                expect(chunk_path not in chunk_owner_paths, f"development document chunk inventory failed: duplicate chunk path {chunk_path}")
                chunk_owner_paths[chunk_path] = rel_path

            if root_rel in DECOMPOSITION_ROOTS:
                seen_area_ids: set[str] = set()
                for chunk in declared_chunks:
                    role = chunk.get("role")
                    expect(role in info["allowed_chunk_roles"], f"development document chunk inventory failed: unsupported decomposition chunk role in {rel_path}")
                    document_coverage = chunk.get("document_coverage")
                    expect(isinstance(document_coverage, list), f"development document content inventory failed: missing document coverage in {rel_path}")
                    expect(document_coverage, f"development document content inventory failed: document coverage must not be empty in {rel_path}")
                    expect(len(document_coverage) == len(set(document_coverage)), f"development document content inventory failed: duplicate document coverage entries in {rel_path}")
                    expected_document_coverage = sorted(area_id for area_id, area_paths in required_content_areas.items() if chunk["path"] in area_paths)
                    expect(set(document_coverage) == set(expected_document_coverage), f"development document content inventory failed: document coverage mismatch in {rel_path}")
                    area_id = chunk.get("area_id")
                    if role == "product-area":
                        expect(isinstance(area_id, str) and area_id, f"development document chunk inventory failed: missing area_id in {rel_path}")
                        expect(area_id not in seen_area_ids, f"development document chunk inventory failed: duplicate area_id in {rel_path}")
                        seen_area_ids.add(area_id)
                        coverage = chunk.get("coverage")
                        expect(isinstance(coverage, list), f"development document chunk inventory failed: missing coverage in {rel_path}")
                        expect(len(coverage) == len(set(coverage)), f"development document chunk inventory failed: duplicate coverage entries in {rel_path}")
                        expect(set(coverage) == set(info["required_chunk_coverage"]), f"development document chunk inventory failed: coverage mismatch in {rel_path}")
                    else:
                        expect(area_id is None, f"development document chunk inventory failed: non-area chunk must not declare area_id in {rel_path}")
                        expect(chunk.get("coverage") is None, f"development document chunk inventory failed: non-area chunk must not declare coverage in {rel_path}")

            orders = [chunk["order"] for chunk in declared_chunks]
            expect(orders == list(range(1, len(orders) + 1)), f"development document chunk inventory failed: non-contiguous order in {rel_path}")

            chunk_index_section = markdown_section(text, "Chunk index")
            chunk_index_links = {resolve_markdown_link_target(rel_path, target) for _label, target in markdown_links(chunk_index_section)}
            expect(chunk_index_links == set(declared_paths), f"development document navigation failed: chunk index link mismatch in {rel_path}")

            for chunk in declared_chunks:
                chunk_path = context.repo_root / chunk["path"]
                expect(chunk_path.exists(), f"development document chunk inventory failed: missing chunk {chunk['path']}")
                expect(chunk_path.is_file(), f"development document chunk inventory failed: chunk path must be a file {chunk['path']}")
                expect(chunk_path.parent == chunk_dir, f"development document path failed: chunk path outside chunk directory {chunk['path']}")
                expect(re.fullmatch(r"\d\d-[a-z0-9][a-z0-9-]*\.md", chunk_path.name) is not None, f"development document path failed: malformed chunk filename {chunk['path']}")

                chunk_text = chunk_path.read_text()
                expect(len(chunk_text.splitlines()) <= MAX_DEVELOPMENT_DOCUMENT_CHUNK_LINES, f"development document size failed: chunk exceeds line limit {chunk['path']}")
                expect(len(chunk_text.encode("utf-8")) <= MAX_DEVELOPMENT_DOCUMENT_CHUNK_BYTES, f"development document size failed: chunk exceeds byte limit {chunk['path']}")
                first_non_empty = next((line for line in chunk_text.splitlines() if line.strip()), "")
                expect(first_non_empty.startswith("# "), f"development document structure failed: chunk must start with a heading {chunk['path']}")
                if root_rel in DECOMPOSITION_ROOTS and chunk.get("role") == "product-area":
                    chunk_headings = markdown_headings(chunk_text)
                    for heading in ["Status", "Purpose", "Responsibilities", "Boundaries", "Dependencies", "Exclusions", "Unresolved decisions", "Successor work"]:
                        expect(heading in chunk_headings, f"development document structure failed: missing product-area heading {heading} in {chunk['path']}")

            canonical_links = {resolve_markdown_link_target(f"{root_rel}README.md", target) for _label, target in markdown_links(markdown_section(readme_text, "Canonical documents"))}
            expect(rel_path in canonical_links, f"development document discovery failed: README does not link to {rel_path}")

    expect(unmarked_docs == owned_compatibility_paths, f"development document classification failed: compatibility registry mismatch; unmarked={sorted(unmarked_docs)}; registered={sorted(owned_compatibility_paths)}")
    check_development_document_relationships(context.repo_root, records, compatibility_registry, chunk_owner_paths)


def get_development_document_records(
    context: ValidationContext,
    *,
    development_roots: dict[str, dict[str, Any]] | None = None,
) -> dict[str, DevelopmentDocumentRecord]:
    if development_roots is None:
        development_roots = DEVELOPMENT_DOCUMENT_ROOTS
    records: dict[str, DevelopmentDocumentRecord] = {}
    chunk_owner_paths: dict[str, str] = {}

    for root_rel, info in development_roots.items():
        root = context.repo_root / root_rel
        if not root.exists():
            continue
        readme = root / "README.md"
        if not readme.exists():
            continue

        docs = sorted(path for path in root.glob("*.md") if path.name != "README.md")
        for path in docs:
            text = path.read_text()
            rel_path = path.relative_to(context.repo_root).as_posix()
            if "## Metadata" not in text:
                continue

            metadata = extract_document_metadata(text, rel_path)
            allowed_artifact_types = info.get("artifact_types", [info.get("artifact_type")])
            expect(
                metadata["artifact_type"] in allowed_artifact_types,
                f"development document metadata failed: artifact type mismatch in {rel_path}",
            )
            metadata["root_path"] = root_rel
            declared_chunks = metadata["subordinate_chunks"]
            declared_paths = [chunk["path"] for chunk in declared_chunks]

            records[rel_path] = DevelopmentDocumentRecord(rel_path, root_rel, info, metadata, declared_paths)
            for chunk_path in declared_paths:
                chunk_owner_paths[chunk_path] = rel_path

    return records
