#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path
import json

from repo_model import RepositoryError, resolve_repo_path


class GitHubProfileError(Exception):
    pass


PROFILE_MANIFEST_PATH = "repo/profiles/github/manifest.json"


def fail(message: str) -> None:
    raise GitHubProfileError(message)


def load_profile_manifest(repo_root: Path) -> dict:
    try:
        manifest = json.loads(resolve_repo_path(repo_root, PROFILE_MANIFEST_PATH).read_text())
    except (OSError, json.JSONDecodeError, RepositoryError) as exc:
        fail(f"missing required profile manifest: {PROFILE_MANIFEST_PATH}")

    if manifest.get("profile_id") != "github":
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    if manifest.get("source_root") != "repo/profiles/github/":
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    if manifest.get("installed_adapter_root") != ".github/":
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    if manifest.get("adapter_generation_policy") != "source-to-adapter":
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")

    deployment_state = manifest.get("deployment_state")
    if not isinstance(deployment_state, dict):
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    for key in (
        "ruleset_desired_state_format",
        "branch_protection_desired_state_format",
        "inspection_procedure",
        "plan_apply_separation",
        "mutation_evidence_record_fields",
        "rollback_and_post_change_verification",
    ):
        if key not in deployment_state:
            fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")

    managed = manifest.get("managed_adapters")
    if not isinstance(managed, list) or not managed:
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    unmanaged = manifest.get("unmanaged_files", [])
    if not isinstance(unmanaged, list):
        fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    for entry in managed:
        if not isinstance(entry, dict):
            fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
        if not isinstance(entry.get("source"), str) or not isinstance(entry.get("installed"), str):
            fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    for item in unmanaged:
        if not isinstance(item, str) or not item:
            fail(f"invalid profile manifest: {PROFILE_MANIFEST_PATH}")
    return manifest


def load_adapter_pairs(repo_root: Path) -> list[tuple[str, str, str]]:
    manifest = load_profile_manifest(repo_root)
    pairs: list[tuple[str, str, str]] = []
    entries = sorted(manifest["managed_adapters"], key=lambda entry: entry["installed"])
    for entry in entries:
        source_rel = entry["source"]
        target_rel = entry["installed"]
        try:
            source = resolve_repo_path(repo_root, source_rel)
            source_text = source.read_text()
        except (OSError, RepositoryError) as exc:
            fail(f"missing required profile source: {source_rel}")
        pairs.append((source_rel, target_rel, source_text))
    return pairs


def render_profile_adapters(repo_root: Path) -> list[tuple[str, str]]:
    return [(target_rel, source_text) for _source_rel, target_rel, source_text in load_adapter_pairs(repo_root)]


def write_profile_adapters(repo_root: Path) -> None:
    for target_rel, content in render_profile_adapters(repo_root):
        target = resolve_repo_path(repo_root, target_rel)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content)


def actual_installed_paths(repo_root: Path) -> list[str]:
    manifest = load_profile_manifest(repo_root)
    root = repo_root / manifest["installed_adapter_root"]
    if not root.exists():
        return []
    return sorted(path.relative_to(repo_root).as_posix() for path in root.rglob("*") if path.is_file())


def check_profile_freshness(repo_root: Path) -> None:
    rendered = render_profile_adapters(repo_root)
    expected_paths = [path for path, _content in rendered]
    actual_paths = actual_installed_paths(repo_root)
    manifest = load_profile_manifest(repo_root)
    unmanaged = set(manifest.get("unmanaged_files", []))

    missing = sorted(set(expected_paths) - set(actual_paths))
    extra = sorted(set(actual_paths) - set(expected_paths) - unmanaged)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append(f"missing managed adapter(s): {', '.join(missing)}")
        if extra:
            parts.append(f"orphaned managed adapter(s): {', '.join(extra)}")
        fail("; ".join(parts))

    for target_rel, content in rendered:
        target = resolve_repo_path(repo_root, target_rel)
        if not target.exists() or target.read_text() != content:
            source_rel = target_rel.replace(".github/", "repo/profiles/github/") if target_rel.startswith(".github/") else target_rel
            fail(f"stale generated adapter: source {source_rel} -> output {target_rel}")


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    mode = argv[2] if len(argv) > 2 else "--write"

    try:
        if mode == "--write":
            write_profile_adapters(repo_root)
            return 0
        if mode == "--check":
            check_profile_freshness(repo_root)
            return 0
        fail(f"unknown mode: {mode}")
    except GitHubProfileError as exc:
        print(f"github profile error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
