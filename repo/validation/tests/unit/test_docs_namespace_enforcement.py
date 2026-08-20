from __future__ import annotations

import tempfile
from pathlib import Path

from validation.checks.development_documents import (
    check_development_document_chunk_entries,
    check_development_document_namespace,
    check_development_document_root_entries,
)
from validation.core.errors import ValidationFailure


def _expect_failure(label: str, action, fragment: str) -> None:
    try:
        action()
    except ValidationFailure as exc:
        if fragment not in str(exc):
            raise AssertionError(f"{label}: unexpected failure: {exc}") from exc
        return
    raise AssertionError(f"{label}: expected validation failure")


def run_phase2_docs_namespace_tests() -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-phase2-docs-") as temp_name:
        root = Path(temp_name)
        namespace = root / "repo/docs"
        for name in ("overview", "decompositions", "plans"):
            target = namespace / name
            target.mkdir(parents=True)
            (target / "README.md").write_text("# Index\n")

        check_development_document_namespace(root, "repo/docs/", ("overview", "decompositions", "plans"))

        (namespace / "architecture").mkdir()
        _expect_failure(
            "unknown namespace directory",
            lambda: check_development_document_namespace(root, "repo/docs/", ("overview", "decompositions", "plans")),
            "direct entries must be exactly",
        )
        (namespace / "architecture").rmdir()

        overview = namespace / "overview"
        controller = overview / "TEST-FUNCTIONAL-SET.md"
        controller.write_text("# Test\n")
        chunk_dir = overview / "test-functional-set"
        chunk_dir.mkdir()
        chunk = chunk_dir / "01-capability.md"
        chunk.write_text("# Capability\n")

        check_development_document_root_entries(
            overview, "repo/docs/overview/", {controller.name}, {chunk_dir.name}
        )
        check_development_document_chunk_entries(
            root, chunk_dir, ["repo/docs/overview/test-functional-set/01-capability.md"]
        )

        (overview / "orphan").mkdir()
        _expect_failure(
            "orphan chunk directory",
            lambda: check_development_document_root_entries(
                overview, "repo/docs/overview/", {controller.name}, {chunk_dir.name}
            ),
            "closed root mismatch",
        )
        (overview / "orphan").rmdir()

        extra = chunk_dir / "02-extra.md"
        extra.write_text("# Extra\n")
        _expect_failure(
            "undeclared chunk",
            lambda: check_development_document_chunk_entries(
                root, chunk_dir, ["repo/docs/overview/test-functional-set/01-capability.md"]
            ),
            "inventory mismatch",
        )


if __name__ == "__main__":
    run_phase2_docs_namespace_tests()
    print("ok: phase2 docs namespace enforcement")
