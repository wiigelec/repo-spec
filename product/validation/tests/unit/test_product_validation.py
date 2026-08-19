from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .generation_support import check_generated_document_write_behavior
from validation.checks.product_checks import validate_product_phases

from .mutation_support import create_repo_fixture, deactivate_product_plans, expect_failure, mutate_json


FIXTURE_DIR = Path(__file__).resolve().parent


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
                    "implementations": [
                        {"id": "impl.kernel", "paths": ["product/src/kernel.py"], "requirements": ["KERNEL-001"]}
                    ],
                    "tests": [
                        {"id": "test.kernel", "paths": ["product/tests/test_kernel.py"], "requirements": ["KERNEL-001"]}
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

def run_product_dependency_policy_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-empty.json", "product/specs/product/manifest.json")
        deactivate_product_plans(temp_repo)
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-2/component.json",
            lambda spec: spec.__setitem__("status", "candidate") or spec,
        )
        mutate_json(
            temp_repo / "product/specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"][2].__setitem__("status", "candidate") or manifest,
        )
        deactivate_product_plans(temp_repo)
        expect_failure(
            "accepted product depends on candidate",
            lambda: validate_product_phases(temp_repo, ('product specification root', 'product completeness')),
            "accepted spec product.orchestration -> candidate target product.component",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        deactivate_product_plans(temp_repo)
        expect_failure(
            "accepted higher level without accepted level 0",
            lambda: validate_product_phases(temp_repo, ('product specification root', 'product completeness')),
            "accepted spec product.primitive -> candidate target product.kernel",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec.__setitem__("dependencies", []) or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure(
            "accepted higher level disconnected from unrelated accepted Level 0",
            lambda: validate_product_phases(temp_repo, ('product specification root', 'product completeness')),
            "product completeness failed: accepted spec product.primitive has no accepted Level 0 specification in its transitive dependency closure",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        mutate_json(
            temp_repo / "product/specs/product/level-3/orchestration.json",
            lambda spec: spec.__setitem__("dependencies", [{"spec_id": "product.kernel"}]) or spec,
        )
        deactivate_product_plans(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/retired.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-0/retired.json",
            lambda spec: (
                spec.__setitem__("spec_id", "product.retired-kernel"),
                spec.__setitem__("title", "Retired Kernel"),
                spec.__setitem__("purpose", "Retired kernel product specification."),
                spec.__setitem__("status", "retired"),
                spec.__setitem__("derived_artifacts", [{"type": "markdown", "path": "product/derived/specs/product/retired-kernel.md"}]),
                spec,
            )[-1],
        )
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["dependencies"].append({"spec_id": "product.retired-kernel"}) or spec,
        )
        mutate_json(
            temp_repo / "product/specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "product.retired-kernel",
                    "path": "product/specs/product/level-0/retired.json",
                    "status": "retired",
                    "level": 0,
                }
            ) or manifest,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("retired dependency target", lambda: validate_product_phases(temp_repo, ('product specification root', 'product completeness')), "product dependencies failed")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/secondary.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/secondary.json",
            lambda spec: (
                spec.__setitem__("spec_id", "product.secondary"),
                spec.__setitem__("title", "Secondary Primitive"),
                spec.__setitem__("purpose", "Secondary primitive product specification."),
                spec["dependencies"].__setitem__(0, {"spec_id": "product.primitive"}),
                spec["derived_artifacts"][0].__setitem__("path", "product/derived/specs/product/secondary.md"),
                spec,
            )[-1],
        )
        mutate_json(
            temp_repo / "product/specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "product.secondary",
                    "path": "product/specs/product/level-1/secondary.json",
                    "status": "accepted",
                    "level": 1,
                }
            ) or manifest,
        )
        deactivate_product_plans(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid-four.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "product/specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "product/specs/product/level-3/orchestration.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_product_phases(temp_repo, ('product specification root', 'product completeness'))

    print("ok: product dependency policy tests")

def run_product_schema_boundary_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "rogue.json", "product/specs/product/level-0/repo-validation.json")
        mutate_json(
            temp_repo / "product/specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "repo.validation",
                    "path": "product/specs/product/level-0/repo-validation.json",
                    "status": "accepted",
                    "level": 0,
                }
            ) or manifest,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("repository file in product manifest", lambda: validate_product_phases(temp_repo, ('product specification root',)), "oneOf mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-missing-title.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        expect_failure("base schema conformance", lambda: validate_product_phases(temp_repo, ('product specification root',)), "missing required property title")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["references"].append({"type": "specification", "spec_id": "repo.validation"}) or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("repository reference in product specification", lambda: validate_product_phases(temp_repo, ('product specification root',)), "oneOf mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"][0].__setitem__(
                "derived_artifacts",
                [{"type": "markdown", "path": "product/derived/specs/product/kernel.md"}],
            ) or manifest,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("manifest repeats derived artifacts", lambda: validate_product_phases(temp_repo, ('product specification root',)), "oneOf mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-wrong-level-root.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-2/kernel.json")
        deactivate_product_plans(temp_repo)
        expect_failure("wrong level root", lambda: validate_product_phases(temp_repo, ('product specification root',)), "oneOf mismatch")

    print("ok: product schema-boundary tests")


