"""Aggregate production validation for the owning domain."""

from pathlib import Path
from typing import Any

from .specifications import load_product_validation_context
from .policy import (
    check_validation_layout,
    check_dependency_directions_phase,
    check_product_acyclic_dependencies_phase,
    check_product_completeness_phase,
    check_product_specification_root_phase,
    check_product_structural_envelopes,
    check_product_source_layout,
)
from .specifications import (
    check_product_conformance_completeness_phase,
    check_product_correspondence_phase,
    check_product_validation_correspondence_packages_phase,
)
from .development_documents import check_product_development_documents
from .policy import check_product_lifecycle_readiness
from .generated_outputs import check_product_generated_freshness

from validation.core.context import ExternalRepositoryValidationContext, ValidationContext, load_repo_specs
from validation.core.schema_subset import load_repo_schemas
from validation.core.errors import expect, fail
from validation.core.invariants import check_supersession_acyclicity, check_supersession_pairs, check_unique_item_properties



# validation-metadata: {"role": "helper"}
def _validate_inactive_product(repo_root: Path) -> None:
    """Validate the inactive product boundary without requiring repository material."""
    product_root = repo_root / "product/specs/product"
    if not product_root.exists():
        return
    if not product_root.is_dir():
        fail("product specification root failed: product/specs/product must be a directory")

    undeclared_json = sorted(
        path.relative_to(repo_root).as_posix()
        for path in product_root.rglob("*.json")
        if path.is_file()
    )
    if undeclared_json:
        fail(
            "product specification root failed: inactive product specification system "
            "contains JSON material: "
            + ", ".join(undeclared_json)
        )

    _manifest, repo_specs, _source_paths, _actual_paths = load_repo_specs(repo_root)
    context = ValidationContext(
        repo_root,
        None,
        None,
        ExternalRepositoryValidationContext(repo_specs, load_repo_schemas(repo_root)),
    )
    check_product_development_documents(context)
    print("ok: product development documents")
    check_product_lifecycle_readiness(context)
    print("ok: product lifecycle authority sequence")



# validation-metadata: {"role": "helper"}
def _load_product_only_context(repo_root: Path) -> ValidationContext:
    _manifest, specs, _source_paths, _actual_paths = load_repo_specs(repo_root)
    external_repository = ExternalRepositoryValidationContext(
        specs,
        load_repo_schemas(repo_root),
    )
    product = load_product_validation_context(repo_root)
    return ValidationContext(repo_root, None, product, external_repository)


# validation-metadata: {"role": "helper"}
def _check_product_unique_spec_ids(context: ValidationContext) -> None:
    expect(context.product is not None, "product validation context missing")
    expect(
        len(context.product.specs) == len(set(context.product.specs)),
        "duplicate product specification id",
    )


# validation-metadata: {"role": "helper"}
def _check_product_unique_item_properties(context: ValidationContext) -> None:
    expect(context.product is not None, "product validation context missing")
    for spec_id in context.product.specs:
        check_unique_item_properties(
            context.product.specs,
            spec_id,
            "normative_requirements",
            ["id"],
        )
        check_unique_item_properties(
            context.product.specs,
            spec_id,
            "dependencies",
            ["spec_id"],
        )
        check_unique_item_properties(
            context.product.specs,
            spec_id,
            "references",
            ["type", "spec_id", "path", "kind"],
        )
        check_unique_item_properties(
            context.product.specs,
            spec_id,
            "derived_artifacts",
            ["path"],
        )


# validation-metadata: {"role": "helper"}
def _check_product_unique_derived_artifact_paths(
    context: ValidationContext,
) -> None:
    expect(context.product is not None, "product validation context missing")
    paths: list[str] = []
    for spec in context.product.specs.values():
        for artifact in spec.get("derived_artifacts", []):
            paths.append(artifact["path"])
    expect(
        len(paths) == len(set(paths)),
        "duplicate product derived artifact paths failed",
    )


# validation-metadata: {"role": "helper"}
def _check_product_lineage(context: ValidationContext) -> None:
    expect(context.product is not None, "product validation context missing")
    for spec_id, spec in context.product.specs.items():
        for field in ("supersedes", "superseded_by"):
            for target_spec_id in spec.get(field, []):
                expect(
                    target_spec_id in context.product.specs,
                    f"product lineage failed: unresolved spec "
                    f"{spec_id} -> {target_spec_id}",
                )
                expect(
                    target_spec_id != spec_id,
                    f"product lineage failed: self reference {spec_id}",
                )
    check_supersession_pairs(
        context.product.specs,
        "product supersession relations",
    )
    check_supersession_acyclicity(
        context.product.specs,
        "product supersession relations",
    )


PRODUCT_LEAF_VALIDATION_PHASES: list[tuple[str, Any]] = [
    ("product structural envelopes", check_product_structural_envelopes),
    ("product validation layout", check_validation_layout),
    ("product source layout", check_product_source_layout),
    ("product unique specification IDs", _check_product_unique_spec_ids),
    ("product unique item properties", _check_product_unique_item_properties),
    (
        "product unique derived artifact paths",
        _check_product_unique_derived_artifact_paths,
    ),
    ("product specification root", check_product_specification_root_phase),
    ("product correspondence inventory", check_product_correspondence_phase),
    (
        "product validation correspondence packages",
        check_product_validation_correspondence_packages_phase,
    ),
    (
        "product conformance completeness",
        check_product_conformance_completeness_phase,
    ),
    ("product dependency directions", check_dependency_directions_phase),
    ("product completeness", check_product_completeness_phase),
    ("product lineage relations", _check_product_lineage),
    (
        "product acyclic dependencies",
        check_product_acyclic_dependencies_phase,
    ),
]


PRODUCT_VALIDATION_PHASES: list[tuple[str, Any]] = [
    *PRODUCT_LEAF_VALIDATION_PHASES,
    ("product development documents", check_product_development_documents),
    ("product lifecycle authority sequence", check_product_lifecycle_readiness),
    ("product generated-document freshness", check_product_generated_freshness),
]


# validation-metadata: {"role": "helper"}
def validate_product_phases(repo_root: Path, phase_labels: tuple[str, ...]) -> None:
    context = _load_product_only_context(repo_root)
    phase_map = dict(PRODUCT_VALIDATION_PHASES)
    leaf_labels = {label for label, _check in PRODUCT_LEAF_VALIDATION_PHASES}
    for label in phase_labels:
        check = phase_map.get(label)
        if check is None:
            raise ValueError(f"unknown product validation phase: {label}")
        if context.product is None and label in leaf_labels:
            continue
        check(context)


# validation-metadata: {"role": "helper"}
def validate_product(repo_root: Path) -> None:
    manifest = repo_root / "product/specs/product/manifest.json"
    if not manifest.exists():
        _validate_inactive_product(repo_root)
        print("ok: product specification system inactive")
        return

    context = _load_product_only_context(repo_root)
    for label, check in PRODUCT_VALIDATION_PHASES:
        check(context)
        print(f"ok: {label}")
