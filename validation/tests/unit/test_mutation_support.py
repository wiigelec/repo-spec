from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from mutation_support import create_repo_fixture, expect_failure


class MutationSupportTests(unittest.TestCase):
    def test_create_repo_fixture_is_repo_only(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        with tempfile.TemporaryDirectory(prefix="repo-spec-root-unit-") as temp_name:
            fixture = create_repo_fixture(repo_root, Path(temp_name), 0)
            self.assertTrue((fixture / "repo").is_dir())
            self.assertFalse((fixture / "product").exists())
            self.assertFalse((fixture / ".github").exists())

    def test_expect_failure_accepts_matching_fragment(self) -> None:
        def fail() -> None:
            raise RuntimeError("expected fragment here")
        expect_failure("matching fragment", fail, "expected fragment")

    def test_expect_failure_rejects_wrong_fragment(self) -> None:
        def fail() -> None:
            raise RuntimeError("actual")
        with self.assertRaises(AssertionError):
            expect_failure("wrong fragment", fail, "expected")
