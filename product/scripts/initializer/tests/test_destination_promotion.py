from __future__ import annotations

import os
import shutil
import stat
import tempfile
import unittest
from pathlib import Path

from initializer.models import (
    DestinationPreflight,
    DestinationState,
    PreflightDecision,
    PromotionPlan,
    PromotionResult,
    TransactionPhase,
)
from initializer.destination import (
    DestinationError,
    resolve_and_normalize,
    paths_are_same,
    path_contains_other,
    paths_are_aliased,
    check_path_conflicts,
    classify_destination,
    check_same_filesystem,
    destination_preflight,
    build_promotion_plan,
    validate_staging_result_complete,
)
from initializer.promotion import (
    BACKUP_PREFIX,
    PromotionError,
    prepare_destination,
    restore_destination,
    promote,
    promote_with_validation,
    _rename,
    _backup_name,
)


def _make_staging_dir(base: Path, name: str = "staging") -> Path:
    staging = base / name
    staging.mkdir(parents=True, exist_ok=True)
    (staging / "file.txt").write_text("content")
    (staging / "subdir").mkdir()
    (staging / "subdir" / "nested.txt").write_text("nested")
    return staging


class DestinationPreflightModelTests(unittest.TestCase):
    def test_absorbed_preflight(self):
        pf = DestinationPreflight(
            staging_path="/tmp/stage",
            destination_path="/tmp/dest",
            destination_state=DestinationState.absent,
            same_filesystem=True,
            aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.allowed,
        )
        self.assertEqual(pf.staging_path, "/tmp/stage")
        self.assertEqual(pf.destination_path, "/tmp/dest")
        self.assertEqual(pf.destination_state, DestinationState.absent)
        self.assertEqual(pf.decision, PreflightDecision.allowed)
        self.assertTrue(pf.same_filesystem)
        self.assertFalse(pf.aliased)

    def test_rejected_preflight(self):
        pf = DestinationPreflight(
            staging_path="/tmp/stage",
            destination_path="/tmp/dest",
            destination_state=DestinationState.nonempty_directory,
            same_filesystem=True,
            aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.rejected,
            rejection_reason="destination is a nonempty directory",
        )
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertEqual(pf.rejection_reason, "destination is a nonempty directory")

    def test_to_dict(self):
        pf = DestinationPreflight(
            staging_path="/s", destination_path="/d",
            destination_state=DestinationState.absent,
            same_filesystem=True, aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.allowed,
        )
        d = pf.to_dict()
        self.assertEqual(d["destination_classification"], DestinationState.absent)
        self.assertEqual(d["decision"], PreflightDecision.allowed)
        self.assertNotIn("rejection_reason", d)

    def test_to_dict_with_rejection(self):
        pf = DestinationPreflight(
            staging_path="/s", destination_path="/d",
            destination_state=DestinationState.nonempty_directory,
            same_filesystem=True, aliased=False,
            staging_inside_destination=False,
            destination_inside_staging=False,
            decision=PreflightDecision.rejected,
            rejection_reason="nonempty",
        )
        d = pf.to_dict()
        self.assertIn("rejection_reason", d)
        self.assertEqual(d["rejection_reason"], "nonempty")

    def test_equality(self):
        a = DestinationPreflight("/s", "/d", DestinationState.absent, True, False, False, False, PreflightDecision.allowed)
        b = DestinationPreflight("/s", "/d", DestinationState.absent, True, False, False, False, PreflightDecision.allowed)
        c = DestinationPreflight("/s", "/d", DestinationState.absent, True, False, False, False, PreflightDecision.rejected, "bad")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(hash(a), hash(b))


