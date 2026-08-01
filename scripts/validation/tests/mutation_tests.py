from __future__ import annotations

from pathlib import Path

from .test_generation_mutations import run_generation_mutations
from .test_repository_mutations import run_repository_mutations
from .test_schema_mutations import run_schema_mutations


def run_mutation_tests(repo_root: Path) -> None:
    run_schema_mutations(repo_root)
    run_repository_mutations(repo_root)
    run_generation_mutations(repo_root)
