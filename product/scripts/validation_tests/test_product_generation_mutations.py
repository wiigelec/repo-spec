from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from docgen import write_all
from product_validation.product_checks import validate_product_phases
from .mutation_support import (
    create_repo_fixture,
    deactivate_product_plans,
    expect_failure,
    mutate_json,
)


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def install_fixture(temp_repo: Path, source_name: str, dest_path: str) -> None:
    source = FIXTURE_DIR / source_name
    target = temp_repo / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def accept_kernel(temp_repo: Path) -> None:
    mutate_json(
        temp_repo / "product/specs/product/manifest.json",
        lambda manifest: manifest["product_specifications"][0].__setitem__(
            "status", "accepted"
        ) or manifest,
    )
    mutate_json(
        temp_repo / "product/specs/product/level-0/kernel.json",
        lambda spec: (
            spec.__setitem__("status", "accepted"),
            spec.__setitem__(
                "correspondence",
                {
                    "implementations": [
                        {
                            "id": "impl.kernel",
                            "paths": ["product/src/kernel.py"],
                            "requirements": ["KERNEL-001"],
                        }
                    ],
                    "tests": [
                        {
                            "id": "test.kernel",
                            "paths": ["product/tests/test_kernel.py"],
                            "requirements": ["KERNEL-001"],
                        }
                    ],
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
            spec,
        )[-1],
    )


def build_product_repo(repo_root: Path, temp_root: Path, index: int) -> Path:
    temp_repo = create_repo_fixture(repo_root, temp_root, index)
    install_fixture(
        temp_repo,
        "manifest-valid-four.json",
        "product/specs/product/manifest.json",
    )
    install_fixture(
        temp_repo,
        "level-0-candidate.json",
        "product/specs/product/level-0/kernel.json",
    )
    install_fixture(
        temp_repo,
        "level-1-accepted.json",
        "product/specs/product/level-1/primitive.json",
    )
    install_fixture(
        temp_repo,
        "level-2-accepted.json",
        "product/specs/product/level-2/component.json",
    )
    install_fixture(
        temp_repo,
        "level-3-accepted.json",
        "product/specs/product/level-3/orchestration.json",
    )
    accept_kernel(temp_repo)
    deactivate_product_plans(temp_repo)
    return temp_repo


def run_product_generation_mutation_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_name:
        temp_root = Path(temp_name)

        temp_repo = build_product_repo(repo_root, temp_root, 0)
        write_all(temp_repo)
        validate_product_phases(temp_repo, ('product generated-document freshness',))

        temp_repo = build_product_repo(repo_root, temp_root, 1)
        write_all(temp_repo)
        product_doc = temp_repo / "product/derived/specs/product/primitive.md"
        product_doc.write_text(
            product_doc.read_text().replace(
                "Primitive",
                "Primitive Projection",
                1,
            )
        )
        expect_failure(
            "product generated artifact freshness",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 2)
        orphan = temp_repo / "product/derived/specs/product/orphaned.md"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("stale\n")
        expect_failure(
            "product orphaned derived markdown",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

    print("ok: product generation mutation tests")