class PromotionPlanModelTests(unittest.TestCase):
    def test_absent_plan(self):
        plan = PromotionPlan(
            staging_path="/tmp/stage",
            destination_path="/tmp/dest",
            destination_state=DestinationState.absent,
            requires_preparation=False,
            same_filesystem=True,
        )
        self.assertFalse(plan.requires_preparation)
        self.assertIsNone(plan.backup_path)

    def test_empty_dir_plan(self):
        plan = PromotionPlan(
            staging_path="/tmp/stage",
            destination_path="/tmp/dest",
            destination_state=DestinationState.empty_directory,
            requires_preparation=True,
            same_filesystem=True,
        )
        self.assertTrue(plan.requires_preparation)

    def test_equality(self):
        a = PromotionPlan("/s", "/d", DestinationState.absent, False, True)
        b = PromotionPlan("/s", "/d", DestinationState.absent, False, True)
        c = PromotionPlan("/s", "/d", DestinationState.empty_directory, True, True)
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertEqual(hash(a), hash(b))


class PromotionResultModelTests(unittest.TestCase):
    def test_success_result(self):
        r = PromotionResult(
            status="success",
            transaction_state=TransactionPhase.committed,
            destination_classification=DestinationState.absent,
            staging_path="/s",
            requested_destination="/d",
            committed_destination="/d",
        )
        self.assertEqual(r.status, "success")
        d = r.to_dict()
        self.assertEqual(d["status"], "success")
        self.assertEqual(d["transaction_state"], TransactionPhase.committed)
        self.assertIn("committed_destination", d)

    def test_failed_result(self):
        r = PromotionResult(
            status="failed",
            transaction_state=TransactionPhase.preflight,
            destination_classification=DestinationState.nonempty_directory,
            staging_path="/s",
            requested_destination="/d",
            failure_reason="nonempty dir",
        )
        self.assertEqual(r.status, "failed")
        d = r.to_dict()
        self.assertNotIn("committed_destination", d)
        self.assertIn("failure_reason", d)

    def test_equality(self):
        a = PromotionResult("success", "committed", "absent", "/s", "/d", committed_destination="/d")
        b = PromotionResult("success", "committed", "absent", "/s", "/d", committed_destination="/d")
        c = PromotionResult("failed", "preflight", "nonempty_directory", "/s", "/d", failure_reason="bad")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class PathSafetyTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_resolve_and_normalize(self):
        p = self.base / "sub" / ".." / "target"
        resolved = resolve_and_normalize(str(p))
        self.assertEqual(resolved, (self.base / "target").resolve())

    def test_paths_are_same(self):
        self.assertTrue(paths_are_same(self.base, self.base))
        self.assertFalse(paths_are_same(self.base, self.base.parent))

    def test_path_contains_other(self):
        child = self.base / "sub"
        child.mkdir()
        self.assertTrue(path_contains_other(self.base, child))
        self.assertFalse(path_contains_other(child, self.base))

    def test_paths_are_aliased(self):
        staging = self.base / "stage"
        dest = self.base / "dest"
        staging.mkdir()
        dest.symlink_to(staging)
        self.assertTrue(paths_are_aliased(staging, dest))

    def test_paths_are_aliased_identical(self):
        staging = self.base / "stage"
        staging.mkdir()
        self.assertTrue(paths_are_aliased(staging, staging))

    def test_paths_not_aliased(self):
        staging = self.base / "stage"
        dest = self.base / "dest"
        staging.mkdir()
        dest.mkdir()
        self.assertFalse(paths_are_aliased(staging, dest))

    def test_check_path_conflicts_no_conflict(self):
        s = self.base / "stage"
        d = self.base / "dest"
        s.mkdir()
        d.mkdir()
        aliased, s_in_d, d_in_s = check_path_conflicts(s, d)
        self.assertFalse(aliased)
        self.assertFalse(s_in_d)
        self.assertFalse(d_in_s)

    def test_check_path_conflicts_nested_staging_in_dest(self):
        d = self.base / "dest"
        s = d / "stage"
        d.mkdir()
        s.mkdir()
        aliased, s_in_d, d_in_s = check_path_conflicts(s, d)
        self.assertFalse(aliased)
        self.assertTrue(s_in_d)
        self.assertFalse(d_in_s)

    def test_check_path_conflicts_nested_dest_in_staging(self):
        s = self.base / "stage"
        d = s / "dest"
        s.mkdir()
        d.mkdir()
        aliased, s_in_d, d_in_s = check_path_conflicts(s, d)
        self.assertFalse(aliased)
        self.assertFalse(s_in_d)
        self.assertTrue(d_in_s)

    def test_check_path_conflicts_aliased_via_symlink(self):
        s = self.base / "stage"
        d = self.base / "dest_link"
        s.mkdir()
        d.symlink_to(s)
        aliased, s_in_d, d_in_s = check_path_conflicts(s, d)
        self.assertTrue(aliased)


class ClassifyDestinationTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_absent(self):
        p = self.base / "nonexistent"
        self.assertEqual(classify_destination(p), DestinationState.absent)

    def test_empty_directory(self):
        p = self.base / "emptydir"
        p.mkdir()
        self.assertEqual(classify_destination(p), DestinationState.empty_directory)

    def test_nonempty_directory(self):
        p = self.base / "nondir"
        p.mkdir()
        (p / "file.txt").write_text("x")
        self.assertEqual(classify_destination(p), DestinationState.nonempty_directory)

    def test_regular_file(self):
        p = self.base / "file.txt"
        p.write_text("content")
        self.assertEqual(classify_destination(p), DestinationState.regular_file)

    def test_symlink(self):
        target = self.base / "target"
        target.write_text("target")
        link = self.base / "link"
        link.symlink_to("target")
        self.assertEqual(classify_destination(link), DestinationState.symlink)

    def test_unsupported_fifo(self):
        fifo = self.base / "myfifo"
        os.mkfifo(str(fifo))
        self.assertEqual(classify_destination(fifo), DestinationState.unsupported)

    def test_inaccessible_parent_missing(self):
        p = self.base / "missing" / "deep"
        self.assertEqual(classify_destination(p), DestinationState.inaccessible)


class SameFilesystemTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_same_fs(self):
        a = self.base / "a"
        b = self.base / "b"
        a.mkdir()
        b.mkdir()
        self.assertTrue(check_same_filesystem(a, b))

    def test_self_is_same_fs(self):
        self.assertTrue(check_same_filesystem(self.base, self.base))


class DestinationPreflightFunctionTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_allows_absent_destination(self):
        dest = self.base / "new_dest"
        pf = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.allowed)
        self.assertEqual(pf.destination_state, DestinationState.absent)
        self.assertTrue(pf.same_filesystem)

    def test_allows_empty_directory(self):
        dest = self.base / "empty_dest"
        dest.mkdir()
        pf = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.allowed)
        self.assertEqual(pf.destination_state, DestinationState.empty_directory)

    def test_rejects_nonempty_directory(self):
        dest = self.base / "nonempty"
        dest.mkdir()
        (dest / "file.txt").write_text("x")
        pf = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("nonempty", (pf.rejection_reason or "").lower())

    def test_rejects_regular_file(self):
        dest = self.base / "file.txt"
        dest.write_text("content")
        pf = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("regular file", (pf.rejection_reason or "").lower())

    def test_rejects_symlink(self):
        target = self.base / "sym_target"
        target.mkdir()
        dest = self.base / "link_to_target"
        dest.symlink_to(target)
        pf = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("symbolic link", (pf.rejection_reason or "").lower())

    def test_rejects_same_path(self):
        pf = destination_preflight(str(self.staging), str(self.staging))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("same path", (pf.rejection_reason or "").lower())

    def test_rejects_staging_inside_destination(self):
        dest = self.base / "wrapper"
        staging_inside = dest / "staging"
        dest.mkdir()
        staging_inside.mkdir()
        (staging_inside / "f.txt").write_text("x")
        pf = destination_preflight(str(staging_inside), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("inside the requested destination", (pf.rejection_reason or "").lower())

    def test_rejects_destination_inside_staging(self):
        dest_inside = self.staging / "inner_dest"
        dest_inside.mkdir()
        pf = destination_preflight(str(self.staging), str(dest_inside))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("inside the staging workspace", (pf.rejection_reason or "").lower())

    def test_rejects_missing_staging(self):
        pf = destination_preflight(str(self.base / "no_such_staging"), str(self.base / "dest"))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("does not exist", (pf.rejection_reason or "").lower())

    def test_rejects_staging_not_dir(self):
        f = self.base / "not_a_dir.txt"
        f.write_text("x")
        pf = destination_preflight(str(f), str(self.base / "dest"))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertIn("not a directory", (pf.rejection_reason or "").lower())

    def test_rejects_unsupported_fifo(self):
        dest = self.base / "myfifo"
        os.mkfifo(str(dest))
        pf = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf.decision, PreflightDecision.rejected)
        self.assertEqual(pf.destination_state, DestinationState.unsupported)

    def test_deterministic_preflight(self):
        dest = self.base / "det_dest"
        pf1 = destination_preflight(str(self.staging), str(dest))
        pf2 = destination_preflight(str(self.staging), str(dest))
        self.assertEqual(pf1, pf2)


class BuildPromotionPlanTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_absent_destination(self):
        dest = self.base / "new_dest"
        pf = destination_preflight(str(self.staging), str(dest))
        plan = build_promotion_plan(pf)
        self.assertEqual(plan.destination_state, DestinationState.absent)
        self.assertFalse(plan.requires_preparation)
        self.assertTrue(plan.same_filesystem)

    def test_empty_directory(self):
        dest = self.base / "empty"
        dest.mkdir()
        pf = destination_preflight(str(self.staging), str(dest))
        plan = build_promotion_plan(pf)
        self.assertEqual(plan.destination_state, DestinationState.empty_directory)
        self.assertTrue(plan.requires_preparation)

    def test_rejected_preflight_raises(self):
        dest = self.base / "file.txt"
        dest.write_text("x")
        pf = destination_preflight(str(self.staging), str(dest))
        with self.assertRaises(DestinationError):
            build_promotion_plan(pf)


class ValidateStagingResultTests(unittest.TestCase):
    def test_complete_result_no_rejected(self):
        validate_staging_result_complete(
            installed=[{"path": "file.txt"}],
            rejected=[],
        )

    def test_rejected_artifacts_raises(self):
        with self.assertRaises(DestinationError):
            validate_staging_result_complete(
                installed=[{"path": "good.txt"}],
                rejected=[{"path": "bad.txt", "reason": "error"}],
            )


class PrepareDestinationTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_absent_prepares_parent(self):
        dest = self.base / "sub" / "new_dest"
        plan = PromotionPlan(
            staging_path=str(self.staging),
            destination_path=str(dest),
            destination_state=DestinationState.absent,
            requires_preparation=False,
            same_filesystem=True,
        )
        backup = prepare_destination(plan)
        self.assertIsNone(backup)
        self.assertTrue(dest.parent.exists())

    def test_empty_dir_backup_created(self):
        dest = self.base / "empty"
        dest.mkdir()
        plan = PromotionPlan(
            staging_path=str(self.staging),
            destination_path=str(dest),
            destination_state=DestinationState.empty_directory,
            requires_preparation=True,
            same_filesystem=True,
        )
        backup = prepare_destination(plan)
        self.assertIsNotNone(backup)
        self.assertFalse(dest.exists())
        backup_p = Path(backup)
        self.assertTrue(backup_p.exists())


class RestoreDestinationTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_restore_empty_dir(self):
        dest = self.base / "empty"
        dest.mkdir()
        plan = PromotionPlan(
            staging_path=str(self.staging),
            destination_path=str(dest),
            destination_state=DestinationState.empty_directory,
            requires_preparation=True,
            same_filesystem=True,
        )
        backup = prepare_destination(plan)
        self.assertIsNotNone(backup)
        self.assertFalse(dest.exists())

        restored = restore_destination(plan, backup)
        self.assertTrue(restored)
        self.assertTrue(dest.exists())

    def test_no_backup_no_restore(self):
        plan = PromotionPlan(
            staging_path="", destination_path="",
            destination_state=DestinationState.absent,
            requires_preparation=False, same_filesystem=True,
        )
        self.assertFalse(restore_destination(plan, None))

    def test_restore_noop_when_dest_exists(self):
        dest = self.base / "empty"
        dest.mkdir()
        backup = self.base / "backup"
        backup.mkdir()
        plan = PromotionPlan(
            staging_path=str(self.staging),
            destination_path=str(dest),
            destination_state=DestinationState.empty_directory,
            requires_preparation=True,
            same_filesystem=True,
        )
        restored = restore_destination(plan, str(backup))
        self.assertFalse(restored)


class PromoteFunctionTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_promote_to_absent_success(self):
        dest = self.base / "new_repo"
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "success")
        self.assertEqual(result.transaction_state, TransactionPhase.committed)
        self.assertTrue(dest.exists())
        self.assertTrue((dest / "file.txt").exists())
        self.assertFalse(self.staging.exists())

    def test_promote_to_empty_dir_success(self):
        dest = self.base / "empty_target"
        dest.mkdir()
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "success")
        self.assertEqual(result.transaction_state, TransactionPhase.committed)
        self.assertTrue(dest.exists())
        self.assertTrue((dest / "file.txt").exists())
        self.assertFalse(self.staging.exists())

    def test_promote_rejects_nonempty(self):
        dest = self.base / "nonempty"
        dest.mkdir()
        (dest / "existing.txt").write_text("existing")
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.transaction_state, TransactionPhase.preflight)
        self.assertTrue(dest.exists())
        self.assertTrue((dest / "existing.txt").exists())
        self.assertTrue(self.staging.exists())

    def test_promote_rejects_regular_file(self):
        dest = self.base / "file.txt"
        dest.write_text("content")
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "failed")
        self.assertTrue(self.staging.exists())

    def test_promote_rejects_symlink(self):
        target = self.base / "target_dir"
        target.mkdir()
        dest = self.base / "link"
        dest.symlink_to(target)
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "failed")
        self.assertTrue(self.staging.exists())

    def test_promote_rejects_same_path(self):
        result = promote(str(self.staging), str(self.staging))
        self.assertEqual(result.status, "failed")
        self.assertTrue(self.staging.exists())

    def test_promote_preserves_staging_on_preflight_failure(self):
        dest = self.base / "file.txt"
        dest.write_text("content")
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "failed")
        self.assertTrue(self.staging.exists())

    def test_promote_deterministic_output(self):
        dest = self.base / "det1"
        r1 = promote(str(self.staging), str(dest))
        self.staging = _make_staging_dir(self.base, "staging2")
        dest2 = self.base / "det2"
        r2 = promote(str(self.staging), str(dest2))
        self.assertEqual(r1.status, r2.status)
        self.assertEqual(r1.destination_classification, r2.destination_classification)


class PromoteWithValidationTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_rejected_artifacts_fails(self):
        dest = self.base / "new_repo"
        result = promote_with_validation(
            str(self.staging), str(dest),
            installed=[{"path": "f.txt"}],
            rejected=[{"path": "bad.txt", "reason": "error"}],
        )
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.transaction_state, TransactionPhase.preflight)
        self.assertTrue(self.staging.exists())

    def test_no_rejected_succeeds(self):
        dest = self.base / "new_repo"
        result = promote_with_validation(
            str(self.staging), str(dest),
            installed=[{"path": "f.txt"}],
            rejected=[],
        )
        self.assertEqual(result.status, "success")
        self.assertTrue(dest.exists())


class NoGitNoPlatformTests(unittest.TestCase):
    def setUp(self):
        self.base = Path(tempfile.mkdtemp())
        self.staging = _make_staging_dir(self.base, "staging")

    def tearDown(self):
        shutil.rmtree(self.base, ignore_errors=True)

    def test_promote_performs_no_git_command(self):
        import subprocess
        dest = self.base / "new_repo"
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "success")
        self.assertFalse((dest / ".git").exists())

    def test_promote_no_network_access(self):
        dest = self.base / "new_repo2"
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "success")

    def test_promote_no_platform_profile(self):
        dest = self.base / "new_repo3"
        result = promote(str(self.staging), str(dest))
        self.assertEqual(result.status, "success")
        self.assertFalse((dest / ".github").exists())


if __name__ == "__main__":
    unittest.main()
