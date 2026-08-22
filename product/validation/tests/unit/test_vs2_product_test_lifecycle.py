from __future__ import annotations

import errno
import json
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from validation.runners import test_validation_impl as test_product_impl


class VS2ProductTestLifecycleTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_repo_spec_current_state_is_explicit_honest_zero(self) -> None:
        root = Path(__file__).resolve().parents[4]
        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "successful-zero-applicable")
        self.assertEqual(result["applicability"], "zero-applicable")
        self.assertEqual(result["evidence"]["accepted_spec_count"], 49)
        self.assertTrue(result["evidence"]["conformance_complete"])
        self.assertEqual(result["obligations"], [])

    # validation-metadata: {"role": "helper"}
    def _empty_repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        return td, root

    # validation-metadata: {"role": "helper"}
    def _active_repo(self, *, accepted: bool = True) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "product/specs/product/level-1").mkdir(parents=True)
        entries = []
        if accepted:
            entries.append(
                {
                    "spec_id": "product.synthetic",
                    "path": "product/specs/product/level-1/synthetic.json",
                    "status": "accepted",
                    "level": 1,
                }
            )
        (root / "product/specs/product/manifest.json").write_text(
            json.dumps(
                {
                    "spec_id": "product.manifest",
                    "status": "accepted",
                    "product_specifications": entries,
                }
            ),
            encoding="utf-8",
        )
        return td, root

    # validation-metadata: {"role": "helper"}
    def _write_spec(
        self,
        root: Path,
        *,
        tests: object,
        conformance: object,
        requirements: list[str] | None = None,
    ) -> None:
        requirement_ids = requirements or ["SYN-001"]
        (root / "product/specs/product/level-1/synthetic.json").write_text(
            json.dumps(
                {
                    "spec_id": "product.synthetic",
                    "status": "accepted",
                    "normative_requirements": [
                        {"id": req, "text": f"Requirement {req}"}
                        for req in requirement_ids
                    ],
                    "correspondence": {
                        "implementations": [],
                        "tests": tests,
                        "conformance": conformance,
                    },
                }
            ),
            encoding="utf-8",
        )

    # validation-metadata: {"role": "helper"}
    def _mapping(self, test_id: str, path: str, requirement: str = "SYN-001") -> dict[str, object]:
        return {
            "id": test_id,
            "paths": [path],
            "requirements": [requirement],
        }

    # validation-metadata: {"role": "helper"}
    def _covered(self, test_id: str, requirement: str = "SYN-001") -> dict[str, object]:
        return {
            "requirement_id": requirement,
            "implementation_ids": ["impl.synthetic"],
            "test_ids": [test_id],
            "status": "covered",
        }

    # validation-metadata: {"role": "helper"}
    def _not_applicable(self, requirement: str = "SYN-001") -> dict[str, object]:
        return {
            "requirement_id": requirement,
            "implementation_ids": [],
            "test_ids": [],
            "status": "not-applicable",
            "rationale": "No governed product implementation test applies.",
        }

    # validation-metadata: {"role": "helper"}
    def _write_executable(self, root: Path, relative: str, body: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    # validation-metadata: {"role": "helper"}
    def test_inactive_product_system_is_honest_zero(self) -> None:
        td, root = self._empty_repo()
        self.addCleanup(td.cleanup)

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "successful-zero-applicable")
        self.assertEqual(result["evidence"]["product_specification_system"], "inactive")

    # validation-metadata: {"role": "helper"}
    def test_active_manifest_with_no_accepted_specs_is_honest_zero(self) -> None:
        td, root = self._active_repo(accepted=False)
        self.addCleanup(td.cleanup)

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "successful-zero-applicable")
        self.assertTrue(result["evidence"]["conformance_complete"])

    # validation-metadata: {"role": "helper"}
    def test_explicit_not_applicable_conformance_proves_zero(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_spec(
            root,
            tests=[],
            conformance=[self._not_applicable()],
        )

        first = test_product_impl.run_product_tests(root)
        second = test_product_impl.run_product_tests(root)

        self.assertEqual(first, second)
        self.assertEqual(first["classification"], "successful-zero-applicable")
        self.assertEqual(first["accepted_specs"], ["product.synthetic"])
        self.assertTrue(first["evidence"]["conformance_complete"])

    # validation-metadata: {"role": "helper"}
    def test_empty_test_mappings_without_complete_conformance_are_invalid_not_zero(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_spec(root, tests=[], conformance=[])

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "applicability-invalid")
        self.assertNotEqual(result["classification"], "successful-zero-applicable")

    # validation-metadata: {"role": "helper"}
    def test_covered_obligations_execute_in_deterministic_order(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        log = root / "order.log"
        self._write_executable(root, "tests/z-test", "#!/bin/sh\nprintf 'z\\n' >> '" + str(log) + "'\n")
        self._write_executable(root, "tests/a-test", "#!/bin/sh\nprintf 'a\\n' >> '" + str(log) + "'\n")
        self._write_spec(
            root,
            tests=[
                self._mapping("test.z", "tests/z-test", "SYN-002"),
                self._mapping("test.a", "tests/a-test", "SYN-001"),
            ],
            conformance=[
                self._covered("test.z", "SYN-002"),
                self._covered("test.a", "SYN-001"),
            ],
            requirements=["SYN-001", "SYN-002"],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "successful-applicable-execution")
        self.assertEqual([x["test_id"] for x in result["obligations"]], ["test.a", "test.z"])
        self.assertEqual(log.read_text(encoding="utf-8"), "a\nz\n")

    # validation-metadata: {"role": "helper"}
    def test_expected_but_missing_test_is_not_zero(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_spec(
            root,
            tests=[self._mapping("test.missing", "tests/missing")],
            conformance=[self._covered("test.missing")],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "unresolved-expected-tests")

    # validation-metadata: {"role": "helper"}
    def test_broken_registration_is_distinct_from_zero(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_spec(
            root,
            tests={"not": "a-list"},
            conformance=[self._not_applicable()],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "discovery-registration-failure")

    # validation-metadata: {"role": "helper"}
    def test_nonzero_test_is_failed_test_class(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_executable(root, "tests/fail", "#!/bin/sh\nexit 7\n")
        self._write_spec(
            root,
            tests=[self._mapping("test.fail", "tests/fail")],
            conformance=[self._covered("test.fail")],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "failed-applicable-tests")

    # validation-metadata: {"role": "helper"}
    def test_missing_runtime_interpreter_is_interface_dependency_failure(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_executable(
            root,
            "tests/missing-interpreter",
            "#!/definitely/not/a/real/interpreter\nexit 0\n",
        )
        self._write_spec(
            root,
            tests=[self._mapping("test.dep", "tests/missing-interpreter")],
            conformance=[self._covered("test.dep")],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "interface-dependency-failure")

    # validation-metadata: {"role": "helper"}
    def test_infrastructure_failure_is_distinct_from_failed_test(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        self._write_executable(root, "tests/ok", "#!/bin/sh\nexit 0\n")
        self._write_spec(
            root,
            tests=[self._mapping("test.infra", "tests/ok")],
            conformance=[self._covered("test.infra")],
        )

        # validation-metadata: {"role": "helper"}
        def broken_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            del args, kwargs
            raise OSError(errno.EIO, "synthetic infrastructure failure")

        result = test_product_impl.run_product_tests(root, runner=broken_runner)

        self.assertEqual(result["classification"], "infrastructure-failure")

    # validation-metadata: {"role": "helper"}
    def test_unexecutable_expected_test_is_unresolved(self) -> None:
        td, root = self._active_repo()
        self.addCleanup(td.cleanup)
        path = root / "tests/not-executable"
        path.parent.mkdir(parents=True)
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        self._write_spec(
            root,
            tests=[self._mapping("test.unexec", "tests/not-executable")],
            conformance=[self._covered("test.unexec")],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "unresolved-expected-tests")


if __name__ == "__main__":
    unittest.main()
