from __future__ import annotations

import tempfile
from pathlib import Path

from validation.core.errors import ValidationFailure

from ..self.mutation_support import create_repo_fixture, declared_repo_fixture_paths


SYNTHETIC_DOC = "repo/docs/plans/SYNTHETIC-IMPLEMENTATION-PLAN.md"
SYNTHETIC_DEP = "repo/docs/plans/synthetic-dependency.md"
SYNTHETIC_CHUNK = "repo/docs/plans/synthetic-chunk.md"


def _expect_validation_failure(label: str, action, fragment: str) -> None:
    try:
        action()
    except ValidationFailure as exc:
        if fragment not in str(exc):
            raise AssertionError(f"{label}: expected {fragment!r}, got {exc}") from exc
        return
    raise AssertionError(f"{label}: expected ValidationFailure")


def _synthetic_document(*, malformed: bool = False, earlier_json: bool = False) -> str:
    prefix = ""
    if earlier_json:
        prefix = '```json\n{"unrelated": true}\n```\n\n'

    metadata = """{
  "artifact_id": "synthetic-implementation-plan",
  "artifact_type": "implementation-plan",
  "product_id": "synthetic",
  "authority_category": "planning",
  "lifecycle_status": "candidate",
  "governing_issue": "#309",
  "controlling_documents": [],
  "predecessor_documents": [],
  "required_content_areas": {
    "synthetic_area": [
      "repo/docs/plans/synthetic-dependency.md"
    ]
  },
  "subordinate_chunks": [
    {
      "path": "repo/docs/plans/synthetic-chunk.md",
      "role": "synthetic"
    }
  ],
  "successor_action": "No successor action."
}"""

    if malformed:
        metadata = metadata.replace(
            '"artifact_id": "synthetic-implementation-plan"',
            '"artifact_id": ',
            1,
        )

    return (
        prefix
        + "# Synthetic Implementation Plan\n\n"
        + "## Status\n\nCandidate.\n\n"
        + "## Metadata\n\n```json\n"
        + metadata
        + "\n```\n\n"
        + "## Planning basis\n\nSynthetic fixture-only document.\n\n"
        + "## Workstreams\n\nNone.\n\n"
        + "## Chunk index\n\nSynthetic.\n\n"
        + "## Relationships\n\nSynthetic.\n\n"
        + "## Next authorized action\n\nNone.\n\n"
        + "## Discoverability\n\nSynthetic.\n"
    )


def _install_synthetic_document(repo_root: Path, text: str) -> None:
    doc_path = repo_root / SYNTHETIC_DOC
    doc_path.parent.mkdir(parents=True, exist_ok=True)
    doc_path.write_text(text)
    (repo_root / SYNTHETIC_DEP).write_text("synthetic dependency\n")
    (repo_root / SYNTHETIC_CHUNK).write_text("synthetic chunk\n")


def run_repository_fixture_metadata_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-repo-fixture-meta-") as temp_root_name:
        temp_root = Path(temp_root_name)

        # Canonical metadata discovers both required-content and subordinate-chunk paths.
        temp_repo = create_repo_fixture(repo_root, temp_root, 0)
        _install_synthetic_document(temp_repo, _synthetic_document())
        baseline = declared_repo_fixture_paths(temp_repo)
        for expected in (SYNTHETIC_DEP, SYNTHETIC_CHUNK):
            if expected not in baseline:
                raise AssertionError(f"synthetic repository fixture dependency missing: {expected}")

        # An unrelated JSON fence before ## Metadata must not redirect discovery.
        temp_repo = create_repo_fixture(repo_root, temp_root, 1)
        _install_synthetic_document(temp_repo, _synthetic_document(earlier_json=True))
        mutated = declared_repo_fixture_paths(temp_repo)
        for expected in (SYNTHETIC_DEP, SYNTHETIC_CHUNK):
            if expected not in mutated:
                raise AssertionError(
                    f"earlier unrelated JSON fence redirected repository fixture discovery: {expected}"
                )

        # Malformed canonical metadata must use the governed validation failure model.
        temp_repo = create_repo_fixture(repo_root, temp_root, 2)
        _install_synthetic_document(temp_repo, _synthetic_document(malformed=True))
        _expect_validation_failure(
            "malformed repository metadata",
            lambda: declared_repo_fixture_paths(temp_repo),
            "development document metadata failed: invalid JSON",
        )
