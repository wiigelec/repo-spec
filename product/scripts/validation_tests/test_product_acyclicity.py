from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from validation.generated_outputs import check_generated_document_write_behavior
from product_validation.product_checks import validate_product

from validation.tests.mutation_support import create_repo_fixture, expect_failure, mutate_json


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def install_fixture(temp_repo: Path, source_name: str, dest_path: str) -> None:
    source = FIXTURE_DIR / source_name
    target = temp_repo / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def write_manifest(temp_repo: Path, entries: list[dict[str, object]]) -> None:
    mutate_json(
        temp_repo / "product/specs/product/manifest.json",
        lambda manifest: manifest.__setitem__("product_specifications", entries) or manifest,
    )


def configure_spec(temp_repo: Path, dest_path: str, *, spec_id: str, title: str, purpose: str, dependency_ids: list[str]) -> None:
    mutate_json(
        temp_repo / dest_path,
        lambda spec: (
            spec.__setitem__("spec_id", spec_id),
            spec.__setitem__("title", title),
            spec.__setitem__("purpose", purpose),
            spec.__setitem__("dependencies", [{"spec_id": dep} for dep in dependency_ids]),
            spec.__setitem__("derived_artifacts", [{"type": "markdown", "path": f"product/derived/specs/product/{Path(dest_path).stem}.md"}]),
            spec,
        )[-1],
    )


