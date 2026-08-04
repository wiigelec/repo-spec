# Repo-Spec Initializer Decomposition

## Status

Directional decomposition record for the initializer overview.

This document is the controlling entry point for the initializer decomposition composite document. It is directional and non-normative.

## Metadata

```json
{
  "artifact_id": "initializer-decomposition",
  "artifact_type": "product-decomposition",
  "document_slug": "initializer-decomposition",
  "root_path": "docs/decompositions/",
  "title": "Repo-Spec Initializer Decomposition",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "accepted",
  "governing_issue": "#175",
  "basis": [
    {"type": "artifact", "path": "docs/overview/INITIALIZER-OVERVIEW.md"},
    {"type": "artifact", "path": "docs/overview/PRODUCT-OVERVIEW.md"},
    {"type": "artifact", "path": "docs/overview/product-overview/02-decomposition-model.md"},
    {"type": "artifact", "path": "docs/overview/product-overview/03-development-and-specifications.md"},
    {"type": "artifact", "path": "docs/overview/product-overview/04-git-and-change-workflow.md"},
    {"type": "artifact", "path": "docs/overview/product-overview/05-human-ai-continuity.md"},
    {"type": "artifact", "path": "docs/overview/product-overview/06-governance-and-evolution.md"}
  ],
  "content_areas": {
    "invocation_and_authority": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md",
    "framework_and_product_foundations": "docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md",
    "platform_and_execution": "docs/decompositions/initializer-decomposition/03-platform-and-execution.md",
    "generation_validation_and_handoff": "docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"
  },
  "subordinate_chunks": [
    {"order": 1, "path": "docs/decompositions/initializer-decomposition/01-invocation-and-authority.md", "title": "Invocation and authority"},
    {"order": 2, "path": "docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md", "title": "Framework and product foundations"},
    {"order": 3, "path": "docs/decompositions/initializer-decomposition/03-platform-and-execution.md", "title": "Platform and execution"},
    {"order": 4, "path": "docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md", "title": "Generation, validation, and handoff"}
  ],
  "successor_action": "Proceed to the initializer implementation plan once the decomposition is accepted.",
  "schema_version": "1"
}
```

## Decomposition basis

This decomposition translates the initializer overview into bounded areas and is intentionally non-normative.

## Bounded areas

The initializer is decomposed into invocation and authority, framework and product foundations, platform and execution, and generation, validation, and handoff.

## Chunk index

- [01 - Invocation and authority](./initializer-decomposition/01-invocation-and-authority.md)
- [02 - Framework and product foundations](./initializer-decomposition/02-framework-and-product-foundations.md)
- [03 - Platform and execution](./initializer-decomposition/03-platform-and-execution.md)
- [04 - Generation, validation, and handoff](./initializer-decomposition/04-generation-validation-and-handoff.md)

## Relationships

The basis records show the controlling overview and predecessor evidence. The decomposition preserves unresolved decisions rather than deciding them early.

## Next authorized action

The next authorized action is an initializer implementation plan under `docs/plans/`.

## Discoverability

- [Initializer decomposition root index](./README.md)
- [Initializer overview](../overview/INITIALIZER-OVERVIEW.md)
- [Initializer implementation plan](../plans/INITIALIZER-IMPLEMENTATION-PLAN.md)
