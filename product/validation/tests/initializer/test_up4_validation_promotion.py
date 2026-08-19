from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from initializer.upgrade_reanchoring import ProspectiveFrameworkReanchoring
from initializer.upgrade_reconciliation import (
    StagedManagedOperation,
    StagedManagedReconciliation,
)
from initializer.upgrade_resolution import (
    FrameworkLineageEntry,
    GitObjectIdentity,
    resolve_accepted_baseline,
    serialize_framework_lineage,
)
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


def git(repo: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    return p.stdout.strip()


def prepare_case(root: Path, validator_body: str = "exit 0\n"):
    target = root / "target"
    target.mkdir()
    git(target, "init", "-q")
    git(target, "config", "user.email", "target@example.invalid")
    git(target, "config", "user.name", "Target")

    (target / "product.txt").write_text("old\n", encoding="utf-8")
    scripts = target / "scripts"
    scripts.mkdir()
    validator = scripts / "validate"
    validator.write_text("#!/usr/bin/env bash\nset -eu\n" + validator_body, encoding="utf-8")
    os.chmod(validator, 0o755)

    prior = lineage_entry(str(root / "framework"), A)
    prospective = lineage_entry(str(root / "framework"), B)
    lineage = target / "repo/initializer/framework-lineage.json"
    lineage.parent.mkdir(parents=True)
    lineage.write_bytes(serialize_framework_lineage((prior,)))
    git(target, "add", "-A")
    git(target, "commit", "-qm", "accepted target")

    stage_root = root / "repo-spec-upgrade-stage-case"
    transaction = stage_root / "transaction"
    repository = stage_root / "repository"
    transaction.mkdir(parents=True)
    shutil.copytree(target, repository, symlinks=True)

    (repository / "product.txt").write_text("new\n", encoding="utf-8")
    staged_lineage = repository / "repo/initializer/framework-lineage.json"
    staged_lineage.write_bytes(serialize_framework_lineage((prior, prospective)))

    staged = StagedManagedReconciliation(
        staging_root=str(stage_root),
        transaction_path=str(transaction),
        repository_path=str(repository),
        operations=(
            StagedManagedOperation(
                material_key="product",
                classification="modified",
                baseline_path="product.txt",
                target_path="product.txt",
            ),
        ),
        conflicts=(),
        repository_content_digest="0" * 64,
    )
    reanchoring = ProspectiveFrameworkReanchoring(
        repository_path=str(repository),
        lineage_path=str(staged_lineage),
        prior_accepted_entries=(prior,),
        prospective_entry=prospective,
        serialized_lineage_sha256="f" * 64,
    )
    return target, stage_root, staged, reanchoring


def make_framework(root: Path) -> tuple[Path, str, str]:
    framework = root / "framework-real"
    framework.mkdir()
    git(framework, "init", "-q")
    git(framework, "config", "user.email", "framework@example.invalid")
    git(framework, "config", "user.name", "Framework")
    (framework / "product/scripts/initializer").mkdir(parents=True)
    (framework / "product/specs/product/level-1").mkdir(parents=True)
    (framework / "materials").mkdir()
    inventory = {
        "schema_version": "1",
        "entries": [
            {
                "material_key": "managed",
                "source_path": "materials/managed.txt",
                "role": "runtime-framework",
                "operation": "copy-verbatim",
                "source_type": "blob",
                "mode": "100644",
            }
        ],
    }
    output_inventory = {
        "spec_id": "product.initializer-output-inventory-v1",
        "status": "accepted",
        "schema_version": "1",
        "material_index": [
            {
                "material_key": "managed",
                "destination_path": "product.txt",
                "producer": "framework-installation",
                "operation": "copy-verbatim",
                "mode": "100644",
                "required": True,
                "role": "runtime-framework",
            }
        ],
    }
    (framework / "product/scripts/initializer/framework-inventory.json").write_text(
        json.dumps(inventory, indent=2) + "\n",
        encoding="utf-8",
    )
    (
        framework
        / "product/specs/product/level-1/initializer-output-inventory-v1.json"
    ).write_text(
        json.dumps(output_inventory, indent=2) + "\n",
        encoding="utf-8",
    )
    (framework / "materials/managed.txt").write_text("one\n", encoding="utf-8")
    git(framework, "add", "-A")
    git(framework, "commit", "-qm", "baseline framework")
    baseline = git(framework, "rev-parse", "HEAD")
    (framework / "materials/managed.txt").write_text("two\n", encoding="utf-8")
    git(framework, "add", "-A")
    git(framework, "commit", "-qm", "target framework")
    target_revision = git(framework, "rev-parse", "HEAD")
    return framework, baseline, target_revision


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


    def test_promoted_head_contains_accepted_lineage_for_next_baseline(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            framework, baseline_revision, target_revision = make_framework(root)

            target = root / "target-real"
            target.mkdir()
            git(target, "init", "-q")
            git(target, "config", "user.email", "target@example.invalid")
            git(target, "config", "user.name", "Target")
            (target / "product.txt").write_text("old\n", encoding="utf-8")
            (target / "user.txt").write_text("committed-user\n", encoding="utf-8")
            scripts = target / "scripts"
            scripts.mkdir()
            validator = scripts / "validate"
            validator.write_text("#!/usr/bin/env bash\nset -eu\nexit 0\n", encoding="utf-8")
            os.chmod(validator, 0o755)

            prior = lineage_entry(str(framework), baseline_revision)
            prospective = lineage_entry(str(framework), target_revision)
            lineage = target / "repo/initializer/framework-lineage.json"
            lineage.parent.mkdir(parents=True)
            lineage.write_bytes(serialize_framework_lineage((prior,)))
            git(target, "add", "-A")
            git(target, "commit", "-qm", "accepted target")
            old_head = git(target, "rev-parse", "HEAD")

            (target / "user.txt").write_text("local-user\n", encoding="utf-8")
            git(target, "add", "user.txt")

            stage_root = root / "repo-spec-upgrade-stage-real"
            transaction = stage_root / "transaction"
            repository = stage_root / "repository"
            transaction.mkdir(parents=True)
            shutil.copytree(target, repository, symlinks=True)
            (repository / "product.txt").write_text("new\n", encoding="utf-8")
            staged_lineage = repository / "repo/initializer/framework-lineage.json"
            staged_lineage.write_bytes(
                serialize_framework_lineage((prior, prospective))
            )

            staged = StagedManagedReconciliation(
                staging_root=str(stage_root),
                transaction_path=str(transaction),
                repository_path=str(repository),
                operations=(
                    StagedManagedOperation(
                        material_key="managed",
                        classification="modified",
                        baseline_path="product.txt",
                        target_path="product.txt",
                    ),
                ),
                conflicts=(),
                repository_content_digest="0" * 64,
            )
            reanchoring = ProspectiveFrameworkReanchoring(
                repository_path=str(repository),
                lineage_path=str(staged_lineage),
                prior_accepted_entries=(prior,),
                prospective_entry=prospective,
                serialized_lineage_sha256="f" * 64,
            )

            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            self.assertTrue(validation.promotion_eligible)
            self.assertNotEqual(validation.candidate_head, old_head)

            committed_names = {
                name for name in git(
                    repository, "show", "--name-only", "--format=", "HEAD"
                ).splitlines()
                if name
            }
            self.assertEqual(
                committed_names,
                {"product.txt", "repo/initializer/framework-lineage.json"},
            )
            self.assertEqual(git(repository, "show", "HEAD:user.txt"), "committed-user")
            self.assertIn("M  user.txt", git(repository, "status", "--short"))

            promotion = promote_validated_candidate(
                staged, reanchoring, validation, str(target)
            )
            self.assertTrue(promotion.accepted)
            self.assertEqual(git(target, "rev-parse", "HEAD"), validation.candidate_head)
            self.assertEqual(git(target, "show", "HEAD:user.txt"), "committed-user")
            self.assertIn("M  user.txt", git(target, "status", "--short"))

            committed_lineage = json.loads(
                git(
                    target,
                    "show",
                    "HEAD:repo/initializer/framework-lineage.json",
                )
            )
            self.assertEqual(
                committed_lineage["entries"][-1]["framework_revision"]["object_id"],
                target_revision,
            )

            resolved = resolve_accepted_baseline(str(target))
            self.assertEqual(resolved.baseline_source, "accepted-lineage")
            self.assertEqual(
                resolved.active_baseline.framework_revision.object_id,
                target_revision,
            )

    def test_promotion_refuses_index_only_change_after_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(root)
            repository = Path(staged.repository_path)

            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            self.assertTrue(validation.promotion_eligible)

            # Alter only index state after validation. HEAD and worktree bytes
            # remain unchanged, so the Git-status guard must block promotion.
            (repository / "index-only.txt").write_text(
                "index-only\n", encoding="utf-8"
            )
            git(repository, "add", "index-only.txt")
            (repository / "index-only.txt").unlink()

            self.assertEqual(
                git(repository, "rev-parse", "HEAD"),
                validation.candidate_head,
            )

            promotion = promote_validated_candidate(
                staged, reanchoring, validation, str(target)
            )
            self.assertEqual(promotion.promotion_outcome, "not-promoted")
            self.assertIn("Git status changed", promotion.failure_reason or "")
            self.assertEqual((target / "product.txt").read_text(), "old\n")

    def test_promotion_refuses_candidate_head_change_after_validation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            target, _stage_root, staged, reanchoring = prepare_case(root)
            repository = Path(staged.repository_path)

            validation = validate_reanchored_candidate(
                staged, reanchoring, str(target)
            )
            self.assertTrue(validation.promotion_eligible)

            git(repository, "commit", "--allow-empty", "-qm", "unexpected head")
            promotion = promote_validated_candidate(
                staged, reanchoring, validation, str(target)
            )
            self.assertEqual(promotion.promotion_outcome, "not-promoted")
            self.assertIn("HEAD changed", promotion.failure_reason or "")
            self.assertEqual((target / "product.txt").read_text(), "old\n")
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
            parsed = json.loads(evidence)
            self.assertEqual(
                len(parsed["validation"]["candidate_status_sha256"]), 64
            )
            self.assertEqual(
                up4_evidence_fingerprint(validation, promotion),
                up4_evidence_fingerprint(validation, promotion),
            )


if __name__ == "__main__":
    unittest.main()
