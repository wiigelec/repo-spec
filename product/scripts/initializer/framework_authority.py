from __future__ import annotations

import atexit
import base64
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .inventory import (
    MANIFEST_PATH,
    OUTPUT_INVENTORY_SPEC_PATH,
    ResolvedSourceMaterial,
    validate_material_manifest,
)

AUTHORITY_ROOT = Path("repo/initializer/framework-authority")
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")
BUNDLE_SCHEMA = "1"
_TEMP_REPOSITORIES: list[Path] = []


class FrameworkAuthorityError(RuntimeError):
    pass


@dataclass(frozen=True)
class GitObject:
    object_id: str
    object_type: str
    content: bytes


@dataclass(frozen=True)
class FrameworkAuthorityBundle:
    framework_revision: str
    objects: dict[str, GitObject]
    manifest: tuple
    output_inventory: dict[str, Any]

    def read_path(self, path: str) -> tuple[str, bytes, str]:
        mode, oid, _visited = _resolve_path(self.objects, self.framework_revision, path)
        obj = self.objects[oid]
        if obj.object_type != "blob":
            raise FrameworkAuthorityError(f"authority path is not a blob: {path}")
        return mode, obj.content, oid


def _canonical_object_id(object_type: str, content: bytes) -> str:
    header = f"{object_type} {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _git_bytes(repository: Path, *args: str) -> bytes:
    env = os.environ.copy()
    env["GIT_NO_REPLACE_OBJECTS"] = "1"
    env["GIT_NO_LAZY_FETCH"] = "1"
    env["GIT_TERMINAL_PROMPT"] = "0"
    p = subprocess.run(
        ["git", "-C", str(repository), *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        check=False,
    )
    if p.returncode:
        raise FrameworkAuthorityError(
            f"git {' '.join(args)} failed: {p.stderr.decode('utf-8', 'replace').strip()}"
        )
    return p.stdout


def _source_object(repository: Path, oid: str) -> GitObject:
    object_type = _git_bytes(repository, "cat-file", "-t", oid).decode("ascii").strip()
    if object_type not in {"commit", "tree", "blob"}:
        raise FrameworkAuthorityError(f"unsupported retained Git object type: {object_type}")
    content = _git_bytes(repository, "cat-file", object_type, oid)
    if _canonical_object_id(object_type, content) != oid:
        raise FrameworkAuthorityError(f"source Git object identity mismatch: {oid}")
    return GitObject(oid, object_type, content)


def _commit_tree(content: bytes) -> str:
    for line in content.splitlines():
        if line.startswith(b"tree "):
            oid = line[5:].decode("ascii")
            if SHA1_RE.fullmatch(oid):
                return oid
            break
    raise FrameworkAuthorityError("retained commit object has invalid tree identity")


def _parse_tree(content: bytes) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    offset = 0
    while offset < len(content):
        space = content.find(b" ", offset)
        nul = content.find(b"\0", space + 1)
        if space < 0 or nul < 0 or nul + 21 > len(content):
            raise FrameworkAuthorityError("retained tree object is malformed")
        mode = content[offset:space].decode("ascii")
        name = content[space + 1:nul].decode("utf-8", "surrogateescape")
        oid = content[nul + 1:nul + 21].hex()
        if name in result:
            raise FrameworkAuthorityError("retained tree object repeats a name")
        result[name] = (mode, oid)
        offset = nul + 21
    return result


def _resolve_path(objects: dict[str, GitObject], commit_oid: str, path: str):
    commit = objects.get(commit_oid)
    if commit is None or commit.object_type != "commit":
        raise FrameworkAuthorityError("accepted lineage commit object is missing")
    current = _commit_tree(commit.content)
    visited = {commit_oid, current}
    parts = Path(path).parts
    if not parts or Path(path).is_absolute() or any(part in {"", ".", ".."} for part in parts):
        raise FrameworkAuthorityError(f"invalid authority path: {path}")
    for index, name in enumerate(parts):
        tree = objects.get(current)
        if tree is None or tree.object_type != "tree":
            raise FrameworkAuthorityError(f"required authority tree object is missing: {current}")
        entries = _parse_tree(tree.content)
        if name not in entries:
            raise FrameworkAuthorityError(f"required authority path is missing: {path}")
        mode, oid = entries[name]
        visited.add(oid)
        if index < len(parts) - 1:
            if mode not in {"40000", "040000"}:
                raise FrameworkAuthorityError(f"authority path component is not a tree: {path}")
            current = oid
        else:
            return mode, oid, visited
    raise FrameworkAuthorityError("unreachable authority traversal")


def _collect_path(repository: Path, commit_oid: str, path: str, objects: dict[str, GitObject]) -> None:
    if commit_oid not in objects:
        objects[commit_oid] = _source_object(repository, commit_oid)
    current = _commit_tree(objects[commit_oid].content)
    if current not in objects:
        objects[current] = _source_object(repository, current)
    for index, name in enumerate(Path(path).parts):
        entries = _parse_tree(objects[current].content)
        if name not in entries:
            raise FrameworkAuthorityError(f"source commit lacks required authority path: {path}")
        _mode, oid = entries[name]
        if oid not in objects:
            objects[oid] = _source_object(repository, oid)
        if index < len(Path(path).parts) - 1:
            if objects[oid].object_type != "tree":
                raise FrameworkAuthorityError(f"source path component is not a tree: {path}")
            current = oid
        elif objects[oid].object_type != "blob":
            raise FrameworkAuthorityError(f"required source path is not a blob: {path}")


def _decode_json(raw: bytes, context: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FrameworkAuthorityError(f"invalid JSON in {context}") from exc
    if not isinstance(value, dict):
        raise FrameworkAuthorityError(f"{context} must be one JSON object")
    return value


def _bundle_record(obj: GitObject) -> bytes:
    payload = {
        "content_base64": base64.b64encode(obj.content).decode("ascii"),
        "object_type": obj.object_type,
    }
    return (json.dumps(payload, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def build_framework_authority_bundle(source_repository: str, commit_oid: str, bundle_dir: Path) -> None:
    source = Path(source_repository).resolve()
    if not SHA1_RE.fullmatch(commit_oid):
        raise FrameworkAuthorityError("framework revision must be exact lowercase SHA-1")
    exact = _git_bytes(source, "rev-parse", "--verify", f"{commit_oid}^{{commit}}").decode().strip()
    if exact != commit_oid:
        raise FrameworkAuthorityError("framework revision does not resolve exactly")

    objects: dict[str, GitObject] = {}
    _collect_path(source, commit_oid, MANIFEST_PATH, objects)
    _collect_path(source, commit_oid, OUTPUT_INVENTORY_SPEC_PATH, objects)
    manifest_raw = _decode_json(_git_bytes(source, "show", f"{commit_oid}:{MANIFEST_PATH}"), MANIFEST_PATH)
    output_raw = _decode_json(_git_bytes(source, "show", f"{commit_oid}:{OUTPUT_INVENTORY_SPEC_PATH}"), OUTPUT_INVENTORY_SPEC_PATH)
    manifest = validate_material_manifest(manifest_raw, output_raw)
    required = [MANIFEST_PATH, OUTPUT_INVENTORY_SPEC_PATH]
    for entry in manifest:
        required.append(entry.source_path)
        _collect_path(source, commit_oid, entry.source_path, objects)

    bundle_dir.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=bundle_dir.name + ".tmp-", dir=bundle_dir.parent))
    try:
        (temp_dir / "objects").mkdir()
        for oid in sorted(objects):
            (temp_dir / "objects" / oid).write_bytes(_bundle_record(objects[oid]))
        index = {
            "schema_version": BUNDLE_SCHEMA,
            "framework_revision": commit_oid,
            "required_paths": sorted(set(required)),
            "object_ids": sorted(objects),
        }
        (temp_dir / "bundle.json").write_text(
            json.dumps(index, sort_keys=True, separators=(",", ":")) + "\n",
            encoding="utf-8",
        )
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        temp_dir.replace(bundle_dir)
    except Exception:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def _load_object_record(oid: str, raw: bytes) -> GitObject:
    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise FrameworkAuthorityError(f"malformed retained object record: {oid}") from exc
    if not isinstance(payload, dict) or set(payload) != {"content_base64", "object_type"}:
        raise FrameworkAuthorityError(f"malformed retained object record: {oid}")
    object_type = payload["object_type"]
    if object_type not in {"commit", "tree", "blob"}:
        raise FrameworkAuthorityError(f"invalid retained object type: {oid}")
    try:
        content = base64.b64decode(payload["content_base64"], validate=True)
    except Exception as exc:
        raise FrameworkAuthorityError(f"invalid retained object content: {oid}") from exc
    if _canonical_object_id(object_type, content) != oid:
        raise FrameworkAuthorityError(f"retained Git object identity mismatch: {oid}")
    return GitObject(oid, object_type, content)


def _verify_loaded(objects: dict[str, GitObject], commit_oid: str) -> FrameworkAuthorityBundle:
    used: set[str] = set()

    def read(path: str):
        mode, oid, visited = _resolve_path(objects, commit_oid, path)
        used.update(visited)
        obj = objects[oid]
        if obj.object_type != "blob":
            raise FrameworkAuthorityError(f"authority path is not a blob: {path}")
        return mode, obj.content, oid

    _mode, manifest_bytes, _oid = read(MANIFEST_PATH)
    _mode, output_bytes, _oid = read(OUTPUT_INVENTORY_SPEC_PATH)
    manifest_raw = _decode_json(manifest_bytes, MANIFEST_PATH)
    output_raw = _decode_json(output_bytes, OUTPUT_INVENTORY_SPEC_PATH)
    manifest = validate_material_manifest(manifest_raw, output_raw)
    for entry in manifest:
        mode, _content, _oid = read(entry.source_path)
        if mode != entry.mode:
            raise FrameworkAuthorityError(f"authority source mode mismatch: {entry.source_path}")
    if set(objects) != used:
        raise FrameworkAuthorityError("framework-authority object closure is not minimal/deterministic")
    return FrameworkAuthorityBundle(commit_oid, objects, manifest, output_raw)


def verify_bundle_directory(bundle_dir: Path, commit_oid: str) -> FrameworkAuthorityBundle:
    if bundle_dir.name != commit_oid or not SHA1_RE.fullmatch(commit_oid):
        raise FrameworkAuthorityError("framework-authority bundle path is not anchored to accepted commit")
    try:
        index = json.loads((bundle_dir / "bundle.json").read_text(encoding="utf-8"))
    except Exception as exc:
        raise FrameworkAuthorityError("framework-authority bundle index is missing or malformed") from exc
    object_dir = bundle_dir / "objects"
    if not object_dir.is_dir():
        raise FrameworkAuthorityError("framework-authority objects directory is missing")
    objects = {}
    for path in sorted(object_dir.iterdir()):
        if not path.is_file() or not SHA1_RE.fullmatch(path.name):
            raise FrameworkAuthorityError("framework-authority object storage is malformed")
        objects[path.name] = _load_object_record(path.name, path.read_bytes())
    bundle = _verify_loaded(objects, commit_oid)
    paths = [MANIFEST_PATH, OUTPUT_INVENTORY_SPEC_PATH] + [entry.source_path for entry in bundle.manifest]
    expected = {
        "schema_version": BUNDLE_SCHEMA,
        "framework_revision": commit_oid,
        "required_paths": sorted(set(paths)),
        "object_ids": sorted(objects),
    }
    if index != expected:
        raise FrameworkAuthorityError("framework-authority subordinate index is inconsistent")
    return bundle


def _git_committed_files(repo: Path, revision: str, prefix: str) -> list[str]:
    p = subprocess.run(
        ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", revision, "--", prefix],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode:
        raise FrameworkAuthorityError("cannot inspect committed framework-authority bundle")
    return [line for line in p.stdout.splitlines() if line]


def _git_show(repo: Path, revision: str, path: str) -> bytes:
    p = subprocess.run(
        ["git", "-C", str(repo), "show", f"{revision}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if p.returncode:
        raise FrameworkAuthorityError(f"cannot read committed authority path: {path}")
    return p.stdout


def load_committed_framework_authority(repo_root: Path, commit_oid: str, revision: str = "HEAD") -> FrameworkAuthorityBundle:
    prefix = (AUTHORITY_ROOT / commit_oid).as_posix()
    files = _git_committed_files(repo_root, revision, prefix)
    index_path = f"{prefix}/bundle.json"
    if index_path not in files:
        raise FrameworkAuthorityError("required framework-authority bundle is missing")
    objects = {}
    marker = f"{prefix}/objects/"
    for path in files:
        if path == index_path:
            continue
        if not path.startswith(marker):
            raise FrameworkAuthorityError("unexpected framework-authority bundle path")
        oid = path[len(marker):]
        if "/" in oid or not SHA1_RE.fullmatch(oid):
            raise FrameworkAuthorityError("invalid framework-authority object path")
        objects[oid] = _load_object_record(oid, _git_show(repo_root, revision, path))
    bundle = _verify_loaded(objects, commit_oid)
    index = _decode_json(_git_show(repo_root, revision, index_path), "framework-authority bundle index")
    paths = [MANIFEST_PATH, OUTPUT_INVENTORY_SPEC_PATH] + [entry.source_path for entry in bundle.manifest]
    expected = {
        "schema_version": BUNDLE_SCHEMA,
        "framework_revision": commit_oid,
        "required_paths": sorted(set(paths)),
        "object_ids": sorted(objects),
    }
    if index != expected:
        raise FrameworkAuthorityError("framework-authority subordinate index is inconsistent")
    return bundle


def materialize_bundle_repository(bundle: FrameworkAuthorityBundle) -> str:
    root = Path(tempfile.mkdtemp(prefix="repo-spec-framework-authority-"))
    _TEMP_REPOSITORIES.append(root)
    p = subprocess.run(["git", "init", "--bare", "-q", str(root)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if p.returncode:
        raise FrameworkAuthorityError("cannot initialize temporary authority object repository")
    for oid, obj in bundle.objects.items():
        envelope = f"{obj.object_type} {len(obj.content)}\0".encode("ascii") + obj.content
        target = root / "objects" / oid[:2] / oid[2:]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(zlib.compress(envelope))
    return str(root)


def cleanup_temp_repositories() -> None:
    while _TEMP_REPOSITORIES:
        shutil.rmtree(_TEMP_REPOSITORIES.pop(), ignore_errors=True)


atexit.register(cleanup_temp_repositories)
