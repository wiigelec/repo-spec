from __future__ import annotations

import tempfile
from pathlib import Path
import unittest

from validation.checks.policy import check_repository_source_layout
from validation.core.context import ValidationContext
from validation.core.errors import ValidationFailure


class RepositorySourceLayoutTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def _context(self, root: Path) -> ValidationContext:
        return ValidationContext(root, None, None, None)

    # validation-metadata: {"role": "helper"}
    def _make_valid_layout(self, root: Path) -> None:
        (root / "repo/src").mkdir(parents=True)
        scripts = root / "repo/scripts"
        scripts.mkdir(parents=True)
        wrapper = scripts / "validate"
        wrapper.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
        wrapper.chmod(0o755)

    # validation-metadata: {"role": "helper"}
    def test_accepts_wrapper_only_scripts_and_src(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_valid_layout(root)
            check_repository_source_layout(self._context(root))

    # validation-metadata: {"role": "helper"}
    def test_rejects_python_implementation_in_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_valid_layout(root)
            impl = root / "repo/scripts/helper.py"
            impl.write_text("pass\n", encoding="utf-8")
            impl.chmod(0o755)
            with self.assertRaises(ValidationFailure):
                check_repository_source_layout(self._context(root))

    # validation-metadata: {"role": "helper"}
    def test_rejects_directory_in_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_valid_layout(root)
            (root / "repo/scripts/helpers").mkdir()
            with self.assertRaises(ValidationFailure):
                check_repository_source_layout(self._context(root))

    # validation-metadata: {"role": "helper"}
    def test_rejects_non_executable_entry_point(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_valid_layout(root)
            wrapper = root / "repo/scripts/generate-docs"
            wrapper.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8")
            wrapper.chmod(0o644)
            with self.assertRaises(ValidationFailure):
                check_repository_source_layout(self._context(root))

    # validation-metadata: {"role": "helper"}
    def test_rejects_validation_under_src(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_valid_layout(root)
            (root / "repo/src/validation").mkdir()
            with self.assertRaises(ValidationFailure):
                check_repository_source_layout(self._context(root))


    # validation-metadata: {"role": "helper"}
    def test_ignores_derived_src_hierarchy(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_valid_layout(root)
            derived_src = root / "repo/derived/generated/src"
            derived_src.mkdir(parents=True)
            (derived_src / "implementation.py").write_text("pass\n", encoding="utf-8")
            check_repository_source_layout(self._context(root))


if __name__ == "__main__":
    unittest.main()
