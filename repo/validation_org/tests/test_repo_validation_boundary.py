from __future__ import annotations

import ast
import re
from pathlib import Path

from validation.core.errors import fail


_PUBLIC_WRAPPERS = (
    "repo/scripts/validate",
    "repo/scripts/test-validation",
)

_SELF = "repo/validation/tests/test_repo_validation_boundary.py"

_FORBIDDEN_IMPORT_PREFIXES = (
    "product",
    "product_validation",
    "validation_tests",
)

_PRODUCT_PREFIXES = (
    "product/scripts/",
    "product/specs/",
    "product/schemas/",
    "product/docs/",
)

_CHECKOUT_ROOT_NAMES = {"repo_root"}


def _literal_string(node: ast.AST) -> str | None:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _call_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        parts: list[str] = []
        current: ast.AST = node
        while isinstance(current, ast.Attribute):
            parts.append(current.attr)
            current = current.value
        if isinstance(current, ast.Name):
            parts.append(current.id)
            return ".".join(reversed(parts))
    return None


def _annotate_parents(tree: ast.AST) -> None:
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            setattr(child, "parent", parent)


def _is_negative_membership_assert(node: ast.AST, value: str) -> bool:
    current = node
    while hasattr(current, "parent"):
        current = current.parent
        if isinstance(current, ast.Compare):
            if any(isinstance(op, ast.NotIn) for op in current.ops):
                values = [current.left, *current.comparators]
                if any(_literal_string(v) == value for v in values):
                    return True
        if isinstance(current, ast.Assert):
            break
        if isinstance(current, ast.Call):
            name = _call_name(current.func)
            if name and name.endswith("expect"):
                first = current.args[0] if current.args else None
                if isinstance(first, ast.Compare) and any(
                    isinstance(op, ast.NotIn) for op in first.ops
                ):
                    values = [first.left, *first.comparators]
                    if any(_literal_string(v) == value for v in values):
                        return True
            break
    return False


def _split_literal_path(value: str) -> list[str]:
    return [part for part in value.split("/") if part not in {"", "."}]


def _rooted_path_segments(node: ast.AST) -> list[str] | None:
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _rooted_path_segments(node.left)
        right = _literal_string(node.right)
        if left is not None and right is not None:
            return left + _split_literal_path(right)
        return None
    if isinstance(node, ast.Name) and node.id in _CHECKOUT_ROOT_NAMES:
        return []
    return None


def _outermost_path(node: ast.BinOp) -> ast.BinOp:
    current = node
    while hasattr(current, "parent"):
        parent = current.parent
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div):
            current = parent
            continue
        break
    return current


def _string_inside_rooted_path(node: ast.Constant) -> bool:
    current: ast.AST = node
    while hasattr(current, "parent"):
        current = current.parent
        if isinstance(current, ast.BinOp) and isinstance(current.op, ast.Div):
            if _rooted_path_segments(_outermost_path(current)) is not None:
                return True
        if isinstance(current, (ast.Call, ast.Assign, ast.AnnAssign, ast.Expr)):
            break
    return False


def _scan_python(rel: str, text: str) -> list[str]:
    violations: list[str] = []
    try:
        tree = ast.parse(text, filename=rel)
    except SyntaxError as exc:
        return [f"{rel}:{exc.lineno or 1}: cannot parse Python: {exc.msg}"]

    _annotate_parents(tree)
    seen_paths: set[int] = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if any(
                    alias.name == prefix or alias.name.startswith(prefix + ".")
                    for prefix in _FORBIDDEN_IMPORT_PREFIXES
                ):
                    violations.append(
                        f"{rel}:{node.lineno}: product-owned import: import {alias.name}"
                    )

        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            if any(
                node.module == prefix or node.module.startswith(prefix + ".")
                for prefix in _FORBIDDEN_IMPORT_PREFIXES
            ):
                violations.append(
                    f"{rel}:{node.lineno}: product-owned import: from {node.module} import ..."
                )

        elif isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
            outer = _outermost_path(node)
            if id(outer) in seen_paths:
                continue
            segments = _rooted_path_segments(outer)
            if segments is None:
                continue
            seen_paths.add(id(outer))
            if segments and segments[0] != "repo":
                violations.append(
                    f"{rel}:{outer.lineno}: checkout-rooted validation path escapes repo/: "
                    + "/".join(segments)
                )

        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            owner = node.func.value
            if isinstance(owner, ast.Name) and owner.id in _CHECKOUT_ROOT_NAMES:
                if node.func.attr in {"iterdir", "glob", "rglob"}:
                    violations.append(
                        f"{rel}:{node.lineno}: checkout-root traversal escapes repo/: "
                        f"{owner.id}.{node.func.attr}(...)"
                    )

        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            value = node.value
            if _is_negative_membership_assert(node, value):
                continue
            if _string_inside_rooted_path(node):
                continue
            if any(prefix in value for prefix in _PRODUCT_PREFIXES):
                violations.append(
                    f"{rel}:{node.lineno}: product-owned path/configuration literal: {value}"
                )

    return violations


def _scan_shell(rel: str, text: str) -> list[str]:
    violations: list[str] = []
    # Match each $root path independently and stop at shell/path-list delimiters.
    pattern = re.compile(r"\$root/([A-Za-z0-9._/-]+)")
    for lineno, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        for match in pattern.finditer(line):
            rooted = match.group(1)
            parts = _split_literal_path(rooted)
            if parts and parts[0] != "repo":
                violations.append(
                    f"{rel}:{lineno}: shell checkout path escapes repo/: $root/{rooted}"
                )
    return violations


def _validation_files(repo_root: Path) -> list[Path]:
    files = [repo_root / rel for rel in _PUBLIC_WRAPPERS]
    validation_root = repo_root / "repo/validation"
    files.extend(
        path
        for path in validation_root.rglob("*")
        if path.is_file()
        and "__pycache__" not in path.parts
        and path.relative_to(repo_root).as_posix() != _SELF
    )
    return sorted(set(files))


def collect_repo_validation_boundary_violations(repo_root: Path) -> list[str]:
    violations: list[str] = []

    for path in _validation_files(repo_root):
        rel = path.relative_to(repo_root).as_posix()
        if not path.exists():
            violations.append(f"{rel}:1: required repository validation file is missing")
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        if path.suffix == ".py":
            violations.extend(_scan_python(rel, text))
        else:
            violations.extend(_scan_shell(rel, text))

    return sorted(set(violations))


def run_repo_validation_boundary_tests(repo_root: Path) -> None:
    violations = collect_repo_validation_boundary_violations(repo_root)
    if violations:
        fail(
            "repository validation boundary failed: repo validation reaches outside "
            "the repo-owned validation domain:\n- "
            + "\n- ".join(violations)
        )

    print("ok: repository validation repo-boundary isolation")
