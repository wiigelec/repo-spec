from __future__ import annotations

from pathlib import Path

from validation.checks.development_documents import DevelopmentDocumentRecord, check_development_document_relationships
from ..self.mutation_support import expect_failure

WHITEBOARD_PATH = "repo/docs/overview/TEST-WHITEBOARD.md"
ANALYSIS_PATH = "repo/docs/overview/TEST-ANALYSIS.md"
FUNCTIONAL_SET_PATH = "repo/docs/overview/TEST-FUNCTIONAL-SET.md"
DECOMPOSITION_PATH = "repo/docs/decompositions/TEST-DECOMPOSITION.md"
ARCHITECTURE_PATH = "repo/docs/architecture/TEST-ARCHITECTURE.md"
PLAN_PATH = "repo/docs/plans/TEST-IMPLEMENTATION-PLAN.md"


# validation-metadata: {"role": "helper"}
def _record(
    path: str,
    artifact_type: str,
    controlling_documents: list[str],
    predecessor_documents: list[str] | None = None,
    *,
    lifecycle_status: str = "candidate",
) -> DevelopmentDocumentRecord:
    return DevelopmentDocumentRecord(
        path=path,
        root_rel=Path(path).parent.as_posix() + "/",
        info={},
        metadata={
            "artifact_id": path.lower().replace("/", ".").replace("-", ".").removesuffix(".md"),
            "artifact_type": artifact_type,
            "product_id": "repo-spec",
            "lifecycle_status": lifecycle_status,
            "controlling_documents": controlling_documents,
            "predecessor_documents": predecessor_documents or [],
            "evidence": ["README.md"],
        },
        chunk_paths=[],
    )


# validation-metadata: {"role": "helper"}
def run_architecture_document_contract_tests(repo_root: Path) -> None:
    architecture = _record(ARCHITECTURE_PATH, "architecture-plan", [])
    expect_failure(
        "retired architecture-plan relationship type",
        lambda: check_development_document_relationships(
            repo_root,
            {ARCHITECTURE_PATH: architecture},
            {},
            {},
        ),
        "unsupported artifact type architecture-plan",
    )

    whiteboard = _record(
        WHITEBOARD_PATH,
        "overview-whiteboard",
        [],
        [],
        lifecycle_status="active",
    )
    analysis = _record(
        ANALYSIS_PATH,
        "overview-analysis",
        [WHITEBOARD_PATH],
        [WHITEBOARD_PATH],
    )
    functional_set = _record(
        FUNCTIONAL_SET_PATH,
        "functional-set",
        [ANALYSIS_PATH],
        [ANALYSIS_PATH],
        lifecycle_status="approved",
    )
    decomposition = _record(
        DECOMPOSITION_PATH,
        "product-decomposition",
        [FUNCTIONAL_SET_PATH],
        [FUNCTIONAL_SET_PATH],
    )
    plan = _record(
        PLAN_PATH,
        "implementation-plan",
        [FUNCTIONAL_SET_PATH],
        [],
    )
    expect_failure(
        "implementation plan still requires decomposition",
        lambda: check_development_document_relationships(
            repo_root,
            {
                WHITEBOARD_PATH: whiteboard,
                ANALYSIS_PATH: analysis,
                FUNCTIONAL_SET_PATH: functional_set,
                DECOMPOSITION_PATH: decomposition,
                PLAN_PATH: plan,
            },
            {},
            {},
        ),
        "missing controlling decomposition",
    )
