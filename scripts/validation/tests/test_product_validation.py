from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from validation.generated_outputs import check_generated_document_write_behavior
from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, expect_failure, mutate_json


FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures" / "product-validation"


def install_fixture(temp_repo: Path, source_name: str, dest_path: str) -> None:
    source = FIXTURE_DIR / source_name
    target = temp_repo / dest_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def run_product_validation_tests(repo_root: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

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
                            "implementations": [
                                {"id": "impl.kernel", "paths": ["src/kernel.py"], "requirements": ["KERNEL-001"]}
                            ],
                            "tests": [
                                {"id": "test.kernel", "paths": ["tests/test_kernel.py"], "requirements": ["KERNEL-001"]}
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

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-empty.json", "specs/product/manifest.json")
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid-four.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "specs/product/level-3/orchestration.json")
        accept_kernel(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        expect_failure(
            "accepted higher level without accepted level 0",
            lambda: validate_repo(temp_repo),
            "product completeness failed",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "rogue.json", "specs/product/level-0/repo-validation.json")
        mutate_json(
            temp_repo / "specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "repo.validation",
                    "path": "specs/product/level-0/repo-validation.json",
                    "status": "accepted",
                    "level": 0,
                }
            ) or manifest,
        )
        expect_failure("repository file in product manifest", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/secondary.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/secondary.json",
            lambda spec: (
                spec.__setitem__("spec_id", "product.secondary"),
                spec.__setitem__("title", "Secondary Primitive"),
                spec.__setitem__("purpose", "Secondary primitive product specification."),
                spec["dependencies"].__setitem__(0, {"spec_id": "product.primitive"}),
                spec["derived_artifacts"][0].__setitem__("path", "derived/specs/product/secondary.md"),
                spec,
            )[-1],
        )
        mutate_json(
            temp_repo / "specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "product.secondary",
                    "path": "specs/product/level-1/secondary.json",
                    "status": "accepted",
                    "level": 1,
                }
            ) or manifest,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-0/kernel.json",
            lambda spec: spec["dependencies"].append({"spec_id": "product.primitive"}) or spec,
        )
        expect_failure("upward dependency", lambda: validate_repo(temp_repo), "product dependency direction failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/secondary.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["dependencies"].append({"spec_id": "product.secondary"}) or spec,
        )
        mutate_json(
            temp_repo / "specs/product/level-1/secondary.json",
            lambda spec: (
                spec.__setitem__("spec_id", "product.secondary"),
                spec.__setitem__("title", "Secondary Primitive"),
                spec.__setitem__("purpose", "Secondary primitive product specification."),
                spec["dependencies"].__setitem__(0, {"spec_id": "product.primitive"}),
                spec["derived_artifacts"][0].__setitem__("path", "derived/specs/product/secondary.md"),
                spec,
            )[-1],
        )
        mutate_json(
            temp_repo / "specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "product.secondary",
                    "path": "specs/product/level-1/secondary.json",
                    "status": "accepted",
                    "level": 1,
                }
            ) or manifest,
        )
        expect_failure("same-level dependency cycle", lambda: validate_repo(temp_repo), "acyclic dependencies failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/retired.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-0/retired.json",
            lambda spec: (
                spec.__setitem__("spec_id", "product.retired-kernel"),
                spec.__setitem__("title", "Retired Kernel"),
                spec.__setitem__("purpose", "Retired kernel product specification."),
                spec.__setitem__("status", "retired"),
                spec.__setitem__("derived_artifacts", [{"type": "markdown", "path": "derived/specs/product/retired-kernel.md"}]),
                spec,
            )[-1],
        )
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["dependencies"].append({"spec_id": "product.retired-kernel"}) or spec,
        )
        mutate_json(
            temp_repo / "specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"].append(
                {
                    "spec_id": "product.retired-kernel",
                    "path": "specs/product/level-0/retired.json",
                    "status": "retired",
                    "level": 0,
                }
            ) or manifest,
        )
        expect_failure("retired dependency target", lambda: validate_repo(temp_repo), "product dependencies failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "rogue.json", "specs/product/level-0/rogue.json")
        expect_failure("product JSON without manifest", lambda: validate_repo(temp_repo), "product specification root failed: undeclared JSON content under specs/product/")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        expect_failure("missing registered file", lambda: validate_repo(temp_repo), "product manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "rogue.json", "specs/product/level-2/rogue.json")
        expect_failure("unregistered product file", lambda: validate_repo(temp_repo), "product manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-duplicate-id.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        expect_failure("duplicate product id", lambda: validate_repo(temp_repo), "duplicate product specification id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-duplicate-path.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        expect_failure("duplicate product path", lambda: validate_repo(temp_repo), "duplicate product specification path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-identity-mismatch.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        expect_failure("identity mismatch", lambda: validate_repo(temp_repo), "product manifest correspondence failed: spec_id mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-level-mismatch.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-level1.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        expect_failure("level mismatch", lambda: validate_repo(temp_repo), "product manifest correspondence failed: level mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-lifecycle-mismatch.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-status-accepted.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        expect_failure("lifecycle mismatch", lambda: validate_repo(temp_repo), "product manifest correspondence failed: lifecycle mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-missing-title.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        expect_failure("base schema conformance", lambda: validate_repo(temp_repo), "missing required property title")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-reference-missing.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted-missing-ref.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        expect_failure("unresolved reference", lambda: validate_repo(temp_repo), "product references failed: unresolved spec")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["references"].append({"type": "specification", "spec_id": "repo.validation"}) or spec,
        )
        expect_failure("repository reference in product specification", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-lineage-missing.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-lineage-missing.json", "specs/product/level-0/kernel.json")
        expect_failure("unresolved lineage", lambda: validate_repo(temp_repo), "product lineage failed: unresolved spec")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-lineage-self.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-lineage-self.json", "specs/product/level-0/kernel.json")
        expect_failure("lineage self reference", lambda: validate_repo(temp_repo), "product lineage failed: self reference")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid-four.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        install_fixture(temp_repo, "level-2-accepted.json", "specs/product/level-2/component.json")
        install_fixture(temp_repo, "level-3-accepted.json", "specs/product/level-3/orchestration.json")
        accept_kernel(temp_repo)
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/manifest.json",
            lambda manifest: manifest["product_specifications"][0].__setitem__(
                "derived_artifacts",
                [{"type": "markdown", "path": "derived/specs/product/kernel.md"}],
            ) or manifest,
        )
        expect_failure("manifest repeats derived artifacts", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-0/kernel.json",
            lambda spec: spec.__setitem__("derived_artifacts", [{"type": "markdown", "path": "derived/specs/product/primitive.md"}]) or spec,
        )
        expect_failure("duplicate derived path", lambda: validate_repo(temp_repo), "duplicate product derived artifact paths failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-wrong-level-root.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-2/kernel.json")
        expect_failure("wrong level root", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0].__setitem__("status", "verified") or spec,
        )
        expect_failure("invalid correspondence status", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: (spec["correspondence"]["implementations"][0].pop("id"), spec)[1],
        )
        expect_failure("missing implementation mapping id", lambda: validate_repo(temp_repo), "missing required property id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "/tests/test_primitive.py") or spec,
        )
        expect_failure("absolute correspondence path", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: (spec["correspondence"]["tests"][0].pop("requirements"), spec)[1],
        )
        expect_failure("missing test mapping requirements", lambda: validate_repo(temp_repo), "missing required property requirements")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0].__setitem__("status", "not-applicable") or spec,
        )
        expect_failure("malformed not-applicable correspondence", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "schemas/product/product-level-1.schema.json",
            lambda schema: schema["allOf"][1]["properties"].__setitem__("correspondence", {"type": "string"}) or schema,
        )
        expect_failure("correspondence field redefined by level schema", lambda: validate_repo(temp_repo), "must be a string")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"][0]["paths"].__setitem__(0, "src/missing.py") or spec,
        )
        expect_failure("missing implementation file", lambda: validate_repo(temp_repo), "missing path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "/tests/test_primitive.py") or spec,
        )
        expect_failure("absolute test path", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "../tests/test_primitive.py") or spec,
        )
        expect_failure("path traversal", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        (temp_repo / "src/dir").mkdir(parents=True, exist_ok=True)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"][0]["paths"].__setitem__(0, "src/dir") or spec,
        )
        expect_failure("directory instead of file", lambda: validate_repo(temp_repo), "must be a file")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"].append({"id": "impl.duplicate", "paths": ["src/primitive.py"], "requirements": ["PRIMITIVE-001"]}) or spec,
        )
        expect_failure("duplicate implementation path", lambda: validate_repo(temp_repo), "duplicate correspondence path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["conformance"][0]["implementation_ids"].__setitem__(0, "impl.missing") or spec,
        )
        expect_failure("unresolved implementation id", lambda: validate_repo(temp_repo), "unresolved implementation")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"][0]["requirements"].__setitem__(0, "KERNEL-001") or spec,
        )
        expect_failure("unknown requirement id", lambda: validate_repo(temp_repo), "unknown requirement")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        (temp_repo / "src/unused.py").parent.mkdir(parents=True, exist_ok=True)
        (temp_repo / "src/unused.py").write_text("pass\n")
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["implementations"].append({"id": "impl.unused", "paths": ["src/unused.py"], "requirements": ["PRIMITIVE-001"]}) or spec,
        )
        expect_failure("unused implementation mapping", lambda: validate_repo(temp_repo), "unreachable implementation mappings")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-valid.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        accept_kernel(temp_repo)
        (temp_repo / "tests/test_unused.py").parent.mkdir(parents=True, exist_ok=True)
        (temp_repo / "tests/test_unused.py").write_text("pass\n")
        mutate_json(
            temp_repo / "specs/product/level-1/primitive.json",
            lambda spec: spec["correspondence"]["tests"].append({"id": "test.unused", "paths": ["tests/test_unused.py"], "requirements": ["PRIMITIVE-001"]}) or spec,
        )
        expect_failure("unused test mapping", lambda: validate_repo(temp_repo), "unreachable test mappings")

    print("ok: product validation tests")
