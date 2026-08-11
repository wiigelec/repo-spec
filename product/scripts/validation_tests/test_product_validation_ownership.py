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
    "_check_generated_freshness_for_domain",
}

SHARED_DEVELOPMENT_DOCUMENT_SYMBOLS = {
    "DEVELOPMENT_DOCUMENT_ROOTS",
    "DevelopmentDocumentRecord",
    "check_development_documents_phase",
    "get_development_document_records",
    "load_development_document_compatibility_registry",
}


SHARED_INVARIANT_SYMBOLS = {
    "check_supersession_acyclicity",
    "check_supersession_pairs",
    "check_unique_item_properties",
    "expect",
    "resolve_repo_path",
}


SHARED_CONTEXT_SYMBOLS = {
    "ExternalRepositoryValidationContext",
    "ValidationContext",
    "load_repo_specs",
    "load_repo_schemas",
}


def _repository_check_imported_symbols(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    imported: set[str] = set()
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.level == 0
            and node.module == "validation.repository_checks"
        ):
            imported.update(alias.name for alias in node.names)
    return imported


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
    "product_generated_freshness.py": {
        "check_product_generated_freshness",
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
    product_root = repo_root / "product/scripts/product_validation"
    shared_leaks: dict[str, list[str]] = {}
    for path in sorted(product_root.glob("*.py")):
        leaked = sorted(SHARED_CONTEXT_SYMBOLS & _repository_check_imported_symbols(path))
        if leaked:
            shared_leaks[path.name] = leaked
    if shared_leaks:
        detail = "; ".join(
            f"{filename}: {', '.join(symbols)}"
            for filename, symbols in shared_leaks.items()
        )
        raise AssertionError(
            "product validation ownership failed: shared context/loading imported "
            "from repository_checks: " + detail
        )

    invariant_leaks: dict[str, list[str]] = {}
    for path in sorted(product_root.glob("*.py")):
        leaked = sorted(SHARED_INVARIANT_SYMBOLS & _repository_check_imported_symbols(path))
        if leaked:
            invariant_leaks[path.name] = leaked
    if invariant_leaks:
        detail = "; ".join(f"{filename}: {', '.join(symbols)}" for filename, symbols in invariant_leaks.items())
        raise AssertionError(
            "product validation ownership failed: shared invariant/path/failure mechanics imported from repository_checks: " + detail
        )

    development_document_leaks: dict[str, list[str]] = {}
    for path in sorted(product_root.glob("*.py")):
        leaked = sorted(
            SHARED_DEVELOPMENT_DOCUMENT_SYMBOLS
            & _repository_check_imported_symbols(path)
        )
        if leaked:
            development_document_leaks[path.name] = leaked
    if development_document_leaks:
        detail = "; ".join(
            f"{filename}: {', '.join(symbols)}"
            for filename, symbols in development_document_leaks.items()
        )
        raise AssertionError(
            "product validation ownership failed: shared development-document mechanics imported from repository_checks: "
            + detail
        )

    shared_development_documents = (
        repo_root / "repo/scripts/validation/development_documents.py"
    )
    required_development_document_symbols = {
        "DevelopmentDocumentRecord",
        "check_development_document_relationships",
        "check_development_documents_phase",
        "get_development_document_records",
        "load_development_document_compatibility_registry",
    }
    if (
        not shared_development_documents.exists()
        or not required_development_document_symbols.issubset(
            _defined_symbols(shared_development_documents)
        )
    ):
        raise AssertionError(
            "product validation ownership failed: shared development-document module incomplete"
        )

    shared_invariants = repo_root / "repo/scripts/validation/invariants.py"
    required_invariants = {"check_supersession_acyclicity", "check_supersession_pairs", "check_unique_item_properties"}
    if not shared_invariants.exists() or not required_invariants.issubset(_defined_symbols(shared_invariants)):
        raise AssertionError("product validation ownership failed: shared invariants module incomplete")
    shared_paths = repo_root / "repo/scripts/validation/paths.py"
    if not shared_paths.exists() or "resolve_repo_path" not in _defined_symbols(shared_paths):
        raise AssertionError("product validation ownership failed: shared paths module incomplete")

    shared_context = repo_root / "repo/scripts/validation/context.py"
    if not shared_context.exists():
        raise AssertionError(
            "product validation ownership failed: missing repo/scripts/validation/context.py"
        )
    shared_symbols = _defined_symbols(shared_context)
    required_shared = {
        "RepositoryValidationContext",
        "ExternalRepositoryValidationContext",
        "ValidationContext",
        "load_repo_specs",
    }
    missing_shared = sorted(required_shared - shared_symbols)
    if missing_shared:
        raise AssertionError(
            "product validation ownership failed: shared context module missing "
            + ", ".join(missing_shared)
        )

    repo_checks = repo_root / "repo/scripts/validation/repository_checks.py"
    repo_symbols = _defined_symbols(repo_checks)
    leaked = sorted(REPO_FORBIDDEN_PRODUCT_SYMBOLS & repo_symbols)
    if leaked:
        raise AssertionError(
            "product validation ownership failed: repository-owned validation defines "
            + ", ".join(leaked)
        )

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
