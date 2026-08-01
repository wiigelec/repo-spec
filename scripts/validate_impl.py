#!/usr/bin/env python3

"""Validation entry point for repo-spec."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

from repo_model import load_specs as load_repo_specs, resolve_repo_path as resolve_repo_path_impl
from validation.errors import ValidationFailure, expect, fail
from validation.generated_outputs import check_generated_document_freshness, check_generated_document_write_behavior
from validation.repository_checks import (
    check_acyclic_dependencies,
    check_clean_failure_behavior,
    check_dependency_targets,
    check_lineage_relations,
    check_manifest_completeness,
    check_resolvable_references,
    check_unique_derived_artifact_paths,
    check_unique_item_properties,
    check_unique_spec_ids,
    load_repo_schemas,
    validate_repo,
    validate_repo_json_schema_conformance,
)
from validation.schema_subset import (
    ensure_schema_keywords,
    instance_location,
    load_json,
    resolve_ref,
    schema_location,
    schema_matches,
    validate_instance,
)


def resolve_repo_path(repo_root: Path, value: str) -> Path:
    try:
        return resolve_repo_path_impl(repo_root, value)
    except ValueError as exc:
        fail(str(exc))


def load_specs(repo_root: Path) -> tuple[dict[str, Any], dict[str, dict[str, Any]], dict[str, str], list[str]]:
    try:
        return load_repo_specs(repo_root)
    except Exception as exc:
        fail(str(exc))


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    mode = argv[2] if len(argv) > 2 else "--write"

    if mode == "--self-test-failure":
        print("forced failure for behavior test", file=sys.stderr)
        return 1

    try:
        if mode == "--write":
            validate_repo(repo_root)
            return 0
        if mode == "--mutation-tests":
            from validate_mutations import main as mutation_main

            return mutation_main([argv[0], str(repo_root)])
        fail(f"unknown mode: {mode}")
    except ValidationFailure as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
