from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from initializer.full_initialization_actions import (
    _AMBIENT_VALIDATION_ENV_KEYS,
    _run_installed_repository_validation,
)


class InstalledValidationGateTests(unittest.TestCase):
    def _repository(self, script: str):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        validator = root / "scripts/validate"
        validator.parent.mkdir(parents=True)
        validator.write_text("#!/usr/bin/env bash\nset -euo pipefail\n" + script)
        validator.chmod(0o755)
        return temp, root

    def test_success_uses_staged_repository_as_working_directory(self) -> None:
        temp, root = self._repository("")
        try:
            marker = root / "observed"
            (root / "scripts/validate").write_text(
                "#!/usr/bin/env bash\nset -euo pipefail\n"
                f'printf "%s" "$PWD" > "{marker}"\n'
            )
            (root / "scripts/validate").chmod(0o755)
            _run_installed_repository_validation(root)
            self.assertEqual(marker.read_text(), str(root))
        finally:
            temp.cleanup()

    def test_ambient_python_shell_and_git_overrides_are_removed(self) -> None:
        checks = "\n".join(
            f'test -z "${{{key}-}}"' for key in _AMBIENT_VALIDATION_ENV_KEYS
        )
        temp, root = self._repository(checks + "\n")
        try:
            poison = {key: "/source-checkout/poison" for key in _AMBIENT_VALIDATION_ENV_KEYS}
            with patch.dict(os.environ, poison, clear=False):
                _run_installed_repository_validation(root)
        finally:
            temp.cleanup()

    def test_nonzero_installed_validation_fails_closed(self) -> None:
        temp, root = self._repository('echo "broken installed validator" >&2\nexit 23\n')
        try:
            with self.assertRaisesRegex(
                RuntimeError,
                r"installed repository validation failed \(exit 23\).*broken installed validator",
            ):
                _run_installed_repository_validation(root)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
