from __future__ import annotations

from pathlib import Path

from validation.checks.development_documents import DevelopmentDocumentRecord, check_development_document_relationships
from ..self.mutation_support import expect_failure

WHITEBOARD = "repo/docs/overview/TEST-WHITEBOARD.md"
ANALYSIS = "repo/docs/overview/TEST-ANALYSIS.md"
FUNCTIONAL_SET = "repo/docs/overview/TEST-FUNCTIONAL-SET.md"
DECOMPOSITION = "repo/docs/decompositions/TEST-DECOMPOSITION.md"


# validation-metadata: {"role": "helper"}
def _record(path: str, artifact_type: str, status: str, controlling: list[str]) -> DevelopmentDocumentRecord:
    metadata = {
        "artifact_id": path.lower().replace("/", ".").replace("-", ".").removesuffix(".md"),
        "artifact_type": artifact_type,
        "product_id": "repo-spec",
        "lifecycle_status": status,
        "controlling_documents": controlling,
        "predecessor_documents": [],
        "evidence": ["README.md"],
    }
    return DevelopmentDocumentRecord(
        path=path,
        root_rel=Path(path).parent.as_posix() + "/",
        info={},
        metadata=metadata,
        chunk_paths=[],
    )


# validation-metadata: {"role": "helper"}
def run_functional_set_overview_contract_tests(repo_root: Path) -> None:
    whiteboard = _record(WHITEBOARD, "overview-whiteboard", "active", [])
    analysis = _record(ANALYSIS, "overview-analysis", "candidate", [WHITEBOARD])
    candidate_fs = _record(FUNCTIONAL_SET, "functional-set", "candidate", [ANALYSIS])
    approved_fs = _record(FUNCTIONAL_SET, "functional-set", "approved", [ANALYSIS])
    decomposition = _record(DECOMPOSITION, "product-decomposition", "candidate", [FUNCTIONAL_SET])

    check_development_document_relationships(
        repo_root,
        {WHITEBOARD: whiteboard, ANALYSIS: analysis, FUNCTIONAL_SET: approved_fs, DECOMPOSITION: decomposition},
        {},
        {},
    )

    expect_failure(
        "candidate functional set cannot govern decomposition",
        lambda: check_development_document_relationships(
            repo_root,
            {WHITEBOARD: whiteboard, ANALYSIS: analysis, FUNCTIONAL_SET: candidate_fs, DECOMPOSITION: decomposition},
            {},
            {},
        ),
        "candidate functional set cannot govern decomposition",
    )

    analysis_without_whiteboard = _record(ANALYSIS, "overview-analysis", "candidate", [])
    expect_failure(
        "analysis requires whiteboard predecessor",
        lambda: check_development_document_relationships(
            repo_root,
            {WHITEBOARD: whiteboard, ANALYSIS: analysis_without_whiteboard},
            {},
            {},
        ),
        "analysis missing whiteboard evidence predecessor",
    )

    fs_without_analysis = _record(FUNCTIONAL_SET, "functional-set", "candidate", [WHITEBOARD])
    expect_failure(
        "functional set requires analysis predecessor",
        lambda: check_development_document_relationships(
            repo_root,
            {WHITEBOARD: whiteboard, FUNCTIONAL_SET: fs_without_analysis},
            {},
            {},
        ),
        "functional set missing analysis predecessor",
    )
