from __future__ import annotations

import tempfile
from pathlib import Path

from repo.validation.core.errors import ValidationFailure

from repo.validation.tests.self.mutation_support import create_repo_fixture, declared_repo_fixture_paths

I5_EVIDENCE = "product/evidence/i5/full-initialization-exit.json"
PLAN = "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"


def _expect_validation_failure(label: str, action, fragment: str) -> None:
    try:
        action()
    except ValidationFailure as exc:
        if fragment not in str(exc):
            raise AssertionError(f"{label}: expected {fragment!r}, got {exc}") from exc
        return
    raise AssertionError(f"{label}: expected ValidationFailure")


def run_mutation_support_tests(repo_root: Path) -> None:
    if I5_EVIDENCE not in declared_repo_fixture_paths(repo_root):
        raise AssertionError("valid I5 evidence disappeared from fixture inventory")

    with tempfile.TemporaryDirectory(prefix="repo-spec-mutation-support-") as temp_root_name:
        temp_root = Path(temp_root_name)

        temp_repo = create_repo_fixture(repo_root, temp_root, 0)
        plan_path = temp_repo / PLAN
        text = plan_path.read_text()
        marker = "## Metadata\n"
        if marker not in text:
            raise AssertionError("initializer plan metadata heading missing")
        plan_path.write_text(
            text.replace(
                marker,
                '```json\n{"unrelated": true}\n```\n\n' + marker,
                1,
            )
        )
        paths = declared_repo_fixture_paths(temp_repo)
        if I5_EVIDENCE not in paths:
            raise AssertionError("earlier unrelated JSON fence redirected fixture metadata parsing")

        temp_repo = create_repo_fixture(repo_root, temp_root, 1)
        plan_path = temp_repo / PLAN
        text = plan_path.read_text()
        canonical = '"artifact_id": "initializer-implementation-plan"'
        if canonical not in text:
            raise AssertionError("initializer plan artifact_id anchor missing")
        plan_path.write_text(text.replace(canonical, '"artifact_id": ', 1))
        _expect_validation_failure(
            "malformed canonical metadata",
            lambda: declared_repo_fixture_paths(temp_repo),
            "development document metadata failed: invalid JSON",
        )
