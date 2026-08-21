# Repo-Spec Repository Decomposition

## Status

Directional decomposition record for the approved Issue Intake and Governance Routing and Normative Requirement Validation Correspondence functional-set capabilities.

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
    "repo/docs/overview/repository-functional-set/10-issue-intake-and-governance-routing.md",
    "repo/docs/overview/repository-functional-set/11-normative-requirement-validation-correspondence-part-1.md",
    "repo/docs/overview/repository-functional-set/12-normative-requirement-validation-correspondence-part-2.md",
    "repo/docs/overview/repository-functional-set/13-normative-requirement-validation-correspondence-part-3.md",
    "repo/docs/overview/repository-functional-set/14-normative-requirement-validation-correspondence-part-4.md"
  ],
  "required_content_areas": {
    "decomposition_basis": [
      "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
      "repo/docs/decompositions/repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md"
    ],
    "product_area_inventory": [
      "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
      "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
      "repo/docs/decompositions/repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md",
      "repo/docs/decompositions/repository-decomposition/06-validation-correspondence-package-model.md",
      "repo/docs/decompositions/repository-decomposition/07-validation-task-correspondence-and-source-auditability.md",
      "repo/docs/decompositions/repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md",
      "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md"
    ],
    "dependency_model": [
      "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
      "repo/docs/decompositions/repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md",
      "repo/docs/decompositions/repository-decomposition/06-validation-correspondence-package-model.md",
      "repo/docs/decompositions/repository-decomposition/07-validation-task-correspondence-and-source-auditability.md",
      "repo/docs/decompositions/repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md",
      "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md"
    ],
    "cross_cutting_concerns": [
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
      "repo/docs/decompositions/repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md",
      "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md"
    ],
    "unresolved_decisions": [
      "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
      "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
      "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
      "repo/docs/decompositions/repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md",
      "repo/docs/decompositions/repository-decomposition/06-validation-correspondence-package-model.md",
      "repo/docs/decompositions/repository-decomposition/07-validation-task-correspondence-and-source-auditability.md",
      "repo/docs/decompositions/repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md",
      "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md"
    ],
    "stopping_criteria": [
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
      "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md"
    ],
    "planning_handoff": [
      "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
      "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md"
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
    },
    {
      "order": 5,
      "path": "repo/docs/decompositions/repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md",
      "title": "Normative-reference identity and active requirement scope",
      "role": "product-area",
      "area_id": "normative-reference-identity-and-active-requirement-scope",
      "document_coverage": [
        "decomposition_basis",
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
      "order": 6,
      "path": "repo/docs/decompositions/repository-decomposition/06-validation-correspondence-package-model.md",
      "title": "Validation-correspondence package model",
      "role": "product-area",
      "area_id": "validation-correspondence-package-model",
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
      "order": 7,
      "path": "repo/docs/decompositions/repository-decomposition/07-validation-task-correspondence-and-source-auditability.md",
      "title": "Validation-task correspondence and source auditability",
      "role": "product-area",
      "area_id": "validation-task-correspondence-and-source-auditability",
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
      "order": 8,
      "path": "repo/docs/decompositions/repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md",
      "title": "Validation-domain ownership and product reconciliation",
      "role": "product-area",
      "area_id": "validation-domain-ownership-and-product-reconciliation",
      "document_coverage": [
        "product_area_inventory",
        "dependency_model",
        "cross_cutting_concerns",
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
      "order": 9,
      "path": "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md",
      "title": "Correspondence integrity, propagation, and migration",
      "role": "product-area",
      "area_id": "correspondence-integrity-propagation-and-migration",
      "document_coverage": [
        "product_area_inventory",
        "dependency_model",
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
  "successor_action": "Draft and accept the required owner-appropriate repository specifications for Normative Requirement Validation Correspondence, including canonical normative-reference identity and completeness scope, package/cardinality/lifecycle rules, source-local validation-task correspondence, repository-constitutional validation-domain ownership and repo.product-correspondence reconciliation, and integrity/propagation/migration semantics, before implementation planning or validation-package migration.",
  "schema_version": "1"
}
```

## Decomposition basis

This decomposition translates the approved **Issue Intake and Governance Routing** and **Normative Requirement Validation Correspondence** functional-set capabilities into bounded repository responsibility areas.

It preserves the directional authority of the functional set and does not itself establish exact repository or product behavior, normative specification semantics, or implementation architecture.

## Bounded areas

The approved capabilities are decomposed into:

1. intake classification;
2. authority routing;
3. governed-work promotion and provenance;
4. platform validation integration;
5. normative-reference identity and active requirement scope;
6. validation-correspondence package model;
7. validation-task correspondence and source auditability;
8. validation-domain ownership and product reconciliation;
9. correspondence integrity, propagation, and migration.

## Dependency direction

The primary dependency direction is:

`intake classification -> authority routing -> governed-work promotion and provenance -> platform validation integration`

The validation-correspondence dependency direction is:

`normative-reference identity and active requirement scope -> validation-correspondence package model -> validation-task correspondence and source auditability -> validation-domain ownership and product reconciliation -> correspondence integrity, propagation, and migration`

The intended downstream normative specification-family dependency direction is:

`existing repository authority and normative-reference/lifecycle foundations -> canonical repository validation-correspondence semantics -> coordinated product-correspondence normalization plus artifact/structure authorization -> delegated validation enforcement -> workflow, projection, and migration integration where required`

This direction is responsibility-oriented rather than a declaration of exact future specification identities. Existing generic authority, generated-projection, structure, product-lifecycle, validation, and Atomic-transition invariants remain controlling dependencies and should be referenced or specialized rather than independently restated.

The two capability chains share repository authority, workflow, validation, and structure dependencies but do not redefine one another. Audit and feature-development lifecycles remain external dependencies and are not redefined by this decomposition.

## Cross-cutting concerns

Cross-cutting concerns include:

- repository-generic versus hosting-platform-specific responsibility;
- provenance preservation;
- lifecycle-state visibility;
- fail-closed governance transitions;
- validation timing;
- compatibility with existing governing-issue and bounded-change authority;
- normative authority remaining superior to validation correspondence;
- repository-constitutional applicability across repo-owned and product-owned requirements;
- avoidance of duplicate requirement-to-validation registries;
- deterministic correspondence projections and propagation;
- valid accepted states across candidate preparation and migration.

## Stopping criteria

Decomposition is complete when each bounded area has a stable responsibility boundary, unresolved semantic decisions remain visible, cross-specification relationships and dependency direction are explicit, and the required owner-appropriate repository specification families are identified well enough for later normative work without embedding exact behavior, schemas, paths, tagging syntax, or implementation choices here.

## Chunk index

- [01 - Intake classification](./repository-decomposition/01-intake-classification.md)
- [02 - Authority routing](./repository-decomposition/02-authority-routing.md)
- [03 - Governed-work promotion and provenance](./repository-decomposition/03-governed-work-promotion-and-provenance.md)
- [04 - Platform validation integration](./repository-decomposition/04-platform-validation-integration.md)
- [05 - Normative-reference identity and active requirement scope](./repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md)
- [06 - Validation-correspondence package model](./repository-decomposition/06-validation-correspondence-package-model.md)
- [07 - Validation-task correspondence and source auditability](./repository-decomposition/07-validation-task-correspondence-and-source-auditability.md)
- [08 - Validation-domain ownership and product reconciliation](./repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md)
- [09 - Correspondence integrity, propagation, and migration](./repository-decomposition/09-correspondence-integrity-propagation-and-migration.md)

## Relationships

The approved repository functional set is the controlling and predecessor directional authority.

## Next authorized action

Draft and accept the required owner-appropriate normative specifications for the decomposed capabilities before implementation planning. Repository-generic routing and validation-correspondence requirements belong under repository specification authority; hosting-platform-specific routing realization remains within the accepted platform-profile boundary. For validation correspondence, specification work must resolve canonical normative-reference identity and completeness scope, package/cardinality/lifecycle rules, task/source auditability, constitutional domain ownership, repo.product-correspondence reconciliation, integrity, propagation, and migration semantics before implementation planning or package migration.

## Discoverability

- [Repository decomposition root index](./README.md)
- [Repository functional set](../overview/REPOSITORY-FUNCTIONAL-SET.md)
