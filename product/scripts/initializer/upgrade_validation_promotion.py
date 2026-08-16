from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path
from collections.abc import Callable

from .upgrade_reanchoring import ProspectiveFrameworkReanchoring
from .upgrade_reconciliation import StagedManagedReconciliation


class UpgradeValidationPromotionError(Exception):
    pass


_AMBIENT_VALIDATION_ENV_KEYS = (
    "BASH_ENV",
    "ENV",
    "CDPATH",
    "PYTHONPATH",
    "PYTHONHOME",
    "PYTHONSTARTUP",
    "PYTHONUSERBASE",
    "GIT_DIR",
    "GIT_WORK_TREE",
    "GIT_INDEX_FILE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_COMMON_DIR",
)


@dataclass(frozen=True)
class UpgradeValidationResult:
    status: str
    repository_content_digest: str
    candidate_head: str
    returncode: int
    failure_reason: str | None

    @property
    def promotion_eligible(self) -> bool:
        return self.status == "pass" and self.returncode == 0 and self.failure_reason is None

    def canonical_evidence_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "repository_content_digest": self.repository_content_digest,
            "candidate_head": self.candidate_head,
            "returncode": self.returncode,
            "failure_reason": self.failure_reason,
        }


@dataclass(frozen=True)
class UpgradePromotionResult:
    promotion_outcome: str
    completion_status: str
    validated_repository_content_digest: str
    promoted_repository_content_digest: str | None
    failure_reason: str | None
    backup_path: str | None

    @property
    def accepted(self) -> bool:
        return self.promotion_outcome == "promoted"

    def canonical_evidence_dict(self) -> dict[str, object]:
        return {
            "promotion_outcome": self.promotion_outcome,
            "completion_status": self.completion_status,
            "validated_repository_content_digest": self.validated_repository_content_digest,
            "promoted_repository_content_digest": self.promoted_repository_content_digest,
            "failure_reason": self.failure_reason,
            "accepted": self.accepted,
        }


def _frame(value: bytes) -> bytes:
    return len(value).to_bytes(8, "big") + value


def repository_content_digest(repository: Path) -> str:
    root = repository.resolve()
    if not root.is_dir() or repository.is_symlink():
        raise UpgradeValidationPromotionError("candidate repository is not a real directory")

    framed = bytearray(b"repo-spec-upgrade-validated-content-v1\0")
    for path in sorted(
        repository.rglob("*"),
        key=lambda item: item.relative_to(repository).as_posix(),
    ):
        relative = path.relative_to(repository).as_posix()
        if relative == ".git" or relative.startswith(".git/"):
            continue

        try:
            st = path.lstat()
        except OSError as exc:
            raise UpgradeValidationPromotionError(
                f"cannot inspect candidate repository path {relative}: {exc}"
            ) from exc

        framed.extend(_frame(relative.encode("utf-8", "strict")))

        if stat.S_ISLNK(st.st_mode):
            framed.extend(_frame(b"symlink"))
            framed.extend(_frame(os.readlink(path).encode("utf-8", "strict")))
        elif stat.S_ISDIR(st.st_mode):
            framed.extend(_frame(b"directory"))
            framed.extend(_frame(b""))
        elif stat.S_ISREG(st.st_mode):
            framed.extend(_frame(b"file"))
            framed.extend(_frame(b"x" if st.st_mode & stat.S_IXUSR else b"-"))
            framed.extend(_frame(path.read_bytes()))
        else:
            raise UpgradeValidationPromotionError(
                f"unsupported candidate repository object: {relative}"
            )

    return hashlib.sha256(bytes(framed)).hexdigest()


