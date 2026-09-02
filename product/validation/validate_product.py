#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "product/specs/FS-001-minimal-repository-initialization.md"
MANIFEST_PATH = ROOT / "product/validation/requirement-evaluation.json"
TEST_PATH = ROOT / "product/validation/test_initializer.py"

TASK_TESTS = {
    "cli-surface": [
        "test_cli_surface_requires_destination_only",
        "test_normal_cli_refuses_unaccepted_feature_revision",
    ],
    "source-integrity": [
        "test_refuses_dirty_supplying_framework_material",
        "test_accepts_linked_git_worktree_as_supplying_checkout",
        "test_source_revision_matches_current_supplying_commit",
        "test_explicit_test_seam_allows_unaccepted_feature_revision",
    ],
    "destination-safety": [
        "test_initializes_absent_destination",
        "test_initializes_existing_empty_directory",
        "test_refuses_nonempty_destination_without_deleting_material",
    ],
    "initialized-state": [
        "test_initialized_repository_state",
    ],
    "validation-boundary": [
        "test_validation_failure_does_not_promote_destination",
    ],
    "regression-integrity": [],
}


def fail(message: str) -> int:
    print(f"FAIL product-validation: {message}", flush=True)
    return 1


def parse_requirements() -> dict[str, str]:
    text = SPEC_PATH.read_text(encoding="utf-8")
    requirements: dict[str, str] = {}
    current: str | None = None

    heading = re.compile(r"^### (FS-\d+-NR-\d+) — ")
    classification = re.compile(r"^Classification: ([MSB])$")

    for line in text.splitlines():
        match = heading.match(line)
        if match:
            current = match.group(1)
            continue
        match = classification.match(line)
        if match and current is not None:
            requirements[current] = match.group(1)
            current = None

    return requirements


def load_manifest() -> dict:
    try:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"required manifest missing: {MANIFEST_PATH.relative_to(ROOT)}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest JSON: {exc}") from exc


def validate_manifest() -> tuple[dict[str, str], dict[str, list[str]]]:
    requirements = parse_requirements()
    mechanical = {rid for rid, cls in requirements.items() if cls in {"M", "B"}}
    semantic = {rid for rid, cls in requirements.items() if cls == "S"}

    manifest = load_manifest()
    if manifest.get("version") != 1:
        raise ValueError("manifest version must be 1")

    bindings = manifest.get("bindings")
    if not isinstance(bindings, list):
        raise ValueError("manifest bindings must be a list")

    observed: dict[str, list[str]] = {}
    for item in bindings:
        if not isinstance(item, dict):
            raise ValueError("each binding must be an object")
        rid = item.get("requirement")
        tasks = item.get("tasks")
        if not isinstance(rid, str) or not isinstance(tasks, list) or not tasks:
            raise ValueError("each binding requires a requirement string and non-empty tasks list")
        if rid in observed:
            raise ValueError(f"duplicate requirement binding: {rid}")
        if rid not in requirements:
            raise ValueError(f"unknown/stale requirement binding: {rid}")
        if rid in semantic:
            raise ValueError(f"purely semantic requirement must not have mechanical binding: {rid}")
        unknown_tasks = [task for task in tasks if task not in TASK_TESTS]
        if unknown_tasks:
            raise ValueError(f"{rid} references unknown tasks: {unknown_tasks}")
        if len(tasks) != len(set(tasks)):
            raise ValueError(f"{rid} contains duplicate tasks")
        observed[rid] = tasks

    missing = sorted(mechanical - set(observed))
    extra = sorted(set(observed) - mechanical)
    if missing:
        raise ValueError(f"mechanical requirements missing bindings: {missing}")
    if extra:
        raise ValueError(f"non-mechanical requirements unexpectedly bound: {extra}")

    return requirements, observed


def load_tests_module():
    spec = importlib.util.spec_from_file_location("fs001_initializer_tests", TEST_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load product regression test module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_task(task: str, module) -> bool:
    print(f"\n===== PRODUCT TASK {task} =====", flush=True)

    methods = TASK_TESTS[task]
    if task == "regression-integrity":
        available = {
            name
            for name in dir(module.InitializerTests)
            if name.startswith("test_")
        }
        referenced = {
            method
            for task_methods in TASK_TESTS.values()
            for method in task_methods
        }
        missing = sorted(referenced - available)
        unbound = sorted(available - referenced)
        if missing:
            print(f"FAIL regression-integrity missing tests: {missing}", flush=True)
            return False
        if unbound:
            print(f"FAIL regression-integrity unbound tests: {unbound}", flush=True)
            return False
        print(
            f"PASS regression-integrity {len(available)} regression tests are task-bound",
            flush=True,
        )
        return True

    suite = unittest.TestSuite()
    for method in methods:
        suite.addTest(module.InitializerTests(method))

    result = unittest.TextTestRunner(
        stream=sys.stdout,
        verbosity=2,
    ).run(suite)
    return result.wasSuccessful()


def main() -> int:
    print("Product Validation: START", flush=True)

    try:
        requirements, bindings = validate_manifest()
    except (ValueError, OSError) as exc:
        return fail(str(exc))

    mechanical_count = sum(cls in {"M", "B"} for cls in requirements.values())
    semantic_count = sum(cls == "S" for cls in requirements.values())
    print(
        f"PASS requirement-evaluation manifest: "
        f"{mechanical_count} mechanical/B requirements bound; "
        f"{semantic_count} semantic-only requirements unbound",
        flush=True,
    )

    required_tasks = []
    for item in json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))["bindings"]:
        for task in item["tasks"]:
            if task not in required_tasks:
                required_tasks.append(task)

    module = load_tests_module()

    all_passed = True
    for task in required_tasks:
        requirements_for_task = [
            rid for rid, tasks in bindings.items() if task in tasks
        ]
        print(
            f"\nTask {task}: requirements {', '.join(requirements_for_task)}",
            flush=True,
        )
        if not run_task(task, module):
            all_passed = False
            break

    if not all_passed:
        print("Product Validation: FAILED", flush=True)
        return 1

    print("\nProduct Validation: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
