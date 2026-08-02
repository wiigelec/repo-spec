from __future__ import annotations

from pathlib import Path

from validation.cli_contracts import check_generate_docs_cli_contract, check_validate_cli_contract

from .test_product_acyclicity import run_product_acyclicity_tests
from .test_product_generation import run_product_generation_tests
from .test_product_dependency_directions import run_product_dependency_direction_tests
from .test_product_level_schemas import run_product_level_schema_tests
from .test_product_validation import run_product_validation_tests
from .test_product_manifest_schema import run_product_manifest_schema_tests
from .test_generation_mutations import run_generation_mutations
from .test_repository_mutations import run_repository_mutations
from .test_schema_mutations import run_schema_mutations


def run_mutation_tests(repo_root: Path) -> None:
    run_product_dependency_direction_tests(repo_root)
    run_product_acyclicity_tests(repo_root)
    run_product_level_schema_tests(repo_root)
    run_product_validation_tests(repo_root)
    run_product_manifest_schema_tests(repo_root)
    run_product_generation_tests(repo_root)
    run_schema_mutations(repo_root)
    run_repository_mutations(repo_root)
    run_generation_mutations(repo_root)


def run_complete_validation_tests(repo_root: Path) -> None:
    check_validate_cli_contract(repo_root)
    check_generate_docs_cli_contract(repo_root)
    run_mutation_tests(repo_root)
