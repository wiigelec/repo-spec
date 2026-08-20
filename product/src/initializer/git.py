from __future__ import annotations

import os
import re
import shutil
import subprocess
import stat
from datetime import datetime
from pathlib import Path

from .models import (
    InitializerError,
    GitEstablishmentPhase,
    GitPreflight,
    GitCommandResult,
    GitEstablishmentPlan,
    GitEstablishmentResult,
)


MINIMUM_GIT_VERSION = (2, 5, 0)

SANITIZE_ENV_REMOVE = frozenset({
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_NAMESPACE",
    "GIT_CEILING_DIRECTORIES",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_COMMON_DIR",
    "GIT_SEQUENCE_EDITOR",
    "GIT_EDITOR",
    "GIT_PAGER",
    "GIT_EXTERNAL_DIFF",
    "GIT_SSH",
    "GIT_SSH_COMMAND",
    "GIT_SSL_NO_VERIFY",
    "GIT_PROXY_COMMAND",
    "GIT_TERMINAL_PROMPT",
    "GIT_CONFIG_PARAMETERS",
    "GIT_PROTOCOL_FROM_USER",
    "GIT_HTTP_PROXY_AUTHMETHOD",
    "GIT_ALLOW_PROTOCOL",
    "GIT_ASKPASS",
    "GIT_CREDENTIAL_HELPER",
    "GIT_TEMPLATE_DIR",
})


class GitError(InitializerError):
    def __init__(self, message: str) -> None:
        self.message = message

    def __str__(self) -> str:
        return self.message


def _sanitize_env() -> dict[str, str]:
    env = dict(os.environ)
    for key in SANITIZE_ENV_REMOVE:
        env.pop(key, None)
    if "GIT_OPTIONAL_LOCKS" not in env:
        env["GIT_OPTIONAL_LOCKS"] = "0"
    if "HOME" not in env:
        env["HOME"] = "/dev/null"
    return env


def _parse_git_version(version_str: str) -> tuple[int, int, int]:
    for line in version_str.splitlines():
        if line.startswith("git version "):
            parts = line.strip().split()
            if len(parts) >= 3:
                ver_str = parts[2]
                ver_parts = ver_str.split(".")
                nums: list[int] = []
                for p in ver_parts:
                    try:
                        nums.append(int(p))
                    except ValueError:
                        break
                while len(nums) < 3:
                    nums.append(0)
                return (nums[0], nums[1], nums[2])
    return (0, 0, 0)


