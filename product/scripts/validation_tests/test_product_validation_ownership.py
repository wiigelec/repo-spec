from __future__ import annotations

import ast
from pathlib import Path


REPO_FORBIDDEN_PRODUCT_SYMBOLS = {
    "ProductValidationContext",
    "actual_product_paths",
    "load_product_validation_context",
    "load_product_schemas",
    "check_dependency_directions",
    "check_product_completeness",
    "check_product_acyclic_dependencies",
    "check_product_specification_root_phase",
    "check_dependency_directions_phase",
    "check_product_completeness_phase",
    "check_product_acyclic_dependencies_phase",
    "ProductCorrespondenceInventory",
    "load_product_correspondence_inventory",
    "check_product_correspondence_phase",
    "check_product_conformance_completeness_phase",
    "_owned_development_roots",
    "_check_development_documents_for_domain",
    "_product_development_roots_for_shared_lifecycle",
    "_check_lifecycle_for_domain",
    "check_lifecycle_lifecycle_phase",
}

PRODUCT_REQUIRED_SYMBOLS = {
    "product_state.py": {
        "ProductValidationContext",
        "actual_product_paths",
        "load_product_validation_context",
        "load_product_schemas",
    },
    "product_policy.py": {
        "check_dependency_directions",
        "check_product_completeness",
        "check_product_acyclic_dependencies",
        "check_product_specification_root_phase",
        "check_dependency_directions_phase",
        "check_product_completeness_phase",
        "check_product_acyclic_dependencies_phase",
    },
    "product_correspondence.py": {
        "ProductCorrespondenceInventory",
        "load_product_correspondence_inventory",
        "check_product_correspondence_phase",
        "check_product_conformance_completeness_phase",
    },
    "product_development_documents.py": {
        "_product_development_roots",
        "check_product_development_documents",
    },
    "product_lifecycle.py": {
        "check_product_lifecycle_readiness",
    },
}


def _defined_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    return {
        node.name
        for node in tree.body
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef))
    }


def run_product_validation_ownership_tests(repo_root: Path) -> None:
    repo_checks = repo_root / "repo/scripts/validation/repository_checks.py"
    repo_symbols = _defined_symbols(repo_checks)
    leaked = sorted(REPO_FORBIDDEN_PRODUCT_SYMBOLS & repo_symbols)
    if leaked:
        raise AssertionError(
            "product validation ownership failed: repository-owned validation defines "
            + ", ".join(leaked)
        )

    product_root = repo_root / "product/scripts/product_validation"
    for filename, expected_symbols in PRODUCT_REQUIRED_SYMBOLS.items():
        path = product_root / filename
        if not path.exists():
            raise AssertionError(
                f"product validation ownership failed: missing {path.relative_to(repo_root)}"
            )
        symbols = _defined_symbols(path)
        missing = sorted(expected_symbols - symbols)
        if missing:
            raise AssertionError(
                "product validation ownership failed: "
                f"{path.relative_to(repo_root)} missing "
                + ", ".join(missing)
            )
