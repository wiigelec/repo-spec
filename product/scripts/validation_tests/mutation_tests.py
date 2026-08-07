from __future__ import annotations

import sys
from pathlib import Path

from validation.cli_contracts import check_product_validate_cli_contract

from .test_product_acyclicity import run_product_acyclicity_tests
from .test_product_dependency_directions import (
    run_product_dependency_direction_tests,
)
from .test_product_generation import run_product_generation_tests
from .test_product_generation_mutations import run_product_generation_mutation_tests
from .test_product_level_schemas import run_product_level_schema_tests
from .test_product_manifest_schema import run_product_manifest_schema_tests
from .test_product_repository_mutations import run_product_repository_mutations
from .test_product_projection_freshness import (
    run_product_projection_freshness_tests,
)
from .test_product_projection_rendering import run_product_projection_rendering_tests
from .test_product_validation import run_product_validation_tests


def run_product_mutation_tests(repo_root: Path) -> None:
    check_product_validate_cli_contract(repo_root)
    run_product_dependency_direction_tests(repo_root)
    run_product_acyclicity_tests(repo_root)
    run_product_level_schema_tests(repo_root)
    run_product_validation_tests(repo_root)
    run_product_manifest_schema_tests(repo_root)
    run_product_generation_tests(repo_root)
    run_product_generation_mutation_tests(repo_root)
    run_product_projection_freshness_tests(repo_root)
    run_product_projection_rendering_tests(repo_root)
    run_product_repository_mutations(repo_root)

    sys.path.insert(0, str(repo_root / "product/scripts"))
    from initializer.tests.run_tests import run_initializer_tests

    run_initializer_tests(repo_root)