def _find_git() -> str | None:
    git_path = shutil.which("git")
    if git_path is None:
        return None
    try:
        result = subprocess.run(
            [git_path, "--version"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            return None
        version = _parse_git_version(result.stdout.strip())
        if version < MINIMUM_GIT_VERSION:
            return None
        return git_path
    except (OSError, subprocess.TimeoutExpired):
        return None


def _build_tree_inventory(destination: Path) -> list[dict[str, object]]:
    inventory: list[dict[str, object]] = []
    if not destination.is_dir():
        return inventory
    for entry in sorted(destination.rglob("*"), key=lambda p: str(p.relative_to(destination))):
        rel = str(entry.relative_to(destination))
        if entry.is_dir():
            inventory.append({"path": rel, "type": "dir"})
        elif entry.is_symlink():
            try:
                target = os.readlink(str(entry))
            except OSError:
                target = ""
            inventory.append({"path": rel, "type": "symlink", "target": target})
        elif entry.is_file():
            try:
                st = entry.stat()
                inventory.append({
                    "path": rel,
                    "type": "file",
                    "size": st.st_size,
                    "mode": stat.S_IMODE(st.st_mode),
                })
            except OSError:
                inventory.append({"path": rel, "type": "file", "size": 0, "mode": 0})
    return inventory


def _tree_inventory_key(inv: list[dict[str, object]]) -> str:
    return "|".join(
        f"{e['path']}:{e['type']}" for e in inv
    )


def git_preflight(
    destination_path: str,
    promotion_result_status: str | None = None,
    promotion_committed_destination: str | None = None,
) -> GitPreflight:
    dest_p = Path(destination_path).resolve()
    dest_str = str(dest_p)

    git_path = _find_git()
    git_available = git_path is not None
    git_version: str | None = None

    if git_path is not None:
        try:
            ver_result = subprocess.run(
                [git_path, "--version"],
                capture_output=True, text=True, timeout=30,
            )
            if ver_result.returncode == 0:
                git_version = ver_result.stdout.strip()
        except (OSError, subprocess.TimeoutExpired):
            git_available = False

    dest_exists = dest_p.exists()
    if not dest_exists:
        return GitPreflight(
            destination_path=dest_str,
            git_available=git_available,
            git_version=git_version,
            destination_exists=False,
            destination_is_dir=False,
            destination_is_symlink=False,
            is_git_repository=False,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=False,
            decision="rejected",
            rejection_reason="destination does not exist",
        )

    if not dest_p.is_dir():
        return GitPreflight(
            destination_path=dest_str,
            git_available=git_available,
            git_version=git_version,
            destination_exists=True,
            destination_is_dir=False,
            destination_is_symlink=dest_p.is_symlink(),
            is_git_repository=False,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=False,
            decision="rejected",
            rejection_reason="destination is not a directory",
        )

    dest_is_symlink = dest_p.is_symlink()

    is_git_repo = False
    inside_worktree = False
    outer_worktree: str | None = None

    if dest_exists and git_path is not None:
        dot_git = dest_p / ".git"
        if dot_git.exists():
            is_git_repo = True

    if dest_exists and git_path is not None and not is_git_repo:
        try:
            parent_result = subprocess.run(
                [git_path, "-C", dest_str, "rev-parse", "--show-toplevel"],
                capture_output=True, text=True, timeout=30,
                env=_sanitize_env(),
            )
            if parent_result.returncode == 0:
                top_level = parent_result.stdout.strip()
                if top_level and Path(top_level).resolve() != dest_p:
                    inside_worktree = True
                    outer_worktree = top_level
        except (OSError, subprocess.TimeoutExpired):
            pass

    content_consistent = True
    content_inconsistency_reason: str | None = None

    if not git_available:
        return GitPreflight(
            destination_path=dest_str,
            git_available=False,
            git_version=None,
            destination_exists=dest_exists,
            destination_is_dir=dest_exists,
            destination_is_symlink=dest_is_symlink,
            is_git_repository=is_git_repo,
            inside_worktree=inside_worktree,
            outer_worktree=outer_worktree,
            content_consistent=False,
            decision="rejected",
            rejection_reason="git executable not found or below minimum version",
        )

    if is_git_repo:
        return GitPreflight(
            destination_path=dest_str,
            git_available=True,
            git_version=git_version,
            destination_exists=True,
            destination_is_dir=True,
            destination_is_symlink=dest_is_symlink,
            is_git_repository=True,
            inside_worktree=False,
            outer_worktree=None,
            content_consistent=False,
            decision="rejected",
            rejection_reason="destination already contains a .git entry",
        )

    if inside_worktree:
        reason = f"destination is inside an outer Git worktree at {outer_worktree}"
        return GitPreflight(
            destination_path=dest_str,
            git_available=True,
            git_version=git_version,
            destination_exists=True,
            destination_is_dir=True,
            destination_is_symlink=dest_is_symlink,
            is_git_repository=False,
            inside_worktree=True,
            outer_worktree=outer_worktree,
            content_consistent=False,
            decision="rejected",
            rejection_reason=reason,
        )

    return GitPreflight(
        destination_path=dest_str,
        git_available=True,
        git_version=git_version,
        destination_exists=dest_exists,
        destination_is_dir=dest_exists,
        destination_is_symlink=dest_is_symlink,
        is_git_repository=False,
        inside_worktree=False,
        outer_worktree=None,
        content_consistent=True,
        content_inconsistency_reason=content_inconsistency_reason,
        decision="allowed",
    )


def _build_plan(preflight: GitPreflight) -> GitEstablishmentPlan:
    return GitEstablishmentPlan(
        destination_path=preflight.destination_path,
    )


def _run_git(
    args: list[str],
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> GitCommandResult:
    git_path = _find_git()
    if git_path is None:
        return GitCommandResult(
            command=["git"] + args,
            returncode=-1,
            stdout="",
            stderr="git not found",
        )

    cmd = [git_path] + args
    effective_env = env if env is not None else _sanitize_env()

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=cwd,
            env=effective_env,
        )
        return GitCommandResult(
            command=cmd,
            returncode=proc.returncode,
            stdout=proc.stdout,
            stderr=proc.stderr,
        )
    except FileNotFoundError:
        return GitCommandResult(
            command=cmd,
            returncode=-1,
            stdout="",
            stderr="git executable not found at runtime",
        )
    except subprocess.TimeoutExpired:
        return GitCommandResult(
            command=cmd,
            returncode=-1,
            stdout="",
            stderr="git command timed out",
        )


def establish_git_repository(
    destination_path: str,
    plan: GitEstablishmentPlan | None = None,
) -> GitEstablishmentResult:
    if plan is None:
        plan = GitEstablishmentPlan(destination_path=destination_path)

    dest_p = Path(plan.destination_path).resolve()
    dest_str = str(dest_p)

    completed: list[str] = []

    if not dest_p.exists():
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path=dest_str,
            failure_reason="destination does not exist",
        )

    if not dest_p.is_dir():
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path=dest_str,
            failure_reason="destination is not a directory",
        )

    dot_git = dest_p / ".git"
    if dot_git.exists():
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path=dest_str,
            failure_reason="destination already contains a .git entry",
        )

    git_path = _find_git()
    if git_path is None:
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path=dest_str,
            failure_reason="git not available",
        )

    git_version_str = ""
    try:
        ver_result = subprocess.run(
            [git_path, "--version"],
            capture_output=True, text=True, timeout=30,
        )
        if ver_result.returncode == 0:
            git_version_str = ver_result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass

    env = _sanitize_env()
    env["GIT_AUTHOR_NAME"] = plan.author_name
    env["GIT_AUTHOR_EMAIL"] = plan.author_email
    env["GIT_COMMITTER_NAME"] = plan.committer_name
    env["GIT_COMMITTER_EMAIL"] = plan.committer_email
    env["GIT_AUTHOR_DATE"] = plan.timestamp
    env["GIT_COMMITTER_DATE"] = plan.timestamp

    init_result = _run_git(
        ["init", "--initial-branch", plan.initial_branch],
        cwd=dest_str,
        env=env,
    )
    if not init_result.succeeded:
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.failed,
            destination_path=dest_str,
            git_version=git_version_str,
            failure_reason=f"git init failed: {init_result.stderr.strip()}",
        )
    completed.append(GitEstablishmentPhase.initialized)

    config_result = _run_git(
        ["config", "user.name", plan.author_name],
        cwd=dest_str, env=env,
    )
    if config_result.succeeded:
        config_result = _run_git(
            ["config", "user.email", plan.author_email],
            cwd=dest_str, env=env,
        )

    add_result = _run_git(
        ["add", "-A"],
        cwd=dest_str, env=env,
    )
    if not add_result.succeeded:
        _cleanup_git(dest_str, GitEstablishmentPhase.indexed)
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.cleaned,
            destination_path=dest_str,
            git_version=git_version_str,
            failure_reason=f"git add failed: {add_result.stderr.strip()}",
            completed_phases=completed,
        )
    completed.append(GitEstablishmentPhase.indexed)

    status_result = _run_git(
        ["status", "--porcelain"],
        cwd=dest_str, env=env,
    )
    if status_result.succeeded:
        untracked = [l for l in status_result.stdout.splitlines() if l.strip()]
    else:
        untracked = []

    commit_result = _run_git(
        ["commit", "-m", plan.commit_message, "--allow-empty"],
        cwd=dest_str, env=env,
    )
    if not commit_result.succeeded:
        _cleanup_git(dest_str, GitEstablishmentPhase.committed)
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.cleaned,
            destination_path=dest_str,
            git_version=git_version_str,
            failure_reason=f"git commit failed: {commit_result.stderr.strip()}",
            completed_phases=completed,
        )
    completed.append(GitEstablishmentPhase.committed)

    verify_result = _run_git(
        ["rev-parse", "HEAD"],
        cwd=dest_str, env=env,
    )
    head_commit = verify_result.stdout.strip() if verify_result.succeeded else ""

    tree_result = _run_git(
        ["rev-parse", "HEAD^{tree}"],
        cwd=dest_str, env=env,
    )
    commit_tree = tree_result.stdout.strip() if tree_result.succeeded else ""

    log_result = _run_git(
        ["log", "--oneline", "--format=%H", "HEAD"],
        cwd=dest_str, env=env,
    )
    commit_count = len([l for l in log_result.stdout.splitlines() if l.strip()]) if log_result.succeeded else 0

    branch_result = _run_git(
        ["rev-parse", "--abbrev-ref", "HEAD"],
        cwd=dest_str, env=env,
    )
    current_branch = branch_result.stdout.strip() if branch_result.succeeded else ""

    parent_result = _run_git(
        ["rev-list", "--parents", "--max-parents=0", "HEAD"],
        cwd=dest_str, env=env,
    )
    is_root = parent_result.succeeded and len(parent_result.stdout.strip().split()) == 1

    clean_result = _run_git(
        ["status", "--porcelain"],
        cwd=dest_str, env=env,
    )
    worktree_clean = clean_result.succeeded and not clean_result.stdout.strip()

    remote_result = _run_git(
        ["remote", "-v"],
        cwd=dest_str, env=env,
    )
    remote_count = len([l for l in remote_result.stdout.splitlines() if l.strip()]) if remote_result.succeeded else 0

    author_identity = f"{plan.author_name} <{plan.author_email}>"
    committer_identity = f"{plan.committer_name} <{plan.committer_email}>"

    issues: list[str] = []
    if current_branch != plan.initial_branch:
        issues.append(f"branch mismatch: expected {plan.initial_branch}, got {current_branch}")
    if not is_root:
        issues.append("commit is not a root commit")
    if commit_count != 1:
        issues.append(f"expected 1 commit, found {commit_count}")
    if not worktree_clean:
        issues.append("worktree is not clean")
    if remote_count != 0:
        issues.append(f"expected 0 remotes, found {remote_count}")

    if issues:
        completed.append(GitEstablishmentPhase.verified)
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.verified,
            destination_path=dest_str,
            git_version=git_version_str,
            initial_branch=current_branch,
            root_commit=head_commit,
            commit_tree=commit_tree,
            author_identity=author_identity,
            committer_identity=committer_identity,
            timestamps=plan.timestamp,
            commit_message=plan.commit_message,
            staged_path_count=0,
            worktree_clean=worktree_clean,
            remote_count=remote_count,
            completed_phases=completed,
            failure_reason="; ".join(issues),
        )

    completed.append(GitEstablishmentPhase.verified)
    return GitEstablishmentResult(
        status="success",
        phase=GitEstablishmentPhase.verified,
        destination_path=dest_str,
        git_version=git_version_str,
        initial_branch=current_branch,
        root_commit=head_commit,
        commit_tree=commit_tree,
        author_identity=author_identity,
        committer_identity=committer_identity,
        timestamps=plan.timestamp,
        commit_message=plan.commit_message,
        staged_path_count=len(untracked),
        ignored_path_count=0,
        worktree_clean=True,
        remote_count=0,
        completed_phases=completed,
    )


