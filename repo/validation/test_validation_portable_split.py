from __future__ import annotations

import ast
from pathlib import Path

from validation.errors import fail
from validation.portable_self_tests import run_repository_portable_self_tests


def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


def run_validation_portable_split_tests(repo_root: Path) -> None:
    repo_impl = repo_root / "repo/scripts/test_validation_impl.py"
    product_impl = repo_root / "product/scripts/test_validation_impl.py"
    repo_portable = repo_root / "repo/scripts/validation/portable_self_tests.py"
    product_portable = repo_root / "product/scripts/product_validation/portable_self_tests.py"

    repo_imports = _top_level_imports(repo_impl)
    product_imports = _top_level_imports(product_impl)
    if "validation.tests.mutation_tests" in repo_imports:
        fail("portable split failed: repository source test suite remains a top-level import")
    if "validation_tests.mutation_tests" in product_imports:
        fail("portable split failed: product source test suite remains a top-level import")

    if "validation.portable_self_tests" not in repo_imports:
        fail("portable split failed: repository stable surface omits portable self-tests")
    if "product_validation.portable_self_tests" not in product_imports:
        fail("portable split failed: product stable surface omits portable self-tests")

    repo_portable_imports = _top_level_imports(repo_portable)
    product_portable_imports = _top_level_imports(product_portable)
    if any(module.startswith("validation.tests") for module in repo_portable_imports):
        fail("portable split failed: repository portable layer imports source test tree")
    if any(module.startswith("validation_tests") for module in product_portable_imports):
        fail("portable split failed: product portable layer imports source test tree")

    # Keep this repo-owned source-development regression test independent of
    # product implementation imports. product/scripts/test-validation executes
    # the product portable self-test under the product-owned environment.
    run_repository_portable_self_tests(repo_root)
    print("ok: validation portable/source split")
