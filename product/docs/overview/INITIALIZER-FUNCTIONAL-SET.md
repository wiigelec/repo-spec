# Repo-Spec Initializer Functional Set

## Status

Approved functional set migrated from the maintained directional overview. Directional and non-normative.

## Metadata

```json
{
  "artifact_id": "initializer.functional-set",
  "artifact_type": "functional-set",
  "document_slug": "initializer-functional-set",
  "filename_stem": "initializer-functional-set",
  "root_path": "product/docs/overview/",
  "title": "Repo-Spec Initializer Functional Set",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "approved",
  "governing_issue": "#374",
  "required_content_areas": {
    "capability_boundary": [
      "product/docs/overview/initializer-functional-set/01-product-identity-and-purpose.md",
      "product/docs/overview/initializer-functional-set/03-users-principles-and-boundaries.md",
      "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md"
    ],
    "included_intent": [
      "product/docs/overview/initializer-functional-set/01-product-identity-and-purpose.md",
      "product/docs/overview/initializer-functional-set/02-problem-and-outcome.md",
      "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md"
    ],
    "exclusions": [
      "product/docs/overview/initializer-functional-set/03-users-principles-and-boundaries.md"
    ],
    "dependencies": [
      "product/docs/overview/initializer-functional-set/03-users-principles-and-boundaries.md",
      "product/docs/overview/initializer-functional-set/06-lifecycle-and-handoff.md"
    ],
    "integration_foundation": [
      "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md"
    ],
    "end_to_end_usability": [
      "product/docs/overview/initializer-functional-set/02-problem-and-outcome.md",
      "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md"
    ],
    "decomposition_handoff": [
      "product/docs/overview/initializer-functional-set/05-unresolved-questions.md",
      "product/docs/overview/initializer-functional-set/06-lifecycle-and-handoff.md"
    ]
  },
  "controlling_documents": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md"
  ],
  "predecessor_documents": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md"
  ],
  "evidence": [
    "product/docs/overview/initializer-analysis/01-migration-analysis.md"
  ],
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "product/docs/overview/initializer-functional-set/01-product-identity-and-purpose.md",
      "title": "Initializer Overview: Product Identity and Purpose",
      "coverage": [
        "capability_boundary",
        "included_intent"
      ]
    },
    {
      "order": 2,
      "path": "product/docs/overview/initializer-functional-set/02-problem-and-outcome.md",
      "title": "Initializer Overview: Problem and Outcome",
      "coverage": [
        "included_intent",
        "end_to_end_usability"
      ]
    },
    {
      "order": 3,
      "path": "product/docs/overview/initializer-functional-set/03-users-principles-and-boundaries.md",
      "title": "Initializer Overview: Users, Principles, and Boundaries",
      "coverage": [
        "capability_boundary",
        "exclusions",
        "dependencies"
      ]
    },
    {
      "order": 4,
      "path": "product/docs/overview/initializer-functional-set/04-capabilities-and-success.md",
      "title": "Initializer Overview: Capabilities and Success",
      "coverage": [
        "capability_boundary",
        "included_intent",
        "integration_foundation",
        "end_to_end_usability"
      ]
    },
    {
      "order": 5,
      "path": "product/docs/overview/initializer-functional-set/05-unresolved-questions.md",
      "title": "Initializer Overview: Unresolved Questions",
      "coverage": [
        "decomposition_handoff"
      ]
    },
    {
      "order": 6,
      "path": "product/docs/overview/initializer-functional-set/06-lifecycle-and-handoff.md",
      "title": "Initializer Overview: Lifecycle and Handoff",
      "coverage": [
        "dependencies",
        "decomposition_handoff"
      ]
    }
  ],
  "successor_action": "Proceed to product decomposition using this approved functional set as the controlling directional authority.",
  "schema_version": "1"
}
```

## Overview

This functional set is the canonical capability-oriented replacement for the maintained legacy directional overview. Its subordinate chunks preserve the existing directional prose while the metadata maps that content into the functional-set contract.

## Chunk index

- [Initializer Overview: Product Identity and Purpose](initializer-functional-set/01-product-identity-and-purpose.md)
- [Initializer Overview: Problem and Outcome](initializer-functional-set/02-problem-and-outcome.md)
- [Initializer Overview: Users, Principles, and Boundaries](initializer-functional-set/03-users-principles-and-boundaries.md)
- [Initializer Overview: Capabilities and Success](initializer-functional-set/04-capabilities-and-success.md)
- [Initializer Overview: Unresolved Questions](initializer-functional-set/05-unresolved-questions.md)
- [Initializer Overview: Lifecycle and Handoff](initializer-functional-set/06-lifecycle-and-handoff.md)

## Relationships

This approved functional set is controlled by and succeeds [Repo-Spec Initializer analysis](./INITIALIZER-ANALYSIS.md).

## Next authorized action

Use this approved functional set as the pre-decomposition directional authority. Decomposition rewiring is intentionally deferred to Patch 2 of issue #374.

## Discoverability

- [Overview root index](./README.md)
