from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .upgrade_reconciliation import StagedManagedReconciliation
from .upgrade_resolution import (
    FrameworkLineageEntry,
    GitObjectIdentity,
    LINEAGE_RELATIVE_PATH,
    UpgradeSetResolution,
    parse_framework_lineage,
    serialize_framework_lineage,
)


class FrameworkReanchoringError(Exception):
    pass


@dataclass(frozen=True)
class ProspectiveFrameworkReanchoring:
    repository_path: str
    lineage_path: str
    prior_accepted_entries: tuple[FrameworkLineageEntry, ...]
    prospective_entry: FrameworkLineageEntry
    serialized_lineage_sha256: str

    def canonical_evidence_dict(self) -> dict[str, object]:
        return {
            "prior_accepted_entries": [
                entry.to_dict() for entry in self.prior_accepted_entries
            ],
            "prospective_entry": self.prospective_entry.to_dict(),
            "serialized_lineage_sha256": self.serialized_lineage_sha256,
            "accepted": False,
        }

    def to_dict(self) -> dict[str, object]:
        return {
            **self.canonical_evidence_dict(),
            "repository_path": self.repository_path,
            "lineage_path": self.lineage_path,
        }


def serialize_reanchoring_evidence(result: ProspectiveFrameworkReanchoring) -> bytes:
    return (
        json.dumps(
            result.canonical_evidence_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def reanchoring_evidence_fingerprint(result: ProspectiveFrameworkReanchoring) -> str:
    return hashlib.sha256(serialize_reanchoring_evidence(result)).hexdigest()


def _prospective_entry(resolution: UpgradeSetResolution) -> FrameworkLineageEntry:
    endpoint = resolution.target_endpoint
    source = resolution.reconciliation_target

    if endpoint.revision.object_format != "sha1":
        raise FrameworkReanchoringError("reconciliation target object format is not sha1")
    if endpoint.revision.object_id != source.commit_id:
        raise FrameworkReanchoringError(
            "reconciliation target endpoint conflicts with resolved supplying framework revision"
        )
    if Path(endpoint.repository).resolve() != Path(source.repository).resolve():
        raise FrameworkReanchoringError(
            "reconciliation target endpoint repository conflicts with resolved supplying framework"
        )

    return FrameworkLineageEntry(
        framework_repository=endpoint.repository,
        framework_revision=GitObjectIdentity(
            object_format=endpoint.revision.object_format,
            object_id=endpoint.revision.object_id,
        ),
    )


def _verify_prior_lineage(
    resolution: UpgradeSetResolution,
) -> tuple[FrameworkLineageEntry, ...]:
    lineage = tuple(resolution.baseline.lineage)
    if not lineage:
        raise FrameworkReanchoringError("accepted lineage history is empty")

    if lineage[-1] != resolution.baseline.active_baseline:
        raise FrameworkReanchoringError(
            "active baseline does not match latest accepted lineage entry"
        )

    seen: set[tuple[str, str]] = set()
    for entry in lineage:
        key = (
            entry.framework_repository,
            entry.framework_revision.object_id,
        )
        if key in seen:
            raise FrameworkReanchoringError(
                "accepted lineage history contains a repeated framework identity"
            )
        seen.add(key)

    return lineage


def reanchor_staged_repository(
    resolution: UpgradeSetResolution,
    staged: StagedManagedReconciliation,
) -> ProspectiveFrameworkReanchoring:
    if staged.status != "staged" or staged.conflicts:
        raise FrameworkReanchoringError(
            "UP3 requires coherent conflict-free UP2 staged managed state"
        )

    repository = Path(staged.repository_path).resolve()
    if not repository.is_dir():
        raise FrameworkReanchoringError("UP2 staged repository no longer exists")

    prior = _verify_prior_lineage(resolution)
    prospective = _prospective_entry(resolution)

    if any(
        entry.framework_repository == prospective.framework_repository
        and entry.framework_revision == prospective.framework_revision
        for entry in prior
    ):
        raise FrameworkReanchoringError(
            "reconciliation target identity is already present in accepted lineage"
        )

    lineage_path = repository / LINEAGE_RELATIVE_PATH
    if lineage_path.exists():
        try:
            existing = json.loads(lineage_path.read_text(encoding="utf-8"))
            parsed = parse_framework_lineage(existing)
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, Exception) as exc:
            if isinstance(exc, FrameworkReanchoringError):
                raise
            raise FrameworkReanchoringError(
                "existing staged framework lineage is invalid"
            ) from exc
        if tuple(parsed) != prior:
            raise FrameworkReanchoringError(
                "staged accepted lineage does not exactly match resolved accepted history"
            )

    entries = prior + (prospective,)
    serialized = serialize_framework_lineage(entries)

    lineage_path.parent.mkdir(parents=True, exist_ok=True)
    lineage_path.write_bytes(serialized)

    # Parse the exact bytes written so the staged representation is proven to be
    # canonical and complete before any later validation/promotion work.
    try:
        observed = json.loads(lineage_path.read_text(encoding="utf-8"))
        reparsed = parse_framework_lineage(observed)
    except Exception as exc:
        raise FrameworkReanchoringError(
            "written prospective lineage cannot be resolved from staged state"
        ) from exc
    if tuple(reparsed) != entries:
        raise FrameworkReanchoringError(
            "written prospective lineage does not match intended final staged representation"
        )

    return ProspectiveFrameworkReanchoring(
        repository_path=str(repository),
        lineage_path=str(lineage_path),
        prior_accepted_entries=prior,
        prospective_entry=prospective,
        serialized_lineage_sha256=hashlib.sha256(serialized).hexdigest(),
    )
