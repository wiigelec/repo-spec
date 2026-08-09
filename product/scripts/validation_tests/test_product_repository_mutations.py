from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from validation.generated_outputs import check_generated_document_write_behavior
from validation.errors import fail
from validation.repository_checks import DevelopmentDocumentRecord, check_development_document_relationships, resolve_repo_path
from product_validation.product_checks import validate_product

from validation.tests.mutation_support import add_lifecycle_spec, create_repo_fixture, expect_failure, mutate_json


def run_product_repository_mutations(repo_root: Path) -> None:
    repository_validation_spec = json.loads(
        (repo_root / "repo/specs/repo/validation.json").read_text()
    )
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_path = temp_repo / "product/docs/overview/initializer-overview/04-capabilities-and-success.md"
        chunk_path.write_text(chunk_path.read_text() + "\n<!--" + ("x" * 30000) + "-->")
        expect_failure("oversized overview chunk bytes", lambda: validate_product(temp_repo), "chunk exceeds byte limit")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_path.write_text(
            decomposition_path.read_text().replace(
                '{"order": 3, "path": "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "title": "Platform and execution", "role": "product-area", "area_id": "platform-and-execution", "document_coverage": ["product_area_inventory", "cross_cutting_concerns", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}',
                '{"order": 3, "path": "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "title": "Platform and execution", "document_coverage": ["cross_cutting_concerns", "unresolved_decisions"], "area_id": "platform-and-execution"}',
                1,
            )
        )
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', 1)
        expect_failure("missing decomposition chunk role", lambda: validate_product(temp_repo), "missing required property role")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"]}', 1)
        decomposition_path.write_text(decomposition_text)
        expect_failure("missing decomposition area coverage", lambda: validate_product(temp_repo), "missing required property coverage")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_path = temp_repo / "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"
        chunk_text = chunk_path.read_text().replace("## Responsibilities\n\nSeparate reusable repository scaffolding from product-specific foundations and identify the governed materials that can be carried forward.\n\n", "")
        chunk_path.write_text(chunk_text)
        expect_failure("missing decomposition section heading", lambda: validate_product(temp_repo), "missing product-area heading Responsibilities")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_path = temp_repo / "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"
        chunk_text = chunk_path.read_text().replace("## Responsibilities\n\nSeparate reusable repository scaffolding from product-specific foundations and identify the governed materials that can be carried forward.\n\n", "")
        chunk_path.write_text(chunk_text)
        expect_failure("missing decomposition section heading", lambda: validate_product(temp_repo), "missing product-area heading Responsibilities")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "decomposition-basis", "document_coverage": ["decomposition_basis", "unresolved_decisions"]}', 1)
        decomposition_text = decomposition_text.replace('  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', 1)
        decomposition_path.write_text(decomposition_text)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "decomposition-basis", "document_coverage": ["decomposition_basis", "unresolved_decisions"]}', 1)
        decomposition_text = decomposition_text.replace('  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', 1)
        decomposition_path.write_text(decomposition_text)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace(
            '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n',
            '  "required_content_areas": {},\n',
            1,
        )
        decomposition_path.write_text(decomposition_text)
        expect_failure("decomposition without required content areas", lambda: validate_product(temp_repo), "missing required property decomposition_basis")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace(
            '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n',
            '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n',
            1,
        )
        decomposition_path.write_text(decomposition_text)
        expect_failure("product-area inventory mismatch", lambda: validate_product(temp_repo), "product-area inventory mismatch")

        plan_a = DevelopmentDocumentRecord(
            "docs/plans/plan-a.md",
            "docs/plans/",
            {},
            {
                "artifact_id": "plan-a",
                "artifact_type": "implementation-plan",
                "document_slug": "plan-a",
                "filename_stem": "plan-a",
                "root_path": "docs/plans/",
                "title": "Plan A",
                "product_id": "test-product",
                "authority_category": "planning",
                "lifecycle_status": "candidate",
                "governing_issue": "#1",
                "controlling_documents": ["docs/overview/overview.md", "docs/decompositions/decomposition.md", "docs/plans/plan-b.md"],
                "predecessor_documents": [],
                "evidence": ["docs/overview/overview.md"],
                "required_content_areas": {"authority_and_basis": ["docs/plans/plan-a/01.md"], "scope_and_exclusions": ["docs/plans/plan-a/01.md"], "workstreams_and_dependencies": ["docs/plans/plan-a/02.md"], "entry_and_exit_conditions": ["docs/plans/plan-a/03.md"], "transition_gates": ["docs/plans/plan-a/03.md"], "validation_strategy": ["docs/plans/plan-a/03.md"], "risks_and_unresolved_decisions": ["docs/plans/plan-a/02.md", "docs/plans/plan-a/03.md"], "completion_and_successor_work": ["docs/plans/plan-a/03.md"]},
                "subordinate_chunks": [],
                "successor_action": "next",
                "schema_version": "1",
            },
            [],
        )
        plan_b = DevelopmentDocumentRecord(
            "docs/plans/plan-b.md",
            "docs/plans/",
            {},
            {
                "artifact_id": "plan-b",
                "artifact_type": "implementation-plan",
                "document_slug": "plan-b",
                "filename_stem": "plan-b",
                "root_path": "docs/plans/",
                "title": "Plan B",
                "product_id": "test-product",
                "authority_category": "planning",
                "lifecycle_status": "candidate",
                "governing_issue": "#1",
                "controlling_documents": ["docs/overview/overview.md", "docs/decompositions/decomposition.md", "docs/plans/plan-a.md"],
                "predecessor_documents": [],
                "evidence": ["docs/overview/overview.md"],
                "required_content_areas": {"authority_and_basis": ["docs/plans/plan-b/01.md"], "scope_and_exclusions": ["docs/plans/plan-b/01.md"], "workstreams_and_dependencies": ["docs/plans/plan-b/02.md"], "entry_and_exit_conditions": ["docs/plans/plan-b/03.md"], "transition_gates": ["docs/plans/plan-b/03.md"], "validation_strategy": ["docs/plans/plan-b/03.md"], "risks_and_unresolved_decisions": ["docs/plans/plan-b/02.md", "docs/plans/plan-b/03.md"], "completion_and_successor_work": ["docs/plans/plan-b/03.md"]},
                "subordinate_chunks": [],
                "successor_action": "next",
                "schema_version": "1",
            },
            [],
        )
        overview = DevelopmentDocumentRecord(
            "docs/overview/overview.md",
            "docs/overview/",
            {},
            {
                "artifact_id": "overview",
                "artifact_type": "product-overview",
                "document_slug": "overview",
                "filename_stem": "overview",
                "root_path": "docs/overview/",
                "title": "Overview",
                "product_id": "test-product",
                "authority_category": "directional",
                "lifecycle_status": "accepted",
                "overview_role": "initial",
                "governing_issue": "#1",
                "controlling_documents": [],
                "predecessor_documents": [],
                "evidence": ["docs/overview/overview.md"],
                "required_content_areas": {"product_identity": ["docs/overview/overview/01.md"], "problem_and_outcome": ["docs/overview/overview/01.md"], "intended_users_and_stakeholders": ["docs/overview/overview/01.md"], "scope_and_non_goals": ["docs/overview/overview/01.md"], "product_boundaries": ["docs/overview/overview/01.md"], "durable_principles": ["docs/overview/overview/01.md"], "capabilities_and_success": ["docs/overview/overview/01.md"], "unresolved_questions": ["docs/overview/overview/01.md"], "readiness_for_decomposition": ["docs/overview/overview/01.md"]},
                "subordinate_chunks": [],
                "successor_action": "next",
                "schema_version": "1",
            },
            [],
        )
        decomposition = DevelopmentDocumentRecord(
            "docs/decompositions/decomposition.md",
            "docs/decompositions/",
            {},
            {
                "artifact_id": "decomposition",
                "artifact_type": "product-decomposition",
                "document_slug": "decomposition",
                "filename_stem": "decomposition",
                "root_path": "docs/decompositions/",
                "title": "Decomposition",
                "product_id": "test-product",
                "authority_category": "directional",
                "lifecycle_status": "accepted",
                "governing_issue": "#1",
                "controlling_documents": ["docs/overview/overview.md"],
                "predecessor_documents": ["docs/overview/overview.md"],
                "evidence": ["docs/overview/overview.md"],
                "required_content_areas": {"decomposition_basis": ["docs/decompositions/decomposition/01.md"], "product_area_inventory": ["docs/decompositions/decomposition/01.md"], "dependency_model": ["docs/decompositions/decomposition/01.md"], "cross_cutting_concerns": ["docs/decompositions/decomposition/01.md"], "unresolved_decisions": ["docs/decompositions/decomposition/01.md"], "stopping_criteria": ["docs/decompositions/decomposition/01.md"], "planning_handoff": ["docs/decompositions/decomposition/01.md"]},
                "subordinate_chunks": [],
                "successor_action": "next",
                "schema_version": "1",
            },
            [],
        )
        expect_failure(
            "controlling document cycle",
            lambda: check_development_document_relationships(
                Path("/tmp"),
                {
                    overview.path: overview,
                    decomposition.path: decomposition,
                    plan_a.path: plan_a,
                    plan_b.path: plan_b,
                },
                {},
                {},
            ),
            "cycle detected",
        )

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_path.write_text(overview_path.read_text().replace('  "artifact_id": "initializer-overview",\n', '  "artifact_id": "initializer.plan.bootstrap",\n'))
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '  "controlling_documents": [\n    "repo/docs/overview/PRODUCT-OVERVIEW.md"\n  ],\n',
            '  "controlling_documents": [],\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '    "repo/docs/overview/product-overview/06-governance-and-evolution.md"\n  ],\n',
            '    "repo/docs/overview/product-overview/06-governance-and-evolution.md",\n    "repo/docs/overview/README.md"\n  ],\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace('  "overview_role": "initial",\n', '', 1)
        overview_path.write_text(overview_text)
        expect_failure("overview without overview role", lambda: validate_product(temp_repo), "overview_role")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace('{"order": 1, "path": "product/docs/overview/initializer-overview/01-product-identity-and-purpose.md", "title": "Product identity and purpose", "coverage": ["product_identity"]}', '{"order": 1, "path": "product/docs/overview/initializer-overview/01-product-identity-and-purpose.md", "title": "Product identity and purpose"}', 1)
        overview_path.write_text(overview_text)
        expect_failure("overview chunk without coverage", lambda: validate_product(temp_repo), "required coverage must be an array")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace('  "overview_role": "initial",\n', '  "overview_role": "revision",\n', 1)
        overview_path.write_text(overview_text)
        expect_failure("revision overview without predecessor", lambda: validate_product(temp_repo), "minItems violation")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_chunk_path = temp_repo / "product/docs/overview/initializer-overview/07-capabilities-addendum.md"
        overview_chunk_path.write_text("# Additional capabilities\n")
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '    "capabilities_and_success": ["product/docs/overview/initializer-overview/04-capabilities-and-success.md"],\n',
            '    "capabilities_and_success": ["product/docs/overview/initializer-overview/04-capabilities-and-success.md", "product/docs/overview/initializer-overview/07-capabilities-addendum.md"],\n',
            1,
        )
        overview_text = overview_text.replace(
            '    {"order": 6, "path": "product/docs/overview/initializer-overview/06-lifecycle-and-handoff.md", "title": "Lifecycle and handoff", "coverage": ["readiness_for_decomposition"]}\n  ],\n',
            '    {"order": 6, "path": "product/docs/overview/initializer-overview/06-lifecycle-and-handoff.md", "title": "Lifecycle and handoff", "coverage": ["readiness_for_decomposition"]},\n    {"order": 7, "path": "product/docs/overview/initializer-overview/07-capabilities-addendum.md", "title": "Capabilities addendum", "coverage": ["capabilities_and_success"]}\n  ],\n',
            1,
        )
        overview_text = overview_text.replace(
            '- [06 - Lifecycle and handoff](./initializer-overview/06-lifecycle-and-handoff.md)\n',
            '- [06 - Lifecycle and handoff](./initializer-overview/06-lifecycle-and-handoff.md)\n- [07 - Capabilities addendum](./initializer-overview/07-capabilities-addendum.md)\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_index_path = temp_repo / "product/docs/overview/INITIALIZER-OVERVIEW.md"
        chunk_index_path.write_text(chunk_index_path.read_text().replace("./initializer-overview/04-capabilities-and-success.md", "./initializer-overview/05-unresolved-questions.md", 1))
        expect_failure("wrong overview chunk link", lambda: validate_product(temp_repo), "chunk index link mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_path.write_text(decomposition_path.read_text().replace("repo/docs/overview/PRODUCT-OVERVIEW.md", "docs/overview/MISSING-OVERVIEW.md", 1))
        expect_failure("missing decomposition predecessor path", lambda: validate_product(temp_repo), "missing evidence path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace("product/docs/decompositions/INITIALIZER-DECOMPOSITION.md", "docs/decompositions/MISSING-DECOMPOSITION.md")
        plan_path.write_text(plan_text)
        expect_failure("plan without controlling decomposition", lambda: validate_product(temp_repo), "unresolved controlling document path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_chunk_path = temp_repo / "product/docs/plans/initializer-implementation-plan/05-validation-addendum.md"
        plan_chunk_path.write_text("# Validation addendum\n")
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace(
            '    "workstreams_and_dependencies": [\n      "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md"\n    ],',
            '    "workstreams_and_dependencies": [\n      "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md",\n      "product/docs/plans/initializer-implementation-plan/05-validation-addendum.md"\n    ],',
            1,
        )
        plan_text = plan_text.replace(
            '      ]\n    }\n  ],\n',
            '      ]\n    },\n    {\n      "order": 5,\n      "path": "product/docs/plans/initializer-implementation-plan/05-validation-addendum.md",\n      "title": "Validation addendum",\n      "coverage": [\n        "workstreams_and_dependencies"\n      ]\n    }\n  ],\n',
            1,
        )
        plan_text = plan_text.replace(
            '- [Risks and unresolved decisions](./initializer-implementation-plan/04-risks-and-unresolved-decisions.md)',
            '- [Risks and unresolved decisions](./initializer-implementation-plan/04-risks-and-unresolved-decisions.md)\n- [Validation addendum](./initializer-implementation-plan/05-validation-addendum.md)',
            1,
        )
        plan_path.write_text(plan_text)
        validate_product(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace(
            '      "order": 1,\n      "path": "product/docs/plans/initializer-implementation-plan/01-authority-scope-and-specification-map.md",\n      "title": "Authority, scope, and specification map",\n      "coverage": [\n        "authority_and_basis",\n        "scope_and_exclusions"\n      ]',
            '      "order": 1,\n      "path": "product/docs/plans/initializer-implementation-plan/01-authority-scope-and-specification-map.md",\n      "title": "Authority, scope, and specification map"',
            1,
        )
        plan_path.write_text(plan_text)
        expect_failure("plan chunk without coverage", lambda: validate_product(temp_repo), "required coverage must be an array")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        product_root = temp_repo / "product/specs/product"
        extra_spec = copy.deepcopy(repository_validation_spec)
        extra_spec["spec_id"] = "repo.product-root-rogue"
        (product_root / "rogue.json").parent.mkdir(parents=True, exist_ok=True)
        (product_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("product root contamination", lambda: validate_product(temp_repo), "undeclared JSON content under product/specs/product/")

        for level_name in ["level-0", "level-1", "level-2", "level-3"]:
            temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
            clone_index += 1
            product_level_root = temp_repo / "product/specs/product" / level_name
            extra_spec = copy.deepcopy(repository_validation_spec)
            extra_spec["spec_id"] = f"repo.{level_name}.rogue"
            product_level_root.mkdir(parents=True, exist_ok=True)
            (product_level_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
            expect_failure(f"product root contamination in {level_name}", lambda: validate_product(temp_repo), "undeclared JSON content under product/specs/product/")


    print("ok: product document/root mutation tests")
