from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


DOMAIN_ROOTS = (Path("validation"), Path("repo/validation"))
IMPLEMENTATION_PARTS = {"checks", "core", "runners"}
PREFIX = "# validation-metadata: "


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
                text = source.read_text(encoding="utf-8")
                lines = text.splitlines()
                tree = ast.parse(text, filename=rel.as_posix())

                for node in ast.walk(tree):
                    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        continue
                    callable_count += 1
                    self.assertEqual(
                        [],
                        node.decorator_list,
                        f"{rel}:{node.lineno}: VCP-I2 metadata is a source annotation, not a runtime decorator",
                    )
                    self.assertGreater(node.lineno, 1, f"{rel}:{node.lineno}: missing metadata line")
                    metadata_line = lines[node.lineno - 2]
                    expected_indent = lines[node.lineno - 1][
                        : len(lines[node.lineno - 1]) - len(lines[node.lineno - 1].lstrip())
                    ]
                    self.assertTrue(
                        metadata_line.startswith(expected_indent + PREFIX),
                        f"{rel}:{node.lineno}: metadata must be immediately before def",
                    )
                    payload = metadata_line[len(expected_indent + PREFIX):]
                    record = json.loads(payload)

                    if record.get("role") == "helper":
                        self.assertEqual({"role"}, set(record))
                        continue

                    self.assertEqual("task", record.get("role"))
                    self.assertEqual(
                        {"role", "task_id", "normative_reference"},
                        set(record),
                    )
                    task_count += 1
                    self.assertIsInstance(record["task_id"], str)
                    self.assertTrue(record["task_id"])
                    ref = record["normative_reference"]
                    self.assertEqual({"spec_id", "requirement_id"}, set(ref))
                    self.assertTrue(ref["spec_id"])
                    self.assertTrue(ref["requirement_id"])
                    self.assertNotIn(record["task_id"], seen_task_ids)
                    seen_task_ids[record["task_id"]] = (rel.as_posix(), node.name)

                self.assertNotIn(
                    ".__validation_metadata__",
                    text,
                    f"{rel}: post-definition metadata assignment remains",
                )

        self.assertEqual(113, callable_count)
        self.assertEqual(18, task_count)

    def test_product_validation_remains_unmodified_handoff_scope(self) -> None:
        product_root = self.repo_root / "product/validation"
        tagged = []
        for source in product_root.rglob("*.py"):
            if not source.is_file():
                continue
            text = source.read_text(encoding="utf-8")
            if PREFIX in text or ".__validation_metadata__" in text:
                tagged.append(source.relative_to(self.repo_root).as_posix())
        self.assertEqual([], tagged)


if __name__ == "__main__":
    unittest.main()
