from __future__ import annotations

import json
import unittest

from initializer.validation import (
    INVALID_STRUCTURE,
    RepositoryCheckResult,
    RepositoryValidationRun,
    ValidationError,
    load_validation_profile_v1,
    validate_validation_report_v1,
)


class I4RepositoryValidationContractTests(unittest.TestCase):
    def test_profile_is_complete_unique_and_two_phase_ordered(self) -> None:
        version, checks = load_validation_profile_v1()
        self.assertEqual(version, "v1")
        ids = [item.check_id for item in checks]
        orders = [item.order for item in checks]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(len(orders), len(set(orders)))
        self.assertEqual(orders, sorted(orders))
        self.assertTrue(all(order <= 70 or order >= 80 for order in orders))
        self.assertEqual(
            ids,
            [
                "request.schema",
                "request.canonicalization",
                "request.authority-propagation",
                "source.repository-local",
                "source.object-format",
                "source.revision-commit",
                "source.objects-complete",
                "material-manifest.schema",
                "material-manifest.source-paths",
                "material-manifest.key-coverage",
                "output.inventory-complete",
                "output.no-undeclared-paths",
                "output.level-readmes",
                "output.copied-bytes-match",
                "output.direction-evidence-match",
                "output.generated-records-valid",
                "output.generated-templates-match",
                "output.repository-digest-match",
                "provenance.consistent",
                "handoff.consistent",
                "git.initial-branch",
                "git.root-commit-count",
                "git.author-identity",
                "git.commit-message",
                "git.worktree-clean",
                "git.remote-count",
            ],
        )

    def test_report_serialization_is_deterministic_and_field_ordered(self) -> None:
        _version, profile = load_validation_profile_v1()
        checks = tuple(
            RepositoryCheckResult(item.check_id, "passed", evidence={"order": item.order})
            for item in profile
        )
        run = RepositoryValidationRun(
            "v1", checks, "pass", "a" * 64, "b" * 64
        )
        first = run.report_bytes()
        self.assertEqual(first, run.report_bytes())
        self.assertTrue(first.endswith(b"\n"))
        raw = json.loads(first)
        self.assertEqual(
            tuple(raw),
            (
                "schema_version",
                "report_version",
                "profile_version",
                "request_fingerprint",
                "repository_content_digest",
                "overall_status",
                "checks",
            ),
        )
        validate_validation_report_v1(
            raw,
            expected_request_fingerprint="a" * 64,
            expected_repository_content_digest="b" * 64,
        )

    def test_required_failure_forces_fail_and_invalid_pass_is_rejected(self) -> None:
        _version, profile = load_validation_profile_v1()
        results = []
        for index, item in enumerate(profile):
            if index == 0:
                results.append(
                    RepositoryCheckResult(
                        item.check_id,
                        "failed",
                        item.failure_codes[0],
                        "negative vector",
                    )
                )
            else:
                results.append(RepositoryCheckResult(item.check_id, "passed"))
        run = RepositoryValidationRun(
            "v1", tuple(results), "fail", "c" * 64, "d" * 64
        )
        raw = run.report_dict()
        validate_validation_report_v1(
            raw,
            expected_request_fingerprint="c" * 64,
            expected_repository_content_digest="d" * 64,
        )
        raw["overall_status"] = "pass"
        with self.assertRaises(ValidationError) as raised:
            validate_validation_report_v1(
                raw,
                expected_request_fingerprint="c" * 64,
                expected_repository_content_digest="d" * 64,
            )
        self.assertEqual(raised.exception.category, INVALID_STRUCTURE)

    def test_report_rejects_unknown_code_duplicate_and_bad_order(self) -> None:
        _version, profile = load_validation_profile_v1()
        checks = [
            RepositoryCheckResult(item.check_id, "passed").to_dict()
            for item in profile
        ]
        report = {
            "schema_version": "1",
            "report_version": "1",
            "profile_version": "v1",
            "request_fingerprint": "e" * 64,
            "repository_content_digest": "f" * 64,
            "overall_status": "pass",
            "checks": checks,
        }

        bad_code = json.loads(json.dumps(report))
        bad_code["checks"][0]["status"] = "failed"
        bad_code["checks"][0]["failure_code"] = "not-declared"
        bad_code["overall_status"] = "fail"
        with self.assertRaises(ValidationError):
            validate_validation_report_v1(
                bad_code,
                expected_request_fingerprint="e" * 64,
                expected_repository_content_digest="f" * 64,
            )

        duplicate = json.loads(json.dumps(report))
        duplicate["checks"][1]["check_id"] = duplicate["checks"][0]["check_id"]
        with self.assertRaises(ValidationError):
            validate_validation_report_v1(
                duplicate,
                expected_request_fingerprint="e" * 64,
                expected_repository_content_digest="f" * 64,
            )

        reordered = json.loads(json.dumps(report))
        reordered["checks"][0], reordered["checks"][1] = reordered["checks"][1], reordered["checks"][0]
        with self.assertRaises(ValidationError):
            validate_validation_report_v1(
                reordered,
                expected_request_fingerprint="e" * 64,
                expected_repository_content_digest="f" * 64,
            )


if __name__ == "__main__":
    unittest.main()
