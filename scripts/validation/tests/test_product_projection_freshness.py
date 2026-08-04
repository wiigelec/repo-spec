from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from docgen import write_all
from validation.generated_outputs import check_generated_document_freshness
from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, expect_failure, mutate_json


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def install_fixture(temp_repo: Path, source_name: str, dest_path: str) -> None:
    source = FIXTURE_DIR / source_name
    target = temp_repo / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def accept_kernel(temp_repo: Path) -> None:
    mutate_json(
        temp_repo / "specs/product/manifest.json",
        lambda manifest: manifest["product_specifications"][0].__setitem__("status", "accepted") or manifest,
    )
    mutate_json(
        temp_repo / "specs/product/level-0/kernel.json",
        lambda spec: (
            spec.__setitem__("status", "accepted"),
            spec.__setitem__(
                "correspondence",
                {
                    "implementations": [{"id": "impl.kernel", "paths": ["src/kernel.py"], "requirements": ["KERNEL-001"]}],
                    "tests": [{"id": "test.kernel", "paths": ["tests/test_kernel.py"], "requirements": ["KERNEL-001"]}],
                    "conformance": [
                        {
                            "requirement_id": "KERNEL-001",
                            "implementation_ids": ["impl.kernel"],
                            "test_ids": ["test.kernel"],
                            "status": "covered",
                        }
                    ],
                },
            ),
            spec.__setitem__("derived_artifacts", [{"type": "markdown", "path": "derived/specs/product/kernel.md"}]),
            spec,
        )[-1],
    )


def build_product_repo(repo_root: Path, temp_root: Path, index: int) -> Path:
    temp_repo = create_repo_fixture(repo_root, temp_root, index)
    install_fixture(temp_repo, "manifest-valid-four.json", "specs/product/manifest.json")
    install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
    install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
    install_fixture(temp_repo, "level-2-accepted.json", "specs/product/level-2/component.json")
    install_fixture(temp_repo, "level-3-accepted.json", "specs/product/level-3/orchestration.json")
    accept_kernel(temp_repo)
    write_all(temp_repo)
    validate_repo(temp_repo)
    return temp_repo


def run_product_projection_freshness_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)

        temp_repo = build_product_repo(repo_root, temp_root, 0)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["normative_requirements"][0].__setitem__("text", "Changed primitive requirement") or spec,
        )
        expect_failure(
            "stale product projection",
            lambda: check_generated_document_freshness(temp_repo),
            "stale generated document: source specs/product/level-1/primitive.json -> output derived/specs/product/primitive.md",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 1)
        (temp_repo / "derived/specs/product/component.md").unlink()
        expect_failure(
            "missing product projection",
            lambda: check_generated_document_freshness(temp_repo),
            "missing derived markdown: derived/specs/product/component.md",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 2)
        orphan = temp_repo / "derived/specs/product/orphaned.md"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("stale\n")
        expect_failure(
            "orphaned product projection",
            lambda: check_generated_document_freshness(temp_repo),
            "orphaned derived markdown",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 3)
        mutate_json(
            temp_repo / "specs/product/level-3/orchestration.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/product/component.md"}) or spec,
        )
        expect_failure(
            "duplicate product projection ownership",
            lambda: check_generated_document_freshness(temp_repo),
            "duplicate derived artifact paths failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 4)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["derived_artifacts"].append({"type": "markdown", "path": "derived/specs/product/primitive.md"}) or spec,
        )
        expect_failure(
            "duplicate product declaration",
            lambda: check_generated_document_freshness(temp_repo),
            "duplicate derived artifact paths failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 5)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/primitive.md"}) or spec,
        )
        expect_failure(
            "invalid product projection root",
            lambda: validate_repo(temp_repo),
            "pattern mismatch",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 6)
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/product/validation.md"}) or spec,
        )
        expect_failure(
            "repository projection in product root",
            lambda: validate_repo(temp_repo),
            "missing derived markdown: derived/specs/product/validation.md; orphaned derived markdown: derived/specs/repo/validation.md",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 7)
        primitive_doc = temp_repo / "derived/specs/product/primitive.md"
        primitive_doc.write_text(primitive_doc.read_text().replace("Generated by `scripts/generate-docs`", "Generated by `scripts/generate-docs` (tampered)", 1))
        expect_failure(
            "modified generated source notice",
            lambda: check_generated_document_freshness(temp_repo),
            "stale generated document: source specs/product/level-1/primitive.json -> output derived/specs/product/primitive.md",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 8)
        mutate_json(
            temp_repo / "specs/product/level-3/orchestration.json",
            lambda spec: spec["dependencies"].reverse() or spec,
        )
        expect_failure(
            "order instability",
            lambda: check_generated_document_freshness(temp_repo),
            "stale generated document: source specs/product/level-3/orchestration.json -> output derived/specs/product/orchestration.md",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 9)
        (temp_repo / "specs/product/level-3/orchestration.json").unlink()
        expect_failure(
            "removed authoritative product source",
            lambda: check_generated_document_freshness(temp_repo),
            "product manifest completeness failed",
        )

    print("ok: product projection freshness tests")
