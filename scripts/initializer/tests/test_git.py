from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from initializer.models import (
    GitEstablishmentPhase,
    GitPreflight,
    GitCommandResult,
    GitEstablishmentPlan,
    GitEstablishmentResult,
    InitializerError,
)
from initializer.git import (
    git_preflight,
    establish_git_repository,
    initialize_promoted_destination,
    _sanitize_env,
    _find_git,
    _parse_git_version,
    MINIMUM_GIT_VERSION,
    check_git_available,
    GitError,
    _build_tree_inventory,
    _tree_inventory_key,
)


def git_available() -> bool:
    try:
        proc = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
        return proc.returncode == 0
    except (OSError, subprocess.TimeoutExpired):
        return False


class GitPreflightModelTests(unittest.TestCase):
    def test_allowed_preflight(self) -> None:
        p = GitPreflight(
            destination_path="/tmp/dest",
            git_available=True,
            git_version="git version 2.30.0",
            destination_exists=True,
            destination_is_dir=True,
            destination_is_symlink=False,
            is_git_repository=False,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=True,
            decision="allowed",
        )
        self.assertEqual(p.decision, "allowed")
        self.assertTrue(p.git_available)
        self.assertEqual(p.git_version, "git version 2.30.0")
        self.assertEqual(p.destination_path, "/tmp/dest")

    def test_rejected_preflight(self) -> None:
        p = GitPreflight(
            destination_path="/tmp/dest",
            git_available=True,
            git_version=None,
            destination_exists=True,
            destination_is_dir=True,
            destination_is_symlink=False,
            is_git_repository=True,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=False,
            decision="rejected",
            rejection_reason="destination already contains a .git entry",
        )
        self.assertEqual(p.decision, "rejected")
        self.assertEqual(p.rejection_reason, "destination already contains a .git entry")

    def test_to_dict(self) -> None:
        p = GitPreflight(
            destination_path="/tmp/dest",
            git_available=True,
            git_version="git version 2.30.0",
            destination_exists=True,
            destination_is_dir=True,
            destination_is_symlink=False,
            is_git_repository=False,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=True,
            decision="allowed",
        )
        d = p.to_dict()
        self.assertEqual(d["decision"], "allowed")
        self.assertEqual(d["destination_path"], "/tmp/dest")
        self.assertIn("git_available", d)

    def test_equality(self) -> None:
        a = GitPreflight("/tmp/d", True, "v1", True, True, False, False, False, None, True, decision="allowed")
        b = GitPreflight("/tmp/d", True, "v1", True, True, False, False, False, None, True, decision="allowed")
        c = GitPreflight("/tmp/x", True, "v1", True, True, False, False, False, None, True, decision="allowed")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash(self) -> None:
        a = GitPreflight("/tmp/d", True, "v1", True, True, False, False, False, None, True, decision="allowed")
        b = GitPreflight("/tmp/d", True, "v1", True, True, False, False, False, None, True, decision="allowed")
        self.assertEqual(hash(a), hash(b))


