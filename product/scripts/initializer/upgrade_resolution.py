from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .inventory import InventoryError, ResolvedSourceMaterial, resolve_source_material
from .models import InitializerError

LINEAGE_RELATIVE_PATH = Path("repo/initializer/framework-lineage.json")
PROVENANCE_RELATIVE_PATH = Path("repo/initializer/provenance.json")
LINEAGE_ROOT_FIELDS = frozenset({"schema_version", "entries"})
LINEAGE_ENTRY_FIELDS = frozenset({"framework_repository", "framework_revision"})
PROVENANCE_FIELDS = (
    "schema_version",
    "initializer_name",
    "initializer_version",
    "framework_repository",
    "framework_revision",
    "initialization_timestamp",
    "request_fingerprint",
)
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")

class UpgradeResolutionError(InitializerError):
    pass

@dataclass(frozen=True)
class GitObjectIdentity:
    object_format: str
    object_id: str

    def to_dict(self) -> dict[str, str]:
        return {"object_format": self.object_format, "object_id": self.object_id}

@dataclass(frozen=True)
class UpgradeRequest:
    target_repository: str

    def to_dict(self) -> dict[str, str]:
        return {"target_repository": self.target_repository}

@dataclass(frozen=True)
class FrameworkLineageEntry:
    framework_repository: str
    framework_revision: GitObjectIdentity

    def to_dict(self) -> dict[str, object]:
        return {
            "framework_repository": self.framework_repository,
            "framework_revision": self.framework_revision.to_dict(),
        }

@dataclass(frozen=True)
class BaselineResolution:
    request: UpgradeRequest
    lineage: tuple[FrameworkLineageEntry, ...]
    active_baseline: FrameworkLineageEntry
    baseline_source: str
    baseline_material: ResolvedSourceMaterial

    def to_dict(self) -> dict[str, object]:
        return {
            "request": self.request.to_dict(),
            "lineage": [entry.to_dict() for entry in self.lineage],
            "active_baseline": self.active_baseline.to_dict(),
            "baseline_source": self.baseline_source,
            "baseline_inventory_material_keys": [
                entry.material_key for entry in self.baseline_material.manifest
            ],
        }

