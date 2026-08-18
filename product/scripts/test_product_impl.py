#!/usr/bin/env python3

from __future__ import annotations

import errno
import json
import os
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any, Callable


SCHEMA_VERSION = "1"

SUCCESS_ZERO = "successful-zero-applicable"
SUCCESS_APPLICABLE = "successful-applicable-execution"
FAILED_TESTS = "failed-applicable-tests"
UNRESOLVED = "unresolved-expected-tests"
INVALID = "applicability-invalid"
INTERFACE_DEPENDENCY = "interface-dependency-failure"
DISCOVERY = "discovery-registration-failure"
INFRASTRUCTURE = "infrastructure-failure"


def _result(
    *,
    applicability: str,
    classification: str,
    accepted_specs: list[str],
    obligations: list[dict[str, Any]],
    detail: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "applicability": applicability,
        "classification": classification,
        "accepted_specs": accepted_specs,
        "obligations": obligations,
    }
    if detail is not None:
        value["detail"] = detail
    return value


def _safe_repository_path(value: object) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    if "\\" in value or value.startswith("/") or "//" in value:
        return None
    path = PurePosixPath(value)
    if any(part == ".." for part in path.parts):
        return None
    return value


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _collect_applicability(repo_root: Path) -> dict[str, Any]:
    manifest_path = repo_root / "product/specs/product/manifest.json"
    if not manifest_path.is_file():
        return _result(
            applicability="applicability-invalid",
            classification=INVALID,
            accepted_specs=[],
            obligations=[],
            detail="accepted product manifest is missing",
        )

    try:
        manifest = _load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return _result(
            applicability="applicability-invalid",
            classification=INVALID,
            accepted_specs=[],
            obligations=[],
            detail=f"accepted product manifest is unreadable or malformed: {type(exc).__name__}",
        )

    if not isinstance(manifest, dict) or not isinstance(manifest.get("product_specifications"), list):
        return _result(
            applicability="applicability-invalid",
            classification=INVALID,
            accepted_specs=[],
            obligations=[],
            detail="accepted product manifest lacks product_specifications",
        )

    accepted_entries: list[tuple[str, str]] = []
    for entry in manifest["product_specifications"]:
        if not isinstance(entry, dict):
            return _result(
                applicability="applicability-invalid",
                classification=INVALID,
                accepted_specs=[],
                obligations=[],
                detail="product manifest contains a non-object entry",
            )
        if entry.get("status") != "accepted":
            continue
        spec_id = entry.get("spec_id")
        spec_path = _safe_repository_path(entry.get("path"))
        if not isinstance(spec_id, str) or not spec_id or spec_path is None:
            return _result(
                applicability="applicability-invalid",
                classification=INVALID,
                accepted_specs=[],
                obligations=[],
                detail="accepted manifest entry has invalid identity or path",
            )
        accepted_entries.append((spec_id, spec_path))

    accepted_entries.sort()
    accepted_specs = [spec_id for spec_id, _ in accepted_entries]
    if len(set(accepted_specs)) != len(accepted_specs):
        return _result(
            applicability="applicability-invalid",
            classification=INVALID,
            accepted_specs=accepted_specs,
            obligations=[],
            detail="accepted product manifest contains duplicate specification identities",
        )

    obligations: list[dict[str, Any]] = []
    seen_obligation_ids: set[tuple[str, str]] = set()

    for spec_id, relative_path in accepted_entries:
        spec_path = repo_root / relative_path
        if not spec_path.is_file():
            return _result(
                applicability="applicability-invalid",
                classification=INVALID,
                accepted_specs=accepted_specs,
                obligations=[],
                detail=f"accepted specification is missing: {spec_id}",
            )

        try:
            spec = _load_json(spec_path)
        except (OSError, json.JSONDecodeError) as exc:
            return _result(
                applicability="applicability-invalid",
                classification=INVALID,
                accepted_specs=accepted_specs,
                obligations=[],
                detail=f"accepted specification is unreadable or malformed: {spec_id}: {type(exc).__name__}",
            )

        if not isinstance(spec, dict) or spec.get("spec_id") != spec_id or spec.get("status") != "accepted":
            return _result(
                applicability="applicability-invalid",
                classification=INVALID,
                accepted_specs=accepted_specs,
                obligations=[],
                detail=f"accepted specification identity/status mismatch: {spec_id}",
            )

        correspondence = spec.get("correspondence")
        if not isinstance(correspondence, dict):
            return _result(
                applicability="applicability-invalid",
                classification=INVALID,
                accepted_specs=accepted_specs,
                obligations=[],
                detail=f"accepted specification lacks correspondence evidence: {spec_id}",
            )

        tests = correspondence.get("tests")
        if not isinstance(tests, list):
            return _result(
                applicability="applicability-invalid",
                classification=DISCOVERY,
                accepted_specs=accepted_specs,
                obligations=[],
                detail=f"test correspondence registration is malformed: {spec_id}",
            )

        for mapping in tests:
            if not isinstance(mapping, dict):
                return _result(
                    applicability="applicability-invalid",
                    classification=DISCOVERY,
                    accepted_specs=accepted_specs,
                    obligations=[],
                    detail=f"test correspondence registration contains a non-object mapping: {spec_id}",
                )

            test_id = mapping.get("id")
            paths = mapping.get("paths")
            requirements = mapping.get("requirements")
            if (
                not isinstance(test_id, str)
                or not test_id.startswith("test.")
                or not isinstance(paths, list)
                or not paths
                or not isinstance(requirements, list)
                or not requirements
                or not all(isinstance(req, str) and req for req in requirements)
            ):
                return _result(
                    applicability="applicability-invalid",
                    classification=DISCOVERY,
                    accepted_specs=accepted_specs,
                    obligations=[],
                    detail=f"test correspondence registration is incomplete: {spec_id}",
                )

            key = (spec_id, test_id)
            if key in seen_obligation_ids:
                return _result(
                    applicability="applicability-invalid",
                    classification=DISCOVERY,
                    accepted_specs=accepted_specs,
                    obligations=[],
                    detail=f"duplicate test obligation registration: {spec_id}:{test_id}",
                )
            seen_obligation_ids.add(key)

            normalized_paths: list[str] = []
            for path_value in paths:
                normalized = _safe_repository_path(path_value)
                if normalized is None:
                    return _result(
                        applicability="applicability-invalid",
                        classification=DISCOVERY,
                        accepted_specs=accepted_specs,
                        obligations=[],
                        detail=f"invalid repository-relative test path: {spec_id}:{test_id}",
                    )
                normalized_paths.append(normalized)

            obligations.append(
                {
                    "spec_id": spec_id,
                    "test_id": test_id,
                    "paths": sorted(set(normalized_paths)),
                    "requirements": sorted(set(requirements)),
                }
            )

    obligations.sort(key=lambda item: (item["spec_id"], item["test_id"], item["paths"]))

    if not obligations:
        return _result(
            applicability="zero-applicable",
            classification=SUCCESS_ZERO,
            accepted_specs=accepted_specs,
            obligations=[],
        )

    return _result(
        applicability="applicable-and-resolved",
        classification="applicable-pending-resolution",
        accepted_specs=accepted_specs,
        obligations=obligations,
    )


