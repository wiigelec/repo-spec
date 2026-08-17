# Repo-Spec Initializer Validation Scaffolding Functional Set

## Status

Candidate initializer validation-scaffolding functional set. Directional and non-normative. Explicit user approval is required before decomposition.

## Metadata

```json
{
  "artifact_id": "initializer-validation-scaffolding.functional-set",
  "artifact_type": "functional-set",
  "document_slug": "initializer-validation-scaffolding-functional-set",
  "filename_stem": "initializer-validation-scaffolding-functional-set",
  "root_path": "product/docs/overview/",
  "title": "Repo-Spec Initializer Validation Scaffolding Functional Set",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "candidate",
  "governing_issue": "#483",
  "required_content_areas": {
    "capability_boundary": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/01-capability-boundary-and-outcome.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/02-common-ci-and-stable-entrypoints.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md"
    ],
    "included_intent": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/01-capability-boundary-and-outcome.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/02-common-ci-and-stable-entrypoints.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/03-product-test-lifecycle.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md"
    ],
    "exclusions": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/05-boundaries-and-unresolved-direction.md"
    ],
    "dependencies": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/02-common-ci-and-stable-entrypoints.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/03-product-test-lifecycle.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/06-decomposition-handoff.md"
    ],
    "integration_foundation": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/02-common-ci-and-stable-entrypoints.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md"
    ],
    "end_to_end_usability": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/01-capability-boundary-and-outcome.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/03-product-test-lifecycle.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md"
    ],
    "decomposition_handoff": [
      "product/docs/overview/initializer-validation-scaffolding-functional-set/05-boundaries-and-unresolved-direction.md",
      "product/docs/overview/initializer-validation-scaffolding-functional-set/06-decomposition-handoff.md"
    ]
  },
  "controlling_documents": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md"
  ],
  "predecessor_documents": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md"
  ],
  "evidence": [
    "product/docs/overview/initializer-analysis/06-product-validation-scaffolding-analysis.md",
    "product/docs/overview/initializer-whiteboard/03-product-validation-scaffolding-intake.md"
  ],
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "product/docs/overview/initializer-validation-scaffolding-functional-set/01-capability-boundary-and-outcome.md",
      "title": "Validation scaffolding capability boundary and outcome",
      "coverage": ["capability_boundary", "included_intent", "end_to_end_usability"]
    },
    {
      "order": 2,
      "path": "product/docs/overview/initializer-validation-scaffolding-functional-set/02-common-ci-and-stable-entrypoints.md",
      "title": "Common CI and stable validation/test entrypoints",
      "coverage": ["capability_boundary", "included_intent", "dependencies", "integration_foundation"]
    },
    {
      "order": 3,
      "path": "product/docs/overview/initializer-validation-scaffolding-functional-set/03-product-test-lifecycle.md",
      "title": "Product-test lifecycle and zero-applicable state",
      "coverage": ["included_intent", "dependencies", "end_to_end_usability"]
    },
    {
      "order": 4,
      "path": "product/docs/overview/initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md",
      "title": "Initialized-output executable closure",
      "coverage": ["capability_boundary", "included_intent", "dependencies", "integration_foundation", "end_to_end_usability"]
    },
    {
      "order": 5,
      "path": "product/docs/overview/initializer-validation-scaffolding-functional-set/05-boundaries-and-unresolved-direction.md",
      "title": "Boundaries and unresolved direction",
      "coverage": ["exclusions", "decomposition_handoff"]
    },
    {
      "order": 6,
      "path": "product/docs/overview/initializer-validation-scaffolding-functional-set/06-decomposition-handoff.md",
      "title": "Decomposition handoff",
      "coverage": ["dependencies", "decomposition_handoff"]
    }
  ],
  "successor_action": "Obtain explicit user approval or rejection/modification of this candidate functional set. Candidate status does not authorize decomposition.",
  "schema_version": "1"
}
```

## Overview

This candidate defines one coherent initializer capability: a newly generated repository should contain a usable common validation/test workflow and the stable local interfaces needed to execute it without manual repair.

It carries forward the accepted analysis direction for common CI, repository/product test ownership, generic `product/scripts/test-product`, honest zero-applicable product-test state, and initialized-output executable closure. It remains non-normative about exact runtime mechanics.

The existing approved [Repo-Spec Initializer functional set](./INITIALIZER-FUNCTIONAL-SET.md) remains unchanged and separately authoritative for its accepted scope.

## Chunk index

- [Validation scaffolding capability boundary and outcome](initializer-validation-scaffolding-functional-set/01-capability-boundary-and-outcome.md)
- [Common CI and stable validation/test entrypoints](initializer-validation-scaffolding-functional-set/02-common-ci-and-stable-entrypoints.md)
- [Product-test lifecycle and zero-applicable state](initializer-validation-scaffolding-functional-set/03-product-test-lifecycle.md)
- [Initialized-output executable closure](initializer-validation-scaffolding-functional-set/04-initialized-output-closure.md)
- [Boundaries and unresolved direction](initializer-validation-scaffolding-functional-set/05-boundaries-and-unresolved-direction.md)
- [Decomposition handoff](initializer-validation-scaffolding-functional-set/06-decomposition-handoff.md)

## Relationships

This candidate is controlled by and succeeds [Repo-Spec Initializer analysis](./INITIALIZER-ANALYSIS.md), specifically the accepted product-validation-scaffolding analysis.

It is separate from the already approved [Repo-Spec Initializer functional set](./INITIALIZER-FUNCTIONAL-SET.md) and from the approved [Repo-Spec Initializer Upgrade functional set](./INITIALIZER-UPGRADE-FUNCTIONAL-SET.md).

## Next authorized action

Review this candidate and obtain explicit user approval, rejection, or requested modification. Do not create or modify decomposition artifacts until approval establishes the directional handoff.

## Discoverability

- [Overview root index](./README.md)
