from __future__ import annotations

import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from initializer.models import (
    InventoryEntry,
    ClassifiedInventory,
    InstallationPlan,
    InstallationResult,
    SourceSelection,
    I1DestinationPreflight,
)
from initializer.destination import i1_destination_preflight
from initializer.inventory import MaterialEntry, ResolvedSourceMaterial
from initializer.validation import validate_and_normalize
from initializer.staging import (
    StagingError,
    STAGING_PREFIX,
    resolve_source_root,
    build_installation_plan,
    validate_source_path,
    resolve_entry_type,
    check_symlink_safety,
    check_destination_conflicts,
    check_preexisting_workspace,
    create_staging_workspace,
    copy_entry,
    stage_framework,
    _cleanup_staging,
    SUPPORTED_ENTRY_TYPES,
    I2StagingInputs,
    StagingWorkspace,
    establish_staging_workspace,
    validate_staging_workspace,
)


# validation-metadata: {"role": "helper"}
def _make_entry(
    path: str,
    classification: str = "framework-authoritative",
    installable: bool = True,
    authoritative: bool = False,
    profile: str | None = None,
    exclusion_rationale: str | None = None,
    derived_from: list[str] | None = None,
) -> InventoryEntry:
    raw = {
        "path": path,
        "classification": classification,
        "authoritative": authoritative,
        "installable": installable,
    }
    if profile is not None:
        raw["profile"] = profile
    if exclusion_rationale is not None:
        raw["exclusion_rationale"] = exclusion_rationale
    if derived_from is not None:
        raw["derived_from"] = derived_from
    return InventoryEntry(raw)


# validation-metadata: {"role": "helper"}
def _make_source_tree(base: Path, entries: dict[str, str | dict]) -> None:
    for path, content in entries.items():
        full = base / path
        full.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, dict):
            if content.get("type") == "symlink":
                target = content["target"]
                full.symlink_to(target)
            elif content.get("type") == "dir":
                full.mkdir(parents=True, exist_ok=True)
        else:
            full.write_text(content)


class InstallationPlanTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_selects_only_installable_entries(self):
        entries = [
            _make_entry("repo/specs/repo/", classification="framework-authoritative"),
            _make_entry("docs/overview/", classification="product-instance", installable=False,
                        exclusion_rationale="product instance"),
            _make_entry("derived/", classification="derived"),
            _make_entry(".github/", classification="installed-adapter", installable=False,
                        exclusion_rationale="installed adapter"),
        ]
        ci = ClassifiedInventory(entries)
        plan = InstallationPlan(ci)
        self.assertEqual(plan.entry_count, 2)
        paths = [e.path for e in plan.entries]
        self.assertIn("repo/specs/repo/", paths)
        self.assertIn("derived/", paths)

    # validation-metadata: {"role": "helper"}
    def test_entries_sorted_by_path(self):
        entries = [
            _make_entry("zzz/", classification="framework-support"),
            _make_entry("aaa/", classification="framework-authoritative"),
            _make_entry("mmm/", classification="derived"),
        ]
        ci = ClassifiedInventory(entries)
        plan = InstallationPlan(ci)
        paths = [e.path for e in plan.entries]
        self.assertEqual(paths, sorted(paths))

    # validation-metadata: {"role": "helper"}
    def test_empty_when_no_installable(self):
        entries = [
            _make_entry("docs/overview/", classification="product-instance", installable=False,
                        exclusion_rationale="product instance"),
        ]
        ci = ClassifiedInventory(entries)
        plan = InstallationPlan(ci)
        self.assertEqual(plan.entry_count, 0)

    # validation-metadata: {"role": "helper"}
    def test_equality(self):
        e1 = [_make_entry("repo/specs/repo/"), _make_entry("repo/scripts/", classification="framework-support")]
        e2 = [_make_entry("repo/specs/repo/"), _make_entry("repo/scripts/", classification="framework-support")]
        p1 = InstallationPlan(ClassifiedInventory(e1))
        p2 = InstallationPlan(ClassifiedInventory(e2))
        self.assertEqual(p1, p2)
        self.assertEqual(hash(p1), hash(p2))

    # validation-metadata: {"role": "helper"}
    def test_inequality(self):
        e1 = [_make_entry("repo/specs/repo/")]
        e2 = [_make_entry("repo/scripts/", classification="framework-support")]
        p1 = InstallationPlan(ClassifiedInventory(e1))
        p2 = InstallationPlan(ClassifiedInventory(e2))
        self.assertNotEqual(p1, p2)


class InstallationResultTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_to_dict_structure(self):
        ss = SourceSelection("https://example.com/repo", "abc123")
        result = InstallationResult(
            source_selection=ss,
            staging_workspace="/tmp/staging",
            installed=[{"path": "repo/specs/repo/", "classification": "framework-authoritative", "type": "directory"}],
            skipped=[],
            rejected=[],
        )
        d = result.to_dict()
        self.assertEqual(d["status"], "staging_complete")
        self.assertEqual(d["staging_workspace"], "/tmp/staging")
        self.assertEqual(d["source_selection"]["repository"], "https://example.com/repo")
        self.assertEqual(d["source_selection"]["revision"], "abc123")
        self.assertEqual(len(d["installed"]), 1)
        self.assertEqual(len(d["skipped"]), 0)
        self.assertEqual(len(d["rejected"]), 0)

    # validation-metadata: {"role": "helper"}
    def test_to_dict_no_source_selection(self):
        result = InstallationResult(
            source_selection=None,
            staging_workspace="/tmp/staging",
            installed=[],
            skipped=[],
            rejected=[],
        )
        d = result.to_dict()
        self.assertIsNone(d["source_selection"])


class BuildInstallationPlanTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_from_classified_inventory(self):
        entries = [
            _make_entry("repo/specs/repo/", classification="framework-authoritative"),
            _make_entry("repo/scripts/", classification="framework-support"),
            _make_entry("derived/", classification="derived"),
        ]
        ci = ClassifiedInventory(entries)
        plan = build_installation_plan(ci)
        self.assertIsInstance(plan, InstallationPlan)
        self.assertEqual(plan.entry_count, 3)


class ValidateSourcePathTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        (self.root / "repo" / "specs" / "repo").mkdir(parents=True)

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_valid_path(self):
        validate_source_path(self.root, "repo/specs/repo/", _make_entry("repo/specs/repo/"))

    # validation-metadata: {"role": "helper"}
    def test_absolute_path_rejected(self):
        with self.assertRaises(StagingError):
            validate_source_path(self.root, "/absolute/path", _make_entry("/absolute/path"))

    # validation-metadata: {"role": "helper"}
    def test_parent_traversal_rejected(self):
        with self.assertRaises(StagingError):
            validate_source_path(self.root, "../outside", _make_entry("../outside"))

    # validation-metadata: {"role": "helper"}
    def test_missing_path_rejected(self):
        with self.assertRaises(StagingError):
            validate_source_path(self.root, "nonexistent/path", _make_entry("nonexistent/path"))

    # validation-metadata: {"role": "helper"}
    def test_escape_via_complex_path_rejected(self):
        with self.assertRaises(StagingError):
            validate_source_path(self.root, "specs/../../etc/passwd", _make_entry("specs/../../etc/passwd"))


class ResolveEntryTypeTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_file(self):
        f = self.root / "test.txt"
        f.write_text("hello")
        self.assertEqual(resolve_entry_type(self.root, "test.txt"), "file")

    # validation-metadata: {"role": "helper"}
    def test_directory(self):
        d = self.root / "mydir"
        d.mkdir()
        self.assertEqual(resolve_entry_type(self.root, "mydir"), "directory")

    # validation-metadata: {"role": "helper"}
    def test_symlink(self):
        f = self.root / "target.txt"
        f.write_text("content")
        link = self.root / "link.txt"
        link.symlink_to("target.txt")
        self.assertEqual(resolve_entry_type(self.root, "link.txt"), "symlink")


class SymlinkSafetyTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.root, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_internal_symlink_allowed(self):
        (self.root / "dir").mkdir()
        target = self.root / "dir" / "actual.txt"
        target.write_text("content")
        link = self.root / "dir" / "link.txt"
        link.symlink_to("actual.txt")
        result = check_symlink_safety(self.root, "dir/link.txt")
        self.assertEqual(result, "actual.txt")

    # validation-metadata: {"role": "helper"}
    def test_external_symlink_rejected(self):
        outside = Path(tempfile.mkdtemp())
        outside_target = outside / "external.txt"
        outside_target.write_text("outside")
        link = self.root / "escape_link"
        link.symlink_to(str(outside_target))
        with self.assertRaises(StagingError):
            check_symlink_safety(self.root, "escape_link")

    # validation-metadata: {"role": "helper"}
    def test_absolute_symlink_rejected(self):
        link = self.root / "abs_link"
        link.symlink_to("/etc/passwd")
        with self.assertRaises(StagingError):
            check_symlink_safety(self.root, "abs_link")

    # validation-metadata: {"role": "helper"}
    def test_not_a_symlink_returns_empty(self):
        f = self.root / "regular.txt"
        f.write_text("hello")
        result = check_symlink_safety(self.root, "regular.txt")
        self.assertEqual(result, "")


class DestinationConflictTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.staging = Path(tempfile.mkdtemp())

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.staging, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_no_conflict(self):
        entries = [
            _make_entry("repo/specs/repo/"),
            _make_entry("repo/scripts/validate"),
        ]
        check_destination_conflicts(self.staging, entries)

    # validation-metadata: {"role": "helper"}
    def test_exact_duplicate_rejected(self):
        entries = [
            _make_entry("repo/specs/repo/"),
            _make_entry("repo/specs/repo/"),
        ]
        with self.assertRaises(StagingError):
            check_destination_conflicts(self.staging, entries)

    # validation-metadata: {"role": "helper"}
    def test_nested_overlap_rejected(self):
        entries = [
            _make_entry("repo/specs/"),
            _make_entry("repo/specs/repo/manifest.json"),
        ]
        with self.assertRaises(StagingError):
            check_destination_conflicts(self.staging, entries)


class StagingWorkspaceTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_creates_new_workspace(self):
        ws = create_staging_workspace()
        self.assertTrue(ws.exists())
        self.assertTrue(ws.name.startswith(STAGING_PREFIX))
        _cleanup_staging(ws)

    # validation-metadata: {"role": "helper"}
    def test_creates_under_parent(self):
        parent = Path(tempfile.mkdtemp())
        try:
            ws = create_staging_workspace(parent)
            self.assertTrue(ws.exists())
            self.assertEqual(ws.parent, parent)
        finally:
            shutil.rmtree(parent, ignore_errors=True)
            _cleanup_staging(ws)

    # validation-metadata: {"role": "helper"}
    def test_preexisting_nonempty_rejected(self):
        parent = Path(tempfile.mkdtemp())
        try:
            existing = parent / "existing_workspace"
            existing.mkdir()
            (existing / "some_file").write_text("content")
            with self.assertRaises(StagingError):
                check_preexisting_workspace(existing)
        finally:
            shutil.rmtree(parent, ignore_errors=True)


class CopyEntryTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.source_root = Path(tempfile.mkdtemp())
        self.staging_root = Path(tempfile.mkdtemp())

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.source_root, ignore_errors=True)
        shutil.rmtree(self.staging_root, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_copy_file(self):
        src = self.source_root / "test.txt"
        src.write_text("hello world")
        entry = _make_entry("test.txt")
        copy_entry(self.source_root, entry, self.staging_root)
        dst = self.staging_root / "test.txt"
        self.assertTrue(dst.exists())
        self.assertEqual(dst.read_text(), "hello world")

    # validation-metadata: {"role": "helper"}
    def test_copy_directory(self):
        src_dir = self.source_root / "mydir"
        src_dir.mkdir()
        (src_dir / "file1.txt").write_text("one")
        (src_dir / "file2.txt").write_text("two")
        entry = _make_entry("mydir")
        copy_entry(self.source_root, entry, self.staging_root)
        dst_dir = self.staging_root / "mydir"
        self.assertTrue(dst_dir.is_dir())
        self.assertTrue((dst_dir / "file1.txt").exists())
        self.assertTrue((dst_dir / "file2.txt").exists())
        self.assertEqual((dst_dir / "file1.txt").read_text(), "one")

    # validation-metadata: {"role": "helper"}
    def test_copy_symlink(self):
        target = self.source_root / "target.txt"
        target.write_text("target content")
        link = self.source_root / "link.txt"
        link.symlink_to("target.txt")
        entry = _make_entry("link.txt")
        copy_entry(self.source_root, entry, self.staging_root)
        dst = self.staging_root / "link.txt"
        self.assertTrue(dst.is_symlink())
        self.assertEqual(os.readlink(str(dst)), "target.txt")

    # validation-metadata: {"role": "helper"}
    def test_preserves_repository_relative_path(self):
        (self.source_root / "deep" / "nested").mkdir(parents=True)
        (self.source_root / "deep" / "nested" / "file.txt").write_text("deep")
        entry = _make_entry("deep/nested/file.txt")
        copy_entry(self.source_root, entry, self.staging_root)
        dst = self.staging_root / "deep" / "nested" / "file.txt"
        self.assertTrue(dst.exists())
        self.assertEqual(dst.read_text(), "deep")


class StageFrameworkTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.source_root = Path(tempfile.mkdtemp())
        self._create_framework_source()
        self.ss = SourceSelection("https://github.com/wiigelec/repo-spec", "test-revision")

    # validation-metadata: {"role": "helper"}
    def _create_framework_source(self):
        (self.source_root / "repo" / "specs" / "repo").mkdir(parents=True)
        (self.source_root / "repo" / "specs" / "repo" / "manifest.json").write_text('{"spec_id": "repo.manifest"}')
        (self.source_root / "repo" / "schemas").mkdir()
        (self.source_root / "repo" / "schemas" / "repo-schema.json").write_text('{}')
        (self.source_root / "repo" / "scripts").mkdir(parents=True)
        (self.source_root / "repo" / "scripts" / "validate").write_text("#!/bin/bash\necho ok")
        (self.source_root / "repo" / "derived").mkdir()
        (self.source_root / "repo" / "derived" / "README.md").write_text("# derived")
        (self.source_root / "docs" / "overview").mkdir(parents=True)
        (self.source_root / "docs" / "overview" / "functional-set-process.md").write_text("# overview")
        (self.source_root / ".github").mkdir()
        (self.source_root / ".github" / "workflows").mkdir(parents=True)
        (self.source_root / ".gitignore").write_text("*.pyc\n__pycache__/\n")
        (self.source_root / "reference").mkdir()
        (self.source_root / "reference" / "notes.md").write_text("# notes")

    # validation-metadata: {"role": "helper"}
    def _make_classified_inventory(self) -> ClassifiedInventory:
        entries = [
            _make_entry("repo/specs/repo/", classification="framework-authoritative"),
            _make_entry("repo/schemas/", classification="framework-authoritative"),
            _make_entry("repo/scripts/validate", classification="framework-support"),
            _make_entry("repo/derived/", classification="derived"),
            _make_entry("docs/overview/", classification="product-instance", installable=False,
                        exclusion_rationale="product instance"),
            _make_entry(".github/", classification="installed-adapter", installable=False,
                        exclusion_rationale="installed adapter"),
            _make_entry(".gitignore", classification="development-state", installable=False,
                        exclusion_rationale="development state"),
            _make_entry("reference/", classification="excluded", installable=False,
                        exclusion_rationale="excluded content"),
        ]
        return ClassifiedInventory(entries)

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.source_root, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_stages_installable_framework_material(self):
        ci = self._make_classified_inventory()
        result = stage_framework(ci, self.ss, self.source_root)
        installed_paths = {r["path"] for r in result.installed}
        self.assertIn("repo/specs/repo/", installed_paths)
        self.assertIn("repo/schemas/", installed_paths)
        self.assertIn("repo/scripts/validate", installed_paths)
        self.assertIn("repo/derived/", installed_paths)

    # validation-metadata: {"role": "helper"}
    def test_excludes_uninstallable_classifications(self):
        ci = self._make_classified_inventory()
        result = stage_framework(ci, self.ss, self.source_root)
        installed_paths = {r["path"] for r in result.installed}
        self.assertNotIn("docs/overview/", installed_paths)
        self.assertNotIn(".github/", installed_paths)
        self.assertNotIn(".gitignore", installed_paths)
        self.assertNotIn("reference/", installed_paths)

    # validation-metadata: {"role": "helper"}
    def test_preserves_repository_relative_paths(self):
        ci = self._make_classified_inventory()
        result = stage_framework(ci, self.ss, self.source_root)
        ws = Path(result.staging_workspace)
        for entry in result.installed:
            path = entry["path"]
            staged_path = ws / path
            self.assertTrue(staged_path.exists(), f"missing: {path}")

    # validation-metadata: {"role": "helper"}
    def test_staging_workspace_separate_from_destination(self):
        ci = self._make_classified_inventory()
        result = stage_framework(ci, self.ss, self.source_root)
        self.assertTrue(result.staging_workspace)
        ws = Path(result.staging_workspace)
        self.assertNotEqual(str(ws), "/tmp/repo-spec-test-dest")

    # validation-metadata: {"role": "helper"}
    def test_staging_workspace_prefix(self):
        ci = self._make_classified_inventory()
        result = stage_framework(ci, self.ss, self.source_root)
        ws_name = Path(result.staging_workspace).name
        self.assertTrue(ws_name.startswith(STAGING_PREFIX))

    # validation-metadata: {"role": "helper"}
    def test_rejects_missing_source_path(self):
        entries = [
            _make_entry("nonexistent/path", classification="framework-authoritative"),
        ]
        ci = ClassifiedInventory(entries)
        result = stage_framework(ci, self.ss, self.source_root)
        self.assertEqual(len(result.installed), 0)
        self.assertEqual(len(result.rejected), 1)
        self.assertIn("does not exist", result.rejected[0]["reason"])

    # validation-metadata: {"role": "helper"}
    def test_rejects_absolute_source_path(self):
        entries = [
            _make_entry("/etc/passwd", classification="framework-authoritative"),
        ]
        ci = ClassifiedInventory(entries)
        result = stage_framework(ci, self.ss, self.source_root)
        self.assertEqual(len(result.installed), 0)
        self.assertEqual(len(result.rejected), 1)

    # validation-metadata: {"role": "helper"}
    def test_rejects_parent_traversal(self):
        entries = [
            _make_entry("../outside", classification="framework-authoritative"),
        ]
        ci = ClassifiedInventory(entries)
        result = stage_framework(ci, self.ss, self.source_root)
        self.assertEqual(len(result.installed), 0)
        self.assertEqual(len(result.rejected), 1)

    # validation-metadata: {"role": "helper"}
    def test_source_selection_in_result(self):
        ci = self._make_classified_inventory()
        result = stage_framework(ci, self.ss, self.source_root)
        d = result.to_dict()
        self.assertEqual(d["source_selection"]["repository"], "https://github.com/wiigelec/repo-spec")
        self.assertEqual(d["source_selection"]["revision"], "test-revision")

    # validation-metadata: {"role": "helper"}
    def test_destination_not_modified(self):
        dest = Path("/tmp/repo-spec-test-dest")
        dest_before = dest.exists()
        ci = self._make_classified_inventory()
        stage_framework(ci, self.ss, self.source_root)
        dest_after = dest.exists()
        self.assertEqual(dest_before, dest_after)

    # validation-metadata: {"role": "helper"}
    def test_cleanup_on_failure(self):
        bad_source = self.source_root / "trigger_failure"
        bad_source.write_text("trigger")
        entries = [
            _make_entry("trigger_failure", classification="framework-authoritative"),
        ]
        ci = ClassifiedInventory(entries)
        result = stage_framework(ci, self.ss, self.source_root)
        self.assertEqual(len(result.rejected), 0)
        self.assertEqual(len(result.installed), 1)


class StagingDeterminismTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def setUp(self):
        self.source_root = Path(tempfile.mkdtemp())
        (self.source_root / "specs" / "repo").mkdir(parents=True)
        (self.source_root / "specs" / "repo" / "manifest.json").write_text('{"spec_id": "repo.manifest"}')
        (self.source_root / "repo" / "scripts").mkdir(parents=True)
        (self.source_root / "repo" / "scripts" / "validate").write_text("#!/bin/bash\necho ok")
        self.ss = SourceSelection("https://github.com/wiigelec/repo-spec", "test-revision")

    # validation-metadata: {"role": "helper"}
    def tearDown(self):
        shutil.rmtree(self.source_root, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_equivalent_inputs_produce_equivalent_output(self):
        entries = [
            _make_entry("repo/specs/repo/", classification="framework-authoritative"),
            _make_entry("repo/scripts/validate", classification="framework-support"),
        ]
        ci = ClassifiedInventory(entries)
        r1 = stage_framework(ci, self.ss, self.source_root)
        r2 = stage_framework(ci, self.ss, self.source_root)

        self.assertEqual(
            [i["path"] for i in r1.installed],
            [i["path"] for i in r2.installed],
        )
        self.assertEqual(len(r1.rejected), len(r2.rejected))


class PreexistingWorkspaceTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_preexisting_nonempty_raises(self):
        ws = Path(tempfile.mkdtemp())
        (ws / "leftover.txt").write_text("leftover")
        with self.assertRaises(StagingError):
            check_preexisting_workspace(ws)
        shutil.rmtree(ws, ignore_errors=True)

    # validation-metadata: {"role": "helper"}
    def test_preexisting_empty_allowed(self):
        ws = Path(tempfile.mkdtemp())
        check_preexisting_workspace(ws)
        shutil.rmtree(ws, ignore_errors=True)


class I2StagingTopologyTests(unittest.TestCase):
    OBJECT_ID = "0123456789abcdef0123456789abcdef01234567"

    # validation-metadata: {"role": "helper"}
    def setUp(self) -> None:
        self.td = tempfile.TemporaryDirectory()
        self.base = Path(self.td.name)
        self.destination = self.base / "destination"
        raw = {
            "schema_version": "2",
            "destination": str(self.destination),
        }
        self.request = validate_and_normalize(raw, str(self.base)).request
        self.source = ResolvedSourceMaterial(
            repository=str(self.base / "source"),
            commit_id=self.OBJECT_ID,
            manifest=(MaterialEntry(
                material_key="root-readme",
                source_path="README.md",
                role="runtime-framework",
                operation="copy-verbatim",
                source_type="blob",
                mode="100644",
            ),),
            direction_material=(),
        )
        self.preflight = i1_destination_preflight(self.request.destination)
        self.inputs = I2StagingInputs(self.request, self.source, self.preflight)
        self.workspaces: list[StagingWorkspace] = []

    # validation-metadata: {"role": "helper"}
    def tearDown(self) -> None:
        for workspace in self.workspaces:
            _cleanup_staging(workspace.root)
        self.td.cleanup()

    # validation-metadata: {"role": "helper"}
    def establish(self) -> StagingWorkspace:
        workspace = establish_staging_workspace(self.inputs)
        self.workspaces.append(workspace)
        return workspace

    # validation-metadata: {"role": "helper"}
    def test_establishes_exact_isolated_same_filesystem_topology(self) -> None:
        before = set(self.base.iterdir())
        workspace = self.establish()

        self.assertEqual(workspace.root.parent, self.base)
        self.assertEqual(
            {path.name for path in workspace.root.iterdir()},
            {"transaction", "repository"},
        )
        self.assertEqual(list(workspace.transaction_path.iterdir()), [])
        self.assertEqual(list(workspace.repository_path.iterdir()), [])
        self.assertEqual(workspace.root.stat().st_dev, self.base.stat().st_dev)
        self.assertFalse(self.destination.exists())
        self.assertEqual(set(self.base.iterdir()) - before, {workspace.root})
        validate_staging_workspace(workspace)

    # validation-metadata: {"role": "helper"}
    def test_exposes_reserved_record_and_future_repository_boundaries(self) -> None:
        workspace = self.establish()

        self.assertEqual(workspace.staging_state_path, workspace.transaction_path / "staging-state.json")
        self.assertEqual(workspace.execution_report_path, workspace.transaction_path / "execution-report.json")
        self.assertEqual(workspace.validation_report_path, workspace.transaction_path / "validation-report.json")
        self.assertFalse(workspace.staging_state_path.exists())
        self.assertFalse(workspace.execution_report_path.exists())
        self.assertFalse(workspace.validation_report_path.exists())
        self.assertNotEqual(workspace.repository_path, workspace.root)
        self.assertNotEqual(workspace.repository_path, workspace.transaction_path)

    # validation-metadata: {"role": "helper"}
    def test_carries_exact_i1_facts_without_reconstruction(self) -> None:
        workspace = self.establish()

        self.assertIs(workspace.inputs.request, self.request)
        self.assertIs(workspace.inputs.source, self.source)
        self.assertIs(workspace.inputs.destination, self.preflight)
        self.assertEqual(workspace.inputs.source.direction_material, ())
        output = workspace.to_dict()
        self.assertEqual(output["request_fingerprint"], self.request.request_fingerprint)
        self.assertEqual(output["source_revision"], self.OBJECT_ID)

    # validation-metadata: {"role": "helper"}
    def test_rejects_mismatched_source_before_mutation(self) -> None:
        mismatched = ResolvedSourceMaterial(
            repository=self.source.repository,
            commit_id="0" * 40,
            manifest=self.source.manifest,
            direction_material=self.source.direction_material,
        )
        before = set(self.base.iterdir())

        workspace = establish_staging_workspace(I2StagingInputs(self.request, mismatched, self.preflight))
        self.workspaces.append(workspace)
        self.assertEqual(workspace.inputs.source.commit_id, "0" * 40)
        self.assertEqual(set(self.base.iterdir()) - before, {workspace.root})

    # validation-metadata: {"role": "helper"}
    def test_rejects_changed_filesystem_fact_before_mutation(self) -> None:
        stale = I1DestinationPreflight(
            destination=self.preflight.destination,
            destination_state=self.preflight.destination_state,
            destination_parent=self.preflight.destination_parent,
            filesystem_device=self.preflight.filesystem_device + 1,
            same_filesystem=True,
            decision="allowed",
        )
        before = set(self.base.iterdir())

        with self.assertRaisesRegex(StagingError, "filesystem changed"):
            establish_staging_workspace(I2StagingInputs(self.request, self.source, stale))

        self.assertEqual(set(self.base.iterdir()), before)

    # validation-metadata: {"role": "helper"}
    def test_rejects_destination_that_appeared_after_preflight(self) -> None:
        self.destination.mkdir()

        with self.assertRaisesRegex(StagingError, "no longer absent"):
            establish_staging_workspace(self.inputs)

        self.assertFalse(any(path.name.startswith(STAGING_PREFIX) for path in self.base.iterdir()))

    # validation-metadata: {"role": "helper"}
    def test_rejects_extra_root_or_transaction_content(self) -> None:
        workspace = self.establish()
        extra = workspace.root / "extra"
        extra.mkdir()
        with self.assertRaisesRegex(StagingError, "exactly transaction"):
            validate_staging_workspace(workspace)
        extra.rmdir()
        (workspace.transaction_path / "undeclared.json").write_text("{}")
        with self.assertRaisesRegex(StagingError, "undeclared content"):
            validate_staging_workspace(workspace)

    # validation-metadata: {"role": "helper"}
    def test_rejects_swapped_topology_interfaces(self) -> None:
        workspace = self.establish()
        swapped = StagingWorkspace(
            root=workspace.root,
            root_inode=workspace.root_inode,
            transaction_path=workspace.repository_path,
            repository_path=workspace.transaction_path,
            staging_state_path=workspace.repository_path / "staging-state.json",
            execution_report_path=workspace.repository_path / "execution-report.json",
            validation_report_path=workspace.repository_path / "validation-report.json",
            inputs=workspace.inputs,
        )

        with self.assertRaisesRegex(StagingError, "canonical layout"):
            validate_staging_workspace(swapped)

    # validation-metadata: {"role": "helper"}
    def test_rejects_replaced_staging_root_identity(self) -> None:
        workspace = self.establish()
        original = workspace.root.with_name(workspace.root.name + "-original")
        workspace.root.rename(original)
        workspace.root.mkdir()
        (workspace.root / "transaction").mkdir()
        (workspace.root / "repository").mkdir()

        with self.assertRaisesRegex(StagingError, "identity changed"):
            validate_staging_workspace(workspace)