def _validate_predecessor(
    staged: StagedManagedReconciliation,
    reanchoring: ProspectiveFrameworkReanchoring,
    target_repository: str,
) -> tuple[Path, Path, Path]:
    if staged.status != "staged" or staged.conflicts:
        raise UpgradeValidationPromotionError(
            "UP4 requires coherent conflict-free UP2 staged state"
        )

    staging_root = Path(staged.staging_root).resolve()
    transaction = Path(staged.transaction_path).resolve()
    repository = Path(staged.repository_path).resolve()
    target = Path(target_repository).expanduser().resolve()

    if not staging_root.is_dir():
        raise UpgradeValidationPromotionError("staging root no longer exists")
    if transaction != staging_root / "transaction" or repository != staging_root / "repository":
        raise UpgradeValidationPromotionError("staging topology is not canonical")
    if set(item.name for item in staging_root.iterdir()) != {"transaction", "repository"}:
        raise UpgradeValidationPromotionError(
            "staging root must contain exactly transaction/ and repository/"
        )
    if not transaction.is_dir() or transaction.is_symlink():
        raise UpgradeValidationPromotionError("transaction/ is invalid")
    if not repository.is_dir() or repository.is_symlink():
        raise UpgradeValidationPromotionError("repository/ is invalid")
    if Path(reanchoring.repository_path).resolve() != repository:
        raise UpgradeValidationPromotionError(
            "UP3 re-anchoring evidence does not identify the UP2 staged repository"
        )
    lineage_path = Path(reanchoring.lineage_path).resolve()
    try:
        lineage_path.relative_to(repository)
    except ValueError as exc:
        raise UpgradeValidationPromotionError(
            "UP3 lineage evidence is outside the staged repository"
        ) from exc
    if not lineage_path.is_file():
        raise UpgradeValidationPromotionError(
            "UP3 prospective lineage file is missing from staged repository"
        )
    if not target.is_dir() or target.is_symlink():
        raise UpgradeValidationPromotionError(
            "maintained target repository is not a real directory"
        )
    if staging_root.parent != target.parent:
        raise UpgradeValidationPromotionError(
            "upgrade staging root must be under the maintained target parent"
        )

    return staging_root, repository, target



# BEGIN UP4 CORRECTION: COMMITTED CANDIDATE AUTHORITY

_CANDIDATE_COMMIT_AUTHOR_NAME = "Repo-Spec Initializer"
_CANDIDATE_COMMIT_AUTHOR_EMAIL = "initializer@repo-spec.local"