def run_product_tests(
    repo_root: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    applicability = _collect_applicability(repo_root)
    if applicability["classification"] in {INVALID, DISCOVERY, SUCCESS_ZERO}:
        return applicability

    obligations = applicability["obligations"]
    accepted_specs = applicability["accepted_specs"]

    for obligation in obligations:
        for relative_path in obligation["paths"]:
            path = repo_root / relative_path
            if not path.is_file():
                return _result(
                    applicability="applicable-and-resolved",
                    classification=UNRESOLVED,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    detail=f"expected product test path is unresolved: {relative_path}",
                )
            if not os.access(path, os.X_OK):
                return _result(
                    applicability="applicable-and-resolved",
                    classification=UNRESOLVED,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    detail=f"expected product test path is not executable: {relative_path}",
                )

    for obligation in obligations:
        for relative_path in obligation["paths"]:
            path = repo_root / relative_path
            try:
                completed = runner(
                    [str(path)],
                    cwd=repo_root,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    check=False,
                )
            except OSError as exc:
                classification = (
                    INTERFACE_DEPENDENCY
                    if exc.errno in {errno.ENOENT, errno.EACCES}
                    else INFRASTRUCTURE
                )
                return _result(
                    applicability="applicable-and-resolved",
                    classification=classification,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    detail=f"product test execution could not start: {relative_path}: {type(exc).__name__}",
                )

            if completed.returncode != 0:
                return _result(
                    applicability="applicable-and-resolved",
                    classification=FAILED_TESTS,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    detail=f"product test failed: {relative_path}: exit {completed.returncode}",
                )

    return _result(
        applicability="applicable-and-resolved",
        classification=SUCCESS_APPLICABLE,
        accepted_specs=accepted_specs,
        obligations=obligations,
    )


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()

    if len(argv) > 2:
        print(f"product test error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1

    result = run_product_tests(repo_root)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))

    if result["classification"] in {SUCCESS_ZERO, SUCCESS_APPLICABLE}:
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