def run_product_acyclicity_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)

        temp_repo = create_repo_fixture(repo_root, temp_root, 0)
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        check_generated_document_write_behavior(temp_repo)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, 1)
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        check_generated_document_write_behavior(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-0/kernel.json",
            lambda spec: spec.__setitem__("dependencies", [{"spec_id": "product.kernel"}]) or spec,
        )
        expect_failure("self dependency", lambda: validate_product(temp_repo), "product acyclic dependencies failed: product.kernel -> product.kernel")

        temp_repo = create_repo_fixture(repo_root, temp_root, 2)
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/a.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/b.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        configure_spec(temp_repo, "product/specs/product/level-0/a.json", spec_id="product.a", title="A", purpose="A product specification.", dependency_ids=["product.b"])
        configure_spec(temp_repo, "product/specs/product/level-0/b.json", spec_id="product.b", title="B", purpose="B product specification.", dependency_ids=["product.a"])
        write_manifest(
            temp_repo,
            [
                {"spec_id": "product.kernel", "path": "product/specs/product/level-0/kernel.json", "status": "accepted", "level": 0},
                {"spec_id": "product.primitive", "path": "product/specs/product/level-1/primitive.json", "status": "accepted", "level": 1},
                {"spec_id": "product.component", "path": "product/specs/product/level-2/component.json", "status": "accepted", "level": 2},
                {"spec_id": "product.orchestration", "path": "product/specs/product/level-3/orchestration.json", "status": "accepted", "level": 3},
                {"spec_id": "product.a", "path": "product/specs/product/level-0/a.json", "status": "accepted", "level": 0},
                {"spec_id": "product.b", "path": "product/specs/product/level-0/b.json", "status": "accepted", "level": 0},
            ],
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("two-node level 0 cycle", lambda: validate_product(temp_repo), "product acyclic dependencies failed: product.a -> product.b -> product.a")

        temp_repo = create_repo_fixture(repo_root, temp_root, 3)
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/a.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/b.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        configure_spec(temp_repo, "product/specs/product/level-1/a.json", spec_id="product.a", title="A", purpose="A product specification.", dependency_ids=["product.b"])
        configure_spec(temp_repo, "product/specs/product/level-1/b.json", spec_id="product.b", title="B", purpose="B product specification.", dependency_ids=["product.a"])
        mutate_json(
            temp_repo / "product/specs/product/level-0/kernel.json",
            lambda spec: (
                spec.__setitem__("status", "accepted"),
                spec.__setitem__(
                    "correspondence",
                    {
                        "implementations": [{"id": "impl.kernel", "paths": ["product/src/kernel.py"], "requirements": ["KERNEL-001"]}],
                        "tests": [{"id": "test.kernel", "paths": ["product/tests/test_kernel.py"], "requirements": ["KERNEL-001"]}],
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
        write_manifest(
            temp_repo,
            [
                {"spec_id": "product.kernel", "path": "product/specs/product/level-0/kernel.json", "status": "accepted", "level": 0},
                {"spec_id": "product.primitive", "path": "product/specs/product/level-1/primitive.json", "status": "accepted", "level": 1},
                {"spec_id": "product.component", "path": "product/specs/product/level-2/component.json", "status": "accepted", "level": 2},
                {"spec_id": "product.orchestration", "path": "product/specs/product/level-3/orchestration.json", "status": "accepted", "level": 3},
                {"spec_id": "product.a", "path": "product/specs/product/level-1/a.json", "status": "accepted", "level": 1},
                {"spec_id": "product.b", "path": "product/specs/product/level-1/b.json", "status": "accepted", "level": 1},
            ],
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("two-node level 1 cycle", lambda: validate_product(temp_repo), "product acyclic dependencies failed: product.a -> product.b -> product.a")

        temp_repo = create_repo_fixture(repo_root, temp_root, 4)
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/a.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/b.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/c.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        configure_spec(temp_repo, "product/specs/product/level-2/a.json", spec_id="product.a", title="A", purpose="A product specification.", dependency_ids=["product.b"])
        configure_spec(temp_repo, "product/specs/product/level-2/b.json", spec_id="product.b", title="B", purpose="B product specification.", dependency_ids=["product.c"])
        configure_spec(temp_repo, "product/specs/product/level-2/c.json", spec_id="product.c", title="C", purpose="C product specification.", dependency_ids=["product.a"])
        mutate_json(
            temp_repo / "product/specs/product/level-0/kernel.json",
            lambda spec: (
                spec.__setitem__("status", "accepted"),
                spec.__setitem__(
                    "correspondence",
                    {
                        "implementations": [{"id": "impl.kernel", "paths": ["product/src/kernel.py"], "requirements": ["KERNEL-001"]}],
                        "tests": [{"id": "test.kernel", "paths": ["product/tests/test_kernel.py"], "requirements": ["KERNEL-001"]}],
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
        write_manifest(
            temp_repo,
            [
                {"spec_id": "product.kernel", "path": "product/specs/product/level-0/kernel.json", "status": "accepted", "level": 0},
                {"spec_id": "product.primitive", "path": "product/specs/product/level-1/primitive.json", "status": "accepted", "level": 1},
                {"spec_id": "product.component", "path": "product/specs/product/level-2/component.json", "status": "accepted", "level": 2},
                {"spec_id": "product.orchestration", "path": "product/specs/product/level-3/orchestration.json", "status": "accepted", "level": 3},
                {"spec_id": "product.a", "path": "product/specs/product/level-2/a.json", "status": "accepted", "level": 2},
                {"spec_id": "product.b", "path": "product/specs/product/level-2/b.json", "status": "accepted", "level": 2},
                {"spec_id": "product.c", "path": "product/specs/product/level-2/c.json", "status": "accepted", "level": 2},
            ],
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("three-node level 2 cycle", lambda: validate_product(temp_repo), "product acyclic dependencies failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, 5)
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/a.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/b.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/c.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/d.json")
        configure_spec(temp_repo, "product/specs/product/level-3/a.json", spec_id="product.a", title="A", purpose="A product specification.", dependency_ids=["product.b"])
        configure_spec(temp_repo, "product/specs/product/level-3/b.json", spec_id="product.b", title="B", purpose="B product specification.", dependency_ids=["product.c"])
        configure_spec(temp_repo, "product/specs/product/level-3/c.json", spec_id="product.c", title="C", purpose="C product specification.", dependency_ids=["product.d"])
        configure_spec(temp_repo, "product/specs/product/level-3/d.json", spec_id="product.d", title="D", purpose="D product specification.", dependency_ids=["product.b"])
        mutate_json(
            temp_repo / "product/specs/product/level-0/kernel.json",
            lambda spec: (
                spec.__setitem__("status", "accepted"),
                spec.__setitem__(
                    "correspondence",
                    {
                        "implementations": [{"id": "impl.kernel", "paths": ["product/src/kernel.py"], "requirements": ["KERNEL-001"]}],
                        "tests": [{"id": "test.kernel", "paths": ["product/tests/test_kernel.py"], "requirements": ["KERNEL-001"]}],
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
        write_manifest(
            temp_repo,
            [
                {"spec_id": "product.kernel", "path": "product/specs/product/level-0/kernel.json", "status": "accepted", "level": 0},
                {"spec_id": "product.primitive", "path": "product/specs/product/level-1/primitive.json", "status": "accepted", "level": 1},
                {"spec_id": "product.component", "path": "product/specs/product/level-2/component.json", "status": "accepted", "level": 2},
                {"spec_id": "product.orchestration", "path": "product/specs/product/level-3/orchestration.json", "status": "accepted", "level": 3},
                {"spec_id": "product.a", "path": "product/specs/product/level-3/a.json", "status": "accepted", "level": 3},
                {"spec_id": "product.b", "path": "product/specs/product/level-3/b.json", "status": "accepted", "level": 3},
                {"spec_id": "product.c", "path": "product/specs/product/level-3/c.json", "status": "accepted", "level": 3},
                {"spec_id": "product.d", "path": "product/specs/product/level-3/d.json", "status": "accepted", "level": 3},
            ],
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("four-node level 3 cycle", lambda: validate_product(temp_repo), "product acyclic dependencies failed")

    print("ok: product acyclicity tests")
