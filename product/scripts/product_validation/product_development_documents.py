"""Product-owned development-document validation orchestration."""

from __future__ import annotations

from typing import Any

from .context import ValidationContext
from .development_documents import DEVELOPMENT_DOCUMENT_ROOTS, check_development_documents_phase, load_development_document_compatibility_registry


def _product_development_roots() -> dict[str, dict[str, Any]]:
    return {
        root_rel: info
        for root_rel, info in DEVELOPMENT_DOCUMENT_ROOTS.items()
        if root_rel.startswith("product/")
    }


def check_product_development_documents(context: ValidationContext) -> None:
    selected_roots = _product_development_roots()
    full_registry = load_development_document_compatibility_registry(
        context.repo_root,
        development_roots=DEVELOPMENT_DOCUMENT_ROOTS,
    )
    prefixes = tuple(selected_roots)
    owned_compatibility_paths = {
        path for path in full_registry if path.startswith(prefixes)
    }
    check_development_documents_phase(
        context,
        development_roots=selected_roots,
        compatibility_registry=full_registry,
        owned_compatibility_paths=owned_compatibility_paths,
    )
