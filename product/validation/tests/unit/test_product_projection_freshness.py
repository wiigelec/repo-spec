from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from docgen import write_all
from validation.checks.domain import validate_product_phases

from ..self.mutation_support import create_repo_fixture, deactivate_product_plans, expect_failure, mutate_json


FIXTURE_DIR = Path(__file__).resolve().parent.parent / "fixtures"


# validation-metadata: {"role": "helper"}
def install_fixture(temp_repo: Path, source_name: str, dest_path: str) -> None:
    if dest_path == "product/specs/product/manifest.json" and source_name.startswith("manifest-"):
        product_specs_root = temp_repo / "product/specs/product"
        if product_specs_root.exists():
            shutil.rmtree(product_specs_root)
        product_specs_root.mkdir(parents=True, exist_ok=True)
    source = FIXTURE_DIR / source_name
    target = temp_repo / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


# validation-metadata: {"role": "helper"}
def accept_kernel(temp_repo: Path) -> None:
    mutate_json(
        temp_repo / "product/specs/product/manifest.json",
        lambda manifest: manifest["product_specifications"][0].__setitem__("status", "accepted") or manifest,
    )
    mutate_json(
        temp_repo / "product/specs/product/level-0/kernel.json",
        lambda spec: (
            spec.__setitem__("status", "accepted"),
            spec.__setitem__(
                "correspondence",
                {
                    "implementations": [{"id": "impl.kernel", "paths": ["product/src/docgen.py"], "requirements": ["KERNEL-001"]}],
                    "tests": [{"id": "test.kernel", "paths": ["product/validation/tests/unit/test_product_validation.py"], "validation_package_refs": [{"spec_id": spec["spec_id"], "requirement_id": "KERNEL-001"}]}],
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
            spec.__setitem__("derived_artifacts", [{"type": "markdown", "path": "product/derived/specs/product/kernel.md"}]),
            spec,
        )[-1],
    )


# validation-metadata: {"role": "helper"}
def build_product_repo(repo_root: Path, temp_root: Path, index: int) -> Path:
    temp_repo = create_repo_fixture(repo_root, temp_root, index)
    install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
    install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
    install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
    install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
    install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
    accept_kernel(temp_repo)
    deactivate_product_plans(temp_repo)
    write_all(temp_repo)
    validate_product_phases(
        temp_repo,
        ('product generated-document freshness',),
    )
    return temp_repo


# validation-metadata: {"role": "helper"}
def run_product_projection_freshness_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)

        temp_repo = build_product_repo(repo_root, temp_root, 0)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["normative_requirements"][0].__setitem__("text", "Changed primitive requirement") or spec,
        )
        expect_failure(
            "stale product projection",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 1)
        (temp_repo / "product/derived/specs/product/component.md").unlink()
        expect_failure(
            "missing product projection",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 2)
        orphan = temp_repo / "product/derived/specs/product/orphaned.md"
        orphan.parent.mkdir(parents=True, exist_ok=True)
        orphan.write_text("stale\n")
        expect_failure(
            "orphaned product projection",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 3)
        mutate_json(
            temp_repo / "product/specs/product/level-3/orchestration.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "product/derived/specs/product/component.md"}) or spec,
        )
        expect_failure(
            "duplicate product projection ownership",
            lambda: validate_product_phases(
                temp_repo,
                (
                    'product unique derived artifact paths',
                    'product generated-document freshness',
                ),
            ),
            "duplicate product derived artifact paths failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 4)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["derived_artifacts"].append({"type": "markdown", "path": "product/derived/specs/product/primitive.md"}) or spec,
        )
        expect_failure(
            "duplicate product declaration",
            lambda: validate_product_phases(
                temp_repo,
                ('product unique item properties',),
            ),
            "derived_artifacts failed: duplicate item properties path",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 5)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "repo/derived/specs/repo/primitive.md"}) or spec,
        )
        expect_failure(
            "invalid product projection root",
            lambda: validate_product_phases(
                temp_repo,
                ('product specification root',),
            ),
            "pattern mismatch",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 7)
        primitive_doc = temp_repo / "product/derived/specs/product/primitive.md"
        primitive_doc.write_text(primitive_doc.read_text().replace("Generated by `product/scripts/generate-docs`", "Generated by `product/scripts/generate-docs` (tampered)", 1))
        expect_failure(
            "modified generated source notice",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 8)
        mutate_json(
            temp_repo / "product/specs/product/level-3/orchestration.json",
            lambda spec: spec["dependencies"].reverse() or spec,
        )
        expect_failure(
            "order instability",
            lambda: validate_product_phases(temp_repo, ('product generated-document freshness',)),
            "generated-document freshness failed",
        )

        temp_repo = build_product_repo(repo_root, temp_root, 9)
        (temp_repo / "product/specs/product/level-3/orchestration.json").unlink()
        expect_failure(
            "removed authoritative product source",
            lambda: validate_product_phases(
                temp_repo,
                ('product correspondence inventory',),
            ),
            "product manifest completeness failed",
        )

    print("ok: product projection freshness tests")
