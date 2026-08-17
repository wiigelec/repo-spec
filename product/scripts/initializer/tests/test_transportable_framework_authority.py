from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from initializer.framework_authority import (
    FrameworkAuthorityError,
    build_framework_authority_bundle,
    materialize_bundle_repository,
    verify_bundle_directory,
)
from initializer.inventory import resolve_source_material


def _run(repo: Path, *args: str) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return p.stdout.strip()


def _fixture_framework(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "framework"
    repo.mkdir()
    _run(repo, "init", "-q")
    _run(repo, "config", "user.name", "Test")
    _run(repo, "config", "user.email", "test@example.invalid")
    (repo / "product/scripts/initializer").mkdir(parents=True)
    (repo / "product/specs/product/level-1").mkdir(parents=True)
    (repo / "repo/scripts").mkdir(parents=True)
    manifest = {
        "schema_version": "1",
        "entries": [{
            "material_key": "m",
            "source_path": "repo/scripts/x",
            "role": "runtime-framework",
            "operation": "copy-verbatim",
            "source_type": "blob",
            "mode": "100644",
        }],
    }
    output = {
        "material_index": [{
            "material_key": "m",
            "destination_path": "repo/scripts/x",
            "producer": "initializer",
            "operation": "copy-verbatim",
            "mode": "100644",
            "required": True,
            "role": "runtime-framework",
        }],
    }
    (repo / "product/scripts/initializer/framework-inventory.json").write_text(json.dumps(manifest) + "\n")
    (repo / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(json.dumps(output) + "\n")
    (repo / "repo/scripts/x").write_text("authority\n")
    _run(repo, "add", ".")
    _run(repo, "commit", "-q", "-m", "fixture")
    return repo, _run(repo, "rev-parse", "HEAD")


def test_bundle_is_deterministic_and_materializable(tmp_path: Path):
    source, sha = _fixture_framework(tmp_path)
    first = tmp_path / "a" / sha
    second = tmp_path / "b" / sha
    build_framework_authority_bundle(str(source), sha, first)
    build_framework_authority_bundle(str(source), sha, second)
    one = {p.relative_to(first): p.read_bytes() for p in first.rglob("*") if p.is_file()}
    two = {p.relative_to(second): p.read_bytes() for p in second.rglob("*") if p.is_file()}
    assert one == two
    bundle = verify_bundle_directory(first, sha)
    material_repo = materialize_bundle_repository(bundle)
    resolved = resolve_source_material(material_repo, sha, (), require_full_connectivity=False)
    assert resolved.commit_id == sha
    assert resolved.manifest[0].source_path == "repo/scripts/x"


def test_bundle_tamper_fails_closed(tmp_path: Path):
    source, sha = _fixture_framework(tmp_path)
    bundle_dir = tmp_path / "bundle" / sha
    build_framework_authority_bundle(str(source), sha, bundle_dir)
    obj = next((bundle_dir / "objects").iterdir())
    raw = json.loads(obj.read_text())
    raw["content_base64"] = raw["content_base64"][:-4] + "AAAA"
    obj.write_text(json.dumps(raw))
    with pytest.raises(FrameworkAuthorityError):
        verify_bundle_directory(bundle_dir, sha)
