"""Aggregate production validation for the owning domain."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ..core.context import RepositoryValidationContext, ValidationContext, load_repo_specs
from ..core.errors import fail
from ..core.schema_subset import load_repo_schemas
from .development_documents import _check_repository_development_documents
from .generated_outputs import _check_repository_generated_freshness
from .policy import _check_repository_lifecycle, check_platform_profile_boundary
from .specifications import (
    check_acyclic_dependencies_phase,
    check_dependency_targets_phase,
    check_lineage_relations_phase,
    check_manifest_phase,
    check_resolvable_references_phase,
    check_schema_conformance,
    check_unique_derived_artifact_paths_phase,
    check_unique_item_properties_phase,
    check_unique_spec_ids_phase,
)

def validate_repository_phase(repo_root: Path, phase_label: str) -> None:
    context = _load_repository_only_context(repo_root)
    for label, check in REPOSITORY_VALIDATION_PHASES:
        if label == phase_label:
            check(context)
            return
    fail(f"unknown repository validation phase: {phase_label}")

def _load_repository_only_context(repo_root: Path) -> ValidationContext:
    manifest, specs, source_paths, actual_paths = load_repo_specs(repo_root)
    schemas = load_repo_schemas(repo_root)
    repository = RepositoryValidationContext(
        manifest,
        specs,
        source_paths,
        actual_paths,
        schemas,
    )
    return ValidationContext(repo_root, repository, None, None)

def validate_repo(repo_root: Path) -> None:
    context = _load_repository_only_context(repo_root)
    for label, check in REPOSITORY_VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")

REPOSITORY_LEAF_VALIDATION_PHASES: list[tuple[str, Any]] = [
    ("repository JSON Schema conformance", check_schema_conformance),
    ("manifest completeness", check_manifest_phase),
    ("unique specification IDs", check_unique_spec_ids_phase),
    ("unique item properties", check_unique_item_properties_phase),
    ("platform profile boundary", check_platform_profile_boundary),
    ("unique derived artifact paths", check_unique_derived_artifact_paths_phase),
    ("dependency target lifecycle", check_dependency_targets_phase),
    ("resolvable references", check_resolvable_references_phase),
    ("lineage relations", check_lineage_relations_phase),
    ("acyclic dependencies", check_acyclic_dependencies_phase),
]

REPOSITORY_VALIDATION_PHASES: list[tuple[str, Any]] = [
    *REPOSITORY_LEAF_VALIDATION_PHASES,
    ("repository development documents", _check_repository_development_documents),
    ("repository lifecycle authority sequence", _check_repository_lifecycle),
    ("repository generated-document freshness", _check_repository_generated_freshness),
]
