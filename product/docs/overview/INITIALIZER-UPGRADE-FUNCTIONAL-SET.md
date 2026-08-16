# Repo-Spec Initializer Upgrade Functional Set

## Status

Approved derived-repository upgrade functional set. Directional and non-normative. Product decomposition is now the next authorized lifecycle step.

## Metadata

```json
{
  "artifact_id": "initializer-upgrade.functional-set",
  "artifact_type": "functional-set",
  "document_slug": "initializer-upgrade-functional-set",
  "filename_stem": "initializer-upgrade-functional-set",
  "root_path": "product/docs/overview/",
  "title": "Repo-Spec Initializer Upgrade Functional Set",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "approved",
  "governing_issue": "#437",
  "required_content_areas": {
    "capability_boundary": [
      "product/docs/overview/initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md",
      "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
      "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md"
    ],
    "included_intent": [
      "product/docs/overview/initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md",
      "product/docs/overview/initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md",
      "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
      "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md"
    ],
    "exclusions": [
      "product/docs/overview/initializer-upgrade-functional-set/05-boundaries-and-unresolved-direction.md"
    ],
    "dependencies": [
      "product/docs/overview/initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md",
      "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
      "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md",
      "product/docs/overview/initializer-upgrade-functional-set/06-decomposition-handoff.md"
    ],
    "integration_foundation": [
      "product/docs/overview/initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md",
      "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
      "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md"
    ],
    "end_to_end_usability": [
      "product/docs/overview/initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md",
      "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
      "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md"
    ],
    "decomposition_handoff": [
      "product/docs/overview/initializer-upgrade-functional-set/05-boundaries-and-unresolved-direction.md",
      "product/docs/overview/initializer-upgrade-functional-set/06-decomposition-handoff.md"
    ]
  },
  "controlling_documents": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md"
  ],
  "predecessor_documents": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md"
  ],
  "evidence": [
    "product/docs/overview/initializer-analysis/02-derived-repository-upgrade-analysis.md",
    "product/docs/overview/initializer-analysis/03-derived-repository-upgrade-architecture-audit.md",
    "product/docs/overview/initializer-analysis/04-derived-repository-upgrade-methodologies.md",
    "product/docs/overview/initializer-analysis/05-derived-repository-upgrade-handoff.md"
  ],
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "product/docs/overview/initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md",
      "title": "Upgrade capability boundary and outcome",
      "coverage": ["capability_boundary", "included_intent", "end_to_end_usability"]
    },
    {
      "order": 2,
      "path": "product/docs/overview/initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md",
      "title": "Framework identity and managed material",
      "coverage": ["included_intent", "dependencies", "integration_foundation"]
    },
    {
      "order": 3,
      "path": "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
      "title": "Staged managed upgrade",
      "coverage": ["capability_boundary", "included_intent", "dependencies", "integration_foundation", "end_to_end_usability"]
    },
    {
      "order": 4,
      "path": "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md",
      "title": "Re-anchoring, validation, and promotion",
      "coverage": ["capability_boundary", "included_intent", "dependencies", "integration_foundation", "end_to_end_usability"]
    },
    {
      "order": 5,
      "path": "product/docs/overview/initializer-upgrade-functional-set/05-boundaries-and-unresolved-direction.md",
      "title": "Boundaries and unresolved direction",
      "coverage": ["exclusions", "decomposition_handoff"]
    },
    {
      "order": 6,
      "path": "product/docs/overview/initializer-upgrade-functional-set/06-decomposition-handoff.md",
      "title": "Decomposition handoff",
      "coverage": ["dependencies", "decomposition_handoff"]
    }
  ],
  "successor_action": "Proceed to product decomposition using this approved upgrade functional set as the controlling directional authority.",
  "schema_version": "1"
}
```

## Overview

This approved functional set defines one coherent derived-repository upgrade capability within the Repo-Spec Initializer product. The capability is an in-place re-initialization of an already initialized target repository: it reconciles initializer-managed material from the target's currently accepted framework state to the supplying repo-spec framework state while preserving repository content outside the initializer-managed material universe. It turns the accepted upgrade analysis into a bounded directional unit without establishing exact interfaces, schemas, algorithms, compatibility policy, implementation architecture, or release readiness.

The existing approved `INITIALIZER-FUNCTIONAL-SET.md` remains the approved directional authority for the original initializer scope. This approved functional set adds upgrade direction without demoting or rewriting that accepted functional set.

## Chunk index

- [Upgrade capability boundary and outcome](initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md)
- [Framework identity and managed material](initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md)
- [Staged managed upgrade](initializer-upgrade-functional-set/03-staged-managed-upgrade.md)
- [Re-anchoring, validation, and promotion](initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md)
- [Boundaries and unresolved direction](initializer-upgrade-functional-set/05-boundaries-and-unresolved-direction.md)
- [Decomposition handoff](initializer-upgrade-functional-set/06-decomposition-handoff.md)

## Relationships

This approved functional set is controlled by and succeeds [Repo-Spec Initializer analysis](./INITIALIZER-ANALYSIS.md).

It is separate from the already approved [Repo-Spec Initializer functional set](./INITIALIZER-FUNCTIONAL-SET.md).

## Next authorized action

Use this approved functional set as the controlling directional authority for product decomposition. This document does not itself create or accept a decomposition.

## Discoverability

- [Overview root index](./README.md)
