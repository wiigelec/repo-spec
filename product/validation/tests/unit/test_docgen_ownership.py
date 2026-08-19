from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


def tree_digest(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result


def find_material(entries: list[dict], material_key: str) -> dict:
    matches = [entry for entry in entries if entry["material_key"] == material_key]
    assert len(matches) == 1, (material_key, len(matches))
    return matches[0]


def run_docgen_ownership_tests(repo_root: Path) -> None:
    repo_docgen = (repo_root / "repo/scripts/docgen.py").read_text()
    product_docgen = (repo_root / "product/scripts/docgen.py").read_text()
    root_entrypoint = (repo_root / "scripts/generate-docs").read_text()
    repo_entrypoint = (repo_root / "repo/scripts/generate-docs").read_text()
    product_entrypoint = (repo_root / "product/scripts/generate-docs").read_text()

    assert "load_product_specs" not in repo_docgen
    assert "product/derived" not in repo_docgen
    assert "product/scripts/docgen.py" not in repo_entrypoint
    assert 'repo/scripts/docgen.py' in repo_entrypoint

    assert "from repo_model" not in product_docgen
    assert 'repo/derived/specs/' not in product_docgen
    assert "repo/scripts/docgen.py" not in product_entrypoint
    assert 'product/scripts/docgen.py' in product_entrypoint

    assert '"$root/repo/scripts/generate-docs" "$mode"' in root_entrypoint
    assert '"$root/product/scripts/generate-docs" "$mode"' in root_entrypoint

    framework = json.loads(
        (repo_root / "product/scripts/initializer/framework-inventory.json").read_text()
    )
    output = json.loads(
        (repo_root / "product/specs/product/level-1/initializer-output-inventory-v1.json").read_text()
    )

    framework_entries = framework["entries"]
    output_entries = output["material_index"]

    framework_keys = [entry["material_key"] for entry in framework_entries]
    output_keys = [entry["material_key"] for entry in output_entries]
    assert len(framework_keys) == len(set(framework_keys))
    assert len(output_keys) == len(set(output_keys))
    assert set(framework_keys) == set(output_keys)

    destinations = [entry["destination_path"] for entry in output_entries]
    assert len(destinations) == len(set(destinations))

    expected = {
        "repo-generate-docs": (
            "product/scripts/initializer/stubs/repo-generate-docs",
            "repo/scripts/generate-docs",
        ),
        "root-generate-docs": (
            "scripts/generate-docs",
            "scripts/generate-docs",
        ),
        "product-docgen": (
            "product/scripts/docgen.py",
            "product/scripts/docgen.py",
        ),
        "product-generate-docs": (
            "product/scripts/generate-docs",
            "product/scripts/generate-docs",
        ),
    }

    for material_key, (source_path, destination_path) in expected.items():
        material = find_material(framework_entries, material_key)
        installed = find_material(output_entries, material_key)
        assert material["source_path"] == source_path
        assert installed["destination_path"] == destination_path
        assert material["operation"] == installed["operation"] == "copy-verbatim"
        assert material["mode"] == installed["mode"]
        assert material["role"] == installed["role"] == "documentation-support"

    stub = repo_root / "product/scripts/initializer/stubs/repo-generate-docs"
    before = tree_digest(repo_root / "repo")
    for mode in ("--write", "--check"):
        completed = subprocess.run(
            [str(stub), mode],
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert completed.returncode == 0, (mode, completed.stdout, completed.stderr)
        assert tree_digest(repo_root / "repo") == before

    rejected = subprocess.run(
        [str(stub), "--unsupported"],
        cwd=repo_root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert rejected.returncode != 0

    for command in (
        ["repo/scripts/generate-docs", "--check"],
        ["product/scripts/generate-docs", "--check"],
        ["scripts/generate-docs", "--check"],
    ):
        completed = subprocess.run(
            command,
            cwd=repo_root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        assert completed.returncode == 0, (command, completed.stdout, completed.stderr)

    print("ok: documentation generation ownership tests")
