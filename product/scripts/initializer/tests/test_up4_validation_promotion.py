from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from initializer.upgrade_reanchoring import ProspectiveFrameworkReanchoring
from initializer.upgrade_reconciliation import StagedManagedReconciliation
from initializer.upgrade_resolution import FrameworkLineageEntry, GitObjectIdentity
from initializer.upgrade_validation_promotion import (
    promote_validated_candidate,
    serialize_up4_evidence,
    up4_evidence_fingerprint,
    validate_reanchored_candidate,
)


A = "1" * 40
B = "2" * 40


def lineage_entry(repo: str, oid: str) -> FrameworkLineageEntry:
    return FrameworkLineageEntry(
        framework_repository=repo,
        framework_revision=GitObjectIdentity("sha1", oid),
    )


def prepare_case(root: Path, validator_body: str = "exit 0\n"):
    target = root / "target"
    target.mkdir()
    (target / ".git").mkdir()
    (target / "product.txt").write_text("old\n", encoding="utf-8")

    stage_root = root / "repo-spec-upgrade-stage-case"
    transaction = stage_root / "transaction"
    repository = stage_root / "repository"
    transaction.mkdir(parents=True)
    repository.mkdir()

    (repository / ".git").mkdir()
    (repository / "product.txt").write_text("new\n", encoding="utf-8")
    scripts = repository / "scripts"
    scripts.mkdir()
    validator = scripts / "validate"
    validator.write_text("#!/usr/bin/env bash\nset -eu\n" + validator_body, encoding="utf-8")
    os.chmod(validator, 0o755)

    lineage = repository / "repo/initializer/framework-lineage.json"
    lineage.parent.mkdir(parents=True)
    lineage.write_text('{"schema_version":"1","entries":[]}\n', encoding="utf-8")

    staged = StagedManagedReconciliation(
        staging_root=str(stage_root),
        transaction_path=str(transaction),
        repository_path=str(repository),
        operations=(),
        conflicts=(),
        repository_content_digest="0" * 64,
    )

    prior = lineage_entry(str(root / "framework"), A)
    prospective = lineage_entry(str(root / "framework"), B)
    reanchoring = ProspectiveFrameworkReanchoring(
        repository_path=str(repository),
        lineage_path=str(lineage),
        prior_accepted_entries=(prior,),
        prospective_entry=prospective,
        serialized_lineage_sha256="f" * 64,
    )
    return target, stage_root, staged, reanchoring


class UP4ValidationPromotionTests(unittest.TestCase):
    def test_staged_repository_suite_passes_then_exact_candidate_promotes(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, stage_root, staged, reanchoring = prepare_case(root)

            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            self.assertTrue(validation.promotion_eligible)
            self.assertEqual((target / "product.txt").read_text(), "old\n")

            promotion = promote_validated_candidate(
                staged, reanchoring, validation, str(target)
            )
            self.assertEqual(promotion.promotion_outcome, "promoted")
            self.assertEqual(promotion.completion_status, "success")
            self.assertTrue(promotion.accepted)
            self.assertEqual(
                promotion.promoted_repository_content_digest,
                validation.repository_content_digest,
            )
            self.assertEqual((target / "product.txt").read_text(), "new\n")
            self.assertTrue((target / "repo/initializer/framework-lineage.json").is_file())
            self.assertFalse(stage_root.exists())

    def test_validation_failure_blocks_promotion_and_preserves_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(
                root, 'echo "broken" >&2\nexit 7\n'
            )

            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            self.assertFalse(validation.promotion_eligible)
            self.assertEqual(validation.returncode, 7)

            promotion = promote_validated_candidate(
                staged, reanchoring, validation, str(target)
            )
            self.assertEqual(promotion.promotion_outcome, "not-promoted")
            self.assertFalse(promotion.accepted)
            self.assertEqual((target / "product.txt").read_text(), "old\n")

    def test_validation_suite_may_not_mutate_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(
                root, 'printf "changed\\n" > product.txt\nexit 0\n'
            )

            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            self.assertFalse(validation.promotion_eligible)
            self.assertIn("mutated", validation.failure_reason or "")
            self.assertEqual((target / "product.txt").read_text(), "old\n")

    def test_failed_candidate_commit_restores_previous_target(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(root)
            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )

            def fault(point: str):
                if point == "after-target-backup":
                    raise OSError("simulated commit failure")

            promotion = promote_validated_candidate(
                staged,
                reanchoring,
                validation,
                str(target),
                fault_injector=fault,
            )
            self.assertEqual(promotion.promotion_outcome, "not-promoted")
            self.assertEqual((target / "product.txt").read_text(), "old\n")

    def test_post_commit_finalization_error_remains_promoted(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(root)
            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )

            def fault(point: str):
                if point == "after-candidate-commit":
                    raise OSError("simulated finalization failure")

            promotion = promote_validated_candidate(
                staged,
                reanchoring,
                validation,
                str(target),
                fault_injector=fault,
            )
            self.assertEqual(promotion.promotion_outcome, "promoted")
            self.assertEqual(
                promotion.completion_status,
                "promoted-with-finalization-error",
            )
            self.assertTrue(promotion.accepted)
            self.assertEqual((target / "product.txt").read_text(), "new\n")

    def test_terminal_evidence_is_deterministic_and_excludes_paths(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(root)
            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            promotion = promote_validated_candidate(
                staged, reanchoring, validation, str(target)
            )
            evidence = serialize_up4_evidence(validation, promotion).decode("utf-8")
            self.assertNotIn(str(root), evidence)
            self.assertEqual(
                up4_evidence_fingerprint(validation, promotion),
                up4_evidence_fingerprint(validation, promotion),
            )


if __name__ == "__main__":
    unittest.main()
