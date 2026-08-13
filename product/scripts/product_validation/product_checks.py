"""Stable product-owned validation entry point.

The inactive validation path is intentionally self-contained so this module can
be transported verbatim into a freshly initialized repository without the
source-only product validation implementation.

Future governed product development may extend or reorganize active product
validation behind ``validate_product``. Keep this entry point product-owned and
do not introduce dependencies on repo-owned validation implementation.
"""

from __future__ import annotations

from pathlib import Path

from validation.errors import fail
from .context import ExternalRepositoryValidationContext, ValidationContext, load_repo_specs
from .schema_subset import load_repo_schemas
from .product_development_documents import check_product_development_documents
from .product_lifecycle import check_product_lifecycle_readiness


def _validate_inactive_product(repo_root: Path) -> None:
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


def validate_product_phases(repo_root: Path, phase_labels: tuple[str, ...]) -> None:
    """Source-validation compatibility hook.

    This helper is intentionally lazy: freshly initialized repositories do not
    call it and therefore do not need the source-only active validation graph.
    """
    from .active_product_checks import validate_product_phases as validate_active_phases

    validate_active_phases(repo_root, phase_labels)


def validate_product(repo_root: Path) -> None:
    manifest = repo_root / "product/specs/product/manifest.json"
    if not manifest.exists():
        _validate_inactive_product(repo_root)
        print("ok: product specification system inactive")
        return

    # repo-spec currently has an active product specification system. Its
    # source-only validation implementation remains product-owned, but it is
    # deliberately imported only after active state is established so a fresh
    # initialized repository does not need those future/full modules.
    from .active_product_checks import validate_product as validate_active_product

    validate_active_product(repo_root)