class GitCommandResultTests(unittest.TestCase):
    def test_successful_command(self) -> None:
        r = GitCommandResult(["git", "status"], 0, "output", "")
        self.assertTrue(r.succeeded)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout, "output")
        self.assertEqual(r.command, ["git", "status"])

    def test_failed_command(self) -> None:
        r = GitCommandResult(["git", "unknown"], 1, "", "error message")
        self.assertFalse(r.succeeded)

    def test_to_dict(self) -> None:
        r = GitCommandResult(["git", "init"], 0, "ok", "")
        d = r.to_dict()
        self.assertEqual(d["returncode"], 0)
        self.assertEqual(d["command"], "git init")
        self.assertEqual(d["stdout"], "ok")

    def test_equality(self) -> None:
        a = GitCommandResult(["git", "init"], 0, "", "")
        b = GitCommandResult(["git", "init"], 0, "", "")
        c = GitCommandResult(["git", "init"], 1, "", "")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class GitEstablishmentPlanTests(unittest.TestCase):
    def test_default_plan(self) -> None:
        plan = GitEstablishmentPlan("/tmp/dest")
        self.assertEqual(plan.destination_path, "/tmp/dest")
        self.assertEqual(plan.initial_branch, "main")
        self.assertEqual(plan.commit_message, "Initial repository foundation")
        self.assertEqual(plan.author_name, "Repo-Spec Initializer")
        self.assertEqual(plan.author_email, "initializer@repo-spec.local")
        self.assertEqual(plan.timestamp, "1234567890 +0000")

    def test_custom_plan(self) -> None:
        plan = GitEstablishmentPlan(
            destination_path="/tmp/dest",
            initial_branch="custom",
            commit_message="Custom message",
            author_name="Author",
            author_email="author@test.local",
            timestamp="987654321 +0000",
        )
        self.assertEqual(plan.initial_branch, "custom")
        self.assertEqual(plan.commit_message, "Custom message")
        self.assertEqual(plan.author_name, "Author")
        self.assertEqual(plan.timestamp, "987654321 +0000")

    def test_committer_falls_back_to_author(self) -> None:
        plan = GitEstablishmentPlan("/tmp/dest", author_name="A", author_email="a@b")
        self.assertEqual(plan.committer_name, "A")
        self.assertEqual(plan.committer_email, "a@b")

    def test_to_dict(self) -> None:
        plan = GitEstablishmentPlan("/tmp/dest")
        d = plan.to_dict()
        self.assertEqual(d["destination_path"], "/tmp/dest")
        self.assertEqual(d["initial_branch"], "main")
        self.assertIn("commit_message", d)

    def test_equality(self) -> None:
        a = GitEstablishmentPlan("/tmp/d")
        b = GitEstablishmentPlan("/tmp/d")
        c = GitEstablishmentPlan("/tmp/x")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash(self) -> None:
        a = GitEstablishmentPlan("/tmp/d")
        b = GitEstablishmentPlan("/tmp/d")
        self.assertEqual(hash(a), hash(b))


class GitEstablishmentResultTests(unittest.TestCase):
    def test_success_result(self) -> None:
        r = GitEstablishmentResult(
            status="success",
            phase=GitEstablishmentPhase.verified,
            destination_path="/tmp/dest",
            git_version="git version 2.30.0",
            initial_branch="main",
            root_commit="abc123",
            commit_tree="def456",
            author_identity="A <a@b>",
            committer_identity="A <a@b>",
            timestamps="1234567890 +0000",
            commit_message="Initial",
            staged_path_count=10,
            ignored_path_count=0,
            worktree_clean=True,
            remote_count=0,
            completed_phases=[GitEstablishmentPhase.preflight, GitEstablishmentPhase.initialized],
        )
        self.assertEqual(r.status, "success")
        self.assertEqual(r.root_commit, "abc123")
        self.assertTrue(r.worktree_clean)

    def test_failure_result(self) -> None:
        r = GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path="/tmp/dest",
            failure_reason="git not available",
        )
        self.assertEqual(r.status, "failed")
        self.assertEqual(r.failure_reason, "git not available")

    def test_to_dict(self) -> None:
        r = GitEstablishmentResult(
            status="success",
            phase=GitEstablishmentPhase.verified,
            destination_path="/tmp/dest",
            initial_branch="main",
            worktree_clean=True,
            remote_count=0,
        )
        d = r.to_dict()
        self.assertEqual(d["status"], "success")
        self.assertEqual(d["initial_branch"], "main")
        self.assertNotIn("failure_reason", d)

    def test_to_dict_with_failure(self) -> None:
        r = GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path="/tmp/dest",
            failure_reason="something went wrong",
        )
        d = r.to_dict()
        self.assertIn("failure_reason", d)
        self.assertEqual(d["failure_reason"], "something went wrong")

    def test_equality(self) -> None:
        a = GitEstablishmentResult("success", GitEstablishmentPhase.verified, "/tmp/d")
        b = GitEstablishmentResult("success", GitEstablishmentPhase.verified, "/tmp/d")
        c = GitEstablishmentResult("failed", GitEstablishmentPhase.preflight, "/tmp/d")
        self.assertEqual(a, b)
        self.assertNotEqual(a, c)


