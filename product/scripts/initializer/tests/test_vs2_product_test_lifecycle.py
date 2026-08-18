from __future__ import annotations

import errno
import json
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_product_impl


class VS2ProductTestLifecycleTests(unittest.TestCase):
    def _repo(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        td = tempfile.TemporaryDirectory()
        root = Path(td.name)
        (root / "product/specs/product/level-1").mkdir(parents=True)
        (root / "product/specs/product/manifest.json").write_text(
            json.dumps(
                {
                    "spec_id": "product.manifest",
                    "status": "accepted",
                    "product_specifications": [
                        {
                            "spec_id": "product.synthetic",
                            "path": "product/specs/product/level-1/synthetic.json",
                            "status": "accepted",
                            "level": 1,
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        return td, root

    def _write_spec(self, root: Path, tests: object) -> None:
        (root / "product/specs/product/level-1/synthetic.json").write_text(
            json.dumps(
                {
                    "spec_id": "product.synthetic",
                    "status": "accepted",
                    "correspondence": {
                        "implementations": [],
                        "tests": tests,
                        "conformance": [],
                    },
                }
            ),
            encoding="utf-8",
        )

    def _test_mapping(self, test_id: str, path: str) -> dict[str, object]:
        return {
            "id": test_id,
            "paths": [path],
            "requirements": ["SYN-001"],
        }

    def _write_executable(self, root: Path, relative: str, body: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def test_honest_zero_is_deterministic_and_authority_derived(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        self._write_spec(root, [])

        first = test_product_impl.run_product_tests(root)
        second = test_product_impl.run_product_tests(root)

        self.assertEqual(first, second)
        self.assertEqual(first["applicability"], "zero-applicable")
        self.assertEqual(first["classification"], "successful-zero-applicable")
        self.assertEqual(first["accepted_specs"], ["product.synthetic"])
        self.assertEqual(first["obligations"], [])

    def test_applicable_obligations_execute_in_deterministic_order(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        log = root / "order.log"
        self._write_executable(
            root, "tests/z-test",
            "#!/bin/sh\nprintf 'z\\n' >> '" + str(log) + "'\n"
        )
        self._write_executable(
            root, "tests/a-test",
            "#!/bin/sh\nprintf 'a\\n' >> '" + str(log) + "'\n"
        )
        self._write_spec(
            root,
            [
                self._test_mapping("test.z", "tests/z-test"),
                self._test_mapping("test.a", "tests/a-test"),
            ],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "successful-applicable-execution")
        self.assertEqual([x["test_id"] for x in result["obligations"]], ["test.a", "test.z"])
        self.assertEqual(log.read_text(encoding="utf-8"), "a\nz\n")

    def test_expected_but_missing_test_is_not_zero(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        self._write_spec(root, [self._test_mapping("test.missing", "tests/missing")])

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "unresolved-expected-tests")
        self.assertEqual(result["applicability"], "applicable-and-resolved")

    def test_invalid_authority_fails_closed(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        (root / "product/specs/product/level-1/synthetic.json").write_text(
            "{not-json", encoding="utf-8"
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "applicability-invalid")

    def test_broken_registration_is_distinct_from_zero(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        self._write_spec(root, {"not": "a-list"})

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "discovery-registration-failure")
        self.assertNotEqual(result["classification"], "successful-zero-applicable")

    def test_nonzero_test_is_failed_test_class(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        self._write_executable(root, "tests/fail", "#!/bin/sh\nexit 7\n")
        self._write_spec(root, [self._test_mapping("test.fail", "tests/fail")])

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "failed-applicable-tests")

    def test_missing_runtime_interpreter_is_interface_dependency_failure(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        self._write_executable(
            root, "tests/missing-interpreter",
            "#!/definitely/not/a/real/interpreter\nexit 0\n"
        )
        self._write_spec(
            root,
            [self._test_mapping("test.dep", "tests/missing-interpreter")],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "interface-dependency-failure")

    def test_infrastructure_failure_is_distinct_from_failed_test(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        self._write_executable(root, "tests/ok", "#!/bin/sh\nexit 0\n")
        self._write_spec(root, [self._test_mapping("test.infra", "tests/ok")])

        def broken_runner(*args: object, **kwargs: object) -> subprocess.CompletedProcess[str]:
            del args, kwargs
            raise OSError(errno.EIO, "synthetic infrastructure failure")

        result = test_product_impl.run_product_tests(root, runner=broken_runner)

        self.assertEqual(result["classification"], "infrastructure-failure")

    def test_unexecutable_expected_test_is_unresolved(self) -> None:
        td, root = self._repo()
        self.addCleanup(td.cleanup)
        path = root / "tests/not-executable"
        path.parent.mkdir(parents=True)
        path.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)
        self._write_spec(
            root,
            [self._test_mapping("test.unexec", "tests/not-executable")],
        )

        result = test_product_impl.run_product_tests(root)

        self.assertEqual(result["classification"], "unresolved-expected-tests")


if __name__ == "__main__":
    unittest.main()