def _cleanup_git(destination_path: str, phase: str) -> None:
    dest_p = Path(destination_path).resolve()
    dot_git = dest_p / ".git"
    if dot_git.exists():
        try:
            if dot_git.is_dir():
                shutil.rmtree(str(dot_git), ignore_errors=True)
            elif dot_git.is_file():
                dot_git.unlink()
        except OSError:
            pass


def initialize_promoted_destination(
    destination_path: str,
    promotion_result: dict[str, object] | None = None,
) -> GitEstablishmentResult:
    if promotion_result is not None:
        status = promotion_result.get("status", "")
        committed = promotion_result.get("committed_destination")
        if status != "success":
            return GitEstablishmentResult(
                status="failed",
                phase=GitEstablishmentPhase.preflight,
                destination_path=str(Path(destination_path).resolve()),
                failure_reason=f"promotion status is '{status}', expected 'success'",
            )
        if committed is not None and isinstance(committed, str):
            dest_p = Path(committed).resolve()
            destination_path = str(dest_p)

    preflight = git_preflight(destination_path)
    if preflight.decision != "allowed":
        return GitEstablishmentResult(
            status="failed",
            phase=GitEstablishmentPhase.preflight,
            destination_path=preflight.destination_path,
            git_version=preflight.git_version or "",
            failure_reason=preflight.rejection_reason or "preflight rejected",
        )

    plan = _build_plan(preflight)
    return establish_git_repository(destination_path, plan)


