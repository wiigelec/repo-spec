from __future__ import annotations

import ast
import unittest
from pathlib import Path


DOMAIN_ROOTS = (Path("validation"), Path("repo/validation"))
IMPLEMENTATION_PARTS = {"checks", "core", "runners"}
METADATA_ATTR = "__validation_metadata__"


def _function_key(path: Path, node: ast.AST, parents: dict[ast.AST, ast.AST]) -> tuple[str, str]:
    parts = [node.name]
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            parts.append(current.name)
        current = parents.get(current)
    return path.as_posix(), ".".join(reversed(parts))


def _literal_metadata(node: ast.AST) -> dict | None:
    try:
        value = ast.literal_eval(node)
    except Exception:
        return None
    return value if isinstance(value, dict) else None


class ValidationCallableMetadataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[3]

    def test_framework_owned_validation_callables_have_exactly_one_role(self) -> None:
        seen_task_ids: dict[str, tuple[str, str]] = {}
        callable_count = 0
        task_count = 0

        for domain_root in DOMAIN_ROOTS:
            absolute_domain = self.repo_root / domain_root
            for source in sorted(absolute_domain.rglob("*.py")):
                relative_to_domain = source.relative_to(absolute_domain)
                if (
                    len(relative_to_domain.parts) < 2
                    or relative_to_domain.parts[0] not in IMPLEMENTATION_PARTS
                    or "__pycache__" in source.parts
                ):
                    continue

                rel = source.relative_to(self.repo_root)
                tree = ast.parse(source.read_text(encoding="utf-8"), filename=rel.as_posix())
                parents: dict[ast.AST, ast.AST] = {}
                for parent in ast.walk(tree):
                    for child in ast.iter_child_nodes(parent):
                        parents[child] = parent

                functions = {
                    _function_key(rel, node, parents): node
                    for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                }
                metadata: dict[tuple[str, str], list[dict]] = {key: [] for key in functions}

                for node in ast.walk(tree):
                    if not isinstance(node, ast.Assign) or len(node.targets) != 1:
                        continue
                    target = node.targets[0]
                    if (
                        not isinstance(target, ast.Attribute)
                        or target.attr != METADATA_ATTR
                        or not isinstance(target.value, ast.Name)
                    ):
                        continue
                    value = _literal_metadata(node.value)
                    self.assertIsNotNone(value, f"{rel}:{node.lineno}: metadata must be a literal object")

                    candidates = [
                        key for key in functions
                        if key[0] == rel.as_posix() and key[1].split(".")[-1] == target.value.id
                    ]
                    self.assertTrue(candidates, f"{rel}:{node.lineno}: metadata target not found")

                    owner = parents.get(node)
                    owner_names: list[str] = []
                    while owner is not None:
                        if isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                            owner_names.append(owner.name)
                        owner = parents.get(owner)
                    owner_prefix = ".".join(reversed(owner_names))
                    matching = [
                        key for key in candidates
                        if ".".join(key[1].split(".")[:-1]) == owner_prefix
                    ]
                    self.assertEqual(1, len(matching), f"{rel}:{node.lineno}: ambiguous metadata target")
                    metadata[matching[0]].append(value)

                for key in functions:
                    callable_count += 1
                    records = metadata[key]
                    self.assertEqual(
                        1,
                        len(records),
                        f"{key[0]}:{key[1]} must have exactly one source-local validation role",
                    )
                    record = records[0]
                    if record.get("role") == "helper":
                        self.assertEqual({"role"}, set(record))
                        continue

                    self.assertEqual("task", record.get("role"))
                    self.assertEqual({"role", "task_id", "normative_reference"}, set(record))
                    task_count += 1
                    self.assertIsInstance(record["task_id"], str)
                    self.assertTrue(record["task_id"])
                    ref = record["normative_reference"]
                    self.assertEqual({"spec_id", "requirement_id"}, set(ref))
                    self.assertTrue(ref["spec_id"])
                    self.assertTrue(ref["requirement_id"])
                    self.assertNotIn(record["task_id"], seen_task_ids)
                    seen_task_ids[record["task_id"]] = key

        self.assertEqual(113, callable_count)
        self.assertEqual(18, task_count)

    def test_product_validation_remains_unmodified_handoff_scope(self) -> None:
        product_root = self.repo_root / "product/validation"
        tagged = []
        for source in product_root.rglob("*.py"):
            if source.is_file() and METADATA_ATTR in source.read_text(encoding="utf-8"):
                tagged.append(source.relative_to(self.repo_root).as_posix())
        self.assertEqual([], tagged)


if __name__ == "__main__":
    unittest.main()
