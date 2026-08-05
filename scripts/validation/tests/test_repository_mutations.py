from __future__ import annotations

import copy
import json
import tempfile
from pathlib import Path

from repo_model import load_specs
from validation.repository_checks import DevelopmentDocumentRecord
from validation.generated_outputs import check_generated_document_write_behavior
from validation.errors import fail
from validation.repository_checks import VALIDATION_PHASES, check_development_document_relationships, resolve_repo_path, validate_repo

from .mutation_support import add_lifecycle_spec, create_repo_fixture, expect_failure, mutate_json


def run_repository_mutations(repo_root: Path) -> None:
    _manifest, specs, _, _ = load_specs(repo_root)
    labels = [label for label, _check in VALIDATION_PHASES]
    expected_labels = [
        "repository JSON Schema conformance",
        "manifest completeness",
        "unique specification IDs",
        "unique item properties",
        "platform profile boundary",
        "GitHub profile freshness",
        "unique derived artifact paths",
        "product specification root",
        "product correspondence inventory",
        "product conformance completeness",
        "dependency target lifecycle",
        "product dependency directions",
        "product completeness",
        "resolvable references",
        "lineage relations",
        "product acyclic dependencies",
        "acyclic dependencies",
        "development documents",
        "generated-document freshness",
    ]
    if labels != expected_labels:
        fail(f"validation phase order changed: {labels}")

    with tempfile.TemporaryDirectory(prefix="repo-spec-validation-") as temp_root_name:
        temp_root = Path(temp_root_name)
        clone_index = 0

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "docs/development-document-compatibility.json",
            lambda registry: registry["entries"].__delitem__(0) or registry,
        )
        expect_failure("legacy development document without registry entry", lambda: validate_repo(temp_repo), "compatibility registry mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_path = temp_repo / "docs/overview/initializer-overview/04-capabilities-and-success.md"
        chunk_path.write_text(chunk_path.read_text() + "\n<!--" + ("x" * 30000) + "-->")
        expect_failure("oversized overview chunk bytes", lambda: validate_repo(temp_repo), "chunk exceeds byte limit")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_path.write_text(
            decomposition_path.read_text().replace(
                '{"order": 3, "path": "docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "title": "Platform and execution", "role": "product-area", "area_id": "platform-and-execution", "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}',
                '{"order": 3, "path": "docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "title": "Platform and execution", "area_id": "platform-and-execution"}',
                1,
            )
        )
        expect_failure("missing decomposition chunk role", lambda: validate_repo(temp_repo), "missing required property role")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority"}', 1)
        decomposition_path.write_text(decomposition_text)
        expect_failure("missing decomposition area coverage", lambda: validate_repo(temp_repo), "missing required property coverage")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "decomposition-basis"}', 1)
        decomposition_path.write_text(decomposition_text)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace('{"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}', '{"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "decomposition-basis", "area_id": "invocation-and-authority"}', 1)
        decomposition_path.write_text(decomposition_text)
        expect_failure("non-area decomposition chunk with area_id", lambda: validate_repo(temp_repo), "non-area chunk must not declare area_id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_text = decomposition_path.read_text()
        decomposition_text = decomposition_text.replace(
            '  "required_content_areas": {\n    "decomposition_basis": ["docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],\n    "product_area_inventory": ["docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "dependency_model": ["docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],\n    "cross_cutting_concerns": ["docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],\n    "unresolved_decisions": ["docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "stopping_criteria": ["docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],\n    "planning_handoff": ["docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]\n  },\n',
            '  "required_content_areas": {},\n',
            1,
        )
        decomposition_path.write_text(decomposition_text)
        expect_failure("decomposition without required content areas", lambda: validate_repo(temp_repo), "missing required property decomposition_basis")

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
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_path.write_text(overview_path.read_text().replace('  "artifact_id": "initializer-overview",\n', '  "artifact_id": "initializer.plan.bootstrap",\n'))
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '  "controlling_documents": [\n    "docs/overview/PRODUCT-OVERVIEW.md"\n  ],\n',
            '  "controlling_documents": [],\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '    "docs/overview/product-overview/06-governance-and-evolution.md"\n  ],\n',
            '    "docs/overview/product-overview/06-governance-and-evolution.md",\n    "docs/overview/README.md"\n  ],\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace('  "overview_role": "initial",\n', '', 1)
        overview_path.write_text(overview_text)
        expect_failure("overview without overview role", lambda: validate_repo(temp_repo), "overview_role")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace('{"order": 1, "path": "docs/overview/initializer-overview/01-product-identity-and-purpose.md", "title": "Product identity and purpose", "coverage": ["product_identity"]}', '{"order": 1, "path": "docs/overview/initializer-overview/01-product-identity-and-purpose.md", "title": "Product identity and purpose"}', 1)
        overview_path.write_text(overview_text)
        expect_failure("overview chunk without coverage", lambda: validate_repo(temp_repo), "required coverage must be an array")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace('  "overview_role": "initial",\n', '  "overview_role": "revision",\n', 1)
        overview_path.write_text(overview_text)
        expect_failure("revision overview without predecessor", lambda: validate_repo(temp_repo), "minItems violation")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        overview_chunk_path = temp_repo / "docs/overview/initializer-overview/07-capabilities-addendum.md"
        overview_chunk_path.write_text("# Additional capabilities\n")
        overview_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        overview_text = overview_path.read_text()
        overview_text = overview_text.replace(
            '    "capabilities_and_success": ["docs/overview/initializer-overview/04-capabilities-and-success.md"],\n',
            '    "capabilities_and_success": ["docs/overview/initializer-overview/04-capabilities-and-success.md", "docs/overview/initializer-overview/07-capabilities-addendum.md"],\n',
            1,
        )
        overview_text = overview_text.replace(
            '    {"order": 6, "path": "docs/overview/initializer-overview/06-lifecycle-and-handoff.md", "title": "Lifecycle and handoff", "coverage": ["readiness_for_decomposition"]}\n  ],\n',
            '    {"order": 6, "path": "docs/overview/initializer-overview/06-lifecycle-and-handoff.md", "title": "Lifecycle and handoff", "coverage": ["readiness_for_decomposition"]},\n    {"order": 7, "path": "docs/overview/initializer-overview/07-capabilities-addendum.md", "title": "Capabilities addendum", "coverage": ["capabilities_and_success"]}\n  ],\n',
            1,
        )
        overview_text = overview_text.replace(
            '- [06 - Lifecycle and handoff](./initializer-overview/06-lifecycle-and-handoff.md)\n',
            '- [06 - Lifecycle and handoff](./initializer-overview/06-lifecycle-and-handoff.md)\n- [07 - Capabilities addendum](./initializer-overview/07-capabilities-addendum.md)\n',
            1,
        )
        overview_path.write_text(overview_text)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        chunk_index_path = temp_repo / "docs/overview/INITIALIZER-OVERVIEW.md"
        chunk_index_path.write_text(chunk_index_path.read_text().replace("./initializer-overview/04-capabilities-and-success.md", "./initializer-overview/05-unresolved-questions.md", 1))
        expect_failure("wrong overview chunk link", lambda: validate_repo(temp_repo), "chunk index link mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        decomposition_path = temp_repo / "docs/decompositions/INITIALIZER-DECOMPOSITION.md"
        decomposition_path.write_text(decomposition_path.read_text().replace("docs/overview/PRODUCT-OVERVIEW.md", "docs/overview/MISSING-OVERVIEW.md", 1))
        expect_failure("missing decomposition predecessor path", lambda: validate_repo(temp_repo), "missing evidence path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace("docs/decompositions/INITIALIZER-DECOMPOSITION.md", "docs/decompositions/MISSING-DECOMPOSITION.md")
        plan_path.write_text(plan_text)
        expect_failure("plan without controlling decomposition", lambda: validate_repo(temp_repo), "unresolved controlling document path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_chunk_path = temp_repo / "docs/plans/initializer-implementation-plan/04-validation-addendum.md"
        plan_chunk_path.write_text("# Validation addendum\n")
        plan_path = temp_repo / "docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace(
            '    "workstreams_and_dependencies": ["docs/plans/initializer-implementation-plan/02-workstreams-and-dependencies.md"],\n',
            '    "workstreams_and_dependencies": ["docs/plans/initializer-implementation-plan/02-workstreams-and-dependencies.md", "docs/plans/initializer-implementation-plan/04-validation-addendum.md"],\n',
            1,
        )
        plan_text = plan_text.replace(
            '    {"order": 3, "path": "docs/plans/initializer-implementation-plan/03-validation-and-completion.md", "title": "Validation and completion", "coverage": ["entry_and_exit_conditions", "transition_gates", "validation_strategy", "risks_and_unresolved_decisions", "completion_and_successor_work"]}\n  ],\n',
            '    {"order": 3, "path": "docs/plans/initializer-implementation-plan/03-validation-and-completion.md", "title": "Validation and completion", "coverage": ["entry_and_exit_conditions", "transition_gates", "validation_strategy", "risks_and_unresolved_decisions", "completion_and_successor_work"]},\n    {"order": 4, "path": "docs/plans/initializer-implementation-plan/04-validation-addendum.md", "title": "Validation addendum", "coverage": ["workstreams_and_dependencies"]}\n  ],\n',
            1,
        )
        plan_text = plan_text.replace(
            '- [03 - Validation and completion](./initializer-implementation-plan/03-validation-and-completion.md)\n',
            '- [03 - Validation and completion](./initializer-implementation-plan/03-validation-and-completion.md)\n- [04 - Validation addendum](./initializer-implementation-plan/04-validation-addendum.md)\n',
            1,
        )
        plan_path.write_text(plan_text)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        plan_path = temp_repo / "docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_text = plan_path.read_text()
        plan_text = plan_text.replace('{"order": 1, "path": "docs/plans/initializer-implementation-plan/01-scope-and-preconditions.md", "title": "Scope and preconditions", "coverage": ["authority_and_basis", "scope_and_exclusions"]}', '{"order": 1, "path": "docs/plans/initializer-implementation-plan/01-scope-and-preconditions.md", "title": "Scope and preconditions"}', 1)
        plan_path.write_text(plan_text)
        expect_failure("plan chunk without coverage", lambda: validate_repo(temp_repo), "required coverage must be an array")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "repo.unlisted"
        (temp_repo / "specs/repo/unlisted.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("unlisted json file", lambda: validate_repo(temp_repo), "manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "product.repo-validation"
        (temp_repo / "specs/repo/product-validation.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"].append({"spec_id": "product.repo-validation", "path": "specs/repo/product-validation.json"}) or manifest,
        )
        expect_failure("product file in repository manifest", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        product_root = temp_repo / "specs/product"
        extra_spec = copy.deepcopy(specs["repo.validation"])
        extra_spec["spec_id"] = "repo.product-root-rogue"
        (product_root / "rogue.json").parent.mkdir(parents=True, exist_ok=True)
        (product_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
        expect_failure("product root contamination", lambda: validate_repo(temp_repo), "undeclared JSON content under specs/product/")

        for level_name in ["level-0", "level-1", "level-2", "level-3"]:
            temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
            clone_index += 1
            product_level_root = temp_repo / "specs/product" / level_name
            extra_spec = copy.deepcopy(specs["repo.validation"])
            extra_spec["spec_id"] = f"repo.{level_name}.rogue"
            product_level_root.mkdir(parents=True, exist_ok=True)
            (product_level_root / "rogue.json").write_text(json.dumps(extra_spec, indent=2) + "\n")
            expect_failure(f"product root contamination in {level_name}", lambda: validate_repo(temp_repo), "undeclared JSON content under specs/product/")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        (temp_repo / "specs/repo/validation.json").unlink()
        expect_failure("missing manifest file", lambda: validate_repo(temp_repo), "manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/manifest.json",
            lambda manifest: manifest["authoritative_specs"][-1].__setitem__("path", "specs/repo/repository-structure.json") or manifest,
        )
        expect_failure("duplicate manifest paths", lambda: validate_repo(temp_repo), "manifest completeness failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/review-proposal.md"}) or spec,
        )
        expect_failure("duplicate derived artifact paths", lambda: validate_repo(temp_repo), "duplicate derived artifact paths failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].__setitem__(0, {"type": "markdown", "path": "derived/specs/repo/validation-missing.md"}) or spec,
        )
        expect_failure("missing derived artifact", lambda: check_generated_document_write_behavior(temp_repo), "generated-document write failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"][-1].__setitem__("path", "../../etc/passwd") or spec,
        )
        expect_failure("artifact reference path escape", lambda: validate_repo(temp_repo), "oneOf mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec.__setitem__("spec_id", "product.validation") or spec,
        )
        expect_failure("product spec under repo root", lambda: validate_repo(temp_repo), "manifest entry repo.validation does not match specs/repo/validation.json")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"][0].__setitem__("path", "../../etc/passwd") or spec,
        )
        expect_failure("derived artifact path escape", lambda: validate_repo(temp_repo), "pattern mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["dependencies"].append({"spec_id": "repo.lifecycle-candidate"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["dependencies"].append({"spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("dependency to retired spec", lambda: validate_repo(temp_repo), "dependencies failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"].append({"type": "specification", "kind": "historical", "spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-retired", "retired")
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"].append({"type": "specification", "spec_id": "repo.lifecycle-retired"}) or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        expect_failure("normative reference to retired spec", lambda: validate_repo(temp_repo), "resolvable references failed")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate", supersedes=["repo.validation"])
        expect_failure("non-reciprocal supersession pair", lambda: validate_repo(temp_repo), "non-reciprocal supersedes pair")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        add_lifecycle_spec(specs, temp_repo, "repo.lifecycle-candidate", "candidate", supersedes=["repo.validation"])
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec.setdefault("superseded_by", []).append("repo.lifecycle-candidate") or spec,
        )
        check_generated_document_write_behavior(temp_repo)
        validate_repo(temp_repo)

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/governing-issue.json",
            lambda spec: spec["issue_fields"].__setitem__(1, copy.deepcopy(spec["issue_fields"][0])) or spec,
        )
        expect_failure("governing issue field uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/review-proposal.json",
            lambda spec: spec["review_fields"].__setitem__(1, copy.deepcopy(spec["review_fields"][0])) or spec,
        )
        expect_failure("review proposal field uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["normative_requirements"].__setitem__(1, copy.deepcopy(spec["normative_requirements"][0])) or spec,
        )
        expect_failure("requirement id uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["dependencies"].append(copy.deepcopy(spec["dependencies"][0])) or spec,
        )
        expect_failure("dependency uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties spec_id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["references"].append(copy.deepcopy(spec["references"][0])) or spec,
        )
        expect_failure("reference uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties type, spec_id, path, kind")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/validation.json",
            lambda spec: spec["derived_artifacts"].append(copy.deepcopy(spec["derived_artifacts"][0])) or spec,
        )
        expect_failure("derived artifact uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties path")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: (
                spec["profiles"][0]["artifact_inventory"][0].__setitem__("classification", "bootstrap-infrastructure"),
                spec["profiles"][0]["artifact_inventory"][0].__setitem__("authority_category", "bootstrap"),
                spec,
            )[-1],
        )
        expect_failure("installed adapter authority", lambda: validate_repo(temp_repo), "artifact classification mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["artifact_inventory"][0].pop("profile_id") and spec,
        )
        expect_failure("profile artifact identity", lambda: validate_repo(temp_repo), "missing required property profile_id")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["remote_state_kinds"].__setitem__(0, "derived/specs/repo/rulesets.json") or spec,
        )
        expect_failure("remote state kinds", lambda: validate_repo(temp_repo), "enum mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0].__setitem__("authority_boundary", "adapter-authoritative") or spec,
        )
        expect_failure("profile authority boundary", lambda: validate_repo(temp_repo), "enum mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"].append(copy.deepcopy(spec["profiles"][0])) or spec,
        )
        expect_failure("duplicate profile identifier", lambda: validate_repo(temp_repo), "duplicate profile identifier github")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["mutation_record_fields"].remove("accepted repository revision") or spec,
        )
        expect_failure("hosting mutation record fields", lambda: validate_repo(temp_repo), "hosting mutation record fields mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/platform-profiles.json",
            lambda spec: spec["profiles"][0]["deployment_state"]["plan_apply_separation"].append("Apply requires a change ticket.") or spec,
        )
        expect_failure("deployment-state contract", lambda: validate_repo(temp_repo), "plan/apply separation mismatch")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        mutate_json(
            temp_repo / "specs/repo/artifact-taxonomy.json",
            lambda spec: spec["artifact_classes"].__setitem__(1, copy.deepcopy(spec["artifact_classes"][0])) or spec,
        )
        expect_failure("artifact class uniqueness", lambda: validate_repo(temp_repo), "duplicate item properties identifier")

        temp_repo = create_repo_fixture(repo_root, temp_root, clone_index)
        clone_index += 1
        expect_failure("repository-relative path helper", lambda: resolve_repo_path(temp_repo, "../../etc/passwd"), "invalid repository-relative path")

    print("ok: repository mutation tests")
