from __future__ import annotations

import ast
from pathlib import Path


PRODUCT_SUPPORT_MODULES = {
    "__init__.py",
    "context.py",
    "development_documents.py",
    "errors.py",
    "invariants.py",
    "paths.py",
    "schema_subset.py",
}


def _imports(path: Path) -> list[tuple[str | None, int]]:
    tree = ast.parse(path.read_text(), filename=str(path))
    imports: list[tuple[str | None, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend((alias.name, 0) for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append((node.module, node.level))
    return imports


def _forbidden_product_imports(path: Path) -> list[str]:
    forbidden: list[str] = []
    for module, level in _imports(path):
        if level or module is None:
            continue
        if module == "repo_model" or module.startswith("repo.") or module.startswith("repo_scripts"):
            forbidden.append(module)
    return sorted(set(forbidden))


def _forbidden_repo_imports(path: Path) -> list[str]:
    forbidden: list[str] = []
    for module, level in _imports(path):
        if level or module is None:
            continue
        if module == "product_validation" or module.startswith("product_validation."):
            forbidden.append(module)
    return sorted(set(forbidden))


def run_product_validation_ownership_tests(repo_root: Path) -> None:
    product_validation = repo_root / "product/scripts/product_validation"
    product_support = repo_root / "product/scripts/validation"
    repo_validation = repo_root / "repo/scripts/validation"

    actual_support = {path.name for path in product_support.glob("*.py")}
    if actual_support != PRODUCT_SUPPORT_MODULES:
        raise AssertionError(
            "product validation ownership failed: product support inventory mismatch: "
            f"expected={sorted(PRODUCT_SUPPORT_MODULES)}, actual={sorted(actual_support)}"
        )

    for path in sorted(product_validation.glob("*.py")) + sorted(product_support.glob("*.py")):
        forbidden = _forbidden_product_imports(path)
        if forbidden:
            raise AssertionError(
                f"product validation ownership failed: {path.relative_to(repo_root)} "
                f"imports repo-owned implementation: {', '.join(forbidden)}"
            )

    for path in sorted(repo_validation.glob("*.py")):
        forbidden = _forbidden_repo_imports(path)
        if forbidden:
            raise AssertionError(
                f"repository validation ownership failed: {path.relative_to(repo_root)} "
                f"imports product-owned implementation: {', '.join(forbidden)}"
            )

    for label in ("product/scripts/validate", "product/scripts/test-validation"):
        if "$root/repo/scripts" in (repo_root / label).read_text():
            raise AssertionError(
                f"product validation ownership failed: {label} exposes repo/scripts on PYTHONPATH"
            )

    root_validation = repo_root / "repo/scripts/root_validation.py"
    if not root_validation.is_file():
        raise AssertionError("repository validation ownership failed: missing root_validation.py")

    allowed_stdlib = {"re", "subprocess", "sys", "pathlib", "__future__"}
    for module, level in _imports(root_validation):
        if level:
            raise AssertionError("transportable root validation uses relative imports")
        top = (module or "").split(".", 1)[0]
        if top and top not in allowed_stdlib:
            raise AssertionError(
                f"transportable root validation imports domain implementation: {module}"
            )
