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
    "product_identifier",
    "source_repository",
    "source_revision",
    "initialization_timestamp",
    "request_identifier",
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
        return {
            "path": str(self.path),
            "byte_length": self.byte_length,
        }


def _require_nonempty(name: str, value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ProvenanceError(f"{name} must be a non-empty string")
    return value


def _request_identifier(workspace: StagingWorkspace) -> str:
    authority = workspace.inputs.request.authority
    if set(authority) != {"granted_by"}:
        raise ProvenanceError("request authority must contain exactly granted_by")
    return _require_nonempty("request_identifier", authority["granted_by"])


def build_provenance_record(
    workspace: StagingWorkspace,
    inputs: ProvenanceInputs,
) -> dict[str, object]:
    validate_staging_workspace(workspace)

    request = workspace.inputs.request
    source = workspace.inputs.source

    if source.repository != request.source_repository:
        raise ProvenanceError("source repository carriage changed before provenance")
    if source.commit_id != request.source_revision.object_id:
        raise ProvenanceError("source revision carriage changed before provenance")
    if request.source_revision.object_format != "sha1":
        raise ProvenanceError("provenance requires canonical SHA-1 source revision identity")

    initializer_name = _require_nonempty("initializer_name", inputs.initializer_name)
    initializer_version = _require_nonempty("initializer_version", inputs.initializer_version)
    timestamp = _require_nonempty(
        "initialization_timestamp",
        inputs.initialization_timestamp,
    )
    if not UTC_TIMESTAMP_RE.fullmatch(timestamp):
        raise ProvenanceError(
            "initialization_timestamp must be ISO 8601 UTC YYYY-MM-DDTHH:MM:SSZ"
        )

    record: dict[str, object] = {
        "schema_version": "1",
        "initializer_name": initializer_name,
        "initializer_version": initializer_version,
        "product_identifier": _require_nonempty("product_identifier", request.product_id),
        "source_repository": _require_nonempty(
            "source_repository",
            request.source_repository,
        ),
        "source_revision": request.source_revision.to_dict(),
        "initialization_timestamp": timestamp,
        "request_identifier": _request_identifier(workspace),
    }
    if tuple(record.keys()) != PROVENANCE_FIELD_ORDER:
        raise ProvenanceError("provenance field order drifted")
    return record


def serialize_provenance_record(record: dict[str, object]) -> bytes:
    if tuple(record.keys()) != PROVENANCE_FIELD_ORDER:
        raise ProvenanceError("provenance record contains unknown, missing, or reordered fields")
    if record.get("schema_version") != "1":
        raise ProvenanceError("unsupported provenance schema_version")
    encoded = (json.dumps(record, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    if not encoded.endswith(b"\n") or encoded.endswith(b"\n\n"):
        raise ProvenanceError("provenance serialization final newline drifted")
    return encoded


def write_provenance_record(
    workspace: StagingWorkspace,
    inputs: ProvenanceInputs,
) -> ProvenanceResult:
    validate_staging_workspace(workspace)
    record = build_provenance_record(workspace, inputs)
    payload = serialize_provenance_record(record)

    destination = workspace.repository_path / PROVENANCE_RELATIVE_PATH
    if destination.exists() or destination.is_symlink():
        raise ProvenanceError("provenance record destination already exists")

    parent = destination.parent
    parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(payload)

    observed = destination.read_bytes()
    if observed != payload:
        raise ProvenanceError("provenance record write verification failed")
    return ProvenanceResult(path=destination, byte_length=len(payload))
