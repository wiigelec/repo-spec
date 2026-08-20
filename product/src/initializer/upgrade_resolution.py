from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .inventory import InventoryError, ResolvedSourceMaterial, resolve_source_material
from .framework_authority import AUTHORITY_ROOT, FrameworkAuthorityError, load_committed_framework_authority, materialize_bundle_repository
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

def _read_json_bytes(raw: bytes, context: str) -> dict[str, Any]:
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


def _read_committed_regular_file(
    repository: Path,
    relative_path: Path,
    context: str,
) -> bytes | None:
    path_text = relative_path.as_posix()
    tree = _git(repository, "ls-tree", "HEAD", "--", path_text)
    if tree.returncode:
        raise UpgradeResolutionError(
            f"cannot resolve committed {context}: {tree.stderr.strip()}"
        )
    line = tree.stdout.strip()
    if not line:
        return None

    fields = line.split(None, 3)
    if len(fields) != 4:
        raise UpgradeResolutionError(f"committed {context} tree entry is invalid")
    mode, object_type, _object_id, observed_path = fields
    if observed_path != path_text:
        raise UpgradeResolutionError(f"committed {context} path is ambiguous")
    if object_type != "blob" or mode not in {"100644", "100755"}:
        raise UpgradeResolutionError(f"committed {context} must be a regular file")

    p = subprocess.run(
        ["git", "-C", str(repository), "show", f"HEAD:{path_text}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise UpgradeResolutionError(
            f"cannot read committed {context}: "
            f"{p.stderr.decode('utf-8', errors='replace').strip()}"
        )
    return p.stdout

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

def _resolve_entry_material(
    entry: FrameworkLineageEntry,
    *,
    target_repository: Path | None = None,
    prefer_portable_authority: bool = False,
) -> ResolvedSourceMaterial:
    if prefer_portable_authority and target_repository is not None:
        bundle_index = (
            AUTHORITY_ROOT
            / entry.framework_revision.object_id
            / "bundle.json"
        )
        committed_index = _read_committed_regular_file(
            target_repository,
            bundle_index,
            "framework-authority bundle index",
        )
        if committed_index is not None:
            try:
                bundle = load_committed_framework_authority(
                    target_repository,
                    entry.framework_revision.object_id,
                )
                repository = materialize_bundle_repository(bundle)
                return resolve_source_material(
                    repository,
                    entry.framework_revision.object_id,
                    (),
                    require_full_connectivity=False,
                )
            except (FrameworkAuthorityError, InventoryError) as exc:
                raise UpgradeResolutionError(
                    f"repository-local framework authority cannot be resolved: {exc}"
                ) from exc
        # No committed bundle means this accepted lineage entry predates the
        # transportable representation. Exact locally resolvable recorded
        # authority remains eligible for governed backfill under UPG-TFA-009.

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
    lineage_raw = _read_committed_regular_file(
        target,
        LINEAGE_RELATIVE_PATH,
        "framework lineage",
    )
    if lineage_raw is not None:
        lineage = parse_framework_lineage(
            _read_json_bytes(lineage_raw, "framework lineage")
        )
        active = lineage[-1]
        source = "accepted-lineage"
        portable = True
    else:
        provenance_raw = _read_committed_regular_file(
            target,
            PROVENANCE_RELATIVE_PATH,
            "bootstrap provenance",
        )
        if provenance_raw is None:
            raise UpgradeResolutionError(
                "target has neither accepted framework lineage nor canonical bootstrap provenance"
            )
        active = _parse_provenance_bootstrap(
            _read_json_bytes(provenance_raw, "bootstrap provenance")
        )
        lineage = (active,)
        source = "legacy-provenance-bootstrap"
        portable = False

    material = _resolve_entry_material(
        active,
        target_repository=target,
        prefer_portable_authority=portable,
    )
    return BaselineResolution(
        request=request,
        lineage=lineage,
        active_baseline=active,
        baseline_source=source,
        baseline_material=material,
    )

OUTPUT_INVENTORY_SPEC_PATH = "product/specs/product/level-1/initializer-output-inventory-v1.json"
UPGRADE_QUALIFICATION_PATH = "product/scripts/initializer/upgrade-qualification.json"
DELTA_CLASSIFICATIONS = frozenset({"unchanged", "added", "modified", "removed", "retargeted"})


@dataclass(frozen=True)
class InventoryEndpoint:
    repository: str
    revision: GitObjectIdentity
    manifest_blob_id: str
    output_inventory_blob_id: str
    materials: dict[str, dict[str, object]]

    def to_dict(self) -> dict[str, object]:
        return {
            "repository": self.repository,
            "revision": self.revision.to_dict(),
            "manifest_blob_id": self.manifest_blob_id,
            "output_inventory_blob_id": self.output_inventory_blob_id,
            "material_keys": sorted(self.materials),
        }


@dataclass(frozen=True)
class ManagedMaterialDeltaEntry:
    material_key: str
    classification: str
    baseline: dict[str, object] | None
    target: dict[str, object] | None

    def to_dict(self) -> dict[str, object]:
        return {
            "material_key": self.material_key,
            "classification": self.classification,
            "baseline": self.baseline,
            "target": self.target,
        }


@dataclass(frozen=True)
class QualificationDecision:
    material_key: str
    disposition: str | None
    order: int | None

    def to_dict(self) -> dict[str, object]:
        return {
            "material_key": self.material_key,
            "disposition": self.disposition,
            "order": self.order,
        }


@dataclass(frozen=True)
class UpgradeSetResolution:
    baseline: BaselineResolution
    reconciliation_target: ResolvedSourceMaterial
    baseline_endpoint: InventoryEndpoint
    target_endpoint: InventoryEndpoint
    delta: tuple[ManagedMaterialDeltaEntry, ...]
    qualification: tuple[QualificationDecision, ...]
    selected_material_keys: tuple[str, ...]
    excluded_material_keys: tuple[str, ...]
    deferred_material_keys: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {
            "baseline_revision": self.baseline.active_baseline.framework_revision.to_dict(),
            "reconciliation_target_revision": {
                "object_format": "sha1",
                "object_id": self.reconciliation_target.commit_id,
            },
            "baseline_endpoint": self.baseline_endpoint.to_dict(),
            "target_endpoint": self.target_endpoint.to_dict(),
            "delta": [entry.to_dict() for entry in self.delta],
            "qualification": [decision.to_dict() for decision in self.qualification],
            "selected_material_keys": list(self.selected_material_keys),
            "excluded_material_keys": list(self.excluded_material_keys),
            "deferred_material_keys": list(self.deferred_material_keys),
        }


def _git_text_at(repository: str, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", repository, *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise UpgradeResolutionError(
            f"git {' '.join(args)} failed for framework endpoint: {p.stderr.strip()}"
        )
    return p.stdout.strip()


def _commit_blob_id(repository: str, revision: str, path: str) -> str:
    value = _git_text_at(repository, "rev-parse", "--verify", f"{revision}:{path}")
    if not SHA1_RE.fullmatch(value):
        raise UpgradeResolutionError(f"commit blob identity is invalid for {path}")
    obj_type = _git_text_at(repository, "cat-file", "-t", value)
    if obj_type != "blob":
        raise UpgradeResolutionError(f"commit path is not a blob: {path}")
    return value


def _read_commit_json_object(repository: str, revision: str, path: str) -> dict[str, Any]:
    blob_id = _commit_blob_id(repository, revision, path)
    p = subprocess.run(
        ["git", "-C", repository, "cat-file", "blob", blob_id],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        raise UpgradeResolutionError(f"cannot read commit JSON blob: {path}")
    try:
        value = json.loads(p.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UpgradeResolutionError(f"invalid UTF-8 JSON at commit path: {path}") from exc
    if not isinstance(value, dict):
        raise UpgradeResolutionError(f"commit JSON must contain one object: {path}")
    return value


def _optional_commit_json_object(
    repository: str,
    revision: str,
    path: str,
) -> dict[str, Any] | None:
    p = subprocess.run(
        ["git", "-C", repository, "rev-parse", "--verify", f"{revision}:{path}"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if p.returncode:
        return None
    return _read_commit_json_object(repository, revision, path)


def _build_inventory_endpoint(source: ResolvedSourceMaterial) -> InventoryEndpoint:
    output = _read_commit_json_object(
        source.repository,
        source.commit_id,
        OUTPUT_INVENTORY_SPEC_PATH,
    )
    material_index = output.get("material_index")
    if not isinstance(material_index, list):
        raise UpgradeResolutionError("output inventory material_index must be an array")

    manifest_by_key = {entry.material_key: entry for entry in source.manifest}
    output_by_key: dict[str, dict[str, object]] = {}
    for index, raw in enumerate(material_index):
        if not isinstance(raw, dict):
            raise UpgradeResolutionError(f"output material_index[{index}] must be an object")
        key = raw.get("material_key")
        if not isinstance(key, str) or not key:
            raise UpgradeResolutionError(
                f"output material_index[{index}].material_key must be a non-empty string"
            )
        if key in output_by_key:
            raise UpgradeResolutionError(f"duplicate output material_key: {key}")
        output_by_key[key] = raw

    if set(output_by_key) != set(manifest_by_key):
        raise UpgradeResolutionError(
            "manifest/output material_key authority is inconsistent at inventory endpoint"
        )

    materials: dict[str, dict[str, object]] = {}
    for key in sorted(output_by_key):
        output_entry = output_by_key[key]
        manifest_entry = manifest_by_key[key]
        destination_path = output_entry.get("destination_path")
        if not isinstance(destination_path, str) or not destination_path:
            raise UpgradeResolutionError(
                f"output material {key!r} has invalid destination_path"
            )
        source_blob_id = _commit_blob_id(
            source.repository,
            source.commit_id,
            manifest_entry.source_path,
        )
        materials[key] = {
            "material_key": key,
            "destination_path": destination_path,
            "producer": output_entry.get("producer"),
            "operation": output_entry.get("operation"),
            "mode": output_entry.get("mode"),
            "required": output_entry.get("required"),
            "role": output_entry.get("role"),
            "source_path": manifest_entry.source_path,
            "source_type": manifest_entry.source_type,
            "profile": manifest_entry.profile,
            "exclusion_rationale": manifest_entry.exclusion_rationale,
            "source_blob_id": source_blob_id,
        }

    return InventoryEndpoint(
        repository=source.repository,
        revision=GitObjectIdentity("sha1", source.commit_id),
        manifest_blob_id=_commit_blob_id(
            source.repository,
            source.commit_id,
            "product/src/initializer/framework-inventory.json",
        ),
        output_inventory_blob_id=_commit_blob_id(
            source.repository,
            source.commit_id,
            OUTPUT_INVENTORY_SPEC_PATH,
        ),
        materials=materials,
    )


def _material_definition_without_destination(
    evidence: dict[str, object],
) -> tuple[tuple[str, object], ...]:
    return tuple(
        (key, evidence.get(key))
        for key in (
            "producer",
            "operation",
            "mode",
            "required",
            "role",
            "source_path",
            "source_type",
            "profile",
            "exclusion_rationale",
            "source_blob_id",
        )
    )


def build_managed_material_delta(
    baseline_endpoint: InventoryEndpoint,
    target_endpoint: InventoryEndpoint,
) -> tuple[ManagedMaterialDeltaEntry, ...]:
    entries: list[ManagedMaterialDeltaEntry] = []
    for key in sorted(set(baseline_endpoint.materials) | set(target_endpoint.materials)):
        before = baseline_endpoint.materials.get(key)
        after = target_endpoint.materials.get(key)
        if before is None:
            classification = "added"
        elif after is None:
            classification = "removed"
        elif before["destination_path"] != after["destination_path"]:
            classification = "retargeted"
        elif (
            _material_definition_without_destination(before)
            == _material_definition_without_destination(after)
        ):
            classification = "unchanged"
        else:
            classification = "modified"
        entries.append(
            ManagedMaterialDeltaEntry(
                material_key=key,
                classification=classification,
                baseline=before,
                target=after,
            )
        )
    return tuple(entries)


def _load_target_qualification(
    source: ResolvedSourceMaterial,
    delta: tuple[ManagedMaterialDeltaEntry, ...],
) -> tuple[QualificationDecision, ...]:
    raw = _optional_commit_json_object(
        source.repository,
        source.commit_id,
        UPGRADE_QUALIFICATION_PATH,
    )
    if raw is None:
        return ()

    if set(raw) != {"schema_version", "transitions"}:
        raise UpgradeResolutionError(
            "upgrade qualification must contain exactly schema_version and transitions"
        )
    if raw.get("schema_version") != "1":
        raise UpgradeResolutionError("upgrade qualification schema_version must be '1'")
    transitions = raw.get("transitions")
    if not isinstance(transitions, list):
        raise UpgradeResolutionError("upgrade qualification transitions must be an array")

    by_key = {entry.material_key: entry for entry in delta}
    seen: set[str] = set()
    decisions: list[QualificationDecision] = []
    for index, item in enumerate(transitions):
        if not isinstance(item, dict):
            raise UpgradeResolutionError(
                f"upgrade qualification transitions[{index}] must be an object"
            )
        if set(item) - {"material_key", "disposition", "order"}:
            raise UpgradeResolutionError(
                f"upgrade qualification transitions[{index}] has unknown fields"
            )
        key = item.get("material_key")
        if not isinstance(key, str) or not key:
            raise UpgradeResolutionError(
                f"upgrade qualification transitions[{index}].material_key is invalid"
            )
        if key in seen:
            raise UpgradeResolutionError(
                f"duplicate upgrade qualification material_key: {key}"
            )
        seen.add(key)
        delta_entry = by_key.get(key)
        if delta_entry is None:
            raise UpgradeResolutionError(
                f"upgrade qualification references unmanaged material: {key}"
            )
        if delta_entry.classification == "unchanged":
            raise UpgradeResolutionError(
                f"upgrade qualification references non-transition material: {key}"
            )

        disposition = item.get("disposition")
        if disposition is not None and disposition not in {"exclude", "defer"}:
            raise UpgradeResolutionError(
                f"upgrade qualification disposition is invalid for {key}"
            )
        order = item.get("order")
        if order is not None and (
            isinstance(order, bool) or not isinstance(order, int) or order < 0
        ):
            raise UpgradeResolutionError(
                f"upgrade qualification order must be a non-negative integer for {key}"
            )
        if disposition is None and order is None:
            raise UpgradeResolutionError(
                f"upgrade qualification must constrain or order transition: {key}"
            )
        decisions.append(
            QualificationDecision(
                material_key=key,
                disposition=disposition,
                order=order,
            )
        )
    return tuple(decisions)


def resolve_upgrade_set(
    target_repository: str,
    executing_framework_repository: str,
) -> UpgradeSetResolution:
    from .inventory import resolve_executing_framework_material

    baseline = resolve_accepted_baseline(target_repository)
    try:
        target_source = resolve_executing_framework_material(
            executing_framework_repository
        )
    except InventoryError as exc:
        raise UpgradeResolutionError(
            f"reconciliation-target framework cannot be resolved: {exc}"
        ) from exc

    baseline_endpoint = _build_inventory_endpoint(baseline.baseline_material)
    target_endpoint = _build_inventory_endpoint(target_source)
    delta = build_managed_material_delta(baseline_endpoint, target_endpoint)
    qualification = _load_target_qualification(target_source, delta)

    decisions = {decision.material_key: decision for decision in qualification}
    selected: list[tuple[int, str]] = []
    excluded: list[str] = []
    deferred: list[str] = []

    for entry in delta:
        if entry.classification == "unchanged":
            continue
        decision = decisions.get(entry.material_key)
        if decision and decision.disposition == "exclude":
            excluded.append(entry.material_key)
            continue
        if decision and decision.disposition == "defer":
            deferred.append(entry.material_key)
            continue
        order = decision.order if decision and decision.order is not None else 2**31
        selected.append((order, entry.material_key))

    selected_keys = tuple(
        key for _order, key in sorted(selected, key=lambda item: (item[0], item[1]))
    )

    return UpgradeSetResolution(
        baseline=baseline,
        reconciliation_target=target_source,
        baseline_endpoint=baseline_endpoint,
        target_endpoint=target_endpoint,
        delta=delta,
        qualification=qualification,
        selected_material_keys=selected_keys,
        excluded_material_keys=tuple(sorted(excluded)),
        deferred_material_keys=tuple(sorted(deferred)),
    )
def serialize_upgrade_set_evidence(resolution: UpgradeSetResolution) -> bytes:
    return (
        json.dumps(
            resolution.to_dict(),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )
        + "\n"
    ).encode("utf-8")


def upgrade_set_evidence_fingerprint(resolution: UpgradeSetResolution) -> str:
    import hashlib

    return hashlib.sha256(serialize_upgrade_set_evidence(resolution)).hexdigest()
