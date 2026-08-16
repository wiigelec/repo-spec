from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from initializer.upgrade_reanchoring import (
    FrameworkReanchoringError,
    reanchor_staged_repository,
    reanchoring_evidence_fingerprint,
    serialize_reanchoring_evidence,
)
from initializer.upgrade_reconciliation import StagedManagedReconciliation
from initializer.upgrade_resolution import (
    FrameworkLineageEntry,
    GitObjectIdentity,
    LINEAGE_RELATIVE_PATH,
    parse_framework_lineage,
)


A = "1" * 40
B = "2" * 40
C = "3" * 40


def entry(repo: str, oid: str) -> FrameworkLineageEntry:
    return FrameworkLineageEntry(
        framework_repository=repo,
        framework_revision=GitObjectIdentity("sha1", oid),
    )


def make_resolution(
    target_repo: str,
    accepted: tuple[FrameworkLineageEntry, ...],
    source_repo: str,
    source_oid: str,
    *,
    endpoint_repo: str | None = None,
    endpoint_oid: str | None = None,
):
    return SimpleNamespace(
        baseline=SimpleNamespace(
            lineage=accepted,
            active_baseline=accepted[-1],
            request=SimpleNamespace(target_repository=target_repo),
        ),
        reconciliation_target=SimpleNamespace(
            repository=source_repo,
            commit_id=source_oid,
        ),
        target_endpoint=SimpleNamespace(
            repository=endpoint_repo or source_repo,
            revision=GitObjectIdentity("sha1", endpoint_oid or source_oid),
        ),
    )


def make_stage(root: Path, *, conflict: bool = False) -> StagedManagedReconciliation:
    repo = root / "repository"
    transaction = root / "transaction"
    repo.mkdir(parents=True)
    transaction.mkdir()
    return StagedManagedReconciliation(
        staging_root=str(root),
        transaction_path=str(transaction),
        repository_path=str(repo),
        operations=(),
        conflicts=(
            (SimpleNamespace(to_dict=lambda: {}),) if conflict else ()
        ),
        repository_content_digest="f" * 64,
    )


class UP3FrameworkReanchoringTests(unittest.TestCase):
    def test_first_reconciliation_materializes_final_form_prospective_lineage(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "framework"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            stage_root = root / "stage"
            stage = make_stage(stage_root)

            baseline = entry(str(source), A)
            resolution = make_resolution(
                str(target), (baseline,), str(source), B
            )

            result = reanchor_staged_repository(resolution, stage)
            lineage_path = Path(stage.repository_path) / LINEAGE_RELATIVE_PATH
            parsed = parse_framework_lineage(
                json.loads(lineage_path.read_text(encoding="utf-8"))
            )

            self.assertEqual(parsed, (baseline, entry(str(source), B)))
            self.assertEqual(result.prior_accepted_entries, (baseline,))
            self.assertEqual(result.prospective_entry, entry(str(source), B))
            self.assertFalse(result.canonical_evidence_dict()["accepted"])
            self.assertNotIn(
                result.repository_path,
                serialize_reanchoring_evidence(result).decode("utf-8"),
            )

    def test_subsequent_reconciliation_preserves_all_accepted_history_in_order(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "framework"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            stage = make_stage(root / "stage")

            accepted = (entry(str(source), A), entry(str(source), B))
            lineage_path = Path(stage.repository_path) / LINEAGE_RELATIVE_PATH
            lineage_path.parent.mkdir(parents=True, exist_ok=True)
            from initializer.upgrade_resolution import serialize_framework_lineage
            lineage_path.write_bytes(serialize_framework_lineage(accepted))

            resolution = make_resolution(
                str(target), accepted, str(source), C
            )
            result = reanchor_staged_repository(resolution, stage)
            parsed = parse_framework_lineage(
                json.loads(lineage_path.read_text(encoding="utf-8"))
            )

            self.assertEqual(parsed, accepted + (entry(str(source), C),))
            self.assertEqual(result.prior_accepted_entries, accepted)

    def test_reanchoring_refuses_conflicted_up2_state(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "framework"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            stage = make_stage(root / "stage", conflict=True)
            resolution = make_resolution(
                str(target), (entry(str(source), A),), str(source), B
            )
            with self.assertRaises(FrameworkReanchoringError):
                reanchor_staged_repository(resolution, stage)

    def test_reanchoring_fails_closed_on_target_identity_mismatch(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "framework"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            stage = make_stage(root / "stage")
            resolution = make_resolution(
                str(target),
                (entry(str(source), A),),
                str(source),
                B,
                endpoint_oid=C,
            )
            with self.assertRaises(FrameworkReanchoringError):
                reanchor_staged_repository(resolution, stage)

    def test_existing_staged_lineage_must_equal_resolved_accepted_history(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "framework"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            stage = make_stage(root / "stage")

            lineage_path = Path(stage.repository_path) / LINEAGE_RELATIVE_PATH
            lineage_path.parent.mkdir(parents=True, exist_ok=True)
            from initializer.upgrade_resolution import serialize_framework_lineage
            lineage_path.write_bytes(
                serialize_framework_lineage((entry(str(source), C),))
            )

            resolution = make_resolution(
                str(target), (entry(str(source), A),), str(source), B
            )
            with self.assertRaises(FrameworkReanchoringError):
                reanchor_staged_repository(resolution, stage)

    def test_equivalent_reanchoring_evidence_is_deterministic_across_staging_roots(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "framework"
            source.mkdir()
            target = root / "target"
            target.mkdir()
            accepted = (entry(str(source), A),)
            resolution = make_resolution(
                str(target), accepted, str(source), B
            )

            first = reanchor_staged_repository(
                resolution, make_stage(root / "stage-a")
            )
            second = reanchor_staged_repository(
                resolution, make_stage(root / "stage-b")
            )

            self.assertNotEqual(first.repository_path, second.repository_path)
            self.assertEqual(
                first.canonical_evidence_dict(),
                second.canonical_evidence_dict(),
            )
            self.assertEqual(
                reanchoring_evidence_fingerprint(first),
                reanchoring_evidence_fingerprint(second),
            )


if __name__ == "__main__":
    unittest.main()
