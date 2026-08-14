# Repo-Spec Issue Intake and Governance Routing Implementation Plan

## Status

Candidate; planning-authoritative only after separate acceptance; non-normative with respect to product semantics.

This document is the controlling entry point for the Issue Intake and Governance Routing implementation-plan composite. Issue #400 authorizes candidate planning only. The plan does not itself authorize implementation issues or maintained implementation mutation.

## Metadata

```json
{
  "artifact_id": "repository-implementation-plan",
  "artifact_type": "implementation-plan",
  "document_slug": "repository-implementation-plan",
  "filename_stem": "repository-implementation-plan",
  "root_path": "repo/docs/plans/",
  "title": "Repo-Spec Issue Intake and Governance Routing Implementation Plan",
  "product_id": "repo-spec",
  "authority_category": "planning",
  "lifecycle_status": "candidate",
  "governing_issue": "#400",
  "controlling_documents": [
    "repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md",
    "repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md"
  ],
  "predecessor_documents": [
    "repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md"
  ],
  "evidence": [
    "repo/docs/overview/repository-functional-set/10-issue-intake-and-governance-routing.md",
    "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
    "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
    "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
    "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
    "product/specs/product/level-0/issue-routing-governance.json",
    "product/specs/product/level-1/issue-routing-classification.json",
    "product/specs/product/level-1/governed-work-provenance.json",
    "product/specs/product/level-2/issue-authority-routing.json",
    "product/specs/product/level-2/governed-work-promotion.json",
    "product/specs/product/level-2/issue-routing-platform-validation.json",
    "product/specs/product/level-3/issue-intake-governance-routing.json"
  ],
  "workstream_authority": [
    {
      "id": "IRP-I1",
      "controlling_product_specifications": [
        "product.issue-routing-governance",
        "product.issue-routing-classification"
      ]
    },
    {
      "id": "IRP-I2",
      "controlling_product_specifications": [
        "product.issue-routing-governance",
        "product.issue-routing-classification",
        "product.issue-authority-routing"
      ]
    },
    {
      "id": "IRP-I3",
      "controlling_product_specifications": [
        "product.issue-routing-governance",
        "product.governed-work-provenance",
        "product.issue-authority-routing",
        "product.governed-work-promotion"
      ]
    },
    {
      "id": "IRP-I4",
      "controlling_product_specifications": [
        "product.issue-routing-governance",
        "product.governed-work-provenance",
        "product.governed-work-promotion",
        "product.issue-routing-platform-validation"
      ]
    },
    {
      "id": "IRP-I5",
      "controlling_product_specifications": [
        "product.issue-routing-governance",
        "product.issue-routing-classification",
        "product.governed-work-provenance",
        "product.issue-authority-routing",
        "product.governed-work-promotion",
        "product.issue-routing-platform-validation",
        "product.issue-intake-governance-routing"
      ]
    }
  ],
  "required_content_areas": {
    "authority_and_basis": [
      "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "scope_and_exclusions": [
      "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "workstreams_and_dependencies": [
      "repo/docs/plans/repository-implementation-plan/02-workstreams-and-dependencies.md"
    ],
    "entry_and_exit_conditions": [
      "repo/docs/plans/repository-implementation-plan/02-workstreams-and-dependencies.md"
    ],
    "transition_gates": [
      "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "validation_strategy": [
      "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "risks_and_unresolved_decisions": [
      "repo/docs/plans/repository-implementation-plan/04-risks-and-unresolved-decisions.md"
    ],
    "completion_and_successor_work": [
      "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md",
      "title": "Authority, scope, and specification map",
      "coverage": [
        "authority_and_basis",
        "scope_and_exclusions"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/plans/repository-implementation-plan/02-workstreams-and-dependencies.md",
      "title": "Workstreams and dependencies",
      "coverage": [
        "workstreams_and_dependencies",
        "entry_and_exit_conditions"
      ]
    },
    {
      "order": 3,
      "path": "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md",
      "title": "Validation, gates, and completion",
      "coverage": [
        "transition_gates",
        "validation_strategy",
        "completion_and_successor_work"
      ]
    },
    {
      "order": 4,
      "path": "repo/docs/plans/repository-implementation-plan/04-risks-and-unresolved-decisions.md",
      "title": "Risks and unresolved decisions",
      "coverage": [
        "risks_and_unresolved_decisions"
      ]
    }
  ],
  "successor_action": "Review and explicitly accept this candidate implementation plan in a separate governed plan-acceptance step before creating Product-artifact implementation issues.",
  "schema_version": "1"
}
```

## Planning basis

The accepted Issue Intake and Governance Routing product specifications are normative product authority. This plan sequences and coordinates implementation without redefining those semantics.

Accepted planning basis: `main` at `d649c51d07d02f8af2c6fc48144c481725c25d01`.

The controlling directional predecessors are the approved repository functional set and accepted repository decomposition. Exact behavior remains controlled by the accepted Level 0-3 product specifications listed in the metadata evidence and workstream authority sets.

## Workstreams

| Workstream | Purpose | Dependency |
| --- | --- | --- |
| IRP-I1 | Intake classification realization | none |
| IRP-I2 | Authority routing realization | IRP-I1 |
| IRP-I3 | Provenance-preserving governed-work promotion | IRP-I1, IRP-I2 |
| IRP-I4 | Hosted validation and platform integration | IRP-I3 |
| IRP-I5 | End-to-end integration and conformance | IRP-I1 through IRP-I4 |

Each workstream's exact controlling accepted product specifications are declared in `workstream_authority`.

## Execution order

Primary order:

`IRP-I1 -> IRP-I2 -> IRP-I3 -> IRP-I4 -> IRP-I5`

Parallel work is allowed only where an implementation issue can prove that its entry conditions and controlling accepted specifications are satisfied without depending on unfinished predecessor behavior.

## Candidate planning boundary

This plan may select implementation mechanics needed to realize accepted product behavior, but it may not manufacture new product semantics. A newly discovered semantic gap must return to specification governance.

## Chunk index

- [Authority, scope, and specification map](./repository-implementation-plan/01-authority-scope-and-specification-map.md)
- [Workstreams and dependencies](./repository-implementation-plan/02-workstreams-and-dependencies.md)
- [Validation, gates, and completion](./repository-implementation-plan/03-validation-gates-and-completion.md)
- [Risks and unresolved decisions](./repository-implementation-plan/04-risks-and-unresolved-decisions.md)

## Relationships

- Governing issue: #400.
- Controlling planning contracts: `repo.implementation-plan`, `repo.development-document-base`, `repo.development-workflow`, and `repo.validation`.
- Controlling functional-set capability: Issue Intake and Governance Routing.
- Controlling decomposition: `repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md`.
- Normative product authority: the seven accepted Issue Intake and Governance Routing product specifications.

## Next authorized action

Review this candidate plan. A separate governed acceptance step must explicitly accept the plan before Product-artifact implementation issues may cite IRP-I1 through IRP-I5 as planning authority.

## Discoverability

- [Repository plan root](./README.md)
- [Repository decomposition](../decompositions/REPOSITORY-DECOMPOSITION.md)
- [Repository functional set](../overview/REPOSITORY-FUNCTIONAL-SET.md)
