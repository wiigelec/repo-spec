"""Product-owned validation policy and orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .product_state import load_product_validation_context
from .product_policy import (
    check_dependency_directions_phase,
    check_product_acyclic_dependencies_phase,
    check_product_completeness_phase,
    check_product_specification_root_phase,
)
from .product_correspondence import (
    check_product_conformance_completeness_phase,
    check_product_correspondence_phase,
)
from .product_development_documents import check_product_development_documents

from validation.repository_checks import (
    ExternalRepositoryValidationContext,
    ValidationContext,
    _check_generated_freshness_for_domain,
    _check_lifecycle_for_domain,
    check_supersession_acyclicity,
    check_supersession_pairs,
    check_unique_item_properties,
    expect,
    load_repo_schemas,
    load_repo_specs,
)


def _load_product_only_context(repo_root: Path) -> ValidationContext:
    _manifest, specs, _source_paths, _actual_paths = load_repo_specs(repo_root)
    external_repository = ExternalRepositoryValidationContext(
        specs,
        load_repo_schemas(repo_root),
    )
    product = load_product_validation_context(repo_root)
    return ValidationContext(repo_root, None, product, external_repository)


def _check_product_unique_spec_ids(context: ValidationContext) -> None:
    expect(context.product is not None, "product validation context missing")
    expect(
        len(context.product.specs) == len(set(context.product.specs)),
        "duplicate product specification id",
    )


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
    ("product unique specification IDs", _check_product_unique_spec_ids),
    ("product unique item properties", _check_product_unique_item_properties),
    (
        "product unique derived artifact paths",
        _check_product_unique_derived_artifact_paths,
    ),
    ("product specification root", check_product_specification_root_phase),
    ("product correspondence inventory", check_product_correspondence_phase),
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


def validate_product(repo_root: Path) -> None:
    context = _load_product_only_context(repo_root)
    if context.product is not None:
        for label, check in PRODUCT_LEAF_VALIDATION_PHASES:
            check(context)
            print(f"ok: {label}")
    else:
        print("ok: product specification system inactive")
    check_product_development_documents(context)
    print("ok: product development documents")
    _check_lifecycle_for_domain(
        context,
        product_mode=True,
    )
    print("ok: product lifecycle authority sequence")
    _check_generated_freshness_for_domain(
        context,
        product_mode=True,
    )
    print("ok: product generated-document freshness")
