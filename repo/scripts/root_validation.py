#!/usr/bin/env python3
# Transportable repository-root and immutable-framework validation.

from __future__ import annotations

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


def _parse_lineage_endpoint(entry: object, context: str) -> tuple[Path, str]:
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

    source = Path(repository).expanduser()
    try:
        source = source.resolve(strict=True)
    except OSError as exc:
        raise RootValidationError(
            f"repo tree integrity failed: {context} framework repository cannot be resolved"
        ) from exc
    if not source.is_dir():
        raise RootValidationError(
            f"repo tree integrity failed: {context} framework repository is not a directory"
        )

    exact = _git(
        source,
        "rev-parse",
        "--verify",
        f"{object_id}^{{commit}}",
        check=False,
    )
    if exact.returncode != 0 or exact.stdout.strip() != object_id:
        raise RootValidationError(
            f"repo tree integrity failed: {context} framework revision cannot be resolved exactly"
        )
    return source, object_id


def _read_framework_lineage(repo_root: Path) -> list[tuple[Path, str]] | None:
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

    endpoints: list[tuple[Path, str]] = []
    seen: set[tuple[str, str]] = set()
    for index, entry in enumerate(entries):
        endpoint = _parse_lineage_endpoint(
            entry,
            f"framework lineage entry {index}",
        )
        identity = (str(endpoint[0]), endpoint[1])
        if identity in seen:
            raise RootValidationError(
                "repo tree integrity failed: framework lineage repeats an identity"
            )
        seen.add(identity)
        endpoints.append(endpoint)
    return endpoints


def _inventory_by_key(
    framework_repository: Path,
    framework_revision: str,
    context: str,
) -> tuple[dict[str, dict], dict[str, dict]]:
    framework = _read_json_at_revision(
        framework_repository,
        framework_revision,
        FRAMEWORK_INVENTORY_PATH,
        f"{context} framework inventory",
    )
    output = _read_json_at_revision(
        framework_repository,
        framework_revision,
        OUTPUT_INVENTORY_PATH,
        f"{context} output inventory",
    )

    framework_entries = framework.get("entries")
    output_entries = output.get("material_index")
    if not isinstance(framework_entries, list) or not isinstance(output_entries, list):
        raise RootValidationError(
            f"repo tree integrity failed: {context} inventory shape is invalid"
        )

    def keyed(entries: list, label: str) -> dict[str, dict]:
        result: dict[str, dict] = {}
        for entry in entries:
            if not isinstance(entry, dict):
                raise RootValidationError(
                    f"repo tree integrity failed: {context} {label} entry is invalid"
                )
            key = entry.get("material_key")
            if not isinstance(key, str) or not key or key in result:
                raise RootValidationError(
                    f"repo tree integrity failed: {context} {label} material identity is invalid"
                )
            result[key] = entry
        return result

    return keyed(framework_entries, "framework"), keyed(output_entries, "output")


def _repo_managed_destinations(
    framework_repository: Path,
    framework_revision: str,
    context: str,
) -> dict[str, tuple[str, str]]:
    framework, output = _inventory_by_key(
        framework_repository,
        framework_revision,
        context,
    )
    managed: dict[str, tuple[str, str]] = {}

    for key, output_entry in output.items():
        destination = output_entry.get("destination_path")
        if not isinstance(destination, str) or not destination.startswith("repo/"):
            continue

        source_entry = framework.get(key)
        if source_entry is None:
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed repo material {key} "
                "has no framework source entry"
            )
        source_path = source_entry.get("source_path")
        if not isinstance(source_path, str) or not source_path:
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed repo material {key} "
                "has an invalid source path"
            )
        if (
            source_entry.get("operation") != "copy-verbatim"
            or source_entry.get("source_type") != "blob"
            or output_entry.get("operation") != "copy-verbatim"
        ):
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed repo material {key} "
                "uses unsupported integrity semantics"
            )
        mode = output_entry.get("mode")
        if mode not in {"100644", "100755"}:
            raise RootValidationError(
                f"repo tree integrity failed: {context} managed repo material {key} "
                "has an invalid destination mode"
            )
        if destination in managed:
            raise RootValidationError(
                f"repo tree integrity failed: {context} duplicates managed repo destination "
                f"{destination}"
            )
        managed[destination] = (source_path, mode)

    return managed


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


def _verify_current_managed_repo_content(
    repo_root: Path,
    framework_repository: Path,
    framework_revision: str,
    current_managed: dict[str, tuple[str, str]],
) -> None:
    for destination, (source_path, expected_mode) in sorted(current_managed.items()):
        target_entry = _tree_entry(repo_root, "HEAD", destination)
        if target_entry is None:
            raise RootValidationError(
                f"repo tree integrity failed: managed repo material is missing: {destination}"
            )
        target_mode, target_type = target_entry
        if target_type != "blob" or target_mode != expected_mode:
            raise RootValidationError(
                f"repo tree integrity failed: managed repo material mode/type mismatch: "
                f"{destination}"
            )

        source_entry = _tree_entry(
            framework_repository,
            framework_revision,
            source_path,
        )
        if source_entry is None or source_entry[1] != "blob":
            raise RootValidationError(
                f"repo tree integrity failed: framework source blob is missing: {source_path}"
            )

        source_bytes = _git_bytes(
            framework_repository,
            "show",
            f"{framework_revision}:{source_path}",
        ).stdout
        target_bytes = _git_bytes(
            repo_root,
            "show",
            f"HEAD:{destination}",
        ).stdout
        if target_bytes != source_bytes:
            raise RootValidationError(
                f"repo tree integrity failed: managed repo material does not match "
                f"accepted framework authority: {destination}"
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
        baseline_repository, baseline_revision = lineage[0]
        current_repository, current_revision = lineage[-1]

        baseline_managed = _repo_managed_destinations(
            baseline_repository,
            baseline_revision,
            "baseline",
        )
        current_managed = _repo_managed_destinations(
            current_repository,
            current_revision,
            "active framework",
        )
        allowed_changed = (
            set(baseline_managed)
            | set(current_managed)
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

        _verify_current_managed_repo_content(
            repo_root,
            current_repository,
            current_revision,
            current_managed,
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
