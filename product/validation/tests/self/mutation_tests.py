"""Mutation-oriented validation-framework self-test extension point."""

from __future__ import annotations

import sys
from pathlib import Path

from .cli_contracts import check_product_validate_cli_contract

from ..unit.test_product_acyclicity import run_product_acyclicity_tests
from ..unit.test_product_dependency_directions import (
    run_product_dependency_direction_tests,
)
from ..unit.test_product_generation import run_product_generation_tests
from ..unit.test_product_generation_mutations import run_product_generation_mutation_tests
from ..unit.test_product_level_schemas import run_product_level_schema_tests
from ..unit.test_product_manifest_schema import run_product_manifest_schema_tests
from ..unit.test_product_repository_mutations import (
    run_product_development_document_tests,
    run_product_root_tests,
)
from ..unit.test_product_projection_freshness import (
    run_product_projection_freshness_tests,
)
from ..unit.test_product_projection_rendering import run_product_projection_rendering_tests
from ..unit.test_product_validation import (
    run_product_correspondence_tests,
    run_product_dependency_policy_tests,
    run_product_lineage_tests,
    run_product_manifest_completeness_tests,
    run_product_manifest_correspondence_tests,
    run_product_manifest_uniqueness_tests,
    run_product_reference_tests,
    run_product_schema_boundary_tests,
)
from ..unit.test_product_validation_ownership import (
    run_product_validation_ownership_tests,
)


# validation-metadata: {"role": "helper"}
def run_product_mutation_tests(repo_root: Path) -> None:
    check_product_validate_cli_contract(repo_root)
    run_product_validation_ownership_tests(repo_root)
    run_product_dependency_direction_tests(repo_root)
    run_product_acyclicity_tests(repo_root)
    run_product_level_schema_tests(repo_root)
    run_product_dependency_policy_tests(repo_root)
    run_product_schema_boundary_tests(repo_root)
    run_product_manifest_completeness_tests(repo_root)
    run_product_manifest_uniqueness_tests(repo_root)
    run_product_manifest_correspondence_tests(repo_root)
    run_product_reference_tests(repo_root)
    run_product_lineage_tests(repo_root)
    run_product_correspondence_tests(repo_root)
    run_product_manifest_schema_tests(repo_root)
    run_product_generation_tests(repo_root)
    run_product_generation_mutation_tests(repo_root)
    run_product_projection_freshness_tests(repo_root)
    run_product_projection_rendering_tests(repo_root)
    run_product_development_document_tests(repo_root)
    run_product_root_tests(repo_root)
