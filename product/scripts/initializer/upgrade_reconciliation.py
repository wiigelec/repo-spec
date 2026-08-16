from __future__ import annotations

import hashlib
import json
import os
import shutil
import stat
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from .upgrade_resolution import ManagedMaterialDeltaEntry, UpgradeSetResolution


class StagedReconciliationError(Exception):
    pass


@dataclass(frozen=True)
class ManagedStateConflict:
    material_key: str
    path: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"material_key": self.material_key, "path": self.path, "reason": self.reason}


@dataclass(frozen=True)
class StagedManagedOperation:
    material_key: str
    classification: str
    baseline_path: str | None
    target_path: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "material_key": self.material_key,
            "classification": self.classification,
            "baseline_path": self.baseline_path,
            "target_path": self.target_path,
        }


@dataclass(frozen=True)
class StagedManagedReconciliation:
    staging_root: str
    transaction_path: str
    repository_path: str
    operations: tuple[StagedManagedOperation, ...]
    conflicts: tuple[ManagedStateConflict, ...]
    repository_content_digest: str

    @property
    def status(self) -> str:
        return "conflict" if self.conflicts else "staged"

    def to_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "staging_root": self.staging_root,
            "transaction_path": self.transaction_path,
            "repository_path": self.repository_path,
            "operations": [item.to_dict() for item in self.operations],
            "conflicts": [item.to_dict() for item in self.conflicts],
            "repository_content_digest": self.repository_content_digest,
        }

    def canonical_evidence_dict(self) -> dict[str, object]:
        return {
            "status": self.status,
            "operations": [item.to_dict() for item in self.operations],
            "conflicts": [item.to_dict() for item in self.conflicts],
            "repository_content_digest": self.repository_content_digest,
        }


