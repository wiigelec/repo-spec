"""Mutation-oriented validation-framework self-test extension point."""

from __future__ import annotations

from pathlib import Path

from validation.checks.cli_contracts import (
    check_generate_docs_cli_contract,
    check_validate_cli_contract,
)

from ..unit.test_architecture_document_contract import run_architecture_document_contract_tests
from ..unit.test_functional_set_overview_contract import run_functional_set_overview_contract_tests
from ..unit.test_generation_mutations import run_generation_mutations
from ..unit.test_issue_intake_governance_routing import run_issue_intake_governance_routing_tests
from ..unit.test_issue_routing_hosted_conformance import run_issue_routing_hosted_conformance_tests
from ..unit.test_repository_mutations import (
    run_repository_validation_phase_contract_tests,
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
from ..unit.test_repository_fixture_metadata import run_repository_fixture_metadata_tests
from ..unit.test_repository_projection_boundary import run_repository_projection_boundary_test
from ..unit.test_repo_validation_boundary import run_repo_validation_boundary_tests
from ..unit.test_schema_mutations import run_schema_mutations
from ..unit.test_validation_entry_points import run_validation_entry_point_tests
from ..unit.test_validation_portable_split import run_validation_portable_split_tests


def run_repository_mutation_tests(repo_root: Path) -> None:
    check_validate_cli_contract(repo_root)
    check_generate_docs_cli_contract(repo_root)
    run_repo_validation_boundary_tests(repo_root)
    run_schema_mutations(repo_root)
    run_architecture_document_contract_tests(repo_root)
    run_functional_set_overview_contract_tests(repo_root)
    run_issue_intake_governance_routing_tests(repo_root)
    run_issue_routing_hosted_conformance_tests(repo_root)
    run_repository_validation_phase_contract_tests(repo_root)
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
    run_repository_projection_boundary_test(repo_root)
    run_generation_mutations(repo_root)
    run_validation_entry_point_tests(repo_root)
    run_validation_portable_split_tests(repo_root)
