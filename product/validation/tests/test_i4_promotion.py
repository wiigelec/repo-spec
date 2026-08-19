from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from initializer.destination import (
    i4_recheck_destination_absent,
    promote_finalized_repository,
)
from initializer.models import GitObjectIdentity
from initializer.staging import (
    FinalizedValidationPair,
    build_validated_staging_state,
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

    def __init__(self, destination: str) -> None:
        self.destination = destination


def _workspace(root: Path, destination: Path):
    transaction = root / "transaction"
    repository = root / "repository"
    transaction.mkdir()
    repository.mkdir()
    (repository / "README.md").write_text("payload\n", encoding="utf-8")
    request = _Request(str(destination))
    return SimpleNamespace(
        root=root,
        transaction_path=transaction,
        repository_path=repository,
        validation_report_path=transaction / "validation-report.json",
        staging_state_path=transaction / "staging-state.json",
        execution_report_path=transaction / "execution-report.json",
        inputs=SimpleNamespace(
            request=request,
            source=SimpleNamespace(repository="/tmp/source", commit_id="b" * 40),
            destination=SimpleNamespace(destination=str(destination)),
        ),
    )


def _run() -> RepositoryValidationRun:
    _version, profile = load_validation_profile_v1()
    checks = tuple(
        RepositoryCheckResult(item.check_id, "passed")
        for item in profile
    )
    return RepositoryValidationRun(
        "v1", checks, "pass", "a" * 64, "c" * 64
    )


def _pair(workspace) -> FinalizedValidationPair:
    run = _run()
    report = run.report_dict()
    state = build_validated_staging_state(
        workspace,
        run,
        initializer_version="test",
        completed_stages=(
            "request-intake",
            "source-resolution",
            "destination-preflight",
            "staging-establishment",
            "framework-installation",
            "direction-evidence-installation",
            "workspace-seeding",
            "provenance-recording",
            "handoff-assembly",
            "git-initialization",
        ),
    )
    return FinalizedValidationPair(report, state)


class I4PromotionTests(unittest.TestCase):
    def test_absent_only_recheck_rejects_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "dest"
            destination.mkdir()
            with self.assertRaises(Exception):
                i4_recheck_destination_absent(destination)

    def test_success_uses_exactly_one_rename_and_removes_transaction_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "txn"
            root.mkdir()
            destination = parent / "dest"
            workspace = _workspace(root, destination)
            pair = _pair(workspace)
            calls = []

            def rename(source: Path, target: Path) -> None:
                calls.append((source, target))
                os.rename(source, target)

            result = promote_finalized_repository(
                workspace,
                pair,
                rename=rename,
            )
            self.assertEqual(result.promotion_outcome, "promoted")
            self.assertEqual(result.completion_status, "success")
            self.assertEqual(len(calls), 1)
            self.assertTrue((destination / "README.md").is_file())
            self.assertFalse(root.exists())

    def test_existing_destination_never_calls_rename(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "txn"
            root.mkdir()
            destination = parent / "dest"
            destination.mkdir()
            workspace = _workspace(root, destination)
            pair = _pair(workspace)
            calls = []

            def rename(source: Path, target: Path) -> None:
                calls.append((source, target))

            result = promote_finalized_repository(
                workspace,
                pair,
                rename=rename,
            )
            self.assertEqual(result.promotion_outcome, "not-promoted")
            self.assertEqual(calls, [])
            self.assertTrue(workspace.repository_path.exists())
            report = json.loads(
                workspace.execution_report_path.read_text(encoding="utf-8")
            )
            self.assertEqual(report["promotion_outcome"], "not-promoted")

    def test_rename_error_is_indeterminate_and_not_retried(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "txn"
            root.mkdir()
            destination = parent / "dest"
            workspace = _workspace(root, destination)
            pair = _pair(workspace)
            calls = []

            def rename(source: Path, target: Path) -> None:
                calls.append((source, target))
                raise OSError("injected")

            result = promote_finalized_repository(
                workspace,
                pair,
                rename=rename,
            )
            self.assertEqual(result.promotion_outcome, "indeterminate")
            self.assertEqual(result.completion_status, "failed")
            self.assertEqual(len(calls), 1)
            self.assertTrue(root.exists())
            state = json.loads(
                workspace.staging_state_path.read_text(encoding="utf-8")
            )
            report = json.loads(
                workspace.execution_report_path.read_text(encoding="utf-8")
            )
            self.assertEqual(state["promotion_outcome"], "indeterminate")
            self.assertEqual(report["promotion_outcome"], "indeterminate")

    def test_cleanup_failure_preserves_promoted_outcome(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "txn"
            root.mkdir()
            destination = parent / "dest"
            workspace = _workspace(root, destination)
            pair = _pair(workspace)

            def cleanup(path: Path) -> None:
                raise OSError("cleanup injected")

            result = promote_finalized_repository(
                workspace,
                pair,
                cleanup=cleanup,
            )
            self.assertEqual(result.promotion_outcome, "promoted")
            self.assertEqual(
                result.completion_status,
                "promoted-with-finalization-error",
            )
            self.assertTrue(destination.exists())
            self.assertTrue(root.exists())
            state = json.loads(
                workspace.staging_state_path.read_text(encoding="utf-8")
            )
            report = json.loads(
                workspace.execution_report_path.read_text(encoding="utf-8")
            )
            self.assertEqual(state["promotion_outcome"], "promoted")
            self.assertEqual(state["failed_stage"], "success-finalization")
            self.assertTrue(state["cleanup_failure"])
            self.assertEqual(report["promotion_outcome"], "promoted")
            self.assertEqual(
                report["completion_status"],
                "promoted-with-finalization-error",
            )

    def test_closed_gate_cannot_mutate_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            root = parent / "txn"
            root.mkdir()
            destination = parent / "dest"
            workspace = _workspace(root, destination)
            pair = _pair(workspace)
            bad_state = dict(pair.staging_state)
            bad_state["validation_overall_status"] = "fail"
            closed = FinalizedValidationPair(pair.validation_report, bad_state)
            with self.assertRaises(Exception):
                promote_finalized_repository(workspace, closed)
            self.assertFalse(destination.exists())
            self.assertTrue(workspace.repository_path.exists())


if __name__ == "__main__":
    unittest.main()
