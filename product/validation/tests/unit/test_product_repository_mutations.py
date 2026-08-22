from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from ..self.generation_support import check_generated_document_write_behavior
from validation.core.errors import fail
from validation.checks.development_documents import DevelopmentDocumentRecord, check_development_document_relationships
from validation.core.paths import resolve_repo_path
from validation.checks.domain import validate_product_phases

from ..self.mutation_support import add_lifecycle_spec, create_repo_fixture, declared_repo_fixture_paths, expect_failure, mutate_json


# validation-metadata: {"role": "helper"}
def run_product_development_document_tests(repo_root: Path) -> None:
    repository_validation_spec = json.loads(
        (repo_root / "repo/specs/repo/validation.json").read_text()
    )
    product_manifest = json.loads((repo_root / "product/specs/product/manifest.json").read_text())
    active_product_paths = list(declared_repo_fixture_paths(repo_root))
    active_product_paths.append("product/specs/product/manifest.json")
    for entry in product_manifest["product_specifications"]:
        active_product_paths.append(entry["path"])
        product_spec = json.loads((repo_root / entry["path"]).read_text())
        active_product_paths.extend(artifact["path"] for artifact in product_spec.get("derived_artifacts", []))
    active_product_paths = list(dict.fromkeys(active_product_paths))
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_path = temp_repo / "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md"
        chunk_path.write_text(chunk_path.read_text() + "\n<!--" + ("x" * 30000) + "-->")
        expect_failure("oversized overview chunk bytes", lambda: validate_product_phases(temp_repo, ('product development documents',)), "chunk exceeds byte limit")
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
        expect_failure("missing decomposition chunk role", lambda: validate_product_phases(temp_repo, ('product development documents',)), "missing required property role")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"]}', 1)
        decomposition_path.write_text(decomposition_text)
        expect_failure("missing decomposition area coverage", lambda: validate_product_phases(temp_repo, ('product development documents',)), "missing required property coverage")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_path = temp_repo / "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"
        chunk_text = chunk_path.read_text().replace("## Responsibilities\n\nSeparate reusable repository scaffolding from product-specific foundations and identify the governed materials that can be carried forward.\n\n", "")
        chunk_path.write_text(chunk_text)
        expect_failure("missing decomposition section heading", lambda: validate_product_phases(temp_repo, ('product development documents',)), "missing product-area heading Responsibilities")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "decomposition-basis", "document_coverage": ["decomposition_basis", "unresolved_decisions"]}', 1)
        decomposition_text = decomposition_text.replace('  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', 1)
        decomposition_path.write_text(decomposition_text)
        validate_product_phases(temp_repo, ('product development documents',))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "decomposition-basis", "document_coverage": ["decomposition_basis", "unresolved_decisions"]}', 1)
        decomposition_text = decomposition_text.replace('  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', '  "required_content_areas": {\n    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n', 1)
        decomposition_path.write_text(decomposition_text)
        validate_product_phases(temp_repo, ('product development documents',))
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
        expect_failure("decomposition without required content areas", lambda: validate_product_phases(temp_repo, ('product development documents',)), "missing required property decomposition_basis")
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
        expect_failure("product-area inventory mismatch", lambda: validate_product_phases(temp_repo, ('product development documents',)), "product-area inventory mismatch")
        whiteboard = DevelopmentDocumentRecord(
            "docs/overview/whiteboard.md",
            "docs/overview/",
            {},
            {
                "artifact_id": "whiteboard",
                "artifact_type": "overview-whiteboard",
                "product_id": "test-product",
                "lifecycle_status": "active",
                "controlling_documents": [],
                "predecessor_documents": [],
                "evidence": [],
            },
            [],
        )
        analysis = DevelopmentDocumentRecord(
            "docs/overview/analysis.md",
            "docs/overview/",
            {},
            {
                "artifact_id": "analysis",
                "artifact_type": "overview-analysis",
                "product_id": "test-product",
                "lifecycle_status": "candidate",
                "controlling_documents": [whiteboard.path],
                "predecessor_documents": [whiteboard.path],
                "evidence": [],
            },
            [],
        )
        functional_set = DevelopmentDocumentRecord(
            "docs/overview/functional-set.md",
            "docs/overview/",
            {},
            {
                "artifact_id": "functional-set",
                "artifact_type": "functional-set",
                "product_id": "test-product",
                "lifecycle_status": "approved",
                "controlling_documents": [analysis.path],
                "predecessor_documents": [analysis.path],
                "evidence": [],
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
                "product_id": "test-product",
                "lifecycle_status": "candidate",
                "controlling_documents": [functional_set.path],
                "predecessor_documents": [functional_set.path],
                "evidence": [],
            },
            [],
        )
        plan_a = DevelopmentDocumentRecord(
            "docs/plans/plan-a.md",
            "docs/plans/",
            {},
            {
                "artifact_id": "plan-a",
                "artifact_type": "implementation-plan",
                "product_id": "test-product",
                "lifecycle_status": "candidate",
                "controlling_documents": [functional_set.path, decomposition.path, "docs/plans/plan-b.md"],
                "predecessor_documents": [decomposition.path],
                "evidence": [],
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
                "product_id": "test-product",
                "lifecycle_status": "candidate",
                "controlling_documents": [functional_set.path, decomposition.path, "docs/plans/plan-a.md"],
                "predecessor_documents": [decomposition.path],
                "evidence": [],
            },
            [],
        )
        expect_failure(
            "controlling document cycle",
            lambda: check_development_document_relationships(
                Path("/tmp"),
                {
                    whiteboard.path: whiteboard,
                    analysis.path: analysis,
                    functional_set.path: functional_set,
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
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
        overview_path.write_text(overview_path.read_text().replace('  "artifact_id": "initializer-functional-set",\n', '  "artifact_id": "initializer.plan.bootstrap",\n'))
        validate_product_phases(temp_repo, ('product development documents',))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '  "controlling_documents": [\n    "repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md"\n  ],\n',
            '  "controlling_documents": [],\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_product_phases(temp_repo, ('product development documents',))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '    "repo/docs/overview/repository-functional-set/09-governance-and-evolution.md"\n  ],\n',
            '    "repo/docs/overview/repository-functional-set/09-governance-and-evolution.md",\n    "repo/docs/overview/README.md"\n  ],\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_product_phases(temp_repo, ('product development documents',))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_chunk_path = temp_repo / "product/docs/overview/initializer-functional-set/07-capabilities-addendum.md"
        overview_chunk_path.write_text("# Additional capabilities\n")
        overview_path = temp_repo / "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
        overview_text = overview_path.read_text()
        metadata_prefix, metadata_rest = overview_text.split("```json\n", 1)
        metadata_text, metadata_suffix = metadata_rest.split("\n```", 1)
        metadata = json.loads(metadata_text)
        addendum_path = "product/docs/overview/initializer-functional-set/07-capabilities-addendum.md"
        metadata["required_content_areas"]["capability_boundary"].append(addendum_path)
        metadata["subordinate_chunks"].append({
            "order": 7,
            "path": addendum_path,
            "title": "Capabilities addendum",
            "coverage": ["capability_boundary"],
        })
        overview_text = (
            metadata_prefix
            + "```json\n"
            + json.dumps(metadata, indent=2)
            + "\n```"
            + metadata_suffix
        )
        index_anchor = "- [Initializer Overview: Lifecycle and Handoff](initializer-functional-set/06-lifecycle-and-handoff.md)\n"
        if overview_text.count(index_anchor) != 1:
            raise AssertionError("functional-set chunk index anchor mismatch")
        overview_text = overview_text.replace(
            index_anchor,
            index_anchor + "- [Capabilities addendum](initializer-functional-set/07-capabilities-addendum.md)\n",
            1,
        )
        overview_path.write_text(overview_text)
        validate_product_phases(temp_repo, ('product development documents',))
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_index_path = temp_repo / "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
        chunk_index_path.write_text(chunk_index_path.read_text().replace("initializer-functional-set/04-capabilities-and-success.md", "initializer-functional-set/05-unresolved-questions.md", 1))
        expect_failure("wrong functional-set chunk link", lambda: validate_product_phases(temp_repo, ('product development documents',)), "chunk coverage mismatch")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        metadata_prefix, metadata_rest = decomposition_text.split("```json\n", 1)
        metadata_text, metadata_suffix = metadata_rest.split("\n```", 1)
        metadata = json.loads(metadata_text)
        expected_predecessor = "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
        if metadata.get("predecessor_documents") != [expected_predecessor]:
            raise AssertionError(
                f"unexpected decomposition predecessor set: {metadata.get('predecessor_documents')!r}"
            )
        metadata["predecessor_documents"] = ["docs/overview/MISSING-FUNCTIONAL-SET.md"]
        decomposition_text = (
            metadata_prefix
            + "```json\n"
            + json.dumps(metadata, indent=2)
            + "\n```"
            + metadata_suffix
        )
        decomposition_path.write_text(decomposition_text)
        expect_failure(
            "missing decomposition predecessor path",
            lambda: validate_product_phases(temp_repo, ('product development documents',)),
            "unresolved predecessor path",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace("product/docs/decompositions/INITIALIZER-DECOMPOSITION.md", "docs/decompositions/MISSING-DECOMPOSITION.md")
        plan_path.write_text(plan_text)
        expect_failure("plan without controlling decomposition", lambda: validate_product_phases(temp_repo, ('product development documents',)), "unresolved controlling document path")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        metadata_prefix, metadata_rest = plan_text.split("```json\n", 1)
        metadata_text, metadata_suffix = metadata_rest.split("\n```", 1)
        metadata = json.loads(metadata_text)
        existing_chunks = metadata["subordinate_chunks"]
        next_order = max(chunk["order"] for chunk in existing_chunks) + 1
        previous_last = existing_chunks[-1]
        plan_chunk_rel = (
            "product/docs/plans/initializer-implementation-plan/"
            f"{next_order:02d}-validation-addendum.md"
        )
        plan_chunk_path = temp_repo / plan_chunk_rel
        plan_chunk_path.write_text("# Validation addendum\n")
        metadata["required_content_areas"]["workstreams_and_dependencies"].append(
            plan_chunk_rel
        )
        metadata["subordinate_chunks"].append(
            {
                "order": next_order,
                "path": plan_chunk_rel,
                "title": "Validation addendum",
                "coverage": ["workstreams_and_dependencies"],
            }
        )
        plan_text = (
            metadata_prefix
            + "```json\n"
            + json.dumps(metadata, indent=2)
            + "\n```"
            + metadata_suffix
        )
        previous_rel = Path(previous_last["path"]).relative_to(
            "product/docs/plans"
        ).as_posix()
        index_anchor = f'- [{previous_last["title"]}](./{previous_rel})\n'
        if plan_text.count(index_anchor) != 1:
            raise AssertionError(
                f"implementation-plan chunk index anchor mismatch: {index_anchor!r}"
            )
        next_rel = Path(plan_chunk_rel).relative_to(
            "product/docs/plans"
        ).as_posix()
        plan_text = plan_text.replace(
            index_anchor,
            index_anchor + f"- [Validation addendum](./{next_rel})\n",
            1,
        )
        plan_path.write_text(plan_text)
        validate_product_phases(temp_repo, ('product development documents',))
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
        expect_failure("plan chunk without coverage", lambda: validate_product_phases(temp_repo, ('product development documents',)), "required coverage must be an array")
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_path.write_text(plan_path.read_text().replace('"id": "I1"', '"id": "B0"', 1))
        expect_failure(
            "duplicate plan workstream authority identifier",
            lambda: validate_product_phases(temp_repo, ('product development documents',)),
            "duplicate workstream authority identifier B0",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index, tuple(active_product_paths))
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_path.write_text(
            plan_path.read_text().replace(
                '"product.execution-profile",\n        "product.full-initialization",',
                '"product.execution-profile",\n        "product.platform-integrated-initialization",',
                1,
            )
        )
        expect_failure(
            "candidate plan workstream authority specification",
            lambda: validate_product_phases(
                temp_repo,
                ('product lifecycle authority sequence',),
            ),
            "non-accepted specification product.platform-integrated-initialization",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_path.write_text(plan_path.read_text().replace('"workstream_authority":', '"missing_workstream_authority":', 1))
        expect_failure(
            "accepted plan without canonical workstream authority",
            lambda: validate_product_phases(temp_repo, ('product development documents',)),
            "additionalProperties disallowed: missing_workstream_authority",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index, tuple(active_product_paths))
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        prefix, metadata_and_rest = plan_text.split("```json\n", 1)
        metadata_text, suffix = metadata_and_rest.split("\n```", 1)
        metadata = json.loads(metadata_text)
        for index, authority in enumerate(metadata["workstream_authority"]):
            authority["controlling_product_specifications"] = [f"product.audit-unknown-{index}"]
        plan_path.write_text(prefix + "```json\n" + json.dumps(metadata, indent=2) + "\n```" + suffix)
        expect_failure(
            "all-unknown plan workstream authority specifications",
            lambda: validate_product_phases(
                temp_repo,
                ('product lifecycle authority sequence',),
            ),
            "unknown specification product.audit-unknown-0",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index, tuple(active_product_paths))
        clone_index += 1
        plan_path = temp_repo / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        prefix, metadata_and_rest = plan_text.split("```json\n", 1)
        metadata_text, suffix = metadata_and_rest.split("\n```", 1)
        metadata = json.loads(metadata_text)
        metadata["workstream_authority"][0]["controlling_product_specifications"].append(
            "product.audit-unknown-mixed"
        )
        plan_path.write_text(prefix + "```json\n" + json.dumps(metadata, indent=2) + "\n```" + suffix)
        expect_failure(
            "mixed known and unknown plan workstream authority specifications",
            lambda: validate_product_phases(
                temp_repo,
                ('product lifecycle authority sequence',),
            ),
            "unknown specification product.audit-unknown-mixed",
        )
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index, tuple(active_product_paths))
        clone_index += 1
        validate_product_phases(
            temp_repo,
            (
                'product development documents',
                'product lifecycle authority sequence',
            ),
        )

    print("ok: product development document tests")

# validation-metadata: {"role": "helper"}
def run_product_root_tests(repo_root: Path) -> None:
    repository_validation_spec = json.loads(
        (repo_root / "repo/specs/repo/validation.json").read_text()
    )
    product_manifest = json.loads((repo_root / "product/specs/product/manifest.json").read_text())
    active_product_paths = list(declared_repo_fixture_paths(repo_root))
    active_product_paths.append("product/specs/product/manifest.json")
    for entry in product_manifest["product_specifications"]:
        active_product_paths.append(entry["path"])
        product_spec = json.loads((repo_root / entry["path"]).read_text())
        active_product_paths.extend(artifact["path"] for artifact in product_spec.get("derived_artifacts", []))
    active_product_paths = list(dict.fromkeys(active_product_paths))
    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0
        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        product_root = temp_repo / "product/specs/product"
        extra_spec = copy.deepcopy(repository_validation_spec)
        extra_spec["spec_id"] = "repo.product-root-rogue"
        (product_root / "rogue.json").parent.mkdir(parents=True, exist_ok=True)
        (product_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("product root contamination", lambda: validate_product_phases(temp_repo, ('product specification root',)), "product manifest completeness failed")
        for level_name in ["level-0", "level-1", "level-2", "level-3"]:
            temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
            clone_index += 1
            product_level_root = temp_repo / "product/specs/product" / level_name
            extra_spec = copy.deepcopy(repository_validation_spec)
            extra_spec["spec_id"] = f"repo.{level_name}.rogue"
            product_level_root.mkdir(parents=True, exist_ok=True)
            (product_level_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
            expect_failure(f"product root contamination in {level_name}", lambda: validate_product_phases(temp_repo, ('product specification root',)), "product manifest completeness failed")

    print("ok: product root tests")
