#!/usr/bin/env python3
# Transportable repository-root and immutable-framework validation.

from __future__ import annotations

import base64
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

SOURCE_REQUIRED_FILES = {".gitignore", "AGENTS.md", "LICENSE", "README.md"}
SOURCE_REQUIRED_DIRS = {".github", "product", "reference", "repo", "scripts", "user"}
INITIALIZED_REQUIRED_FILES = {".gitignore", "AGENTS.md", "LICENSE", "README.md"}
INITIALIZED_REQUIRED_DIRS = {".github", "product", "repo", "scripts", "user"}
IGNORED_ROOT_ENTRIES = {".git"}


class RootValidationError(RuntimeError):
    pass


def _git(repo_root: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RootValidationError(f"git command failed: git {' '.join(args)}: {detail}")
    return result


def _is_initialized(repo_root: Path) -> bool:
    return not (repo_root / "reference").exists()


def validate_root_boundary(repo_root: Path, initialized: bool) -> None:
    required_files = INITIALIZED_REQUIRED_FILES if initialized else SOURCE_REQUIRED_FILES
    required_dirs = INITIALIZED_REQUIRED_DIRS if initialized else SOURCE_REQUIRED_DIRS
    actual = {
        path.name: path
        for path in repo_root.iterdir()
        if path.name not in IGNORED_ROOT_ENTRIES
    }
    expected = required_files | required_dirs

    missing = sorted(expected - set(actual))
    if missing:
        raise RootValidationError(
            "repository root boundary failed: missing required top-level entries: "
            + ", ".join(missing)
        )

    extra = sorted(set(actual) - expected)
    if extra:
        raise RootValidationError(
            "repository root boundary failed: undeclared top-level entries: "
            + ", ".join(extra)
        )

    wrong_kind: list[str] = []
    for name in sorted(required_files):
        if not actual[name].is_file():
            wrong_kind.append(f"{name} (expected file)")
    for name in sorted(required_dirs):
        if not actual[name].is_dir():
            wrong_kind.append(f"{name} (expected directory)")
    if wrong_kind:
        raise RootValidationError(
            "repository root boundary failed: wrong-kind top-level entries: "
            + ", ".join(wrong_kind)
        )

    print("ok: repository root boundary")


LINEAGE_RELATIVE_PATH = "repo/initializer/framework-lineage.json"
FRAMEWORK_INVENTORY_PATH = "product/scripts/initializer/framework-inventory.json"
OUTPUT_INVENTORY_PATH = "product/specs/product/level-1/initializer-output-inventory-v1.json"
SHA1_RE = re.compile(r"^[0-9a-f]{40}$")


def _git_bytes(
    repo_root: Path,
    *args: str,
    check: bool = True,
) -> subprocess.CompletedProcess[bytes]:
    result = subprocess.run(
        ["git", *args],
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        if not detail:
            detail = result.stdout.decode("utf-8", errors="replace").strip()
        raise RootValidationError(
            f"git command failed: git {' '.join(args)}: {detail}"
        )
    return result


def _read_json_at_revision(
    repository: Path,
    revision: str,
    relative_path: str,
    context: str,
) -> dict:
    result = _git_bytes(
        repository,
        "show",
        f"{revision}:{relative_path}",
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise RootValidationError(
            f"repo tree integrity failed: cannot resolve {context}"
            + (f": {detail}" if detail else "")
        )
    try:
        value = json.loads(result.stdout.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RootValidationError(
            f"repo tree integrity failed: invalid JSON in {context}"
        ) from exc
    if not isinstance(value, dict):
        raise RootValidationError(
            f"repo tree integrity failed: {context} must be one JSON object"
        )
    return value


def _parse_lineage_endpoint(entry: object, context: str) -> tuple[str, str]:
    if not isinstance(entry, dict) or set(entry) != {
        "framework_repository",
        "framework_revision",
    }:
        raise RootValidationError(
            f"repo tree integrity failed: {context} is invalid"
        )
    repository = entry.get("framework_repository")
    revision = entry.get("framework_revision")
    if not isinstance(repository, str) or not repository:
        raise RootValidationError(
            f"repo tree integrity failed: {context} framework repository is invalid"
        )
    if not isinstance(revision, dict) or set(revision) != {
        "object_format",
        "object_id",
    }:
        raise RootValidationError(
            f"repo tree integrity failed: {context} framework revision is invalid"
        )
    if revision.get("object_format") != "sha1":
        raise RootValidationError(
            f"repo tree integrity failed: {context} object format is not sha1"
        )
    object_id = revision.get("object_id")
    if not isinstance(object_id, str) or not SHA1_RE.fullmatch(object_id):
        raise RootValidationError(
            f"repo tree integrity failed: {context} object id is invalid"
        )
    return repository, object_id

def _read_framework_lineage(repo_root: Path) -> list[tuple[str, str]] | None:
    tree = _git(
        repo_root,
        "ls-tree",
        "HEAD",
        "--",
        LINEAGE_RELATIVE_PATH,
        check=False,
    )
    if tree.returncode != 0:
        raise RootValidationError(
            "repo tree integrity failed: cannot inspect framework lineage"
        )
    if not tree.stdout.strip():
        return None

    raw = _read_json_at_revision(
        repo_root,
        "HEAD",
        LINEAGE_RELATIVE_PATH,
        "committed framework lineage",
    )
    if set(raw) != {"schema_version", "entries"}:
        raise RootValidationError(
            "repo tree integrity failed: framework lineage root fields are invalid"
        )
    if raw.get("schema_version") != "1":
        raise RootValidationError(
            "repo tree integrity failed: framework lineage schema version is invalid"
        )
    entries = raw.get("entries")
    if not isinstance(entries, list) or not entries:
        raise RootValidationError(
            "repo tree integrity failed: framework lineage entries are invalid"
        )

    endpoints: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        endpoint = _parse_lineage_endpoint(
            entry,
            f"framework lineage entry {index}",
        )
        identity = (endpoint[0], endpoint[1])
        if identity in seen:
            raise RootValidationError(
                "repo tree integrity failed: framework lineage repeats an identity"
            )
        seen.add(identity)
        endpoints.append(endpoint)
    return endpoints



AUTHORITY_ROOT = "repo/initializer/framework-authority"

def _canonical_git_object_id(object_type: str, content: bytes) -> str:
    header = f"{object_type} {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()

def _parse_authority_tree(content: bytes) -> dict[str, tuple[str, str]]:
    result: dict[str, tuple[str, str]] = {}
    offset = 0
    while offset < len(content):
        space = content.find(b" ", offset)
        nul = content.find(b"\0", space + 1)
        if space < 0 or nul < 0 or nul + 21 > len(content):
            raise RootValidationError("repo tree integrity failed: malformed retained Git tree object")
        mode = content[offset:space].decode("ascii")
        name = content[space + 1:nul].decode("utf-8", "surrogateescape")
        oid = content[nul + 1:nul + 21].hex()
        if name in result:
            raise RootValidationError("repo tree integrity failed: retained Git tree repeats a name")
        result[name] = (mode, oid)
        offset = nul + 21
    return result

def _authority_commit_tree(content: bytes) -> str:
    for line in content.splitlines():
        if line.startswith(b"tree "):
            oid = line[5:].decode("ascii")
            if SHA1_RE.fullmatch(oid):
                return oid
            break
    raise RootValidationError("repo tree integrity failed: retained framework commit has invalid tree identity")

def _decode_authority_object(oid: str, raw: bytes) -> tuple[str, bytes]:
    try:
        record = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RootValidationError(
            f"repo tree integrity failed: malformed retained Git object record {oid}"
        ) from exc
    if not isinstance(record, dict) or set(record) != {"content_base64", "object_type"}:
        raise RootValidationError(
            f"repo tree integrity failed: malformed retained Git object record {oid}"
        )
    object_type = record.get("object_type")
    if object_type not in {"commit", "tree", "blob"}:
        raise RootValidationError(
            f"repo tree integrity failed: invalid retained Git object type {oid}"
        )
    try:
        content = base64.b64decode(record.get("content_base64"), validate=True)
    except Exception as exc:
        raise RootValidationError(
            f"repo tree integrity failed: invalid retained Git object bytes {oid}"
        ) from exc
    if _canonical_git_object_id(object_type, content) != oid:
        raise RootValidationError(
            f"repo tree integrity failed: retained Git object identity mismatch {oid}"
        )
    return object_type, content

def _authority_resolve_path(
    objects: dict[str, tuple[str, bytes]],
    commit_oid: str,
    relative_path: str,
) -> tuple[str, bytes, str, set[str]]:
    commit = objects.get(commit_oid)
    if commit is None or commit[0] != "commit":
        raise RootValidationError(
            "repo tree integrity failed: accepted lineage commit object is missing from authority"
        )
    current = _authority_commit_tree(commit[1])
    visited = {commit_oid, current}
    parts = Path(relative_path).parts
    if (
        not parts
        or Path(relative_path).is_absolute()
        or any(part in {"", ".", ".."} for part in parts)
    ):
        raise RootValidationError(
            f"repo tree integrity failed: invalid authority path {relative_path}"
        )
    for index, name in enumerate(parts):
        tree = objects.get(current)
        if tree is None or tree[0] != "tree":
            raise RootValidationError(
                f"repo tree integrity failed: required authority tree object is missing {current}"
            )
        entries = _parse_authority_tree(tree[1])
        if name not in entries:
            raise RootValidationError(
                f"repo tree integrity failed: required authority path is missing {relative_path}"
            )
        mode, oid = entries[name]
        visited.add(oid)
        if index < len(parts) - 1:
            current = oid
        else:
            obj = objects.get(oid)
            if obj is None or obj[0] != "blob":
                raise RootValidationError(
                    f"repo tree integrity failed: authority path is not a retained blob {relative_path}"
                )
            return mode, obj[1], oid, visited
    raise RootValidationError("repo tree integrity failed: unreachable authority path")

def _read_committed_authority_bundle(
    repo_root: Path,
    framework_revision: str,
    context: str,
) -> dict:
    prefix = f"{AUTHORITY_ROOT}/{framework_revision}"
    listing = _git(
        repo_root,
        "ls-tree",
        "-r",
        "--name-only",
        "HEAD",
        "--",
        prefix,
        check=False,
    )
    if listing.returncode != 0:
        raise RootValidationError(
            f"repo tree integrity failed: cannot inspect {context} framework authority"
        )
    files = [line for line in listing.stdout.splitlines() if line]
    index_path = f"{prefix}/bundle.json"
    if index_path not in files:
        raise RootValidationError(
            f"repo tree integrity failed: required {context} framework authority bundle is missing"
        )

    objects: dict[str, tuple[str, bytes]] = {}
    bundle_paths = set(files)
    marker = f"{prefix}/objects/"
    for path in files:
        if path == index_path:
            continue
        if not path.startswith(marker):
            raise RootValidationError(
                f"repo tree integrity failed: unexpected {context} framework authority path {path}"
            )
        oid = path[len(marker):]
        if "/" in oid or not SHA1_RE.fullmatch(oid):
            raise RootValidationError(
                f"repo tree integrity failed: invalid {context} authority object path"
            )
        raw = _git_bytes(repo_root, "show", f"HEAD:{path}").stdout
        objects[oid] = _decode_authority_object(oid, raw)

    used: set[str] = set()

    def read(path: str) -> tuple[str, bytes, str]:
        mode, content, oid, visited = _authority_resolve_path(
            objects, framework_revision, path
        )
        used.update(visited)
        return mode, content, oid

    _m_mode, manifest_bytes, _m_oid = read(FRAMEWORK_INVENTORY_PATH)
    _o_mode, output_bytes, _o_oid = read(OUTPUT_INVENTORY_PATH)
    try:
        manifest = json.loads(manifest_bytes.decode("utf-8"))
        output = json.loads(output_bytes.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RootValidationError(
            f"repo tree integrity failed: invalid inventory JSON in {context} authority"
        ) from exc
    if not isinstance(manifest, dict) or not isinstance(output, dict):
        raise RootValidationError(
            f"repo tree integrity failed: invalid inventory shape in {context} authority"
        )

    framework_entries = manifest.get("entries")
    output_entries = output.get("material_index")
    if not isinstance(framework_entries, list) or not isinstance(output_entries, list):
        raise RootValidationError(
            f"repo tree integrity failed: invalid inventory arrays in {context} authority"
        )

    source_by_key: dict[str, dict] = {}
    for entry in framework_entries:
        if not isinstance(entry, dict):
            raise RootValidationError(
                f"repo tree integrity failed: invalid framework entry in {context} authority"
            )
        key = entry.get("material_key")
        source_path = entry.get("source_path")
        if (
            not isinstance(key, str)
            or not key
            or key in source_by_key
            or not isinstance(source_path, str)
            or not source_path
        ):
            raise RootValidationError(
                f"repo tree integrity failed: invalid framework material identity in {context} authority"
            )
        source_by_key[key] = entry
        source_mode, _source_bytes, _source_oid = read(source_path)
        if source_mode != entry.get("mode"):
            raise RootValidationError(
                f"repo tree integrity failed: source mode mismatch in {context} authority: {source_path}"
            )

    if set(objects) != used:
        raise RootValidationError(
            f"repo tree integrity failed: {context} framework authority closure is not minimal"
        )

    raw_index = _git_bytes(repo_root, "show", f"HEAD:{index_path}").stdout
    try:
        index = json.loads(raw_index.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise RootValidationError(
            f"repo tree integrity failed: malformed {context} framework authority index"
        ) from exc
    expected_index = {
        "schema_version": "1",
        "framework_revision": framework_revision,
        "required_paths": sorted(
            {FRAMEWORK_INVENTORY_PATH, OUTPUT_INVENTORY_PATH}
            | {entry["source_path"] for entry in framework_entries}
        ),
        "object_ids": sorted(objects),
    }
    if index != expected_index:
        raise RootValidationError(
            f"repo tree integrity failed: inconsistent {context} framework authority index"
        )

    managed: dict[str, tuple[str, str]] = {}
    for item in output_entries:
        if not isinstance(item, dict):
            raise RootValidationError(
                f"repo tree integrity failed: invalid output entry in {context} authority"
            )
        key = item.get("material_key")
        destination = item.get("destination_path")
        if not isinstance(destination, str) or not destination.startswith("repo/"):
            continue
        source = source_by_key.get(key)
        if source is None:
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed material lacks source entry {key}"
            )
        if (
            source.get("operation") != "copy-verbatim"
            or source.get("source_type") != "blob"
            or item.get("operation") != "copy-verbatim"
        ):
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed material uses unsupported integrity semantics {key}"
            )
        mode = item.get("mode")
        if mode not in {"100644", "100755"} or mode != source.get("mode"):
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed material has invalid mode {key}"
            )
        if destination in managed:
            raise RootValidationError(
                f"repo tree integrity failed: {context} duplicates managed destination {destination}"
            )
        managed[destination] = (source["source_path"], mode)

    return {
        "managed": managed,
        "paths": bundle_paths,
        "read": read,
    }

def _tree_entry(
    repository: Path,
    revision: str,
    relative_path: str,
) -> tuple[str, str] | None:
    result = _git(
        repository,
        "ls-tree",
        revision,
        "--",
        relative_path,
        check=False,
    )
    if result.returncode != 0:
        raise RootValidationError(
            f"repo tree integrity failed: cannot inspect {revision}:{relative_path}"
        )
    line = result.stdout.strip()
    if not line:
        return None
    fields = line.split(None, 3)
    if len(fields) != 4 or fields[3] != relative_path:
        raise RootValidationError(
            f"repo tree integrity failed: ambiguous tree entry for {relative_path}"
        )
    mode, object_type, _object_id, _path = fields
    return mode, object_type

def _verify_current_managed_repo_content_from_authority(
    repo_root: Path,
    bundle: dict,
) -> None:
    for destination, (source_path, expected_mode) in sorted(bundle["managed"].items()):
        target_entry = _tree_entry(repo_root, "HEAD", destination)
        if target_entry is None:
            raise RootValidationError(
                f"repo tree integrity failed: managed repo material is missing: {destination}"
            )
        target_mode, target_type = target_entry
        if target_type != "blob" or target_mode != expected_mode:
            raise RootValidationError(
                f"repo tree integrity failed: managed repo material mode/type mismatch: {destination}"
            )
        source_mode, source_bytes, _source_oid = bundle["read"](source_path)
        if source_mode != expected_mode:
            raise RootValidationError(
                f"repo tree integrity failed: framework source mode mismatch: {source_path}"
            )
        target_bytes = _git_bytes(repo_root, "show", f"HEAD:{destination}").stdout
        if target_bytes != source_bytes:
            raise RootValidationError(
                f"repo tree integrity failed: managed repo material does not match accepted framework authority: {destination}"
            )

def validate_repo_tree_integrity(repo_root: Path) -> None:
    if not (repo_root / ".git").exists():
        raise RootValidationError(
            "repo tree integrity failed: initialized repository is missing .git"
        )

    roots = [
        line.strip()
        for line in _git(
            repo_root,
            "rev-list",
            "--max-parents=0",
            "HEAD",
        ).stdout.splitlines()
        if line.strip()
    ]
    if len(roots) != 1:
        raise RootValidationError(
            f"repo tree integrity failed: expected exactly one root commit, found {len(roots)}"
        )
    root_commit = roots[0]

    baseline_result = _git(
        repo_root,
        "rev-parse",
        f"{root_commit}:repo",
        check=False,
    )
    if baseline_result.returncode != 0:
        raise RootValidationError(
            "repo tree integrity failed: repo/ is absent from the root commit"
        )
    baseline_tree = baseline_result.stdout.strip()

    current_result = _git(
        repo_root,
        "rev-parse",
        "HEAD:repo",
        check=False,
    )
    if current_result.returncode != 0:
        raise RootValidationError(
            "repo tree integrity failed: repo/ is absent from HEAD"
        )
    current_tree = current_result.stdout.strip()

    lineage = _read_framework_lineage(repo_root)
    if lineage is None:
        if current_tree != baseline_tree:
            raise RootValidationError(
                "repo tree integrity failed: committed repo/ tree differs from initialized baseline"
            )
    else:
        bundles: list[dict] = []
        authority_paths: set[str] = set()
        for index, (_recorded_repository, framework_revision) in enumerate(lineage):
            bundle = _read_committed_authority_bundle(
                repo_root,
                framework_revision,
                f"lineage entry {index}",
            )
            bundles.append(bundle)
            authority_paths.update(bundle["paths"])

        baseline_managed = bundles[0]["managed"]
        current_managed = bundles[-1]["managed"]
        allowed_changed = (
            set(baseline_managed)
            | set(current_managed)
            | authority_paths
            | {LINEAGE_RELATIVE_PATH}
        )

        changed = _git(
            repo_root,
            "diff",
            "--name-only",
            root_commit,
            "HEAD",
            "--",
            "repo",
        ).stdout.splitlines()
        unauthorized = sorted(
            path for path in changed if path and path not in allowed_changed
        )
        if unauthorized:
            raise RootValidationError(
                "repo tree integrity failed: committed repo/ drift is outside "
                "initializer-managed authority: "
                + ", ".join(unauthorized)
            )

        _verify_current_managed_repo_content_from_authority(
            repo_root,
            bundles[-1],
        )

        for removed in sorted(set(baseline_managed) - set(current_managed)):
            if _tree_entry(repo_root, "HEAD", removed) is not None:
                raise RootValidationError(
                    "repo tree integrity failed: removed managed repo material remains present: "
                    + removed
                )

    status = _git(
        repo_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
        "--",
        "repo",
    ).stdout.strip()
    if status:
        raise RootValidationError(
            "repo tree integrity failed: working tree changes exist under repo/"
        )

    if lineage is None:
        print(f"ok: immutable repo tree ({baseline_tree})")
    else:
        print(
            "ok: managed repo tree "
            f"(active framework {lineage[-1][1]})"
        )



def validate(repo_root: Path) -> bool:
    initialized = _is_initialized(repo_root)
    validate_root_boundary(repo_root, initialized)
    if initialized:
        validate_repo_tree_integrity(repo_root)
    return initialized


def main(argv: list[str]) -> int:
    if len(argv) > 2:
        print(f"validation error: unknown argument: {argv[2]}", file=sys.stderr)
        return 1

    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()

    try:
        validate(repo_root)
        return 0
    except (RootValidationError, OSError) as exc:
        print(f"validation error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
