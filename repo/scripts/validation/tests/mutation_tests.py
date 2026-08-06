from __future__ import annotations

import sys
from pathlib import Path

from validation.cli_contracts import check_generate_docs_cli_contract, check_validate_cli_contract

from .test_product_acyclicity import run_product_acyclicity_tests
from .test_product_generation import run_product_generation_tests
from .test_product_projection_freshness import run_product_projection_freshness_tests
from .test_product_dependency_directions import run_product_dependency_direction_tests
from .test_product_level_schemas import run_product_level_schema_tests
from .test_product_validation import run_product_validation_tests
from .test_product_manifest_schema import run_product_manifest_schema_tests
from .test_reference_isolated_copy import run_reference_isolated_copy_tests
from .test_generation_mutations import run_generation_mutations
from .test_github_profile_generation import run_github_profile_generation_tests, run_github_profile_mutation_tests
from .test_repository_mutations import run_repository_mutations
from .test_schema_mutations import run_schema_mutations


def run_mutation_tests(repo_root: Path) -> None:
    run_product_dependency_direction_tests(repo_root)
    run_product_acyclicity_tests(repo_root)
    run_product_level_schema_tests(repo_root)
    run_product_validation_tests(repo_root)
    run_product_manifest_schema_tests(repo_root)
    run_product_generation_tests(repo_root)
    run_product_projection_freshness_tests(repo_root)
    run_schema_mutations(repo_root)
    run_repository_mutations(repo_root)
    run_github_profile_generation_tests(repo_root)
    run_github_profile_mutation_tests(repo_root)
    run_generation_mutations(repo_root)
    run_reference_isolated_copy_tests(repo_root)


def run_initializer_tests(repo_root: Path) -> None:
    sys.path.insert(0, str(repo_root / "product/scripts"))
    from initializer.tests.run_tests import run_initializer_tests as _run_init

    _run_init(repo_root)


def run_complete_validation_tests(repo_root: Path) -> None:
    check_validate_cli_contract(repo_root)
    check_generate_docs_cli_contract(repo_root)
    run_mutation_tests(repo_root)
    run_initializer_tests(repo_root)
