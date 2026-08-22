from __future__ import annotations

import ast
import json
import unittest
from pathlib import Path


DOMAIN_ROOTS = (
    Path("validation"),
    Path("repo/validation"),
    Path("product/validation"),
)
IMPLEMENTATION_PARTS = {"checks", "core", "runners", "github"}
TEST_PARTS = {("tests", "unit"), ("tests", "self")}
PREFIX = "# validation-metadata: "


class ValidationCallableMetadataTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    @classmethod
    def setUpClass(cls) -> None:
        cls.repo_root = Path(__file__).resolve().parents[3]

    # validation-metadata: {"role": "helper"}
    def test_framework_owned_validation_callables_have_exactly_one_role(self) -> None:
        seen_task_ids: dict[str, tuple[str, str]] = {}
        callable_count = 0
        task_count = 0

        for domain_root in DOMAIN_ROOTS:
            absolute_domain = self.repo_root / domain_root
            for source in sorted(absolute_domain.rglob("*")):
                if not source.is_file():
                    continue
                is_python_source = source.suffix == ".py"
                if not is_python_source:
                    try:
                        probe_text = source.read_text(encoding="utf-8")
                        probe_lines = probe_text.splitlines()
                        first_line = probe_lines[0] if probe_lines else ""
                    except (OSError, UnicodeDecodeError):
                        continue
                    is_python_source = first_line.startswith("#!") and "python" in first_line.lower()
                if not is_python_source:
                    continue
                relative_to_domain = source.relative_to(absolute_domain)
                parts = relative_to_domain.parts
                in_implementation = len(parts) >= 2 and parts[0] in IMPLEMENTATION_PARTS
                in_tests = len(parts) >= 3 and (parts[0], parts[1]) in TEST_PARTS
                if (
                    not (in_implementation or in_tests)
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
                    declaration_line = min(
                        [node.lineno] + [decorator.lineno for decorator in node.decorator_list]
                    )
                    self.assertGreater(
                        declaration_line,
                        1,
                        f"{rel}:{node.lineno}: missing metadata line",
                    )
                    metadata_line = lines[declaration_line - 2]
                    declaration_text = lines[declaration_line - 1]
                    expected_indent = declaration_text[
                        : len(declaration_text) - len(declaration_text.lstrip())
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

                post_definition_assignments = []
                for candidate in ast.walk(tree):
                    if not isinstance(candidate, ast.Assign):
                        continue
                    for target in candidate.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and target.attr == "__validation_metadata__"
                        ):
                            post_definition_assignments.append(candidate.lineno)
                self.assertEqual(
                    [],
                    post_definition_assignments,
                    f"{rel}: post-definition metadata assignment remains",
                )

        self.assertGreater(callable_count, 113)
        self.assertEqual(19, task_count)


if __name__ == "__main__":
    unittest.main()