def run_product_manifest_completeness_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        deactivate_product_plans(temp_repo)
        expect_failure("missing registered file", lambda: validate_product_phases(temp_repo, ('product correspondence inventory',)), "product manifest completeness failed")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "rogue.json", "product/specs/product/level-2/rogue.json")
        deactivate_product_plans(temp_repo)
        expect_failure("unregistered product file", lambda: validate_product_phases(temp_repo, ('product correspondence inventory',)), "product manifest completeness failed")

    print("ok: product manifest completeness tests")


def run_product_manifest_uniqueness_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-duplicate-id.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        deactivate_product_plans(temp_repo)
        expect_failure("duplicate product id", lambda: validate_product_phases(temp_repo, ('product unique specification IDs', 'product unique item properties')), "duplicate product specification id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-duplicate-path.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        deactivate_product_plans(temp_repo)
        expect_failure("duplicate product path", lambda: validate_product_phases(temp_repo, ('product unique specification IDs', 'product unique item properties')), "duplicate product specification path")

    print("ok: product manifest uniqueness tests")


def run_product_manifest_correspondence_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-identity-mismatch.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        expect_failure("identity mismatch", lambda: validate_product_phases(temp_repo, ('product correspondence inventory',)), "product manifest correspondence failed: spec_id mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-level-mismatch.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-level1.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        expect_failure("level mismatch", lambda: validate_product_phases(temp_repo, ('product correspondence inventory',)), "product manifest correspondence failed: level mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-lifecycle-mismatch.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        deactivate_product_plans(temp_repo)
        expect_failure("lifecycle mismatch", lambda: validate_product_phases(temp_repo, ('product correspondence inventory',)), "product manifest correspondence failed: lifecycle mismatch")

    print("ok: product manifest correspondence tests")


def run_product_reference_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-reference-missing.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted-missing-ref.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        deactivate_product_plans(temp_repo)
        expect_failure("unresolved reference", lambda: validate_product_phases(temp_repo, ('product specification root',)), "product references failed: unresolved spec")

    print("ok: product reference tests")


def run_product_lineage_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-lineage-missing.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-lineage-missing.json", "product/specs/product/level-0/kernel.json")
        deactivate_product_plans(temp_repo)
        expect_failure("unresolved lineage", lambda: validate_product_phases(temp_repo, ('product lineage relations',)), "product lineage failed: unresolved spec")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-lineage-self.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-lineage-self.json", "product/specs/product/level-0/kernel.json")
        deactivate_product_plans(temp_repo)
        expect_failure("lineage self reference", lambda: validate_product_phases(temp_repo, ('product lineage relations',)), "product lineage failed: self reference")

    print("ok: product lineage tests")

def run_product_correspondence_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-empty.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        mutate_json(
            temp_repo / "product/specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "product.kernel",
                    "path": "product/specs/product/level-0/kernel.json",
                    "status": "candidate",
                    "level": 0,
                }
            ) or manifest,
        )
        mutate_json(
            temp_repo / "product/specs/product/level-0/kernel.json",
            lambda spec: (
                spec["correspondence"]["implementations"].append({"id": "impl.kernel", "paths": ["product/src/kernel.py"], "requirements": ["KERNEL-001"]}),
                spec["correspondence"]["tests"].append({"id": "test.kernel", "paths": ["product/tests/test_kernel.py"], "requirements": ["KERNEL-001"]}),
                spec,
            )[-1],
        )
        deactivate_product_plans(temp_repo)
        expect_failure(
            "candidate unreachable correspondence mappings",
            lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')),
            "unreachable implementation mappings impl.kernel",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec.__setitem__("correspondence", {"implementations": [], "tests": [], "conformance": []}) or spec,
        )
        deactivate_product_plans(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness'))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"].append(spec["correspondence"]["conformance"][0].copy()) or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("duplicate conformance record", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "duplicate conformance")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0]["implementation_ids"].clear() or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("covered requirement without implementation mapping", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "requires at least one implementation mapping")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0]["test_ids"].clear() or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("covered requirement without test mapping", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "requires at least one test mapping")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: (
                spec["correspondence"]["conformance"][0].__setitem__("status", "not-applicable"),
                spec["correspondence"]["conformance"][0].__setitem__("implementation_ids", []),
                spec["correspondence"]["conformance"][0].__setitem__("test_ids", []),
                spec["correspondence"]["conformance"][0].__setitem__("rationale", "   "),
                spec,
            )[-1],
        )
        deactivate_product_plans(temp_repo)
        expect_failure("not-applicable without rationale", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "requires rationale")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: (
                spec["correspondence"]["conformance"][0].__setitem__("status", "not-applicable"),
                spec["correspondence"]["conformance"][0].__setitem__("rationale", "Not applicable for this product."),
                spec,
            )[-1],
        )
        deactivate_product_plans(temp_repo)
        expect_failure("not-applicable with implementation mapping", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "must not reference implementation mappings")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: (
                spec["correspondence"]["conformance"][0].__setitem__("status", "not-applicable"),
                spec["correspondence"]["conformance"][0].__setitem__("implementation_ids", []),
                spec["correspondence"]["conformance"][0].__setitem__("rationale", "Not applicable for this product."),
                spec,
            )[-1],
        )
        deactivate_product_plans(temp_repo)
        expect_failure("not-applicable with test mapping", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "must not reference test mappings")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0].__setitem__("status", "verified") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("invalid correspondence status", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "oneOf mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: (spec["correspondence"]["implementations"][0].pop("id"), spec)[1],
        )
        deactivate_product_plans(temp_repo)
        expect_failure("missing implementation mapping id", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "missing required property id")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "/product/tests/test_primitive.py") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("absolute correspondence path", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "pattern mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: (spec["correspondence"]["tests"][0].pop("requirements"), spec)[1],
        )
        deactivate_product_plans(temp_repo)
        expect_failure("missing test mapping requirements", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "missing required property requirements")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0].__setitem__("status", "not-applicable") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("malformed not-applicable correspondence", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "oneOf mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/schemas/product/product-level-1.schema.json",
            lambda schema: schema["allOf"][1]["properties"].__setitem__("correspondence", {"type": "string"}) or schema,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("correspondence field redefined by level schema", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "must be a string")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"][0]["paths"].__setitem__(0, "product/src/missing.py") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("missing implementation file", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "missing path")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "/product/tests/test_primitive.py") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("absolute test path", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "pattern mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "../product/tests/test_primitive.py") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("path traversal", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "pattern mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        (temp_repo / "product/src/dir").mkdir(parents=True, exist_ok=True)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "product/src/dir") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("directory instead of file", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "must be a file")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"].append({"id": "impl.duplicate", "paths": ["product/src/primitive.py"], "requirements": ["PRIMITIVE-001"]}) or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("duplicate implementation path", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "duplicate correspondence path")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0].__setitem__("requirement_id", "KERNEL-001") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("unknown conformance requirement", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "unknown requirement")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"][0]["requirements"].__setitem__(0, "KERNEL-001") or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("unknown requirement id", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "unknown requirement")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        (temp_repo / "product/src/unused.py").parent.mkdir(parents=True, exist_ok=True)
        (temp_repo / "product/src/unused.py").write_text("pass\n")
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"].append({"id": "impl.unused", "paths": ["product/src/unused.py"], "requirements": ["PRIMITIVE-001"]}) or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("unused implementation mapping", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "unreachable implementation mappings")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "product/specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "product/specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "product/specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        (temp_repo / "product/tests/test_unused.py").parent.mkdir(parents=True, exist_ok=True)
        (temp_repo / "product/tests/test_unused.py").write_text("pass\n")
        mutate_json(
            temp_repo / "product/specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"].append({"id": "test.unused", "paths": ["product/tests/test_unused.py"], "requirements": ["PRIMITIVE-001"]}) or spec,
        )
        deactivate_product_plans(temp_repo)
        expect_failure("unused test mapping", lambda: validate_product_phases(temp_repo, ('product correspondence inventory', 'product conformance completeness')), "unreachable test mappings")

    print("ok: product correspondence tests")
