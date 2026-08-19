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
    validation_root = repo_root / "product/validation"
    if (validation_root / "__init__.py").exists():
        raise AssertionError(
            "product validation ownership failed: product/validation must not be "
            "an importable root package"
        )
    expected_dirs = {"checks", "core", "runners", "tests"}
    actual_dirs = {path.name for path in validation_root.iterdir() if path.is_dir()}
    if actual_dirs != expected_dirs:
        raise AssertionError(
            "product validation ownership failed: product/validation directory "
            "layout mismatch: " + ", ".join(sorted(actual_dirs))
        )

    bootstrap = scripts / "validate_bootstrap_impl.py"
    if bootstrap.exists():
        raise AssertionError(
            "product validation ownership failed: special bootstrap validator remains"
        )

    validate_impl = validation_root / "runners/validate_impl.py"
    validate_text = validate_impl.read_text()
    if "from validation.core.errors import ValidationFailure" not in validate_text:
        raise AssertionError(
            "product validation ownership failed: validate_impl missing stable "
            "ValidationFailure contract"
        )
    if (
        "from validation.checks.product_checks import validate_product"
        not in validate_text
    ):
        raise AssertionError(
            "product validation ownership failed: validate_impl missing stable "
            "product_checks entry point"
        )

    product_checks = validation_root / "checks/product_checks.py"
    checks_text = product_checks.read_text()
    if "Future governed product development" not in checks_text:
        raise AssertionError(
            "product validation ownership failed: future expansion note missing"
        )
    if "from .active_product_checks import" not in checks_text:
        raise AssertionError(
            "product validation ownership failed: active validation is not deferred"
        )

    forbidden: list[str] = []
    for owned_dir in ("core", "checks", "runners"):
        for path in sorted((validation_root / owned_dir).glob("*.py")):
            for module in sorted(_absolute_imports(path)):
                if module == "repo_model" or module.startswith("repo."):
                    forbidden.append(f"{owned_dir}/{path.name}: {module}")
    if forbidden:
        raise AssertionError(
            "product validation ownership failed: product implementation crosses "
            "ownership boundary: " + "; ".join(forbidden)
        )

    repo_validation = repo_root / "repo/validation"
    repo_forbidden: list[str] = []
    for path in sorted(repo_validation.rglob("*.py")):
        for module in sorted(_absolute_imports(path)):
            if module == "product_validation" or module.startswith("product_validation."):
                repo_forbidden.append(
                    f"{path.relative_to(repo_validation)}: {module}"
                )
    if repo_forbidden:
        raise AssertionError(
            "product validation ownership failed: repo validation imports product "
            "implementation: " + "; ".join(repo_forbidden)
        )
