from __future__ import annotations

from pathlib import Path

from validation.cli_contracts import (
    check_generate_docs_cli_contract,
    check_validate_cli_contract,
)

from .test_architecture_document_contract import run_architecture_document_contract_tests
from .test_functional_set_overview_contract import run_functional_set_overview_contract_tests
from .test_generation_mutations import run_generation_mutations
from .test_github_field_policy import run_github_field_policy_tests
from .test_issue_intake_governance_routing import run_issue_intake_governance_routing_tests
from .test_issue_routing_hosted_conformance import run_issue_routing_hosted_conformance_tests
from .test_github_profile_generation import (
    run_github_profile_generation_tests,
    run_github_profile_mutation_tests,
)
from .test_reference_isolated_copy import run_reference_isolated_copy_tests
from .test_repository_mutations import (
    run_repository_validation_phase_contract_tests,
    run_repository_root_boundary_tests,
    run_repository_initialized_tree_integrity_tests,
    run_repository_development_document_compatibility_tests,
    run_repository_manifest_completeness_tests,
    run_repository_schema_conformance_tests,
    run_repository_derived_artifact_tests,
    run_repository_dependency_lifecycle_tests,
    run_repository_reference_tests,
    run_repository_lineage_tests,
    run_repository_unique_item_property_tests,
    run_repository_platform_profile_boundary_tests,
    run_repository_path_helper_tests,
)
from .test_repository_fixture_metadata import run_repository_fixture_metadata_tests
from .test_mutation_support import run_mutation_support_tests
from .test_repository_projection_boundary import run_repository_projection_boundary_test
from .test_schema_mutations import run_schema_mutations
from .test_validation_entry_points import run_validation_entry_point_tests
from .test_validation_portable_split import run_validation_portable_split_tests


def run_repository_mutation_tests(repo_root: Path) -> None:
    check_validate_cli_contract(repo_root)
    check_generate_docs_cli_contract(repo_root)
    run_schema_mutations(repo_root)
    run_architecture_document_contract_tests(repo_root)
    run_functional_set_overview_contract_tests(repo_root)
    run_github_field_policy_tests(repo_root)
    run_issue_intake_governance_routing_tests(repo_root)
    run_issue_routing_hosted_conformance_tests(repo_root)
    run_repository_validation_phase_contract_tests(repo_root)
    run_repository_root_boundary_tests(repo_root)
    run_repository_initialized_tree_integrity_tests(repo_root)
    run_repository_development_document_compatibility_tests(repo_root)
    run_repository_manifest_completeness_tests(repo_root)
    run_repository_schema_conformance_tests(repo_root)
    run_repository_derived_artifact_tests(repo_root)
    run_repository_dependency_lifecycle_tests(repo_root)
    run_repository_reference_tests(repo_root)
    run_repository_lineage_tests(repo_root)
    run_repository_unique_item_property_tests(repo_root)
    run_repository_platform_profile_boundary_tests(repo_root)
    run_repository_path_helper_tests(repo_root)
    run_repository_fixture_metadata_tests(repo_root)
    run_mutation_support_tests(repo_root)
    run_repository_projection_boundary_test(repo_root)
    run_github_profile_generation_tests(repo_root)
    run_github_profile_mutation_tests(repo_root)
    run_generation_mutations(repo_root)
    run_reference_isolated_copy_tests(repo_root)
    run_validation_entry_point_tests(repo_root)
    run_validation_portable_split_tests(repo_root)