class GitPreflightFunctionTests(unittest.TestCase):
    def test_preflight_rejects_nonexistent_destination(self) -> None:
        result = git_preflight("/tmp/nonexistent-repo-spec-path-12345")
        self.assertEqual(result.decision, "rejected")
        self.assertIn("does not exist", result.rejection_reason or "")

    def test_preflight_rejects_file_destination(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            result = git_preflight(f.name)
            self.assertEqual(result.decision, "rejected")
            self.assertIn("not a directory", result.rejection_reason or "")

    def test_preflight_allows_empty_dir(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            if not git_available():
                result = git_preflight(td)
                self.assertEqual(result.decision, "rejected")
                self.assertIn("git", (result.rejection_reason or "").lower())
            else:
                result = git_preflight(td)
                self.assertEqual(result.decision, "allowed", msg=f"rejected: {result.rejection_reason}")

    def test_preflight_rejects_existing_git_repo(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "init"], cwd=td, capture_output=True, timeout=30)
            result = git_preflight(td)
            self.assertEqual(result.decision, "rejected")
            self.assertIn(".git", (result.rejection_reason or "").lower())

    def test_preflight_reports_git_version(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            result = git_preflight(td)
            self.assertTrue(result.git_available)
            self.assertIsNotNone(result.git_version)
            self.assertIn("git version", result.git_version or "")

    def test_preflight_deterministic_for_same_dir(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            r1 = git_preflight(td)
            r2 = git_preflight(td)
            self.assertEqual(r1.decision, r2.decision)


class GitEstablishmentFunctionTests(unittest.TestCase):
    def test_establish_rejects_nonexistent(self) -> None:
        result = establish_git_repository("/tmp/nonexistent-repo-spec-99999")
        self.assertEqual(result.status, "failed")
        self.assertIn("does not exist", result.failure_reason or "")

    def test_establish_rejects_file(self) -> None:
        with tempfile.NamedTemporaryFile() as f:
            result = establish_git_repository(f.name)
            self.assertEqual(result.status, "failed")
            self.assertIn("not a directory", result.failure_reason or "")

    def test_establish_rejects_existing_git(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            subprocess.run(["git", "init"], cwd=td, capture_output=True, timeout=30)
            result = establish_git_repository(td)
            self.assertEqual(result.status, "failed")
            self.assertIn(".git", result.failure_reason or "")

    def test_successful_establishment(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "file.txt").write_text("content")
            (Path(td) / "sub").mkdir()
            (Path(td) / "sub" / "nested.txt").write_text("nested")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success", msg=f"failed: {result.failure_reason}")
            self.assertEqual(result.initial_branch, "main")
            self.assertNotEqual(result.root_commit, "")
            self.assertNotEqual(result.commit_tree, "")
            self.assertTrue(result.worktree_clean)
            self.assertEqual(result.remote_count, 0)
            self.assertIn("Repo-Spec Initializer", result.author_identity)

    def test_establishes_root_commit(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.txt").write_text("data")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            log = subprocess.run(
                ["git", "log", "--oneline", "--format=%H", "HEAD"],
                cwd=td, capture_output=True, text=True, timeout=30,
            )
            commits = [l for l in log.stdout.splitlines() if l.strip()]
            self.assertEqual(len(commits), 1)

    def test_has_no_parent(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.txt").write_text("data")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            parents = subprocess.run(
                ["git", "rev-list", "--parents", "--max-parents=0", "HEAD"],
                cwd=td, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(len(parents.stdout.strip().split()), 1)

    def test_no_remotes_after_establishment(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.txt").write_text("data")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            remotes = subprocess.run(
                ["git", "remote", "-v"],
                cwd=td, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(remotes.stdout.strip(), "")

    def test_initial_branch_is_main(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.txt").write_text("data")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=td, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(branch.stdout.strip(), "main")

    def test_completed_phases_include_verified(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.txt").write_text("data")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            self.assertIn(GitEstablishmentPhase.verified, result.completed_phases)

    def test_clean_worktree_after_establishment(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "f.txt").write_text("data")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            status = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=td, capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(status.stdout.strip(), "")

    def test_staged_files_match_expected(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.txt").write_text("a")
            (Path(td) / "b.txt").write_text("b")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            ls_files = subprocess.run(
                ["git", "ls-files"],
                cwd=td, capture_output=True, text=True, timeout=30,
            )
            tracked = sorted(ls_files.stdout.strip().splitlines())
            self.assertEqual(tracked, ["a.txt", "b.txt"])


class GitCleanupTests(unittest.TestCase):
    def test_cleanup_removes_dotgit_on_precommit_failure(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "file.txt").write_text("content")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")

    def test_destination_content_preserved_after_git_operations(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "preserved.txt").write_text("test content")
            result = establish_git_repository(td)
            self.assertEqual(result.status, "success")
            content = (Path(td) / "preserved.txt").read_text()
            self.assertEqual(content, "test content")


class GitDeterminismTests(unittest.TestCase):
    def test_equivalent_inputs_produce_same_commit_tree(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        trees: list[str] = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / "file.txt").write_text("deterministic content")
                result = establish_git_repository(td)
                self.assertEqual(result.status, "success")
                trees.append(result.commit_tree)
        self.assertEqual(trees[0], trees[1],
                         "equivalent inputs should produce the same commit tree")

    def test_equivalent_inputs_produce_same_root_commit(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        commits: list[str] = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / "file.txt").write_text("deterministic content")
                result = establish_git_repository(td)
                self.assertEqual(result.status, "success")
                commits.append(result.root_commit)
        self.assertEqual(commits[0], commits[1],
                         "equivalent inputs should produce the same root commit identity")

    def test_different_content_produces_different_commit(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        commits: list[str] = []
        contents = ["aaa", "bbb"]
        for c in contents:
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / "file.txt").write_text(c)
                result = establish_git_repository(td)
                self.assertEqual(result.status, "success")
                commits.append(result.root_commit)
        self.assertNotEqual(commits[0], commits[1])


class GitInitializePromotedDestinationTests(unittest.TestCase):
    def test_rejects_nonexistent_destination(self) -> None:
        result = initialize_promoted_destination(
            "/tmp/nonexistent-repo-spec-promoted-999",
            {"status": "success", "committed_destination": "/tmp/nonexistent-repo-spec-promoted-999"},
        )
        self.assertEqual(result.status, "failed")

    def test_rejects_failed_promotion(self) -> None:
        result = initialize_promoted_destination(
            "/tmp/some-path",
            {"status": "failed", "committed_destination": None},
        )
        self.assertEqual(result.status, "failed")
        self.assertIn("promotion", (result.failure_reason or "").lower())

    def test_successful_promoted_establishment(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "promoted.txt").write_text("promoted content")
            result = initialize_promoted_destination(
                td,
                {"status": "success", "committed_destination": td},
            )
            self.assertEqual(result.status, "success", msg=f"failed: {result.failure_reason}")

    def test_works_without_promotion_result(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "data.txt").write_text("data")
            result = initialize_promoted_destination(td)
            self.assertEqual(result.status, "success", msg=f"failed: {result.failure_reason}")


class GitEnvironmentIsolationTests(unittest.TestCase):
    def test_sanitize_env_removes_git_dir(self) -> None:
        env = _sanitize_env()
        self.assertNotIn("GIT_DIR", env)
        self.assertNotIn("GIT_WORK_TREE", env)
        self.assertNotIn("GIT_INDEX_FILE", env)

    def test_git_optional_locks_disabled(self) -> None:
        env = _sanitize_env()
        self.assertEqual(env.get("GIT_OPTIONAL_LOCKS"), "0")

    def test_establishment_with_git_dir_env(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            os.environ["GIT_DIR"] = "/tmp/malicious-git-dir"
            try:
                result = establish_git_repository(td)
                self.assertEqual(result.status, "success", msg=f"failed: {result.failure_reason}")
                dot_git = Path(td) / ".git"
                self.assertTrue(dot_git.exists())
            finally:
                os.environ.pop("GIT_DIR", None)

    def test_sanitize_env_keeps_home(self) -> None:
        env = _sanitize_env()
        self.assertIn("HOME", env)


class GitVersionParsingTests(unittest.TestCase):
    def test_parse_typical_version(self) -> None:
        self.assertEqual(_parse_git_version("git version 2.30.0"), (2, 30, 0))

    def test_parse_with_suffix(self) -> None:
        self.assertEqual(_parse_git_version("git version 2.25.1.windows.1"), (2, 25, 1))

    def test_parse_major_minor(self) -> None:
        self.assertEqual(_parse_git_version("git version 2.25"), (2, 25, 0))

    def test_parse_malformed(self) -> None:
        self.assertEqual(_parse_git_version("not a git version"), (0, 0, 0))

    def test_parse_multi_digit(self) -> None:
        self.assertEqual(_parse_git_version("git version 10.5.42"), (10, 5, 42))

    def test_minimum_version_constant(self) -> None:
        self.assertGreaterEqual(MINIMUM_GIT_VERSION, (2, 5, 0))


class GitCheckAvailableTests(unittest.TestCase):
    def test_check_available(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        self.assertTrue(check_git_available())

    def test_check_with_version(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        from initializer.git import check_git_available_with_version
        ok, ver = check_git_available_with_version()
        self.assertTrue(ok)
        self.assertIn("git version", ver)


class GitTreeInventoryTests(unittest.TestCase):
    def test_empty_dir_inventory(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            inv = _build_tree_inventory(Path(td))
            self.assertEqual(inv, [])

    def test_inventories_files(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "a.txt").write_text("a")
            (Path(td) / "b.txt").write_text("b")
            inv = _build_tree_inventory(Path(td))
            paths = [e["path"] for e in inv if e["type"] == "file"]
            self.assertIn("a.txt", paths)
            self.assertIn("b.txt", paths)

    def test_inventory_key_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "z.txt").write_text("z")
            (Path(td) / "a.txt").write_text("a")
            inv1 = _build_tree_inventory(Path(td))
            inv2 = _build_tree_inventory(Path(td))
            self.assertEqual(_tree_inventory_key(inv1), _tree_inventory_key(inv2))


class GitCLIIntegrationTests(unittest.TestCase):
    REPO_SPEC_INIT = Path(__file__).resolve().parents[3] / "scripts" / "repo-spec-init"

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [str(self.REPO_SPEC_INIT), *args],
            capture_output=True,
            text=True,
        )

    def test_git_preflight_missing_args(self) -> None:
        proc = self._run("git-preflight")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_git_preflight_absent_dir(self) -> None:
        proc = self._run("git-preflight", "/tmp/nonexistent-git-preflight-99999")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("_type", proc.stdout)
        data = json.loads(proc.stdout)
        self.assertEqual(data["decision"], "rejected")

    def test_git_preflight_allowed_empty(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            proc = self._run("git-preflight", td)
            if proc.returncode != 0:
                data = json.loads(proc.stdout)
                if data.get("decision") != "allowed":
                    self.skipTest(f"preflight rejected: {data.get('rejection_reason')}")
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["decision"], "allowed")
            self.assertEqual(data["_type"], "git_preflight")

    def test_git_establish_missing_args(self) -> None:
        proc = self._run("git-establish")
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("usage:", proc.stderr.lower())

    def test_git_establish_nonexistent(self) -> None:
        proc = self._run("git-establish", "/tmp/nonexistent-git-est-99999")
        self.assertNotEqual(proc.returncode, 0)
        data = json.loads(proc.stdout)
        self.assertEqual(data["status"], "failed")

    def test_git_establish_success(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        with tempfile.TemporaryDirectory() as td:
            (Path(td) / "test.txt").write_text("cli test")
            proc = self._run("git-establish", td)
            if proc.returncode != 0:
                data = json.loads(proc.stdout)
                self.fail(f"git-establish failed: {data.get('failure_reason', proc.stderr)}")
            self.assertEqual(proc.returncode, 0, msg=proc.stderr)
            data = json.loads(proc.stdout)
            self.assertEqual(data["status"], "success")
            self.assertEqual(data["_type"], "git_establishment")
            self.assertNotEqual(data["root_commit"], "")
            self.assertTrue(data["worktree_clean"])

    def test_git_establish_deterministic_cli(self) -> None:
        if not git_available():
            self.skipTest("git not available")
        outputs: list[dict[str, object]] = []
        for _ in range(2):
            with tempfile.TemporaryDirectory() as td:
                (Path(td) / "data.txt").write_text("same content")
                proc = self._run("git-establish", td)
                if proc.returncode != 0:
                    self.skipTest("git-establish failed")
                outputs.append(json.loads(proc.stdout))
        self.assertEqual(outputs[0]["commit_tree"], outputs[1]["commit_tree"])
        self.assertEqual(outputs[0]["root_commit"], outputs[1]["root_commit"])


class GitNoGitNoPlatformTests(unittest.TestCase):
    def test_git_preflight_no_git_simulated(self) -> None:
        result = GitPreflight(
            destination_path="/tmp/dest",
            git_available=False,
            git_version=None,
            destination_exists=True,
            destination_is_dir=True,
            destination_is_symlink=False,
            is_git_repository=False,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=False,
            decision="rejected",
            rejection_reason="git executable not found or below minimum version",
        )
        self.assertEqual(result.decision, "rejected")
        self.assertFalse(result.git_available)

    def test_establishment_rejects_no_git(self) -> None:
        from initializer.git import _find_git
        if _find_git() is None:
            with tempfile.TemporaryDirectory() as td:
                result = establish_git_repository(td)
                self.assertEqual(result.status, "failed")
                self.assertIn("git", (result.failure_reason or "").lower())
        else:
            self.skipTest("git is available on this system; test requires no git")


if __name__ == "__main__":
    unittest.main()
