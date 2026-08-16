from __future__ import annotations

import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import initializer.cli as cli
from initializer.upgrade_orchestration import (
    DerivedRepositoryUpgradeResult,
    execute_repository_upgrade,
    serialize_upgrade_evidence,
    upgrade_evidence_fingerprint,
)
from initializer.upgrade_resolution import resolve_accepted_baseline


REQUIREMENT_TEST_MAP = {
    "UPG-FULL-001": "test_public_repo_spec_upgrade_drives_real_lifecycle",
    "UPG-FULL-002": "test_first_and_subsequent_upgrade_compose_complete_lifecycle",
    "UPG-FULL-003": "test_public_repo_spec_upgrade_drives_real_lifecycle",
    "UPG-FULL-004": "test_managed_conflict_rejects_without_target_mutation",
    "UPG-FULL-005": "test_first_and_subsequent_upgrade_compose_complete_lifecycle",
    "UPG-FULL-006": "test_validation_failure_prevents_promotion",
    "UPG-FULL-007": "test_first_and_subsequent_upgrade_compose_complete_lifecycle",
    "UPG-FULL-008": "test_validation_failure_prevents_promotion",
    "UPG-FULL-009": "test_equivalent_inputs_produce_equivalent_reconciliation_and_content",
    "UPG-FULL-010": "test_public_cli_dispatch_has_no_framework_revision_selector",
}