def serialize_staged_reconciliation_evidence(result: StagedManagedReconciliation) -> bytes:
    return (
        json.dumps(
            result.canonical_evidence_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def staged_reconciliation_evidence_fingerprint(result: StagedManagedReconciliation) -> str:
    return hashlib.sha256(serialize_staged_reconciliation_evidence(result)).hexdigest()


def _validate_relative_path(value: str) -> Path:
    if not isinstance(value, str) or not value or value.startswith("/") or "\x00" in value:
        raise StagedReconciliationError(f"invalid managed destination path: {value!r}")
    parts = value.replace("\\", "/").split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise StagedReconciliationError(f"non-canonical managed destination path: {value!r}")
    if parts[0] == ".git":
        raise StagedReconciliationError("managed reconciliation may not target Git administrative state")
    return Path(*parts)


def _lstat_kind(path: Path) -> str:
    try:
        st = path.lstat()
    except FileNotFoundError:
        return "absent"
    if stat.S_ISLNK(st.st_mode):
        return "symlink"
    if stat.S_ISREG(st.st_mode):
        return "file"
    if stat.S_ISDIR(st.st_mode):
        return "directory"
    return "other"


def _read_git_blob(repository: str, blob_id: str) -> bytes:
    p = subprocess.run(
        ["git", "-C", repository, "cat-file", "blob", blob_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise StagedReconciliationError(
            "cannot read authoritative managed source blob: "
            + p.stderr.decode("utf-8", errors="replace").strip()
        )
    return p.stdout


def _expected_material_bytes(repository: str, evidence: dict[str, object]) -> bytes:
    blob_id = evidence.get("source_blob_id")
    if not isinstance(blob_id, str) or len(blob_id) != 40:
        raise StagedReconciliationError("managed material lacks canonical source blob identity")
    return _read_git_blob(repository, blob_id)


def _matches_authoritative_material(root: Path, repository: str, evidence: dict[str, object]) -> bool:
    relative = _validate_relative_path(str(evidence.get("destination_path")))
    path = root / relative
    source_type = evidence.get("source_type")
    expected = _expected_material_bytes(repository, evidence)
    kind = _lstat_kind(path)

    if source_type == "symlink":
        if kind != "symlink":
            return False
        try:
            target = os.readlink(path).encode("utf-8")
        except (OSError, UnicodeEncodeError):
            return False
        return target == expected

    if source_type != "blob" or kind != "file":
        return False
    try:
        actual = path.read_bytes()
    except OSError:
        return False
    if actual != expected:
        return False

    expected_mode = evidence.get("mode")
    if expected_mode in {"100644", "100755"}:
        actual_exec = bool(path.stat().st_mode & stat.S_IXUSR)
        if actual_exec != (expected_mode == "100755"):
            return False
    return True


def _ensure_absent_for_add(root: Path, evidence: dict[str, object]) -> bool:
    relative = _validate_relative_path(str(evidence.get("destination_path")))
    return _lstat_kind(root / relative) == "absent"


def _delta_map(resolution: UpgradeSetResolution) -> dict[str, ManagedMaterialDeltaEntry]:
    by_key = {entry.material_key: entry for entry in resolution.delta}
    if len(by_key) != len(resolution.delta):
        raise StagedReconciliationError("duplicate managed material identity in UP1 delta")
    return by_key


def _selected_entries(resolution: UpgradeSetResolution) -> tuple[ManagedMaterialDeltaEntry, ...]:
    by_key = _delta_map(resolution)
    selected = []
    for key in resolution.selected_material_keys:
        entry = by_key.get(key)
        if entry is None:
            raise StagedReconciliationError(f"UP1 selected material is absent from managed delta: {key}")
        if entry.classification not in {"added", "modified", "removed", "retargeted"}:
            raise StagedReconciliationError(
                f"UP1 selected material has non-transition classification: {key}"
            )
        selected.append(entry)
    return tuple(selected)


def _preflight_conflicts(
    resolution: UpgradeSetResolution,
    staged_repository: Path,
) -> tuple[ManagedStateConflict, ...]:
    conflicts = []
    baseline_repository = resolution.baseline_endpoint.repository

    for entry in _selected_entries(resolution):
        before = entry.baseline
        after = entry.target

        if entry.classification == "added":
            assert after is not None
            path = str(after["destination_path"])
            if not _ensure_absent_for_add(staged_repository, after):
                conflicts.append(
                    ManagedStateConflict(
                        entry.material_key,
                        path,
                        "selected add destination already exists in target state",
                    )
                )
            continue

        if before is None:
            raise StagedReconciliationError(
                f"{entry.classification} transition lacks baseline evidence: {entry.material_key}"
            )

        baseline_path = str(before["destination_path"])
        if not _matches_authoritative_material(staged_repository, baseline_repository, before):
            conflicts.append(
                ManagedStateConflict(
                    entry.material_key,
                    baseline_path,
                    "target-local managed state is not equivalent to accepted baseline",
                )
            )
            continue

        if entry.classification == "retargeted":
            if after is None:
                raise StagedReconciliationError(
                    f"retargeted transition lacks target evidence: {entry.material_key}"
                )
            target_path = str(after["destination_path"])
            if target_path != baseline_path and not _ensure_absent_for_add(staged_repository, after):
                conflicts.append(
                    ManagedStateConflict(
                        entry.material_key,
                        target_path,
                        "retarget destination already contains target-local content",
                    )
                )
    return tuple(conflicts)


def _remove_path(path: Path) -> None:
    kind = _lstat_kind(path)
    if kind == "absent":
        return
    if kind in {"file", "symlink"}:
        path.unlink()
        return
    if kind == "directory":
        shutil.rmtree(path)
        return
    raise StagedReconciliationError(f"cannot remove unsupported managed path type: {path}")


def _write_target_material(
    staged_repository: Path,
    source_repository: str,
    evidence: dict[str, object],
) -> None:
    if evidence.get("operation") != "copy-verbatim":
        raise StagedReconciliationError(
            "UP2 currently requires selected managed material to use copy-verbatim semantics"
        )
    relative = _validate_relative_path(str(evidence.get("destination_path")))
    destination = staged_repository / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    _remove_path(destination)

    payload = _expected_material_bytes(source_repository, evidence)
    source_type = evidence.get("source_type")
    if source_type == "symlink":
        try:
            target = payload.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise StagedReconciliationError("managed symlink target is not UTF-8") from exc
        destination.symlink_to(target)
        return
    if source_type != "blob":
        raise StagedReconciliationError(f"unsupported selected managed source type: {source_type!r}")

    destination.write_bytes(payload)
    mode = evidence.get("mode")
    if mode == "100755":
        destination.chmod(0o755)
    elif mode == "100644":
        destination.chmod(0o644)
    else:
        raise StagedReconciliationError(f"unsupported selected managed file mode: {mode!r}")


def _apply_selected_operations(
    resolution: UpgradeSetResolution,
    staged_repository: Path,
) -> tuple[StagedManagedOperation, ...]:
    operations = []
    source_repository = resolution.target_endpoint.repository

    for entry in _selected_entries(resolution):
        before = entry.baseline
        after = entry.target
        baseline_path = str(before["destination_path"]) if before is not None else None
        target_path = str(after["destination_path"]) if after is not None else None

        if entry.classification == "added":
            assert after is not None
            _write_target_material(staged_repository, source_repository, after)
        elif entry.classification == "modified":
            assert after is not None
            _write_target_material(staged_repository, source_repository, after)
        elif entry.classification == "removed":
            assert before is not None and baseline_path is not None
            _remove_path(staged_repository / _validate_relative_path(baseline_path))
        elif entry.classification == "retargeted":
            assert before is not None and after is not None and baseline_path is not None
            _remove_path(staged_repository / _validate_relative_path(baseline_path))
            _write_target_material(staged_repository, source_repository, after)

        operations.append(
            StagedManagedOperation(
                material_key=entry.material_key,
                classification=entry.classification,
                baseline_path=baseline_path,
                target_path=target_path,
            )
        )
    return tuple(operations)


def _hash_repository_tree(repository: Path) -> str:
    digest = hashlib.sha256()
    paths = sorted(repository.rglob("*"), key=lambda p: p.relative_to(repository).as_posix())
    for path in paths:
        relative = path.relative_to(repository).as_posix().encode("utf-8")
        st = path.lstat()
        if stat.S_ISLNK(st.st_mode):
            digest.update(b"L\0" + relative + b"\0")
            digest.update(os.readlink(path).encode("utf-8"))
        elif stat.S_ISDIR(st.st_mode):
            digest.update(b"D\0" + relative + b"\0")
        elif stat.S_ISREG(st.st_mode):
            digest.update(b"F\0" + relative + b"\0")
            digest.update(f"{stat.S_IMODE(st.st_mode):04o}".encode("ascii") + b"\0")
            digest.update(path.read_bytes())
        else:
            raise StagedReconciliationError(f"unsupported staged repository object: {path}")
    return digest.hexdigest()


def stage_managed_reconciliation(
    resolution: UpgradeSetResolution,
    *,
    staging_parent: str | None = None,
) -> StagedManagedReconciliation:
    target = Path(resolution.baseline.request.target_repository).resolve()
    if not target.is_dir():
        raise StagedReconciliationError("UP1 target repository no longer exists")

    parent = Path(staging_parent).resolve() if staging_parent else target.parent
    root = Path(tempfile.mkdtemp(prefix="repo-spec-upgrade-stage-", dir=str(parent)))
    transaction = root / "transaction"
    staged_repository = root / "repository"

    try:
        transaction.mkdir()
        shutil.copytree(target, staged_repository, symlinks=True)

        if set(root.iterdir()) != {transaction, staged_repository}:
            raise StagedReconciliationError(
                "staging transaction root must contain exactly transaction/ and repository/"
            )

        conflicts = _preflight_conflicts(resolution, staged_repository)
        operations = ()
        if not conflicts:
            operations = _apply_selected_operations(resolution, staged_repository)

        return StagedManagedReconciliation(
            staging_root=str(root),
            transaction_path=str(transaction),
            repository_path=str(staged_repository),
            operations=operations,
            conflicts=conflicts,
            repository_content_digest=_hash_repository_tree(staged_repository),
        )
    except BaseException:
        shutil.rmtree(root, ignore_errors=True)
        raise
