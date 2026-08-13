# Repo-Spec Repository Functional Set

## Status

Approved functional set migrated from the maintained directional overview. Directional and non-normative.

## Metadata

```json
{
  "artifact_id": "repository.functional-set",
  "artifact_type": "functional-set",
  "document_slug": "repository-functional-set",
  "filename_stem": "repository-functional-set",
  "root_path": "repo/docs/overview/",
  "title": "Repo-Spec Repository Functional Set",
  "product_id": "repo-spec",
  "authority_category": "directional",
  "lifecycle_status": "approved",
  "governing_issue": "#374",
  "required_content_areas": {
    "capability_boundary": [
      "repo/docs/overview/repository-functional-set/01-product-direction.md"
    ],
    "included_intent": [
      "repo/docs/overview/repository-functional-set/01-product-direction.md",
      "repo/docs/overview/repository-functional-set/02-decomposition-model-part-1.md",
      "repo/docs/overview/repository-functional-set/03-decomposition-model-part-2.md"
    ],
    "exclusions": [
      "repo/docs/overview/repository-functional-set/01-product-direction.md"
    ],
    "dependencies": [
      "repo/docs/overview/repository-functional-set/02-decomposition-model-part-1.md",
      "repo/docs/overview/repository-functional-set/03-decomposition-model-part-2.md",
      "repo/docs/overview/repository-functional-set/04-development-and-specifications-part-1.md",
      "repo/docs/overview/repository-functional-set/05-development-and-specifications-part-2.md",
      "repo/docs/overview/repository-functional-set/06-development-and-specifications-part-3.md",
      "repo/docs/overview/repository-functional-set/07-git-and-change-workflow.md"
    ],
    "integration_foundation": [
      "repo/docs/overview/repository-functional-set/04-development-and-specifications-part-1.md",
      "repo/docs/overview/repository-functional-set/05-development-and-specifications-part-2.md",
      "repo/docs/overview/repository-functional-set/06-development-and-specifications-part-3.md",
      "repo/docs/overview/repository-functional-set/07-git-and-change-workflow.md",
      "repo/docs/overview/repository-functional-set/09-governance-and-evolution.md"
    ],
    "end_to_end_usability": [
      "repo/docs/overview/repository-functional-set/01-product-direction.md",
      "repo/docs/overview/repository-functional-set/08-human-ai-continuity.md"
    ],
    "decomposition_handoff": [
      "repo/docs/overview/repository-functional-set/02-decomposition-model-part-1.md",
      "repo/docs/overview/repository-functional-set/03-decomposition-model-part-2.md",
      "repo/docs/overview/repository-functional-set/09-governance-and-evolution.md"
    ]
  },
  "controlling_documents": [
    "repo/docs/overview/REPOSITORY-ANALYSIS.md"
  ],
  "predecessor_documents": [
    "repo/docs/overview/REPOSITORY-ANALYSIS.md"
  ],
  "evidence": [
    "repo/docs/overview/repository-analysis/01-migration-analysis.md"
  ],
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/overview/repository-functional-set/01-product-direction.md",
      "title": "Product Overview: Product Direction",
      "coverage": [
        "capability_boundary",
        "included_intent",
        "exclusions",
        "end_to_end_usability"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/overview/repository-functional-set/02-decomposition-model-part-1.md",
      "title": "Product Overview: Decomposition Model \u2014 Part 1",
      "coverage": [
        "included_intent",
        "dependencies",
        "decomposition_handoff"
      ]
    },
    {
      "order": 3,
      "path": "repo/docs/overview/repository-functional-set/03-decomposition-model-part-2.md",
      "title": "Product Overview: Decomposition Model \u2014 Part 2",
      "coverage": [
        "included_intent",
        "dependencies",
        "decomposition_handoff"
      ]
    },
    {
      "order": 4,
      "path": "repo/docs/overview/repository-functional-set/04-development-and-specifications-part-1.md",
      "title": "Product Overview: Development and Specifications \u2014 Part 1",
      "coverage": [
        "dependencies",
        "integration_foundation"
      ]
    },
    {
      "order": 5,
      "path": "repo/docs/overview/repository-functional-set/05-development-and-specifications-part-2.md",
      "title": "Product Overview: Development and Specifications \u2014 Part 2",
      "coverage": [
        "dependencies",
        "integration_foundation"
      ]
    },
    {
      "order": 6,
      "path": "repo/docs/overview/repository-functional-set/06-development-and-specifications-part-3.md",
      "title": "Product Overview: Development and Specifications \u2014 Part 3",
      "coverage": [
        "dependencies",
        "integration_foundation"
      ]
    },
    {
      "order": 7,
      "path": "repo/docs/overview/repository-functional-set/07-git-and-change-workflow.md",
      "title": "Product Overview: Git and Change Workflow",
      "coverage": [
        "dependencies",
        "integration_foundation"
      ]
    },
    {
      "order": 8,
      "path": "repo/docs/overview/repository-functional-set/08-human-ai-continuity.md",
      "title": "Product Overview: Human and AI Continuity",
      "coverage": [
        "end_to_end_usability"
      ]
    },
    {
      "order": 9,
      "path": "repo/docs/overview/repository-functional-set/09-governance-and-evolution.md",
      "title": "Product Overview: Governance and Evolution",
      "coverage": [
        "integration_foundation",
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

- [Product Overview: Product Direction](repository-functional-set/01-product-direction.md)
- [Product Overview: Decomposition Model — Part 1](repository-functional-set/02-decomposition-model-part-1.md)
- [Product Overview: Decomposition Model — Part 2](repository-functional-set/03-decomposition-model-part-2.md)
- [Product Overview: Development and Specifications — Part 1](repository-functional-set/04-development-and-specifications-part-1.md)
- [Product Overview: Development and Specifications — Part 2](repository-functional-set/05-development-and-specifications-part-2.md)
- [Product Overview: Development and Specifications — Part 3](repository-functional-set/06-development-and-specifications-part-3.md)
- [Product Overview: Git and Change Workflow](repository-functional-set/07-git-and-change-workflow.md)
- [Product Overview: Human and AI Continuity](repository-functional-set/08-human-ai-continuity.md)
- [Product Overview: Governance and Evolution](repository-functional-set/09-governance-and-evolution.md)

## Relationships

This approved functional set is controlled by and succeeds [Repo-Spec Repository analysis](./REPOSITORY-ANALYSIS.md).

## Next authorized action

Use this approved functional set as the pre-decomposition directional authority. Decomposition rewiring is intentionally deferred to Patch 2 of issue #374.

## Discoverability

- [Overview root index](./README.md)