def git(repo: Path, *args: str, check: bool = True) -> str:
    p = subprocess.run(
        ["git", "-C", str(repo), *args],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and p.returncode:
        raise RuntimeError(p.stderr or p.stdout)
    return p.stdout.strip()


def write_inventory(repo: Path, definitions: dict[str, tuple[str, str]]) -> None:
    manifest = []
    output = []
    for key, (destination, content) in sorted(definitions.items()):
        source = f"materials/{key}.txt"
        (repo / source).parent.mkdir(parents=True, exist_ok=True)
        (repo / source).write_text(content, encoding="utf-8")
        manifest.append({
            "material_key": key,
            "source_path": source,
            "role": "runtime-framework",
            "operation": "copy-verbatim",
            "source_type": "blob",
            "mode": "100644",
        })
        output.append({
            "material_key": key,
            "destination_path": destination,
            "producer": "framework-installation",
            "operation": "copy-verbatim",
            "mode": "100644",
            "required": True,
            "role": "runtime-framework",
        })

    (repo / "product/scripts/initializer").mkdir(parents=True, exist_ok=True)
    (repo / "product/specs/product/level-1").mkdir(parents=True, exist_ok=True)
    (repo / "product/scripts/initializer/framework-inventory.json").write_text(
        json.dumps({"schema_version": "1", "entries": manifest}, indent=2) + "\n",
        encoding="utf-8",
    )
    (repo / "product/specs/product/level-1/initializer-output-inventory-v1.json").write_text(
        json.dumps({
            "spec_id": "product.initializer-output-inventory-v1",
            "status": "accepted",
            "schema_version": "1",
            "material_index": output,
        }, indent=2) + "\n",
        encoding="utf-8",
    )


def commit(repo: Path, message: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-qm", message)
    return git(repo, "rev-parse", "HEAD")


def make_framework(root: Path) -> Path:
    framework = root / "framework"
    framework.mkdir()
    git(framework, "init", "-q")
    git(framework, "config", "user.email", "framework@example.invalid")
    git(framework, "config", "user.name", "Framework")
    return framework


def make_target(
    root: Path,
    framework: Path,
    baseline_revision: str,
    *,
    validator_exit: int = 0,
    valid_provenance: bool = True,
) -> Path:
    target = root / "target"
    target.mkdir()
    git(target, "init", "-q")
    git(target, "config", "user.email", "target@example.invalid")
    git(target, "config", "user.name", "Target")

    (target / "managed.txt").write_text("one\n", encoding="utf-8")
    (target / "user-owned.txt").write_text("preserve\n", encoding="utf-8")
    scripts = target / "scripts"
    scripts.mkdir()
    validator = scripts / "validate"
    validator.write_text(
        "#!/usr/bin/env bash\nset -eu\nexit " + str(validator_exit) + "\n",
        encoding="utf-8",
    )
    os.chmod(validator, 0o755)

    (target / "repo/initializer").mkdir(parents=True)
    provenance = {
        "schema_version": "2",
        "initializer_name": "repo-spec-init",
        "initializer_version": "1",
        "framework_repository": str(framework),
        "framework_revision": {
            "object_format": "sha1",
            "object_id": baseline_revision,
        },
        "initialization_timestamp": "2026-01-01T00:00:00Z",
        "request_fingerprint": "a" * 64,
    }
    if not valid_provenance:
        del provenance["request_fingerprint"]
    (target / "repo/initializer/provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n",
        encoding="utf-8",
    )
    commit(target, "target")
    return target


class UP5UpgradeOrchestrationTests(unittest.TestCase):
    def test_public_repo_spec_upgrade_drives_real_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source_root = Path(__file__).resolve().parents[4]
            baseline_framework = root / "baseline-framework"
            current_framework = root / "current-framework"
            target = root / "target"

            subprocess.run(
                [
                    "git",
                    "clone",
                    "-q",
                    "--no-hardlinks",
                    str(source_root),
                    str(baseline_framework),
                ],
                check=True,
            )
            git(
                baseline_framework,
                "checkout",
                "-q",
                "--detach",
                "691bf74513eaadc85856d951221a4deae87da25b",
            )

            subprocess.run(
                [
                    "git",
                    "clone",
                    "-q",
                    "--no-hardlinks",
                    str(source_root),
                    str(current_framework),
                ],
                check=True,
            )
            current_revision = git(current_framework, "rev-parse", "HEAD")

            init_cli = baseline_framework / "product/scripts/repo-spec"
            init_proc = subprocess.run(
                [str(init_cli), "init", "--repo", str(target)],
                cwd=baseline_framework,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(init_proc.returncode, 0, init_proc.stderr)

            upgrade_cli = current_framework / "product/scripts/repo-spec"
            proc = subprocess.run(
                [str(upgrade_cli), "upgrade", "--repo", str(target)],
                cwd=current_framework,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(
                proc.returncode,
                0,
                "stdout:\n" + proc.stdout + "\nstderr:\n" + proc.stderr,
            )
            result = json.loads(proc.stdout)
            self.assertEqual(result["terminal_result"], "promoted-success")
            self.assertTrue(result["succeeded"])
            self.assertTrue(result["accepted"])
            self.assertEqual(
                result["reconciliation_target_revision"],
                current_revision,
            )

            accepted = resolve_accepted_baseline(str(target))
            self.assertEqual(accepted.baseline_source, "accepted-lineage")
            self.assertEqual(
                accepted.active_baseline.framework_revision.object_id,
                current_revision,
            )

    def test_equivalent_inputs_produce_equivalent_reconciliation_and_content(self):
        from initializer.upgrade_validation_promotion import repository_content_digest

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            framework = make_framework(root)
            write_inventory(framework, {"managed": ("managed.txt", "one\n")})
            baseline = commit(framework, "baseline")

            first_root = root / "case-one"
            second_root = root / "case-two"
            first_root.mkdir()
            second_root.mkdir()
            first_target = make_target(first_root, framework, baseline)
            second_target = make_target(second_root, framework, baseline)

            write_inventory(framework, {"managed": ("managed.txt", "two\n")})
            target_revision = commit(framework, "target")

            first = execute_repository_upgrade(str(first_target), str(framework))
            second = execute_repository_upgrade(str(second_target), str(framework))

            self.assertTrue(first.succeeded)
            self.assertTrue(second.succeeded)
            self.assertEqual(first.reconciliation_target_revision, target_revision)
            self.assertEqual(second.reconciliation_target_revision, target_revision)
            self.assertEqual(first.selected_material_keys, second.selected_material_keys)
            self.assertEqual(first.upgrade_set_fingerprint, second.upgrade_set_fingerprint)
            self.assertEqual(
                repository_content_digest(first_target),
                repository_content_digest(second_target),
            )
            self.assertEqual(
                (first_target / "managed.txt").read_bytes(),
                (second_target / "managed.txt").read_bytes(),
            )
            self.assertEqual(
                (first_target / "user-owned.txt").read_bytes(),
                (second_target / "user-owned.txt").read_bytes(),
            )

    def test_requirement_map_covers_all_level3_requirements(self):
        self.assertEqual(
            set(REQUIREMENT_TEST_MAP),
            {f"UPG-FULL-{index:03d}" for index in range(1, 11)},
        )

    def test_first_and_subsequent_upgrade_compose_complete_lifecycle(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            framework = make_framework(root)
            write_inventory(framework, {"managed": ("managed.txt", "one\n")})
            baseline = commit(framework, "baseline")
            target = make_target(root, framework, baseline)

            write_inventory(framework, {"managed": ("managed.txt", "two\n")})
            first_target = commit(framework, "first upgrade target")
            first = execute_repository_upgrade(str(target), str(framework))

            self.assertTrue(first.succeeded)
            self.assertTrue(first.accepted)
            self.assertEqual(first.terminal_result, "promoted-success")
            self.assertEqual(first.baseline_source, "legacy-provenance-bootstrap")
            self.assertEqual(first.baseline_revision, baseline)
            self.assertEqual(first.reconciliation_target_revision, first_target)
            self.assertEqual((target / "managed.txt").read_text(), "two\n")
            self.assertEqual((target / "user-owned.txt").read_text(), "preserve\n")

            after_first = resolve_accepted_baseline(str(target))
            self.assertEqual(after_first.baseline_source, "accepted-lineage")
            self.assertEqual(
                after_first.active_baseline.framework_revision.object_id,
                first_target,
            )

            write_inventory(framework, {"managed": ("managed.txt", "three\n")})
            second_target = commit(framework, "second upgrade target")
            second = execute_repository_upgrade(str(target), str(framework))

            self.assertTrue(second.succeeded)
            self.assertEqual(second.baseline_source, "accepted-lineage")
            self.assertEqual(second.baseline_revision, first_target)
            self.assertEqual(second.reconciliation_target_revision, second_target)
            self.assertEqual((target / "managed.txt").read_text(), "three\n")

            after_second = resolve_accepted_baseline(str(target))
            self.assertEqual(
                after_second.active_baseline.framework_revision.object_id,
                second_target,
            )
            lineage = json.loads(
                git(target, "show", "HEAD:repo/initializer/framework-lineage.json")
            )
            revisions = [
                item["framework_revision"]["object_id"]
                for item in lineage["entries"]
            ]
            self.assertEqual(revisions, [baseline, first_target, second_target])

    def test_invalid_legacy_provenance_fails_closed_before_staging(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            framework = make_framework(root)
            write_inventory(framework, {"managed": ("managed.txt", "one\n")})
            baseline = commit(framework, "baseline")
            target = make_target(root, framework, baseline, valid_provenance=False)
            before_head = git(target, "rev-parse", "HEAD")

            write_inventory(framework, {"managed": ("managed.txt", "two\n")})
            commit(framework, "target")
            siblings_before = sorted(p.name for p in root.iterdir())

            result = execute_repository_upgrade(str(target), str(framework))
            self.assertFalse(result.succeeded)
            self.assertEqual(result.terminal_result, "pre-promotion-failure")
            self.assertIn("canonical ordered provenance", result.failure_reason or "")
            self.assertEqual(git(target, "rev-parse", "HEAD"), before_head)
            self.assertEqual(sorted(p.name for p in root.iterdir()), siblings_before)

    def test_managed_conflict_rejects_without_target_mutation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            framework = make_framework(root)
            write_inventory(framework, {"managed": ("managed.txt", "one\n")})
            baseline = commit(framework, "baseline")
            target = make_target(root, framework, baseline)

            (target / "managed.txt").write_text("local change\n", encoding="utf-8")
            commit(target, "local managed divergence")
            before_head = git(target, "rev-parse", "HEAD")

            write_inventory(framework, {"managed": ("managed.txt", "two\n")})
            commit(framework, "target")
            result = execute_repository_upgrade(str(target), str(framework))

            self.assertFalse(result.succeeded)
            self.assertEqual(result.terminal_result, "rejected")
            self.assertEqual(result.reconciliation_status, "conflict")
            self.assertEqual(git(target, "rev-parse", "HEAD"), before_head)
            self.assertEqual((target / "managed.txt").read_text(), "local change\n")

    def test_validation_failure_prevents_promotion(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            framework = make_framework(root)
            write_inventory(framework, {"managed": ("managed.txt", "one\n")})
            baseline = commit(framework, "baseline")
            target = make_target(root, framework, baseline, validator_exit=7)
            before_head = git(target, "rev-parse", "HEAD")

            write_inventory(framework, {"managed": ("managed.txt", "two\n")})
            target_revision = commit(framework, "target")
            result = execute_repository_upgrade(str(target), str(framework))

            self.assertFalse(result.succeeded)
            self.assertEqual(result.terminal_result, "pre-promotion-failure")
            self.assertEqual(result.validation_status, "fail")
            self.assertEqual(result.reconciliation_target_revision, target_revision)
            self.assertEqual(git(target, "rev-parse", "HEAD"), before_head)
            self.assertEqual((target / "managed.txt").read_text(), "one\n")

    def test_terminal_evidence_is_deterministic(self):
        result = DerivedRepositoryUpgradeResult(
            terminal_result="rejected",
            succeeded=False,
            accepted=False,
            baseline_source="accepted-lineage",
            baseline_revision="1" * 40,
            reconciliation_target_revision="2" * 40,
            selected_material_keys=("a", "b"),
            reconciliation_status="conflict",
            validation_status=None,
            promotion_outcome=None,
            failure_reason="managed reconciliation conflict",
            upgrade_set_fingerprint="a" * 64,
            staged_reconciliation_fingerprint="b" * 64,
            reanchoring_fingerprint=None,
            up4_fingerprint=None,
        )
        self.assertEqual(
            serialize_upgrade_evidence(result),
            serialize_upgrade_evidence(result),
        )
        self.assertEqual(
            upgrade_evidence_fingerprint(result),
            upgrade_evidence_fingerprint(result),
        )

    def test_public_cli_dispatch_has_no_framework_revision_selector(self):
        fake = DerivedRepositoryUpgradeResult(
            terminal_result="promoted-success",
            succeeded=True,
            accepted=True,
            baseline_source="accepted-lineage",
            baseline_revision="1" * 40,
            reconciliation_target_revision="2" * 40,
            selected_material_keys=(),
            reconciliation_status="staged",
            validation_status="pass",
            promotion_outcome="promoted",
            failure_reason=None,
            upgrade_set_fingerprint="a" * 64,
            staged_reconciliation_fingerprint="b" * 64,
            reanchoring_fingerprint="c" * 64,
            up4_fingerprint="d" * 64,
        )
        with mock.patch(
            "initializer.upgrade_orchestration.execute_repository_upgrade",
            return_value=fake,
        ) as execute:
            with mock.patch("builtins.print"):
                rc = cli.main([
                    "/path/to/cli.py",
                    "/framework/root",
                    "upgrade",
                    "--repo",
                    "/target/root",
                ])

        self.assertEqual(rc, 0)
        execute.assert_called_once_with("/target/root", "/framework/root")


if __name__ == "__main__":
    unittest.main()
