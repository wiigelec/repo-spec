from __future__ import annotations

from pathlib import Path

from validation.cli_contracts import (
    check_generate_docs_cli_contract,
    check_validate_cli_contract,
)

from .test_generation_mutations import run_generation_mutations
from .test_github_field_policy import run_github_field_policy_tests
from .test_github_profile_generation import (
    run_github_profile_generation_tests,
    run_github_profile_mutation_tests,
)
from .test_reference_isolated_copy import run_reference_isolated_copy_tests
from .test_repository_mutations import run_repository_mutations
from .test_repository_fixture_metadata import run_repository_fixture_metadata_tests
from .test_mutation_support import run_mutation_support_tests
from .test_repository_projection_boundary import run_repository_projection_boundary_test
from .test_schema_mutations import run_schema_mutations


def run_repository_mutation_tests(repo_root: Path) -> None:
    check_validate_cli_contract(repo_root)
    check_generate_docs_cli_contract(repo_root)
    run_schema_mutations(repo_root)
    run_github_field_policy_tests(repo_root)
    run_repository_mutations(repo_root)
    run_repository_fixture_metadata_tests(repo_root)
    run_mutation_support_tests(repo_root)
    run_repository_projection_boundary_test(repo_root)
    run_github_profile_generation_tests(repo_root)
    run_github_profile_mutation_tests(repo_root)
    run_generation_mutations(repo_root)
    run_reference_isolated_copy_tests(repo_root)
