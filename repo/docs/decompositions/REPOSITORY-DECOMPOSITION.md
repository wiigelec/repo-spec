# Repo-Spec Repository Decomposition

## Status

Directional decomposition record for the approved Issue Intake and Governance Routing functional-set capability.

This document is the controlling entry point for the repository decomposition composite document. It is directional and non-normative.

## Metadata

```json
{
  "artifact_id": "repository-decomposition",
  "artifact_type": "product-decomposition",
  "document_slug": "repository-decomposition",
  "filename_stem": "repository-decomposition",
  "root_path": "repo/docs/decompositions/",
  "title": "Repo-Spec Repository Decomposition",
  "product_id": "repo-spec",
  "authority_category": "directional",
  "lifecycle_status": "accepted",
  "governing_issue": "#394",
  "controlling_documents": [
    "repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md"
  ],
  "predecessor_documents": [
    "repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md"
  ],
  "evidence": [
    "repo/docs/overview/repository-functional-set/10-issue-intake-and-governance-routing.md"
  ],
  "required_content_areas": {
    "decomposition_basis": [
      "repo/docs/decompositions/repository-decomposition/01-intake-classification.md"
    ],
    "product_area_inventory": [
      "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
      "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md"
    ],
    "dependency_model": [
      "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md"
    ],
    "cross_cutting_concerns": [
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md"
    ],
    "unresolved_decisions": [
      "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
      "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md"
    ],
    "stopping_criteria": [
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md"
    ],
    "planning_handoff": [
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
      "title": "Intake classification",
      "role": "product-area",
      "area_id": "intake-classification",
      "document_coverage": [
        "decomposition_basis",
        "product_area_inventory",
        "unresolved_decisions"
      ],
      "coverage": [
        "purpose",
        "responsibilities",
        "boundaries",
        "dependencies",
        "exclusions",
        "unresolved-decisions",
        "successor-work"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "title": "Authority routing",
      "role": "product-area",
      "area_id": "authority-routing",
      "document_coverage": [
        "product_area_inventory",
        "dependency_model",
        "unresolved_decisions"
      ],
      "coverage": [
        "purpose",
        "responsibilities",
        "boundaries",
        "dependencies",
        "exclusions",
        "unresolved-decisions",
        "successor-work"
      ]
    },
    {
      "order": 3,
      "path": "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
      "title": "Governed-work promotion and provenance",
      "role": "product-area",
      "area_id": "governed-work-promotion-and-provenance",
      "document_coverage": [
        "product_area_inventory",
        "dependency_model",
        "unresolved_decisions"
      ],
      "coverage": [
        "purpose",
        "responsibilities",
        "boundaries",
        "dependencies",
        "exclusions",
        "unresolved-decisions",
        "successor-work"
      ]
    },
    {
      "order": 4,
      "path": "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
      "title": "Platform validation integration",
      "role": "product-area",
      "area_id": "platform-validation-integration",
      "document_coverage": [
        "product_area_inventory",
        "cross_cutting_concerns",
        "unresolved_decisions",
        "stopping_criteria",
        "planning_handoff"
      ],
      "coverage": [
        "purpose",
        "responsibilities",
        "boundaries",
        "dependencies",
        "exclusions",
        "unresolved-decisions",
        "successor-work"
      ]
    }
  ],
  "successor_action": "Draft and accept the required owner-appropriate normative specifications for Issue Intake and Governance Routing, with repository-generic requirements under repository specification authority and hosting-platform realization kept within the accepted platform-profile boundary, before implementation planning.",
  "schema_version": "1"
}
```

## Decomposition basis

This decomposition translates the approved **Issue Intake and Governance Routing** functional-set capability into bounded repository responsibility areas.

It preserves the directional authority of the functional set and does not itself establish exact product behavior or implementation architecture.

## Bounded areas

The capability is decomposed into:

1. intake classification;
2. authority routing;
3. governed-work promotion and provenance;
4. platform validation integration.

## Dependency direction

The primary dependency direction is:

`intake classification -> authority routing -> governed-work promotion and provenance -> platform validation integration`

Audit and feature-development lifecycles remain external dependencies and are not redefined by this decomposition.

## Cross-cutting concerns

Cross-cutting concerns include:

- repository-generic versus hosting-platform-specific responsibility;
- provenance preservation;
- lifecycle-state visibility;
- fail-closed governance transitions;
- validation timing;
- compatibility with existing governing-issue and bounded-change authority.

## Stopping criteria

Decomposition is complete when each bounded area has a stable responsibility boundary, unresolved semantic decisions remain visible, and the required specification families are identified well enough for later normative work without embedding exact behavior here.

## Chunk index

- [01 - Intake classification](./repository-decomposition/01-intake-classification.md)
- [02 - Authority routing](./repository-decomposition/02-authority-routing.md)
- [03 - Governed-work promotion and provenance](./repository-decomposition/03-governed-work-promotion-and-provenance.md)
- [04 - Platform validation integration](./repository-decomposition/04-platform-validation-integration.md)

## Relationships

The approved repository functional set is the controlling and predecessor directional authority.

## Next authorized action

Draft and accept the required owner-appropriate normative specifications for these areas before implementation planning. Repository-generic routing requirements belong under repository specification authority; hosting-platform-specific realization remains within the accepted platform-profile boundary.

## Discoverability

- [Repository decomposition root index](./README.md)
- [Repository functional set](../overview/REPOSITORY-FUNCTIONAL-SET.md)
