from __future__ import annotations

import ast
from pathlib import Path

from validation.core.errors import fail
from validation.tests.self.portable_self_tests import run_repository_portable_self_tests


# validation-metadata: {"role": "helper"}
def _top_level_imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: set[str] = set()
    for node in tree.body:
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.add(node.module)
    return modules


# validation-metadata: {"role": "helper"}
def run_validation_portable_split_tests(repo_root: Path) -> None:
    repo_impl = repo_root / "repo/validation/runners/test_validation_impl.py"
    repo_portable = repo_root / "repo/validation/tests/self/portable_self_tests.py"

    repo_imports = _top_level_imports(repo_impl)
    if "validation.tests.self.mutation_tests" in repo_imports:
        fail("portable split failed: repository source test suite remains a top-level import")
    if "validation.tests.self.portable_self_tests" not in repo_imports:
        fail("portable split failed: repository stable surface omits portable self-tests")

    repo_portable_imports = _top_level_imports(repo_portable)
    if any(module.startswith("validation.tests") for module in repo_portable_imports):
        fail("portable split failed: repository portable layer imports source test tree")

    run_repository_portable_self_tests(repo_root)
    print("ok: repository validation portable/source split")
