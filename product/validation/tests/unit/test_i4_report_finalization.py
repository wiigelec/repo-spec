from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from initializer.models import GitObjectIdentity
from initializer.staging import (
    FinalizedValidationPair,
    ReportFinalizationError,
    build_execution_report_v1,
    build_validated_staging_state,
    execution_report_bytes_v1,
    finalize_validation_records,
    staging_state_bytes_v1,
    validate_execution_report_v1,
    validate_staging_state_v1,
)
from initializer.validation import (
    RepositoryCheckResult,
    RepositoryValidationRun,
    load_validation_profile_v1,
)

class _Request:
    request_fingerprint = "a" * 64
    source_revision = GitObjectIdentity("sha1", "b" * 40)
    source_repository = "/tmp/source"
    destination = "/tmp/destination"

# validation-metadata: {"role": "helper"}
def _workspace(root: Path):
    transaction = root / "transaction"
    repository = root / "repository"
    transaction.mkdir()
    repository.mkdir()
    return SimpleNamespace(
        root=root,
        transaction_path=transaction,
        repository_path=repository,
        validation_report_path=transaction / "validation-report.json",
        staging_state_path=transaction / "staging-state.json",
        execution_report_path=transaction / "execution-report.json",
        inputs=SimpleNamespace(
            request=_Request(),
            source=SimpleNamespace(repository="/tmp/source", commit_id="b" * 40),
            destination=SimpleNamespace(destination="/tmp/destination"),
        ),
    )

# validation-metadata: {"role": "helper"}
def _validation_run(status: str = "pass") -> RepositoryValidationRun:
    _version, profile = load_validation_profile_v1()
    results = []
    for index, item in enumerate(profile):
        if status == "fail" and index == 0:
            results.append(
                RepositoryCheckResult(
                    item.check_id, "failed", item.failure_codes[0], "negative"
                )
            )
        else:
            results.append(RepositoryCheckResult(item.check_id, "passed"))
    return RepositoryValidationRun(
        "v1", tuple(results), status, "a" * 64, "c" * 64
    )

class I4ReportFinalizationTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_staging_state_is_closed_ordered_and_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = _workspace(Path(directory))
            state = build_validated_staging_state(
                workspace,
                _validation_run(),
                initializer_version="test",
                completed_stages=("request-intake", "git-initialization"),
            )
            validate_staging_state_v1(state)
            first = staging_state_bytes_v1(state)
            self.assertEqual(first, staging_state_bytes_v1(state))
            self.assertTrue(first.endswith(b"\n"))

    # validation-metadata: {"role": "helper"}
    def test_report_is_written_before_completed_staging_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = _workspace(Path(directory))
            observed = {}
            # validation-metadata: {"role": "helper"}
            def injector(point: str) -> None:
                observed[point] = (
                    workspace.validation_report_path.exists(),
                    workspace.staging_state_path.exists(),
                )
            pair = finalize_validation_records(
                workspace,
                _validation_run(),
                initializer_version="test",
                completed_stages=("request-intake", "git-initialization"),
                fault_injector=injector,
            )
            self.assertTrue(pair.promotion_gate_open())
            self.assertEqual(observed["before-validation-report-write"], (False, False))
            self.assertEqual(observed["after-validation-report-write"], (True, False))
            self.assertEqual(observed["after-staging-state-write"], (True, True))

    # validation-metadata: {"role": "helper"}
    def test_each_fault_boundary_raises_and_never_returns_gate(self) -> None:
        points = (
            "after-in-memory-construction",
            "after-staging-state-validation",
            "after-validation-report-validation",
            "before-validation-report-write",
            "after-validation-report-write",
            "before-staging-state-write",
            "after-staging-state-write",
            "after-durable-consistency-verification",
        )
        for target in points:
            with self.subTest(target=target), tempfile.TemporaryDirectory() as directory:
                workspace = _workspace(Path(directory))
                # validation-metadata: {"role": "helper"}
                def injector(point: str) -> None:
                    if point == target:
                        raise ReportFinalizationError("injected-fault", target)
                with self.assertRaises(ReportFinalizationError):
                    finalize_validation_records(
                        workspace,
                        _validation_run(),
                        initializer_version="test",
                        completed_stages=("request-intake", "git-initialization"),
                        fault_injector=injector,
                    )
                if workspace.staging_state_path.exists():
                    state = json.loads(
                        workspace.staging_state_path.read_text(encoding="utf-8")
                    )
                    if state.get("validation_completed") is True:
                        self.assertTrue(workspace.validation_report_path.exists())

    # validation-metadata: {"role": "helper"}
    def test_failed_validation_pair_does_not_open_promotion_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = _workspace(Path(directory))
            pair = finalize_validation_records(
                workspace,
                _validation_run("fail"),
                initializer_version="test",
                completed_stages=("request-intake", "git-initialization"),
            )
            self.assertIsInstance(pair, FinalizedValidationPair)
            self.assertFalse(pair.promotion_gate_open())

    # validation-metadata: {"role": "helper"}
    def test_execution_report_pre_promotion_failure_shape(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = _workspace(Path(directory))
            report = build_execution_report_v1(
                workspace,
                promotion_outcome="not-promoted",
                completion_status="failed",
                stage_status={
                    "request-intake": "completed",
                    "repository-validation": "failed",
                    "promotion": "deferred",
                    "success-finalization": "deferred",
                },
                stage_errors={
                    "repository-validation": [
                        "transaction/validation-report.json: overall_status=fail"
                    ]
                },
            )
            validate_execution_report_v1(report)
            first = execution_report_bytes_v1(report)
            self.assertEqual(first, execution_report_bytes_v1(report))
            self.assertTrue(first.endswith(b"\n"))

    # validation-metadata: {"role": "helper"}
    def test_execution_report_rejects_bad_terminal_combination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = _workspace(Path(directory))
            with self.assertRaises(Exception):
                build_execution_report_v1(
                    workspace,
                    promotion_outcome="promoted",
                    completion_status="failed",
                    stage_status={"success-finalization": "failed"},
                    stage_errors={"success-finalization": ["cleanup failed"]},
                )

if __name__ == "__main__":
    unittest.main()
