#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SPECS_ROOT = ROOT / "product" / "specs"
MANIFEST_PATH = ROOT / "product" / "validation" / "requirement-evaluation.json"
TEST_PATH = ROOT / "product" / "validation" / "test_initializer.py"

TASK_TESTS = {
    "cli-surface": [
        "test_cli_surface_requires_destination_only",
        "test_normal_cli_refuses_unaccepted_feature_revision",
    ],
    "source-integrity": [
        "test_refuses_dirty_supplying_framework_material",
        "test_refuses_dirty_initializer_source_material",
        "test_accepts_linked_git_worktree_as_supplying_checkout",
        "test_source_revision_matches_current_supplying_commit",
        "test_internal_test_seam_allows_unaccepted_feature_revision",
    ],
    "destination-safety": [
        "test_initializes_absent_destination",
        "test_initializes_existing_empty_directory",
        "test_refuses_nonempty_destination_without_deleting_material",
        "test_refuses_symlink_destination_without_mutating_target",
    ],
    "initialized-state": [
        "test_initialized_repository_state",
        "test_initialized_repository_validates_after_source_checkout_removed",
    ],
    "validation-boundary": [
        "test_validation_failure_does_not_promote_destination",
    ],
    "regression-integrity": [],
}

CLASS_RE = re.compile(r"^(?:\*\*)?Classification: ([MSB])(?:\*\*)?$")
STATE_RE = re.compile(r"^(?:\*\*)?State: (active|inactive)(?:\*\*)?$")


def fail(message: str) -> int:
    print(f"FAIL product-validation: {message}", flush=True)
    return 1


def parse_requirement_state() -> tuple[dict[str, str], set[str]]:
    requirements: dict[str, str] = {}
    inactive: set[str] = set()

    if not SPECS_ROOT.is_dir():
        raise ValueError("product/specs must exist")

    for spec_path in sorted(SPECS_ROOT.glob("FS-*.md")):
        text = spec_path.read_text(encoding="utf-8")
        headings = list(re.finditer(r"^### (FS-\d{3}-NR-\d{3}) — .+$", text, re.MULTILINE))
        for index, match in enumerate(headings):
            rid = match.group(1)
            if rid in requirements:
                raise ValueError(f"duplicate requirement identity: {rid}")
            end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
            block = text[match.end():end]
            classes = [m.group(1) for line in block.splitlines() if (m := CLASS_RE.match(line))]
            if len(classes) != 1:
                raise ValueError(f"{rid} must have exactly one Classification")
            requirements[rid] = classes[0]
            states = [m.group(1) for line in block.splitlines() if (m := STATE_RE.match(line))]
            if len(states) > 1:
                raise ValueError(f"{rid} has multiple State declarations")
            if states == ["inactive"]:
                inactive.add(rid)

    return requirements, inactive


def load_manifest() -> dict:
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError("required manifest missing: product/validation/requirement-evaluation.json") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid manifest JSON: {exc}") from exc
    if data.get("version") != 1 or not isinstance(data.get("bindings"), list):
        raise ValueError("invalid product Requirement Evaluation Manifest structure")
    return data


def validate_manifest() -> tuple[dict[str, str], dict[str, list[str]]]:
    requirements, inactive = parse_requirement_state()
    required = {rid for rid, cls in requirements.items() if cls in {"M", "B"} and rid not in inactive}
    forbidden = {rid for rid, cls in requirements.items() if cls == "S" or rid in inactive}

    data = load_manifest()
    observed: dict[str, list[str]] = {}
    for item in data["bindings"]:
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
        if rid in forbidden:
            raise ValueError(f"requirement must not have mechanical binding: {rid}")
        if len(tasks) != len(set(tasks)) or not all(isinstance(task, str) and task for task in tasks):
            raise ValueError(f"{rid} contains invalid or duplicate tasks")
        unknown = [task for task in tasks if task not in TASK_TESTS]
        if unknown:
            raise ValueError(f"{rid} references unknown tasks: {unknown}")
        observed[rid] = tasks

    missing = sorted(required - set(observed))
    if missing:
        raise ValueError(f"mechanical requirements missing bindings: {missing}")
    return requirements, observed


def load_tests_module():
    spec = importlib.util.spec_from_file_location("initializer_tests", TEST_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load product regression test module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_task(task: str, module) -> bool:
    print(f"\n===== PRODUCT TASK {task} =====", flush=True)
    methods = TASK_TESTS[task]
    if task == "regression-integrity":
        available = {name for name in dir(module.InitializerTests) if name.startswith("test_")}
        referenced = {method for task_methods in TASK_TESTS.values() for method in task_methods}
        missing = sorted(referenced - available)
        unbound = sorted(available - referenced)
        if missing:
            print(f"FAIL regression-integrity missing tests: {missing}", flush=True)
            return False
        if unbound:
            print(f"FAIL regression-integrity unbound tests: {unbound}", flush=True)
            return False
        print(f"PASS regression-integrity {len(available)} regression tests are task-bound", flush=True)
        return True
    suite = unittest.TestSuite(module.InitializerTests(method) for method in methods)
    return unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite).wasSuccessful()


def required_tasks(bindings: dict[str, list[str]]) -> list[str]:
    ordered: list[str] = []
    for item in load_manifest()["bindings"]:
        for task in item["tasks"]:
            if task not in ordered:
                ordered.append(task)
    return ordered


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument("--list-tasks", action="store_true")
    parser.add_argument("--task")
    args = parser.parse_args(argv)

    if args.list_tasks and args.task:
        return fail("--list-tasks and --task are mutually exclusive")
    if args.list_tasks:
        for task in sorted(TASK_TESTS):
            print(task)
        return 0

    try:
        requirements, bindings = validate_manifest()
    except (ValueError, OSError) as exc:
        return fail(str(exc))

    if args.task:
        if args.task not in TASK_TESTS:
            return fail(f"unknown product Validation task: {args.task}")
        module = load_tests_module()
        return 0 if run_task(args.task, module) else 1

    print("Product Validation: START", flush=True)
    module = load_tests_module()
    for task in required_tasks(bindings):
        owners = [rid for rid, tasks in bindings.items() if task in tasks]
        print(f"\nTask {task}: requirements {', '.join(owners)}", flush=True)
        if not run_task(task, module):
            print("Product Validation: FAILED", flush=True)
            return 1
    print("\nProduct Validation: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