def _candidate_git(
    repository: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    effective_env = dict(os.environ) if env is None else dict(env)
    for key in _AMBIENT_VALIDATION_ENV_KEYS:
        effective_env.pop(key, None)
    return subprocess.run(
        ["git", "-C", str(repository), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=effective_env,
    )


def _candidate_head(repository: Path) -> str:
    p = _candidate_git(repository, "rev-parse", "--verify", "HEAD")
    value = p.stdout.strip()
    if p.returncode or len(value) != 40 or any(c not in "0123456789abcdef" for c in value):
        raise UpgradeValidationPromotionError(
            "staged candidate does not have one resolvable SHA-1 HEAD commit"
        )
    return value


def _authorized_candidate_paths(
    staged: StagedManagedReconciliation,
    reanchoring: ProspectiveFrameworkReanchoring,
) -> tuple[str, ...]:
    repository = Path(staged.repository_path).resolve()
    paths: set[str] = set()

    lineage = Path(reanchoring.lineage_path).resolve()
    try:
        lineage_relative = lineage.relative_to(repository).as_posix()
    except ValueError as exc:
        raise UpgradeValidationPromotionError(
            "UP3 lineage path is outside the staged repository"
        ) from exc
    paths.add(lineage_relative)

    for operation in staged.operations:
        for value in (operation.baseline_path, operation.target_path):
            if value is None:
                continue
            path = Path(value)
            if path.is_absolute() or not value or any(part in {"", ".", ".."} for part in path.parts):
                raise UpgradeValidationPromotionError(
                    f"UP2 operation contains invalid candidate commit path: {value!r}"
                )
            if path.parts and path.parts[0] == ".git":
                raise UpgradeValidationPromotionError(
                    "candidate commit may not target Git administrative state"
                )
            paths.add(path.as_posix())

    return tuple(sorted(paths))


def _commit_reanchored_candidate(
    staged: StagedManagedReconciliation,
    reanchoring: ProspectiveFrameworkReanchoring,
) -> str:
    repository = Path(staged.repository_path).resolve()

    root = _candidate_git(repository, "rev-parse", "--show-toplevel")
    if root.returncode or Path(root.stdout.strip()).resolve() != repository:
        raise UpgradeValidationPromotionError(
            "staged candidate must be the root of an existing local Git repository"
        )

    parent_head = _candidate_head(repository)
    paths = _authorized_candidate_paths(staged, reanchoring)
    if not paths:
        raise UpgradeValidationPromotionError("candidate commit has no governed paths")

    add = _candidate_git(repository, "add", "-A", "--", *paths)
    if add.returncode:
        raise UpgradeValidationPromotionError(
            "cannot stage governed candidate paths: " + add.stderr.strip()
        )

    env = dict(os.environ)
    for key in _AMBIENT_VALIDATION_ENV_KEYS:
        env.pop(key, None)
    env["GIT_AUTHOR_NAME"] = _CANDIDATE_COMMIT_AUTHOR_NAME
    env["GIT_AUTHOR_EMAIL"] = _CANDIDATE_COMMIT_AUTHOR_EMAIL
    env["GIT_COMMITTER_NAME"] = _CANDIDATE_COMMIT_AUTHOR_NAME
    env["GIT_COMMITTER_EMAIL"] = _CANDIDATE_COMMIT_AUTHOR_EMAIL

    message = (
        "Repo-Spec framework upgrade to "
        + reanchoring.prospective_entry.framework_revision.object_id
    )
    commit = _candidate_git(
        repository,
        "-c",
        "commit.gpgSign=false",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "--only",
        "--no-verify",
        "-m",
        message,
        "--",
        *paths,
        env=env,
    )
    if commit.returncode:
        raise UpgradeValidationPromotionError(
            "cannot commit governed staged candidate paths: "
            + (commit.stderr.strip() or commit.stdout.strip())
        )

    candidate_head = _candidate_head(repository)
    if candidate_head == parent_head:
        raise UpgradeValidationPromotionError(
            "candidate commit did not advance staged repository HEAD"
        )

    parent = _candidate_git(repository, "rev-parse", "--verify", "HEAD^")
    if parent.returncode or parent.stdout.strip() != parent_head:
        raise UpgradeValidationPromotionError(
            "candidate commit does not directly extend prior accepted target HEAD"
        )

    diff = _candidate_git(repository, "diff", "--quiet", "HEAD", "--", *paths)
    if diff.returncode not in {0, 1}:
        raise UpgradeValidationPromotionError(
            "cannot verify governed candidate worktree paths"
        )
    if diff.returncode != 0:
        raise UpgradeValidationPromotionError(
            "governed candidate paths do not match committed candidate HEAD"
        )

    cached = _candidate_git(
        repository, "diff", "--cached", "--quiet", "HEAD", "--", *paths
    )
    if cached.returncode not in {0, 1}:
        raise UpgradeValidationPromotionError(
            "cannot verify governed candidate index paths"
        )
    if cached.returncode != 0:
        raise UpgradeValidationPromotionError(
            "governed candidate paths remain staged after candidate commit"
        )

    lineage_relative = Path(reanchoring.lineage_path).resolve().relative_to(
        repository
    ).as_posix()
    committed_lineage = _candidate_git(
        repository, "show", f"HEAD:{lineage_relative}"
    )
    if committed_lineage.returncode:
        raise UpgradeValidationPromotionError(
            "candidate HEAD does not contain the prospective lineage"
        )
    try:
        worktree_lineage = (repository / lineage_relative).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise UpgradeValidationPromotionError(
            "cannot read staged prospective lineage after candidate commit"
        ) from exc
    if committed_lineage.stdout != worktree_lineage:
        raise UpgradeValidationPromotionError(
            "candidate HEAD lineage differs from staged prospective lineage"
        )

    return candidate_head


def _candidate_git_state(repository: Path) -> tuple[str, bytes]:
    head = _candidate_head(repository)
    env = dict(os.environ)
    for key in _AMBIENT_VALIDATION_ENV_KEYS:
        env.pop(key, None)
    p = subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "status",
            "--porcelain=v1",
            "-z",
            "--untracked-files=all",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
        env=env,
    )
    if p.returncode:
        raise UpgradeValidationPromotionError(
            "cannot inspect staged candidate Git state: "
            + p.stderr.decode("utf-8", errors="replace").strip()
        )
    return head, p.stdout

# END UP4 CORRECTION: COMMITTED CANDIDATE AUTHORITY

def validate_reanchored_candidate(
    staged: StagedManagedReconciliation,
    reanchoring: ProspectiveFrameworkReanchoring,
    target_repository: str,
) -> UpgradeValidationResult:
    _staging_root, repository, _target = _validate_predecessor(
        staged, reanchoring, target_repository
    )

    candidate_head = _commit_reanchored_candidate(staged, reanchoring)
    before_git = _candidate_git_state(repository)
    if before_git[0] != candidate_head:
        raise UpgradeValidationPromotionError(
            "candidate HEAD changed immediately after candidate commit"
        )

    validator = repository / "scripts/validate"
    if not validator.is_file():
        return UpgradeValidationResult(
            status="fail",
            repository_content_digest=repository_content_digest(repository),
            candidate_head=candidate_head,
            returncode=127,
            failure_reason="staged repository validation failed: scripts/validate is missing",
        )

    before = repository_content_digest(repository)

    env = dict(os.environ)
    for key in _AMBIENT_VALIDATION_ENV_KEYS:
        env.pop(key, None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"

    completed = subprocess.run(
        ["bash", "scripts/validate"],
        cwd=repository,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    after = repository_content_digest(repository)
    after_git = _candidate_git_state(repository)
    if after_git != before_git:
        return UpgradeValidationResult(
            status="fail",
            repository_content_digest=after,
            candidate_head=after_git[0],
            returncode=completed.returncode,
            failure_reason=(
                "staged repository validation mutated candidate Git state "
                f"(head_before={before_git[0]}, head_after={after_git[0]})"
            ),
        )

    if after != before:
        return UpgradeValidationResult(
            status="fail",
            repository_content_digest=after,
            candidate_head=candidate_head,
            returncode=completed.returncode,
            failure_reason=(
                "staged repository validation mutated the candidate repository "
                f"(before={before}, after={after})"
            ),
        )

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip()
        if len(detail) > 4000:
            detail = detail[-4000:]
        suffix = f": {detail}" if detail else ""
        return UpgradeValidationResult(
            status="fail",
            repository_content_digest=before,
            candidate_head=candidate_head,
            returncode=completed.returncode,
            failure_reason=(
                "staged repository validation failed "
                f"(exit {completed.returncode}){suffix}"
            ),
        )

    return UpgradeValidationResult(
        status="pass",
        repository_content_digest=before,
        candidate_head=candidate_head,
        returncode=0,
        failure_reason=None,
    )

def _unique_backup(target: Path) -> Path:
    base = target.parent / f".repo-spec-upgrade-backup-{target.name}"
    candidate = base
    suffix = 0
    while candidate.exists():
        suffix += 1
        candidate = target.parent / f"{base.name}.{suffix}"
    return candidate


def _cleanup_tree(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.exists():
        shutil.rmtree(path)


def promote_validated_candidate(
    staged: StagedManagedReconciliation,
    reanchoring: ProspectiveFrameworkReanchoring,
    validation: UpgradeValidationResult,
    target_repository: str,
    *,
    fault_injector: Callable[[str], None] | None = None,
) -> UpgradePromotionResult:
    staging_root, repository, target = _validate_predecessor(
        staged, reanchoring, target_repository
    )

    if not validation.promotion_eligible:
        return UpgradePromotionResult(
            promotion_outcome="not-promoted",
            completion_status="failed",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=None,
            failure_reason="promotion gate is closed because staged validation did not pass",
            backup_path=None,
        )

    try:
        current_head, _current_status = _candidate_git_state(repository)
    except UpgradeValidationPromotionError as exc:
        return UpgradePromotionResult(
            promotion_outcome="not-promoted",
            completion_status="failed",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=None,
            failure_reason=f"staged candidate Git state cannot be verified: {exc}",
            backup_path=None,
        )
    if current_head != validation.candidate_head:
        return UpgradePromotionResult(
            promotion_outcome="not-promoted",
            completion_status="failed",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=None,
            failure_reason="staged candidate HEAD changed after successful validation",
            backup_path=None,
        )

    current_digest = repository_content_digest(repository)
    if current_digest != validation.repository_content_digest:
        return UpgradePromotionResult(
            promotion_outcome="not-promoted",
            completion_status="failed",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=None,
            failure_reason="staged repository changed after successful validation",
            backup_path=None,
        )

    backup = _unique_backup(target)
    target_moved = False
    candidate_committed = False

    def fault(point: str) -> None:
        if fault_injector is not None:
            fault_injector(point)

    try:
        fault("before-target-backup")
        os.rename(target, backup)
        target_moved = True
        fault("after-target-backup")

        os.rename(repository, target)
        candidate_committed = True
        fault("after-candidate-commit")

    except BaseException as exc:
        if candidate_committed:
            # Promotion is already committed. Do not roll it back automatically.
            promoted_digest = None
            try:
                promoted_digest = repository_content_digest(target)
            except Exception:
                pass
            return UpgradePromotionResult(
                promotion_outcome="promoted",
                completion_status="promoted-with-finalization-error",
                validated_repository_content_digest=validation.repository_content_digest,
                promoted_repository_content_digest=promoted_digest,
                failure_reason=f"post-commit finalization error: {exc}",
                backup_path=str(backup) if backup.exists() else None,
            )

        if target_moved:
            try:
                if not target.exists() and backup.exists():
                    os.rename(backup, target)
                    target_moved = False
            except BaseException as restore_exc:
                return UpgradePromotionResult(
                    promotion_outcome="indeterminate",
                    completion_status="failed",
                    validated_repository_content_digest=validation.repository_content_digest,
                    promoted_repository_content_digest=None,
                    failure_reason=(
                        f"candidate commit failed ({exc}); "
                        f"accepted target restoration also failed ({restore_exc})"
                    ),
                    backup_path=str(backup) if backup.exists() else None,
                )

        return UpgradePromotionResult(
            promotion_outcome="not-promoted",
            completion_status="failed",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=None,
            failure_reason=f"candidate promotion failed before commit: {exc}",
            backup_path=str(backup) if backup.exists() else None,
        )

    promoted_digest = repository_content_digest(target)
    if promoted_digest != validation.repository_content_digest:
        return UpgradePromotionResult(
            promotion_outcome="promoted",
            completion_status="promoted-with-finalization-error",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=promoted_digest,
            failure_reason=(
                "promoted repository digest differs from the exact validated staged state"
            ),
            backup_path=str(backup) if backup.exists() else None,
        )

    try:
        fault("before-success-finalization")
        _cleanup_tree(backup)
        fault("after-backup-cleanup")
        _cleanup_tree(staging_root)
        fault("after-staging-cleanup")
    except BaseException as exc:
        return UpgradePromotionResult(
            promotion_outcome="promoted",
            completion_status="promoted-with-finalization-error",
            validated_repository_content_digest=validation.repository_content_digest,
            promoted_repository_content_digest=promoted_digest,
            failure_reason=f"post-promotion cleanup failed: {exc}",
            backup_path=str(backup) if backup.exists() else None,
        )

    return UpgradePromotionResult(
        promotion_outcome="promoted",
        completion_status="success",
        validated_repository_content_digest=validation.repository_content_digest,
        promoted_repository_content_digest=promoted_digest,
        failure_reason=None,
        backup_path=None,
    )


def serialize_up4_evidence(
    validation: UpgradeValidationResult,
    promotion: UpgradePromotionResult | None,
) -> bytes:
    payload: dict[str, object] = {
        "validation": validation.canonical_evidence_dict(),
        "promotion": (
            promotion.canonical_evidence_dict() if promotion is not None else None
        ),
    }
    return (
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def up4_evidence_fingerprint(
    validation: UpgradeValidationResult,
    promotion: UpgradePromotionResult | None,
) -> str:
    return hashlib.sha256(serialize_up4_evidence(validation, promotion)).hexdigest()
