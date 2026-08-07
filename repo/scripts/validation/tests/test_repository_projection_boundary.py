from __future__ import annotations

import tempfile
from pathlib import Path

from validation.errors import ValidationFailure, fail
from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, mutate_json


def run_repository_projection_boundary_test(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        temp_repo = create_repo_fixture(repo_root, temp_root, 0)
        mutate_json(
            temp_repo / "repo/specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(
                0,
                {
                    "type": "markdown",
                    "path": "product/derived/specs/product/validation.md",
                },
            ) or spec,
        )
        try:
            validate_repo(temp_repo)
        except ValidationFailure:
            pass
        else:
            fail(
                "mutation test failed: repository projection into product root "
                "did not fail"
            )

    print("ok: repository projection boundary test")
