# Repo-Spec Initializer Overview

## Status

Directional product overview for the `repo-spec` initializer.

This document is the controlling entry point for the initializer overview composite document. It is directional and non-normative.

## Metadata

```json
{
  "artifact_id": "initializer-overview",
  "artifact_type": "product-overview",
  "document_slug": "initializer-overview",
  "filename_stem": "initializer-overview",
  "root_path": "product/docs/overview/",
  "title": "Repo-Spec Initializer Overview",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "accepted",
  "overview_role": "initial",
  "governing_issue": "#175",
  "controlling_documents": [
    "repo/docs/overview/PRODUCT-OVERVIEW.md"
  ],
  "predecessor_documents": [],
  "evidence": [
    "repo/docs/overview/product-overview/01-product-direction.md",
    "repo/docs/overview/product-overview/02-decomposition-model.md",
    "repo/docs/overview/product-overview/03-development-and-specifications.md",
    "repo/docs/overview/product-overview/04-git-and-change-workflow.md",
    "repo/docs/overview/product-overview/05-human-ai-continuity.md",
    "repo/docs/overview/product-overview/06-governance-and-evolution.md"
  ],
  "required_content_areas": {
    "product_identity": ["product/docs/overview/initializer-overview/01-product-identity-and-purpose.md"],
    "problem_and_outcome": ["product/docs/overview/initializer-overview/02-problem-and-outcome.md"],
    "intended_users_and_stakeholders": ["product/docs/overview/initializer-overview/03-users-principles-and-boundaries.md"],
    "scope_and_non_goals": ["product/docs/overview/initializer-overview/03-users-principles-and-boundaries.md"],
    "product_boundaries": ["product/docs/overview/initializer-overview/03-users-principles-and-boundaries.md"],
    "durable_principles": ["product/docs/overview/initializer-overview/03-users-principles-and-boundaries.md"],
    "capabilities_and_success": ["product/docs/overview/initializer-overview/04-capabilities-and-success.md"],
    "unresolved_questions": ["product/docs/overview/initializer-overview/05-unresolved-questions.md"],
    "readiness_for_decomposition": ["product/docs/overview/initializer-overview/06-lifecycle-and-handoff.md"]
  },
  "subordinate_chunks": [
    {"order": 1, "path": "product/docs/overview/initializer-overview/01-product-identity-and-purpose.md", "title": "Product identity and purpose", "coverage": ["product_identity"]},
    {"order": 2, "path": "product/docs/overview/initializer-overview/02-problem-and-outcome.md", "title": "Problem and outcome", "coverage": ["problem_and_outcome"]},
    {"order": 3, "path": "product/docs/overview/initializer-overview/03-users-principles-and-boundaries.md", "title": "Users, principles, and boundaries", "coverage": ["intended_users_and_stakeholders", "scope_and_non_goals", "product_boundaries", "durable_principles"]},
    {"order": 4, "path": "product/docs/overview/initializer-overview/04-capabilities-and-success.md", "title": "Capabilities and success", "coverage": ["capabilities_and_success"]},
    {"order": 5, "path": "product/docs/overview/initializer-overview/05-unresolved-questions.md", "title": "Unresolved questions", "coverage": ["unresolved_questions"]},
    {"order": 6, "path": "product/docs/overview/initializer-overview/06-lifecycle-and-handoff.md", "title": "Lifecycle and handoff", "coverage": ["readiness_for_decomposition"]}
  ],
  "successor_action": "Proceed to the initializer decomposition document once the overview direction is accepted.",
  "schema_version": "1"
}
```

## Overview

The initializer is the maintained `repo-spec` product that applies the framework to create a governed starting point for a new repository. It remains directional and non-normative.

## Chunk index

- [01 - Product identity and purpose](./initializer-overview/01-product-identity-and-purpose.md)
- [02 - Problem and outcome](./initializer-overview/02-problem-and-outcome.md)
- [03 - Users, principles, and boundaries](./initializer-overview/03-users-principles-and-boundaries.md)
- [04 - Capabilities and success](./initializer-overview/04-capabilities-and-success.md)
- [05 - Unresolved questions](./initializer-overview/05-unresolved-questions.md)
- [06 - Lifecycle and handoff](./initializer-overview/06-lifecycle-and-handoff.md)

## Relationships

Bootstrap authority is recorded in metadata through `governing_issue` and `evidence` because this overview is initial. The predecessor product overview remains repository evidence and does not become normative product authority.

## Next authorized action

The next authorized action is initializer decomposition under `repo/docs/decompositions/`.

## Discoverability

- [Initializer overview root index](./README.md)
- [Initializer decomposition](../decompositions/INITIALIZER-DECOMPOSITION.md)

- [Initializer implementation plan](../plans/INITIALIZER-IMPLEMENTATION-PLAN.md)
