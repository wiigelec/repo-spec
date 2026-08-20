\
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validation.checks.policy import RootValidationError, validate_repo_tree_integrity, validate_root_boundary

SOURCE_REQUIRED_FILES = {".gitignore", "AGENTS.md", "LICENSE", "README.md"}
SOURCE_REQUIRED_DIRS = {".github", "product", "reference", "repo", "scripts", "user", "validation"}

def _git(repo: Path, *args: str) -> str:
    p = subprocess.run(["git", "-C", str(repo), *args], text=True,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    return p.stdout.strip()

def _write_source_root(root: Path) -> None:
    for name in SOURCE_REQUIRED_FILES:
        (root / name).write_text(name + "\n", encoding="utf-8")
    for name in SOURCE_REQUIRED_DIRS:
        (root / name).mkdir()

def _write_framework_inventory(framework: Path, content: str) -> None:
    source = framework / "repo/scripts/tool.py"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(content, encoding="utf-8")
    manifest = framework / "product/src/initializer/framework-inventory.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"schema_version":"1","entries":[{
        "material_key":"repo-tool","source_path":"repo/scripts/tool.py",
        "role":"validation-utility","operation":"copy-verbatim",
        "source_type":"blob","mode":"100644"}]}, indent=2)+"\n", encoding="utf-8")
    output = framework / "product/specs/product/level-1/initializer-output-inventory-v1.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"material_index":[{
        "material_key":"repo-tool","destination_path":"repo/scripts/tool.py",
        "producer":"framework-installation","operation":"copy-verbatim",
        "mode":"100644","required":True,"role":"validation-utility"}]}, indent=2)+"\n", encoding="utf-8")

def _make_framework(root: Path):
    framework = root / "framework"
    framework.mkdir()
    _git(framework,"init","-q")
    _git(framework,"config","user.email","validation@example.invalid")
    _git(framework,"config","user.name","Validation")
    _write_framework_inventory(framework,"baseline\n")
    _git(framework,"add","-A"); _git(framework,"commit","-qm","baseline")
    baseline = _git(framework,"rev-parse","HEAD")
    _write_framework_inventory(framework,"current\n")
    _git(framework,"add","-A"); _git(framework,"commit","-qm","current")
    current = _git(framework,"rev-parse","HEAD")
    return framework, baseline, current

def _build_bundle(source_checkout: Path, repo: Path, framework: Path, revision: str) -> None:
    product_scripts = source_checkout / "product/scripts"
    inserted = str(product_scripts) not in sys.path
    if inserted:
        sys.path.insert(0, str(product_scripts))
    try:
        from initializer.framework_authority import build_framework_authority_bundle
        build_framework_authority_bundle(str(framework), revision,
            repo / "repo/initializer/framework-authority" / revision)
    finally:
        if inserted:
            sys.path.remove(str(product_scripts))

def _make_initialized_fixture(source_checkout: Path, root: Path, name: str,
                              framework: Path, baseline: str, current: str,
                              *, add_unmanaged_drift=False) -> Path:
    repo = root / name
    repo.mkdir()
    _git(repo,"init","-q")
    _git(repo,"config","user.email","target@example.invalid")
    _git(repo,"config","user.name","Target")
    tool = repo / "repo/scripts/tool.py"
    tool.parent.mkdir(parents=True)
    tool.write_text("baseline\n", encoding="utf-8")
    _git(repo,"add","-A"); _git(repo,"commit","-qm","initialized baseline")
    tool.write_text("current\n", encoding="utf-8")
    lineage = repo / "repo/initializer/framework-lineage.json"
    lineage.parent.mkdir(parents=True, exist_ok=True)
    lineage.write_text(json.dumps({"schema_version":"1","entries":[
        {"framework_repository":str(framework.resolve()),"framework_revision":{"object_format":"sha1","object_id":baseline}},
        {"framework_repository":str(framework.resolve()),"framework_revision":{"object_format":"sha1","object_id":current}}
    ]}, indent=2)+"\n", encoding="utf-8")
    _build_bundle(source_checkout, repo, framework, baseline)
    _build_bundle(source_checkout, repo, framework, current)
    if add_unmanaged_drift:
        (repo / "repo/unmanaged.txt").write_text("unauthorized\n", encoding="utf-8")
    _git(repo,"add","-A"); _git(repo,"commit","-qm","framework reconciliation")
    return repo

class RootBoundaryTests(unittest.TestCase):
    def test_valid_source_root(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-boundary-") as td:
            repo=Path(td); _write_source_root(repo); validate_root_boundary(repo, initialized=False)
    def test_rejects_undeclared_file(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-boundary-") as td:
            repo=Path(td); _write_source_root(repo); (repo/"extra.txt").write_text("x\n")
            with self.assertRaisesRegex(RootValidationError,"undeclared top-level entries: extra.txt"):
                validate_root_boundary(repo, initialized=False)
    def test_rejects_legacy_docs(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-boundary-") as td:
            repo=Path(td); _write_source_root(repo); (repo/"docs").mkdir()
            with self.assertRaisesRegex(RootValidationError,"undeclared top-level entries: docs"):
                validate_root_boundary(repo, initialized=False)
    def test_rejects_missing_required_root(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-boundary-") as td:
            repo=Path(td); _write_source_root(repo); (repo/"README.md").unlink()
            with self.assertRaisesRegex(RootValidationError,"missing required top-level entries: README.md"):
                validate_root_boundary(repo, initialized=False)
    def test_rejects_wrong_kind(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-boundary-") as td:
            repo=Path(td); _write_source_root(repo); shutil.rmtree(repo/"user"); (repo/"user").write_text("x\n")
            with self.assertRaisesRegex(RootValidationError,"user \\(expected directory\\)"):
                validate_root_boundary(repo, initialized=False)

class InitializedTreeIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_checkout = Path(__file__).resolve().parents[3]
    def test_accepts_legal_managed_transition(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-integrity-") as td:
            root=Path(td); framework,baseline,current=_make_framework(root)
            repo=_make_initialized_fixture(self.source_checkout,root,"legal",framework,baseline,current)
            validate_repo_tree_integrity(repo)
    def test_rejects_unmanaged_drift(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-integrity-") as td:
            root=Path(td); framework,baseline,current=_make_framework(root)
            repo=_make_initialized_fixture(self.source_checkout,root,"drift",framework,baseline,current,add_unmanaged_drift=True)
            with self.assertRaisesRegex(RootValidationError,"outside initializer-managed authority"):
                validate_repo_tree_integrity(repo)
    def test_rejects_managed_tampering(self):
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-integrity-") as td:
            root=Path(td); framework,baseline,current=_make_framework(root)
            repo=_make_initialized_fixture(self.source_checkout,root,"tamper",framework,baseline,current)
            (repo/"repo/scripts/tool.py").write_text("tampered\n", encoding="utf-8")
            _git(repo,"add","-A"); _git(repo,"commit","-qm","tamper managed material")
            with self.assertRaisesRegex(RootValidationError,"does not match accepted framework authority"):
                validate_repo_tree_integrity(repo)

if __name__ == "__main__":
    unittest.main()
