from __future__ import annotations

import ast
from pathlib import Path


def _absolute_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(), filename=str(path))
    modules: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


def run_product_validation_ownership_tests(repo_root: Path) -> None:
    scripts = repo_root / "product/scripts"
    validation_dir = scripts / "validation"
    actual_validation_files = sorted(
        path.name for path in validation_dir.glob("*.py") if path.is_file()
    )
    if actual_validation_files != ["__init__.py", "errors.py"]:
        raise AssertionError(
            "product validation ownership failed: validation/ must contain only "
            "__init__.py and errors.py, found " + ", ".join(actual_validation_files)
        )

    bootstrap = scripts / "validate_bootstrap_impl.py"
    if bootstrap.exists():
        raise AssertionError(
            "product validation ownership failed: special bootstrap validator remains"
        )

    validate_impl = scripts / "validate_impl.py"
    validate_text = validate_impl.read_text()
    if "from validation.errors import ValidationFailure" not in validate_text:
        raise AssertionError(
            "product validation ownership failed: validate_impl missing stable "
            "ValidationFailure contract"
        )
    if (
        "from product_validation.product_checks import validate_product"
        not in validate_text
    ):
        raise AssertionError(
            "product validation ownership failed: validate_impl missing stable "
            "product_checks entry point"
        )

    product_checks = scripts / "product_validation/product_checks.py"
    checks_text = product_checks.read_text()
    if "Future governed product development" not in checks_text:
        raise AssertionError(
            "product validation ownership failed: future expansion note missing"
        )
    if "from .active_product_checks import" not in checks_text:
        raise AssertionError(
            "product validation ownership failed: active validation is not deferred"
        )

    product_root = scripts / "product_validation"
    forbidden: list[str] = []
    for path in sorted(product_root.glob("*.py")):
        for module in sorted(_absolute_imports(path)):
            if module == "repo_model" or module.startswith("repo."):
                forbidden.append(f"{path.name}: {module}")
            if module.startswith("validation.") and module != "validation.errors":
                forbidden.append(f"{path.name}: {module}")
    if forbidden:
        raise AssertionError(
            "product validation ownership failed: product implementation crosses "
            "ownership boundary: " + "; ".join(forbidden)
        )

    repo_validation = repo_root / "repo/scripts/validation"
    repo_forbidden: list[str] = []
    for path in sorted(repo_validation.glob("*.py")):
        for module in sorted(_absolute_imports(path)):
            if module == "product_validation" or module.startswith("product_validation."):
                repo_forbidden.append(f"{path.name}: {module}")
    if repo_forbidden:
        raise AssertionError(
            "product validation ownership failed: repo validation imports product "
            "implementation: " + "; ".join(repo_forbidden)
        )
