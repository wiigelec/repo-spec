from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .models import InitializerError
from .staging import StagingWorkspace, validate_staging_workspace


class ProvenanceError(InitializerError):
    pass


PROVENANCE_RELATIVE_PATH = Path("repo/initializer/provenance.json")
PROVENANCE_FIELD_ORDER = (
    "schema_version",
    "initializer_name",
    "initializer_version",
    "framework_repository",
    "framework_revision",
    "initialization_timestamp",
    "request_fingerprint",
)
UTC_TIMESTAMP_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")


@dataclass(frozen=True)
class ProvenanceInputs:
    initializer_name: str
    initializer_version: str
    initialization_timestamp: str


@dataclass(frozen=True)
class ProvenanceResult:
    path: Path
    byte_length: int

    def to_dict(self) -> dict[str, object]:
        return {"path": str(self.path), "byte_length": self.byte_length}


def _require_nonempty(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProvenanceError(f"{name} must be a non-empty string")
    return value


def build_provenance_record(
    workspace: StagingWorkspace,
    inputs: ProvenanceInputs,
) -> dict[str, object]:
    validate_staging_workspace(workspace)
    request = workspace.inputs.request
    source = workspace.inputs.source
    timestamp = _require_nonempty("initialization_timestamp", inputs.initialization_timestamp)
    if not UTC_TIMESTAMP_RE.fullmatch(timestamp):
        raise ProvenanceError("initialization_timestamp must be ISO 8601 UTC YYYY-MM-DDTHH:MM:SSZ")
    revision = _require_nonempty("framework_revision.object_id", source.commit_id)
    if len(revision) != 40 or any(c not in "0123456789abcdef" for c in revision):
        raise ProvenanceError("framework revision must be an exact lowercase SHA-1 commit ID")
    fingerprint = _require_nonempty("request_fingerprint", request.request_fingerprint)
    record: dict[str, object] = {
        "schema_version": "2",
        "initializer_name": _require_nonempty("initializer_name", inputs.initializer_name),
        "initializer_version": _require_nonempty("initializer_version", inputs.initializer_version),
        "framework_repository": _require_nonempty("framework_repository", source.repository),
        "framework_revision": {"object_format": "sha1", "object_id": revision},
        "initialization_timestamp": timestamp,
        "request_fingerprint": fingerprint,
    }
    if tuple(record.keys()) != PROVENANCE_FIELD_ORDER:
        raise ProvenanceError("provenance field order drifted")
    return record


def serialize_provenance_record(record: dict[str, object]) -> bytes:
    if tuple(record.keys()) != PROVENANCE_FIELD_ORDER or record.get("schema_version") != "2":
        raise ProvenanceError("invalid provenance record shape")
    return (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def write_provenance_record(
    workspace: StagingWorkspace,
    inputs: ProvenanceInputs,
) -> ProvenanceResult:
    validate_staging_workspace(workspace)
    payload = serialize_provenance_record(build_provenance_record(workspace, inputs))
    destination = workspace.repository_path / PROVENANCE_RELATIVE_PATH
    if destination.exists() or destination.is_symlink():
        raise ProvenanceError("provenance record destination already exists")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)
    if destination.read_bytes() != payload:
        raise ProvenanceError("provenance record write verification failed")
    return ProvenanceResult(path=destination, byte_length=len(payload))
