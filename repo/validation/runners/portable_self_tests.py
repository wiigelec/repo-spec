from __future__ import annotations

import tempfile
from pathlib import Path

from validation.errors import ValidationFailure
from validation.repository_checks import validate_repo


def run_repository_portable_self_tests(repo_root: Path) -> None:
    validate_repo(repo_root)

    with tempfile.TemporaryDirectory(prefix="repo-validation-self-test-") as temp_name:
        empty_repo = Path(temp_name)
        try:
            validate_repo(empty_repo)
        except Exception:
            pass
        else:
            raise ValidationFailure(
                "repository validation self-test failed: empty repository was accepted"
            )

    print("ok: portable repository validation self-tests")
