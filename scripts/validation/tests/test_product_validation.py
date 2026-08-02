from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from validation.repository_checks import validate_repo

from .mutation_support import create_repo_fixture, expect_failure


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
        validate_repo(temp_repo)

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
        expect_failure("identity mismatch", lambda: validate_repo(temp_repo), "product manifest correspondence failed: spec_id mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-level-mismatch.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate-level1.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
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
        expect_failure("base schema conformance", lambda: validate_repo(temp_repo), "missing required property title")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-reference-missing.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted-missing-ref.json", "specs/product/level-1/primitive.json")
        expect_failure("unresolved reference", lambda: validate_repo(temp_repo), "product references failed: unresolved spec")

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
        install_fixture(temp_repo, "manifest-duplicate-derived.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-0/kernel.json")
        install_fixture(temp_repo, "level-1-accepted.json", "specs/product/level-1/primitive.json")
        expect_failure("duplicate derived path", lambda: validate_repo(temp_repo), "duplicate product derived artifact paths failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        install_fixture(temp_repo, "manifest-wrong-level-root.json", "specs/product/manifest.json")
        install_fixture(temp_repo, "level-0-candidate.json", "specs/product/level-2/kernel.json")
        expect_failure("wrong level root", lambda: validate_repo(temp_repo), "oneOf mismatch")

    print("ok: product validation tests")
