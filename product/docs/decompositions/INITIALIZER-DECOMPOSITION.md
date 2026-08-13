# Repo-Spec Initializer Decomposition

## Status

Directional decomposition record for the approved initializer functional set.

This document is the controlling entry point for the initializer decomposition composite document. It is directional and non-normative.

## Metadata

```json
{
  "artifact_id": "initializer-decomposition",
  "artifact_type": "product-decomposition",
  "document_slug": "initializer-decomposition",
  "filename_stem": "initializer-decomposition",
  "root_path": "product/docs/decompositions/",
  "title": "Repo-Spec Initializer Decomposition",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "accepted",
  "governing_issue": "#175",
  "controlling_documents": [
    "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
  ],
  "predecessor_documents": [
    "product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md"
  ],
  "evidence": [
    "product/docs/overview/initializer-functional-set/01-product-identity-and-purpose.md",
    "product/docs/overview/initializer-functional-set/02-problem-and-outcome.md",
    "product/docs/overview/initializer-functional-set/03-users-principles-and-boundaries.md",
    "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md",
    "product/docs/overview/initializer-functional-set/05-unresolved-questions.md",
    "product/docs/overview/initializer-functional-set/06-lifecycle-and-handoff.md"
  ],
  "required_content_areas": {
    "decomposition_basis": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md"],
    "product_area_inventory": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],
    "dependency_model": ["product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md"],
    "cross_cutting_concerns": ["product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md"],
    "unresolved_decisions": ["product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],
    "stopping_criteria": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"],
    "planning_handoff": ["product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"]
  },
  "subordinate_chunks": [
    {"order": 1, "path": "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority", "role": "product-area", "area_id": "invocation-and-authority", "document_coverage": ["decomposition_basis", "product_area_inventory", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 2, "path": "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "title": "Framework and product foundations", "role": "product-area", "area_id": "framework-and-product-foundations", "document_coverage": ["product_area_inventory", "dependency_model", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 3, "path": "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "title": "Platform and execution", "role": "product-area", "area_id": "platform-and-execution", "document_coverage": ["product_area_inventory", "cross_cutting_concerns", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 4, "path": "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md", "title": "Generation, validation, and handoff", "role": "product-area", "area_id": "generation-validation-and-handoff", "document_coverage": ["product_area_inventory", "unresolved_decisions", "stopping_criteria", "planning_handoff"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}
  ],
  "successor_action": "Proceed to the initializer implementation plan once the decomposition is accepted.",
  "schema_version": "1"
}
```

## Decomposition basis

This decomposition translates the approved initializer functional set into bounded areas and is intentionally non-normative.

## Bounded areas

The initializer is decomposed into invocation and authority, framework and product foundations, platform and execution, and generation, validation, and handoff.

## Chunk index

- [01 - Invocation and authority](./initializer-decomposition/01-invocation-and-authority.md)
- [02 - Framework and product foundations](./initializer-decomposition/02-framework-and-product-foundations.md)
- [03 - Platform and execution](./initializer-decomposition/03-platform-and-execution.md)
- [04 - Generation, validation, and handoff](./initializer-decomposition/04-generation-validation-and-handoff.md)

## Relationships

The basis records show the approved initializer functional set as controlling and predecessor authority. The decomposition preserves unresolved decisions rather than deciding them early.

## Next authorized action

The next authorized action is an initializer implementation plan under `product/docs/plans/`.

## Discoverability

- [Initializer decomposition root index](./README.md)
- [Initializer functional set](../overview/INITIALIZER-FUNCTIONAL-SET.md)

- [Initializer implementation plan](../plans/INITIALIZER-IMPLEMENTATION-PLAN.md)
