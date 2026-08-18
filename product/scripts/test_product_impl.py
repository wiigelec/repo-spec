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

SUCCESS_CLASSES = {SUCCESS_ZERO, SUCCESS_APPLICABLE}


def _result(
    *,
    applicability: str,
    classification: str,
    accepted_specs: list[str],
    obligations: list[dict[str, Any]],
    evidence: dict[str, Any],
    detail: str | None = None,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "applicability": applicability,
        "classification": classification,
        "accepted_specs": accepted_specs,
        "obligations": obligations,
        "evidence": evidence,
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


def _invalid(
    accepted_specs: list[str],
    evidence: dict[str, Any],
    detail: str,
    *,
    classification: str = INVALID,
) -> dict[str, Any]:
    return _result(
        applicability="applicability-invalid",
        classification=classification,
        accepted_specs=accepted_specs,
        obligations=[],
        evidence=evidence,
        detail=detail,
    )


def _collect_applicability(repo_root: Path) -> dict[str, Any]:
    manifest_path = repo_root / "product/specs/product/manifest.json"

    if not manifest_path.exists():
        return _result(
            applicability="zero-applicable",
            classification=SUCCESS_ZERO,
            accepted_specs=[],
            obligations=[],
            evidence={
                "product_specification_system": "inactive",
                "basis": "canonical product manifest absent",
            },
        )

    evidence: dict[str, Any] = {
        "product_specification_system": "active",
        "manifest": "product/specs/product/manifest.json",
        "conformance_complete": False,
    }

    if not manifest_path.is_file():
        return _invalid([], evidence, "canonical product manifest is not a regular file")

    try:
        manifest = _load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return _invalid(
            [],
            evidence,
            f"canonical product manifest is unreadable or malformed: {type(exc).__name__}",
        )

    if not isinstance(manifest, dict):
        return _invalid([], evidence, "canonical product manifest is not an object")
    if manifest.get("spec_id") != "product.manifest":
        return _invalid([], evidence, "canonical product manifest identity is invalid")

    entries = manifest.get("product_specifications")
    if not isinstance(entries, list):
        return _invalid([], evidence, "canonical product manifest lacks product_specifications")

    accepted_entries: list[tuple[str, str]] = []
    all_ids: set[str] = set()
    all_paths: set[str] = set()

    for entry in entries:
        if not isinstance(entry, dict):
            return _invalid([], evidence, "product manifest contains a non-object entry")

        spec_id = entry.get("spec_id")
        spec_path = _safe_repository_path(entry.get("path"))
        status = entry.get("status")

        if not isinstance(spec_id, str) or not spec_id or spec_path is None:
            return _invalid([], evidence, "product manifest entry has invalid identity or path")
        if spec_id in all_ids or spec_path in all_paths:
            return _invalid([], evidence, "product manifest contains duplicate identity or path")
        all_ids.add(spec_id)
        all_paths.add(spec_path)

        if status == "accepted":
            accepted_entries.append((spec_id, spec_path))

    accepted_entries.sort()
    accepted_specs = [spec_id for spec_id, _ in accepted_entries]
    evidence["accepted_spec_count"] = len(accepted_specs)

    if not accepted_entries:
        evidence["conformance_complete"] = True
        evidence["basis"] = "active product manifest contains no accepted specifications"
        return _result(
            applicability="zero-applicable",
            classification=SUCCESS_ZERO,
            accepted_specs=[],
            obligations=[],
            evidence=evidence,
        )

    obligations_by_key: dict[tuple[str, str], dict[str, Any]] = {}

    for spec_id, relative_path in accepted_entries:
        spec_path = repo_root / relative_path
        if not spec_path.is_file():
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification is missing: {spec_id}",
            )

        try:
            spec = _load_json(spec_path)
        except (OSError, json.JSONDecodeError) as exc:
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification is unreadable or malformed: {spec_id}: {type(exc).__name__}",
            )

        if not isinstance(spec, dict) or spec.get("spec_id") != spec_id or spec.get("status") != "accepted":
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification identity/status mismatch: {spec_id}",
            )

        requirements = spec.get("normative_requirements")
        correspondence = spec.get("correspondence")
        if not isinstance(requirements, list) or not isinstance(correspondence, dict):
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification lacks normative/correspondence evidence: {spec_id}",
            )

        requirement_ids: list[str] = []
        for requirement in requirements:
            if (
                not isinstance(requirement, dict)
                or not isinstance(requirement.get("id"), str)
                or not requirement["id"]
            ):
                return _invalid(
                    accepted_specs,
                    evidence,
                    f"accepted specification has malformed normative requirement: {spec_id}",
                )
            requirement_ids.append(requirement["id"])

        if len(set(requirement_ids)) != len(requirement_ids):
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification has duplicate normative requirement IDs: {spec_id}",
            )

        tests = correspondence.get("tests")
        conformance = correspondence.get("conformance")
        if not isinstance(tests, list) or not isinstance(conformance, list):
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification has malformed correspondence collections: {spec_id}",
                classification=DISCOVERY,
            )

        test_mappings: dict[str, dict[str, Any]] = {}
        for mapping in tests:
            if not isinstance(mapping, dict):
                return _invalid(
                    accepted_specs,
                    evidence,
                    f"test correspondence registration contains a non-object mapping: {spec_id}",
                    classification=DISCOVERY,
                )

            test_id = mapping.get("id")
            paths = mapping.get("paths")
            mapping_requirements = mapping.get("requirements")
            if (
                not isinstance(test_id, str)
                or not test_id.startswith("test.")
                or test_id in test_mappings
                or not isinstance(paths, list)
                or not paths
                or not isinstance(mapping_requirements, list)
                or not mapping_requirements
                or not all(isinstance(req, str) and req for req in mapping_requirements)
            ):
                return _invalid(
                    accepted_specs,
                    evidence,
                    f"test correspondence registration is incomplete or duplicate: {spec_id}",
                    classification=DISCOVERY,
                )

            normalized_paths: list[str] = []
            for path_value in paths:
                normalized = _safe_repository_path(path_value)
                if normalized is None:
                    return _invalid(
                        accepted_specs,
                        evidence,
                        f"invalid repository-relative test path: {spec_id}:{test_id}",
                        classification=DISCOVERY,
                    )
                normalized_paths.append(normalized)

            test_mappings[test_id] = {
                "spec_id": spec_id,
                "test_id": test_id,
                "paths": sorted(set(normalized_paths)),
                "requirements": sorted(set(mapping_requirements)),
            }

        conformance_by_requirement: dict[str, dict[str, Any]] = {}
        referenced_test_ids: set[str] = set()

        for record in conformance:
            if not isinstance(record, dict):
                return _invalid(
                    accepted_specs,
                    evidence,
                    f"conformance registration contains a non-object record: {spec_id}",
                    classification=DISCOVERY,
                )

            requirement_id = record.get("requirement_id")
            status = record.get("status")
            test_ids = record.get("test_ids")

            if (
                not isinstance(requirement_id, str)
                or requirement_id not in requirement_ids
                or requirement_id in conformance_by_requirement
                or status not in {"covered", "not-applicable"}
                or not isinstance(test_ids, list)
            ):
                return _invalid(
                    accepted_specs,
                    evidence,
                    f"conformance registration is malformed or contradictory: {spec_id}",
                    classification=DISCOVERY,
                )

            conformance_by_requirement[requirement_id] = record

            if status == "not-applicable":
                if test_ids:
                    return _invalid(
                        accepted_specs,
                        evidence,
                        f"not-applicable conformance references tests: {spec_id}:{requirement_id}",
                        classification=DISCOVERY,
                    )
                rationale = record.get("rationale")
                if not isinstance(rationale, str) or not rationale.strip():
                    return _invalid(
                        accepted_specs,
                        evidence,
                        f"not-applicable conformance lacks rationale: {spec_id}:{requirement_id}",
                        classification=DISCOVERY,
                    )
                continue

            if not test_ids or not all(isinstance(test_id, str) for test_id in test_ids):
                return _invalid(
                    accepted_specs,
                    evidence,
                    f"covered conformance lacks governed test mappings: {spec_id}:{requirement_id}",
                    classification=DISCOVERY,
                )

            for test_id in test_ids:
                mapping = test_mappings.get(test_id)
                if mapping is None:
                    return _invalid(
                        accepted_specs,
                        evidence,
                        f"covered conformance references unknown test mapping: {spec_id}:{requirement_id}:{test_id}",
                        classification=DISCOVERY,
                    )
                if requirement_id not in mapping["requirements"]:
                    return _invalid(
                        accepted_specs,
                        evidence,
                        f"test mapping does not claim covered requirement: {spec_id}:{requirement_id}:{test_id}",
                        classification=DISCOVERY,
                    )
                referenced_test_ids.add(test_id)
                obligations_by_key[(spec_id, test_id)] = mapping

        missing_conformance = sorted(set(requirement_ids) - set(conformance_by_requirement))
        if missing_conformance:
            return _invalid(
                accepted_specs,
                evidence,
                f"accepted specification has undeclared applicability evidence: {spec_id}:{','.join(missing_conformance)}",
            )

        unreachable = sorted(set(test_mappings) - referenced_test_ids)
        if unreachable:
            return _invalid(
                accepted_specs,
                evidence,
                f"test mappings are not reachable from conformance: {spec_id}:{','.join(unreachable)}",
                classification=DISCOVERY,
            )

    evidence["conformance_complete"] = True
    obligations = sorted(
        obligations_by_key.values(),
        key=lambda item: (item["spec_id"], item["test_id"], item["paths"]),
    )

    if not obligations:
        evidence["basis"] = "all accepted normative requirements explicitly not-applicable to product tests"
        return _result(
            applicability="zero-applicable",
            classification=SUCCESS_ZERO,
            accepted_specs=accepted_specs,
            obligations=[],
            evidence=evidence,
        )

    evidence["basis"] = "covered conformance records reference governed product test mappings"
    return _result(
        applicability="applicable-and-resolved",
        classification="applicable-pending-resolution",
        accepted_specs=accepted_specs,
        obligations=obligations,
        evidence=evidence,
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
    evidence = applicability["evidence"]

    for obligation in obligations:
        for relative_path in obligation["paths"]:
            path = repo_root / relative_path
            if not path.is_file():
                return _result(
                    applicability="applicable-and-resolved",
                    classification=UNRESOLVED,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    evidence=evidence,
                    detail=f"expected product test path is unresolved: {relative_path}",
                )
            if not os.access(path, os.X_OK):
                return _result(
                    applicability="applicable-and-resolved",
                    classification=UNRESOLVED,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    evidence=evidence,
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
                    evidence=evidence,
                    detail=f"product test execution could not start: {relative_path}: {type(exc).__name__}",
                )

            if completed.returncode != 0:
                return _result(
                    applicability="applicable-and-resolved",
                    classification=FAILED_TESTS,
                    accepted_specs=accepted_specs,
                    obligations=obligations,
                    evidence=evidence,
                    detail=f"product test failed: {relative_path}: exit {completed.returncode}",
                )

    return _result(
        applicability="applicable-and-resolved",
        classification=SUCCESS_APPLICABLE,
        accepted_specs=accepted_specs,
        obligations=obligations,
        evidence=evidence,
    )


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()

    if len(argv) > 2:
        print(f"product test error: unknown mode: {argv[2]}", file=sys.stderr)
        return 1

    result = run_product_tests(repo_root)
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))

    return 0 if result["classification"] in SUCCESS_CLASSES else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
