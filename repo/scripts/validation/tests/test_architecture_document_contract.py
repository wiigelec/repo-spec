from __future__ import annotations

from pathlib import Path

from validation.repository_checks import DevelopmentDocumentRecord, check_development_document_relationships
from .mutation_support import expect_failure

OVERVIEW_PATH = "repo/docs/overview/TEST-OVERVIEW.md"
DECOMPOSITION_PATH = "repo/docs/decompositions/TEST-DECOMPOSITION.md"
ARCHITECTURE_PATH = "repo/docs/architecture/TEST-ARCHITECTURE.md"
PLAN_PATH = "repo/docs/plans/TEST-IMPLEMENTATION-PLAN.md"


def _record(path: str, artifact_type: str, controlling_documents: list[str]) -> DevelopmentDocumentRecord:
    metadata = {
        "artifact_id": path.lower().replace("/", ".").replace("-", ".").removesuffix(".md"),
        "artifact_type": artifact_type,
        "product_id": "repo-spec",
        "lifecycle_status": "candidate",
        "controlling_documents": controlling_documents,
        "predecessor_documents": [],
        "evidence": ["README.md"],
    }
    if artifact_type == "product-overview":
        metadata["overview_role"] = "initial"
    return DevelopmentDocumentRecord(
        path=path,
        root_rel=Path(path).parent.as_posix() + "/",
        info={},
        metadata=metadata,
        chunk_paths=[],
    )


def run_architecture_document_contract_tests(repo_root: Path) -> None:
    overview = _record(OVERVIEW_PATH, "product-overview", [])
    architecture = _record(ARCHITECTURE_PATH, "architecture-plan", [OVERVIEW_PATH])
    check_development_document_relationships(
        repo_root,
        {OVERVIEW_PATH: overview, ARCHITECTURE_PATH: architecture},
        {},
        {},
    )

    decomposition = _record(DECOMPOSITION_PATH, "product-decomposition", [OVERVIEW_PATH])
    plan = _record(PLAN_PATH, "implementation-plan", [OVERVIEW_PATH])
    expect_failure(
        "implementation plan still requires controlling decomposition",
        lambda: check_development_document_relationships(
            repo_root,
            {OVERVIEW_PATH: overview, DECOMPOSITION_PATH: decomposition, PLAN_PATH: plan},
            {},
            {},
        ),
        "missing controlling decomposition",
    )

    architecture_without_overview = _record(ARCHITECTURE_PATH, "architecture-plan", [])
    expect_failure(
        "architecture plan requires controlling overview",
        lambda: check_development_document_relationships(
            repo_root,
            {OVERVIEW_PATH: overview, ARCHITECTURE_PATH: architecture_without_overview},
            {},
            {},
        ),
        "missing controlling overview",
    )