def check_git_available() -> bool:
    return _find_git() is not None


def check_git_available_with_version() -> tuple[bool, str]:
    git_path = _find_git()
    if git_path is None:
        return False, ""
    try:
        result = subprocess.run(
            [git_path, "--version"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return True, ""


# BEGIN I3 PATCH 3 DETERMINISTIC LOCAL GIT BOOTSTRAP

from dataclasses import dataclass as _i3_dataclass
import tempfile as _i3_tempfile


I3_BOOTSTRAP_PROFILE_ID = "standard-v2"
I3_BOOTSTRAP_SCHEMA_VERSION = "1"
I3_INITIAL_BRANCH = "main"
I3_AUTHOR_NAME = "Repo-Spec Initializer"
I3_AUTHOR_EMAIL = "initializer@repo-spec.local"
I3_COMMIT_MESSAGE = "Initial repository foundation"


@_i3_dataclass(frozen=True)
class I3GitObjectIdentity:
    object_format: str
    object_id: str

    def to_dict(self) -> dict[str, str]:
        return {
            "object_format": self.object_format,
            "object_id": self.object_id,
        }


@_i3_dataclass(frozen=True)
class I3GitResult:
    repository_path: Path
    profile_id: str
    branch: str
    commit: I3GitObjectIdentity
    tree: I3GitObjectIdentity
    commit_count: int
    worktree_clean: bool
    remote_count: int
    tag_count: int
    refs: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "repository_path": str(self.repository_path),
            "profile_id": self.profile_id,
            "branch": self.branch,
            "commit": self.commit.to_dict(),
            "tree": self.tree.to_dict(),
            "commit_count": self.commit_count,
            "worktree_clean": self.worktree_clean,
            "remote_count": self.remote_count,
            "tag_count": self.tag_count,
            "refs": list(self.refs),
        }


def _i3_git_env(initialization_timestamp: str | None = None) -> dict[str, str]:
    env = dict(os.environ)
    for key in SANITIZE_ENV_REMOVE:
        env.pop(key, None)
    env.update({
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_AUTHOR_NAME": I3_AUTHOR_NAME,
        "GIT_AUTHOR_EMAIL": I3_AUTHOR_EMAIL,
        "GIT_COMMITTER_NAME": I3_AUTHOR_NAME,
        "GIT_COMMITTER_EMAIL": I3_AUTHOR_EMAIL,
        "GIT_AUTHOR_DATE": initialization_timestamp,
        "GIT_COMMITTER_DATE": initialization_timestamp,
        "LC_ALL": "C",
        "LANG": "C",
    })
    if initialization_timestamp is None:
        env.pop("GIT_AUTHOR_DATE", None)
        env.pop("GIT_COMMITTER_DATE", None)
    return env


def _i3_run_git(
    repository: Path,
    *args: str,
    initialization_timestamp: str | None = None,
) -> str:
    git_path = _find_git()
    if git_path is None:
        raise GitError("git executable not found or below minimum version")
    proc = subprocess.run(
        [git_path, "-C", str(repository), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=_i3_git_env(initialization_timestamp),
        check=False,
        timeout=120,
    )
    if proc.returncode:
        raise GitError(
            f"git {' '.join(args)} failed: {proc.stderr.strip() or proc.stdout.strip()}"
        )
    return proc.stdout


def _i3_identity(object_id: str, label: str) -> I3GitObjectIdentity:
    if len(object_id) != 40 or any(c not in "0123456789abcdef" for c in object_id):
        raise GitError(f"{label} is not a full lowercase SHA-1 object id")
    return I3GitObjectIdentity("sha1", object_id)



def verify_i3_git_repository(
    repository_path: str | Path,
    initialization_timestamp: str | None = None,
) -> I3GitResult:
    repository = Path(repository_path).resolve()
    if not repository.is_dir() or repository.is_symlink():
        raise GitError("I3 Git repository path must be a real directory")
    dot_git = repository / ".git"
    if not dot_git.is_dir() or dot_git.is_symlink():
        raise GitError("I3 repository must contain one .git directory")

    object_format = _i3_run_git(repository, "rev-parse", "--show-object-format").strip()
    if object_format != "sha1":
        raise GitError(f"I3 repository object format must be sha1, observed {object_format}")

    branch = _i3_run_git(repository, "symbolic-ref", "--short", "HEAD").strip()
    if branch != I3_INITIAL_BRANCH:
        raise GitError(f"I3 branch mismatch: {branch}")

    commit_id = _i3_run_git(repository, "rev-parse", "HEAD").strip()
    tree_id = _i3_run_git(repository, "rev-parse", "HEAD^{tree}").strip()
    commit = _i3_identity(commit_id, "generated commit")
    tree = _i3_identity(tree_id, "generated tree")

    commit_count_text = _i3_run_git(repository, "rev-list", "--count", "HEAD").strip()
    if commit_count_text != "1":
        raise GitError(f"I3 repository must contain exactly one commit: {commit_count_text}")

    parents = _i3_run_git(repository, "rev-list", "--parents", "-n", "1", "HEAD").strip().split()
    if parents != [commit_id]:
        raise GitError("I3 root commit must have no parent")

    message = _i3_run_git(repository, "log", "-1", "--format=%s", "HEAD").rstrip("\n")
    if message != I3_COMMIT_MESSAGE:
        raise GitError(f"I3 commit message mismatch: {message!r}")

    author = _i3_run_git(
        repository, "log", "-1", "--format=%an%n%ae%n%at%n%aI", "HEAD"
    ).splitlines()
    committer = _i3_run_git(
        repository, "log", "-1", "--format=%cn%n%ce%n%ct%n%cI", "HEAD"
    ).splitlines()
    if author[:2] != [I3_AUTHOR_NAME, I3_AUTHOR_EMAIL]:
        raise GitError(f"I3 author identity mismatch: {author[:2]}")
    if committer[:2] != [I3_AUTHOR_NAME, I3_AUTHOR_EMAIL]:
        raise GitError(f"I3 committer identity mismatch: {committer[:2]}")
    if author[2] != committer[2]:
        raise GitError(f"I3 author/committer timestamps differ: {author[2]} != {committer[2]}")
    if initialization_timestamp is not None:
        expected = datetime.fromisoformat(initialization_timestamp.replace("Z", "+00:00"))
        expected_epoch = str(int(expected.timestamp()))
        if author[2] != expected_epoch:
            raise GitError(
                f"I3 initialization timestamp mismatch: expected {expected_epoch}, observed {author[2]}"
            )

    status = _i3_run_git(
        repository, "status", "--porcelain=v1", "--untracked-files=all"
    )
    if status:
        raise GitError("I3 repository worktree is not clean")

    remotes = [line for line in _i3_run_git(repository, "remote").splitlines() if line]
    if remotes:
        raise GitError(f"I3 repository must have no remotes: {remotes}")

    tags = [line for line in _i3_run_git(repository, "tag", "--list").splitlines() if line]
    if tags:
        raise GitError(f"I3 repository must have no tags: {tags}")

    refs = tuple(
        line for line in _i3_run_git(
            repository, "for-each-ref", "--format=%(refname)"
        ).splitlines() if line
    )
    if refs != ("refs/heads/main",):
        raise GitError(f"I3 repository contains unexpected refs: {refs}")

    committed_tree = _i3_run_git(repository, "write-tree").strip()
    if committed_tree != tree_id:
        raise GitError("I3 index tree does not match root commit tree")

    return I3GitResult(
        repository_path=repository,
        profile_id=I3_BOOTSTRAP_PROFILE_ID,
        branch=branch,
        commit=commit,
        tree=tree,
        commit_count=1,
        worktree_clean=True,
        remote_count=0,
        tag_count=0,
        refs=refs,
    )


def initialize_i3_git_repository(
    repository_path: str | Path,
    initialization_timestamp: str,
) -> I3GitResult:
    repository = Path(repository_path).resolve()
    if not repository.is_dir() or repository.is_symlink():
        raise GitError("I3 Git initialization requires a real repository directory")
    dot_git = repository / ".git"
    if dot_git.exists() or dot_git.is_symlink():
        raise GitError("I3 Git initialization requires absent .git state")

    git_path = _find_git()
    if git_path is None:
        raise GitError("git executable not found or below minimum version")

    try:
        with _i3_tempfile.TemporaryDirectory(prefix="repo-spec-i3-git-template-") as template:
            init = subprocess.run(
                [
                    git_path,
                    "-C",
                    str(repository),
                    "init",
                    "--object-format=sha1",
                    "--initial-branch=main",
                    f"--template={template}",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=_i3_git_env(initialization_timestamp),
                check=False,
                timeout=120,
            )
            if init.returncode:
                raise GitError(
                    f"git init failed: {init.stderr.strip() or init.stdout.strip()}"
                )

        _i3_run_git(repository, "config", "--local", "core.autocrlf", "false", initialization_timestamp=initialization_timestamp)
        _i3_run_git(repository, "config", "--local", "core.safecrlf", "false", initialization_timestamp=initialization_timestamp)
        _i3_run_git(repository, "config", "--local", "commit.gpgSign", "false", initialization_timestamp=initialization_timestamp)
        _i3_run_git(repository, "add", "-A", initialization_timestamp=initialization_timestamp)

        staged = _i3_run_git(repository, "diff", "--cached", "--name-only", initialization_timestamp=initialization_timestamp)
        if not staged.strip():
            raise GitError("I3 root commit may not be empty")

        _i3_run_git(
            repository,
            "commit",
            "--no-gpg-sign",
            "--no-verify",
            "-m",
            I3_COMMIT_MESSAGE,
            initialization_timestamp=initialization_timestamp,
        )
        return verify_i3_git_repository(repository, initialization_timestamp)
    except BaseException:
        if dot_git.exists() and not dot_git.is_symlink():
            shutil.rmtree(dot_git, ignore_errors=True)
        raise


# END I3 PATCH 3 DETERMINISTIC LOCAL GIT BOOTSTRAP
