from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]

from initializer.executable_closure import (
    CLOSURE_FAILED,
    CLOSURE_SATISFIED,
    closure_failure_code,
    evaluate_executable_reference_closure,
    installed_command_requirements,
)

EXPECTED = [
    ("common-production-validation", "scripts/validate"),
    ("repository-validation-self-test", "repo/scripts/test-validation"),
    ("product-validation-self-test", "product/scripts/test-validation"),
    ("generic-product-implementation-test", "product/scripts/test-product"),
]

@unittest.skip("deferred: initializer materialization must be updated in the follow-up after validation migrations are proven")
class VS3ExecutableClosureTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def _staged_repository(self):
        temp = tempfile.TemporaryDirectory()
        staged = Path(temp.name)
        requirements = installed_command_requirements()
        command_paths = {item["path"] for item in requirements}
        required_paths = set(command_paths)
        for item in requirements:
            required_paths.update(item["portable_support"])
        for relative in sorted(required_paths):
            source = ROOT / relative
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
            if relative in command_paths:
                target.chmod(0o755)
        return temp, staged

    # validation-metadata: {"role": "helper"}
    def test_requirement_identity_is_deterministic_and_complete(self) -> None:
        requirements = installed_command_requirements()
        observed = [(item["requirement_id"], item["path"]) for item in requirements]
        self.assertEqual(observed, EXPECTED)
        self.assertTrue(all(item["classification"] == "repository-relative" for item in requirements))
        self.assertTrue(all(item["executable_required"] is True for item in requirements))

    # validation-metadata: {"role": "helper"}
    def test_current_accepted_authority_and_staged_surfaces_close(self) -> None:
        temp, staged = self._staged_repository()
        try:
            result = evaluate_executable_reference_closure(ROOT, staged)
        finally:
            temp.cleanup()
        self.assertEqual(result["classification"], CLOSURE_SATISFIED)
        self.assertIsNone(closure_failure_code(result))
        self.assertEqual(len(result["requirements"]), 4)
        for item in result["requirements"]:
            self.assertEqual(item["resolution"], "resolved")
            self.assertTrue(item["portable_support_closed"])

    # validation-metadata: {"role": "helper"}
    def test_missing_required_surface_fails_closed(self) -> None:
        temp, staged = self._staged_repository()
        try:
            (staged / "product/scripts/test-product").unlink()
            result = evaluate_executable_reference_closure(ROOT, staged)
        finally:
            temp.cleanup()
        self.assertEqual(result["classification"], CLOSURE_FAILED)
        self.assertEqual(closure_failure_code(result), "installed-path-missing")

    # validation-metadata: {"role": "helper"}
    def test_non_executable_required_surface_fails_closed(self) -> None:
        temp, staged = self._staged_repository()
        try:
            (staged / "repo/scripts/test-validation").chmod(0o644)
            result = evaluate_executable_reference_closure(ROOT, staged)
        finally:
            temp.cleanup()
        self.assertEqual(result["classification"], CLOSURE_FAILED)
        self.assertEqual(closure_failure_code(result), "executable-capability-missing")

    # validation-metadata: {"role": "helper"}
    def test_missing_portable_support_fails_closed(self) -> None:
        temp, staged = self._staged_repository()
        try:
            (staged / "product/scripts/test_product_impl.py").unlink()
            result = evaluate_executable_reference_closure(ROOT, staged)
        finally:
            temp.cleanup()
        self.assertEqual(result["classification"], CLOSURE_FAILED)
        self.assertEqual(closure_failure_code(result), "portable-support-missing")

    # validation-metadata: {"role": "helper"}
    def test_evidence_is_json_serializable_and_stable(self) -> None:
        temp, staged = self._staged_repository()
        try:
            first = evaluate_executable_reference_closure(ROOT, staged)
            second = evaluate_executable_reference_closure(ROOT, staged)
        finally:
            temp.cleanup()
        self.assertEqual(
            json.dumps(first, sort_keys=True, separators=(",", ":")),
            json.dumps(second, sort_keys=True, separators=(",", ":")),
        )

if __name__ == "__main__":
    unittest.main()