def _git(target: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(target), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

def _read_json_object(path: Path, context: str) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise UpgradeResolutionError(f"cannot read {context}: {path}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise UpgradeResolutionError(f"{context} is not UTF-8") from exc
    try:
        value = json.loads(text)
    except json.JSONDecodeError as exc:
        raise UpgradeResolutionError(f"invalid JSON in {context}: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise UpgradeResolutionError(f"{context} must contain one JSON object")
    return value

def _parse_git_identity(value: object, context: str) -> GitObjectIdentity:
    if not isinstance(value, dict):
        raise UpgradeResolutionError(f"{context} must be an object")
    if set(value) != {"object_format", "object_id"}:
        raise UpgradeResolutionError(
            f"{context} must contain exactly object_format and object_id"
        )
    if value.get("object_format") != "sha1":
        raise UpgradeResolutionError(f"{context}.object_format must be 'sha1'")
    object_id = value.get("object_id")
    if not isinstance(object_id, str) or not SHA1_RE.fullmatch(object_id):
        raise UpgradeResolutionError(
            f"{context}.object_id must be exactly 40 lowercase hexadecimal characters"
        )
    return GitObjectIdentity(object_format="sha1", object_id=object_id)

def resolve_upgrade_request(target_repository: str) -> UpgradeRequest:
    if not isinstance(target_repository, str) or not target_repository.strip():
        raise UpgradeResolutionError("upgrade target must be one non-empty local path")
    text = target_repository.strip()
    lowered = text.lower()
    if "://" in text or lowered.startswith(("git@", "ssh:", "http:", "https:", "file:")):
        raise UpgradeResolutionError("upgrade target must be a local filesystem repository")
    target = Path(text).expanduser()
    try:
        target = target.resolve(strict=True)
    except OSError as exc:
        raise UpgradeResolutionError("upgrade target does not exist") from exc
    if not target.is_dir():
        raise UpgradeResolutionError("upgrade target must be a repository directory")
    if _git(target, "rev-parse", "--show-toplevel").returncode:
        raise UpgradeResolutionError("upgrade target is not a local Git repository")
    observed_root = _git(target, "rev-parse", "--show-toplevel").stdout.strip()
    if Path(observed_root).resolve() != target:
        raise UpgradeResolutionError(
            "upgrade target path must identify the Git repository root exactly"
        )
    return UpgradeRequest(target_repository=str(target))

def parse_framework_lineage(raw: dict[str, Any]) -> tuple[FrameworkLineageEntry, ...]:
    unknown_root = set(raw) - LINEAGE_ROOT_FIELDS
    if unknown_root:
        raise UpgradeResolutionError(
            f"framework lineage has unknown root field(s): {sorted(unknown_root)}"
        )
    if raw.get("schema_version") != "1":
        raise UpgradeResolutionError("framework lineage schema_version must be '1'")
    entries = raw.get("entries")
    if not isinstance(entries, list) or not entries:
        raise UpgradeResolutionError("framework lineage entries must be a non-empty array")
    parsed: list[FrameworkLineageEntry] = []
    seen: set[tuple[str, str]] = set()
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise UpgradeResolutionError(f"framework lineage entries[{index}] must be an object")
        if set(item) != LINEAGE_ENTRY_FIELDS:
            raise UpgradeResolutionError(
                f"framework lineage entries[{index}] must contain exactly "
                "framework_repository and framework_revision"
            )
        repository = item.get("framework_repository")
        if not isinstance(repository, str) or not repository.strip():
            raise UpgradeResolutionError(
                f"framework lineage entries[{index}].framework_repository "
                "must be a non-empty string"
            )
        revision = _parse_git_identity(
            item.get("framework_revision"),
            f"framework lineage entries[{index}].framework_revision",
        )
        key = (repository, revision.object_id)
        if key in seen:
            raise UpgradeResolutionError("framework lineage must not repeat an accepted identity")
        seen.add(key)
        parsed.append(
            FrameworkLineageEntry(
                framework_repository=repository,
                framework_revision=revision,
            )
        )
    return tuple(parsed)

def serialize_framework_lineage(entries: tuple[FrameworkLineageEntry, ...]) -> bytes:
    if not entries:
        raise UpgradeResolutionError("framework lineage cannot be empty")
    payload = {
        "schema_version": "1",
        "entries": [entry.to_dict() for entry in entries],
    }
    return (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8")

def _parse_provenance_bootstrap(raw: dict[str, Any]) -> FrameworkLineageEntry:
    if tuple(raw.keys()) != PROVENANCE_FIELDS:
        raise UpgradeResolutionError(
            "legacy provenance must contain exactly the canonical ordered provenance fields"
        )
    if raw.get("schema_version") != "2":
        raise UpgradeResolutionError("legacy provenance schema_version must be '2'")
    repository = raw.get("framework_repository")
    if not isinstance(repository, str) or not repository.strip():
        raise UpgradeResolutionError("legacy provenance framework_repository is invalid")
    revision = _parse_git_identity(
        raw.get("framework_revision"),
        "legacy provenance framework_revision",
    )
    return FrameworkLineageEntry(
        framework_repository=repository,
        framework_revision=revision,
    )

def _resolve_entry_material(entry: FrameworkLineageEntry) -> ResolvedSourceMaterial:
    repository = Path(entry.framework_repository).expanduser()
    try:
        repository = repository.resolve(strict=True)
    except OSError as exc:
        raise UpgradeResolutionError(
            "framework inventory authority repository cannot be resolved"
        ) from exc
    if not repository.is_dir():
        raise UpgradeResolutionError(
            "framework inventory authority repository is not a directory"
        )
    try:
        return resolve_source_material(
            str(repository),
            entry.framework_revision.object_id,
            (),
        )
    except InventoryError as exc:
        raise UpgradeResolutionError(
            f"framework inventory authority cannot be resolved: {exc}"
        ) from exc

def resolve_accepted_baseline(target_repository: str) -> BaselineResolution:
    request = resolve_upgrade_request(target_repository)
    target = Path(request.target_repository)
    lineage_path = target / LINEAGE_RELATIVE_PATH
    provenance_path = target / PROVENANCE_RELATIVE_PATH

    if lineage_path.exists() or lineage_path.is_symlink():
        if lineage_path.is_symlink() or not lineage_path.is_file():
            raise UpgradeResolutionError("framework lineage must be a regular file")
        lineage = parse_framework_lineage(
            _read_json_object(lineage_path, "framework lineage")
        )
        active = lineage[-1]
        source = "accepted-lineage"
    else:
        if provenance_path.is_symlink() or not provenance_path.is_file():
            raise UpgradeResolutionError(
                "target has neither accepted framework lineage nor canonical bootstrap provenance"
            )
        active = _parse_provenance_bootstrap(
            _read_json_object(provenance_path, "bootstrap provenance")
        )
        lineage = (active,)
        source = "legacy-provenance-bootstrap"

    material = _resolve_entry_material(active)
    return BaselineResolution(
        request=request,
        lineage=lineage,
        active_baseline=active,
        baseline_source=source,
        baseline_material=material,
    )
