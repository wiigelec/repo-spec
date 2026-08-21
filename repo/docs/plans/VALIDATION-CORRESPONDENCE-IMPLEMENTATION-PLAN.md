# Validation Correspondence Implementation Plan

## Status

Candidate implementation plan; non-normative with respect to repository and product semantics.

Issue #568 governs creation, correction, and later explicit acceptance of this plan. The completed normative-specification stage is recorded by issue #561 and final accepted specification-stage revision `21577021da0187d2310b808079a1ec573ea54b0a`.

Merging this candidate revision does **not** make the plan accepted. Durable planning authority exists only after a separate bounded acceptance revision changes this document's status and machine-readable `lifecycle_status` to `accepted`, that exact revision is reviewed and validated, and the user manually merges it.

This candidate plan does not authorize maintained implementation mutation.

## Metadata

```json
{
  "artifact_id": "validation-correspondence-implementation-plan",
  "artifact_type": "implementation-plan",
  "document_slug": "validation-correspondence-implementation-plan",
  "filename_stem": "validation-correspondence-implementation-plan",
  "root_path": "repo/docs/plans/",
  "title": "Validation Correspondence Implementation Plan",
  "product_id": "repo-spec",
  "authority_category": "planning",
  "lifecycle_status": "candidate",
  "governing_issue": "#568",
  "controlling_documents": [
    "repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md",
    "repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md"
  ],
  "predecessor_documents": [
    "repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md"
  ],
  "evidence": [
    "repo/docs/overview/repository-functional-set/11-normative-requirement-validation-correspondence-part-1.md",
    "repo/docs/overview/repository-functional-set/12-normative-requirement-validation-correspondence-part-2.md",
    "repo/docs/overview/repository-functional-set/13-normative-requirement-validation-correspondence-part-3.md",
    "repo/docs/overview/repository-functional-set/14-normative-requirement-validation-correspondence-part-4.md",
    "repo/docs/decompositions/repository-decomposition/05-normative-reference-identity-and-active-requirement-scope.md",
    "repo/docs/decompositions/repository-decomposition/06-validation-correspondence-package-model.md",
    "repo/docs/decompositions/repository-decomposition/07-validation-task-correspondence-and-source-auditability.md",
    "repo/docs/decompositions/repository-decomposition/08-validation-domain-ownership-and-product-reconciliation.md",
    "repo/docs/decompositions/repository-decomposition/09-correspondence-integrity-propagation-and-migration.md",
    "repo/specs/repo/validation-correspondence.json",
    "repo/specs/repo/validation.json",
    "repo/specs/repo/artifact-taxonomy.json",
    "repo/specs/repo/repository-structure.json",
    "repo/specs/repo/product-correspondence.json",
    "repo/specs/repo/product-manifest.json",
    "repo/specs/repo/product-spec-base.json",
    "repo/specs/repo/authority-model.json",
    "repo/specs/repo/development-workflow.json"
  ],
  "applicable_accepted_specifications": [
    "repo.artifact-taxonomy",
    "repo.authority-model",
    "repo.development-workflow",
    "repo.product-correspondence",
    "repo.product-manifest",
    "repo.product-spec-base",
    "repo.repository-structure",
    "repo.validation",
    "repo.validation-correspondence"
  ],
  "workstream_authority": [
    {
      "id": "VCP-I1",
      "controlling_product_specifications": [
        "repo.authority-model",
        "repo.validation-correspondence",
        "repo.artifact-taxonomy",
        "repo.repository-structure",
        "repo.validation"
      ]
    },
    {
      "id": "VCP-I2",
      "controlling_product_specifications": [
        "repo.validation-correspondence",
        "repo.repository-structure",
        "repo.validation"
      ]
    },
    {
      "id": "VCP-I3",
      "controlling_product_specifications": [
        "repo.validation-correspondence",
        "repo.artifact-taxonomy",
        "repo.repository-structure",
        "repo.product-correspondence",
        "repo.product-manifest",
        "repo.product-spec-base",
        "repo.validation",
        "repo.development-workflow"
      ]
    },
    {
      "id": "VCP-I4",
      "controlling_product_specifications": [
        "repo.authority-model",
        "repo.validation-correspondence",
        "repo.repository-structure",
        "repo.product-correspondence",
        "repo.validation",
        "repo.development-workflow"
      ]
    },
    {
      "id": "VCP-I5",
      "controlling_product_specifications": [
        "repo.authority-model",
        "repo.validation-correspondence",
        "repo.repository-structure",
        "repo.validation",
        "repo.development-workflow"
      ]
    },
    {
      "id": "VCP-I6",
      "controlling_product_specifications": [
        "repo.authority-model",
        "repo.validation-correspondence",
        "repo.artifact-taxonomy",
        "repo.repository-structure",
        "repo.product-correspondence",
        "repo.product-manifest",
        "repo.product-spec-base",
        "repo.validation",
        "repo.development-workflow"
      ]
    }
  ],
  "required_content_areas": {
    "authority_and_basis": [
      "repo/docs/plans/validation-correspondence-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "scope_and_exclusions": [
      "repo/docs/plans/validation-correspondence-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "workstreams_and_dependencies": [
      "repo/docs/plans/validation-correspondence-implementation-plan/02-workstreams-and-dependencies.md"
    ],
    "entry_and_exit_conditions": [
      "repo/docs/plans/validation-correspondence-implementation-plan/02-workstreams-and-dependencies.md"
    ],
    "transition_gates": [
      "repo/docs/plans/validation-correspondence-implementation-plan/03-migration-validation-gates-and-completion.md"
    ],
    "validation_strategy": [
      "repo/docs/plans/validation-correspondence-implementation-plan/03-migration-validation-gates-and-completion.md"
    ],
    "risks_and_unresolved_decisions": [
      "repo/docs/plans/validation-correspondence-implementation-plan/04-risks-and-unresolved-planning-decisions.md"
    ],
    "completion_and_successor_work": [
      "repo/docs/plans/validation-correspondence-implementation-plan/03-migration-validation-gates-and-completion.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/plans/validation-correspondence-implementation-plan/01-authority-scope-and-specification-map.md",
      "title": "Authority, scope, and specification map",
      "coverage": [
        "authority_and_basis",
        "scope_and_exclusions"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/plans/validation-correspondence-implementation-plan/02-workstreams-and-dependencies.md",
      "title": "Workstreams and dependencies",
      "coverage": [
        "workstreams_and_dependencies",
        "entry_and_exit_conditions"
      ]
    },
    {
      "order": 3,
      "path": "repo/docs/plans/validation-correspondence-implementation-plan/03-migration-validation-gates-and-completion.md",
      "title": "Migration, validation gates, and completion",
      "coverage": [
        "transition_gates",
        "validation_strategy",
        "completion_and_successor_work"
      ]
    },
    {
      "order": 4,
      "path": "repo/docs/plans/validation-correspondence-implementation-plan/04-risks-and-unresolved-planning-decisions.md",
      "title": "Risks and unresolved planning decisions",
      "coverage": [
        "risks_and_unresolved_decisions"
      ]
    }
  ],
  "successor_action": "This candidate revision does not authorize implementation issues, even if merged. After candidate content is reviewed and merged, #568 must govern a separate explicit acceptance revision that changes this plan's durable lifecycle state to accepted. Only after that accepted revision is manually merged and verified may separately governed repository-generic implementation issues cite VCP-I1 through VCP-I6. Product-owned package population, product-specification correspondence mutation, and product-specific materialization require separately governed product-owned planning and implementation authority with exact applicable accepted product specifications.",
  "schema_version": "1"
}
```

## Planning basis

The accepted validation-correspondence specifications are normative authority. This plan selects and orders implementation mechanics without redefining correspondence semantics.

Accepted planning basis: `main` at `21577021da0187d2310b808079a1ec573ea54b0a`.

The controlling directional predecessors are the approved repository functional set and accepted repository decomposition. The controlling normative requirements are the accepted repository specifications declared in `applicable_accepted_specifications` and each workstream's exact authority set.

This repository-owned plan controls repository-generic realization only. It may define framework-wide product correspondence rules and cross-domain validation behavior, but it does not by itself authorize mutation of product-owned packages, product-specification correspondence declarations, product-specific test artifacts, or product-specific materialization surfaces. Those mutations require separately governed product-owned planning/implementation authority citing exact applicable accepted product specifications.

## Workstreams

| Workstream | Purpose | Primary dependency |
| --- | --- | --- |
| VCP-I1 | Package schema and canonical correspondence-source realization | none |
| VCP-I2 | Source-local role metadata and validation-task identity adaptation | VCP-I1 |
| VCP-I3 | Repository-owned package population framework and product-authority handoff | VCP-I1, VCP-I2 |
| VCP-I4 | Mechanical integrity enforcement and deterministic projections | VCP-I1, VCP-I2, VCP-I3 |
| VCP-I5 | Repository-generic propagation/materialization and freshness/equivalence realization | VCP-I1, VCP-I4 |
| VCP-I6 | Repository-generic migration completion and cross-domain conformance integration | VCP-I1 through VCP-I5 plus required product-owned evidence |

Each workstream's exact controlling accepted repository specifications are declared in `workstream_authority`.

## Execution order

Primary repository-generic order:

`VCP-I1 -> VCP-I2 -> VCP-I3 -> VCP-I4 -> VCP-I5 -> VCP-I6`

Product-owned planning may proceed only after this plan is accepted and only under applicable product lifecycle authority. VCP-I6 cannot claim end-to-end feature completion until required product-owned realization evidence exists.

Parallel repository-generic work is allowed only where a governed implementation issue proves its entry conditions and controlling specification closure without depending on unfinished predecessor state.

## Planning boundary

This plan is specification-complete for repository-generic semantics: the final #561 audit found no remaining material normative corrections. Repository-generic implementation issues may choose exact JSON Schema keywords, source metadata syntax, task-ID naming, validator organization, projection presentation, propagation mechanics, and migration batching only within accepted specification constraints.

This plan intentionally does not choose product-specific implementation mechanics or product-specification authority sets. Those belong to separately governed product-owned planning.

If implementation planning or execution discovers a required semantic decision not already controlled by accepted specifications, the affected workstream blocks and returns that decision to specification governance.

No Atomic transition is pre-authorized. A later governed implementation issue may use Atomic only if `repo.development-workflow` proves the existing no-valid-intermediate eligibility condition for the exact proposed transition.

## Candidate-to-accepted transition

The lifecycle is explicit:

1. review and merge candidate planning content without treating the candidate artifact as accepted authority;
2. keep #568 open;
3. perform a separate bounded acceptance revision that changes the durable status prose and `lifecycle_status` from `candidate` to `accepted`, without changing implementation semantics;
4. validate and manually merge that exact acceptance revision;
5. verify merged `main` and perform a final read-only acceptance audit;
6. only then create successor implementation issues.

## Chunk index

- [Authority, scope, and specification map](./validation-correspondence-implementation-plan/01-authority-scope-and-specification-map.md)
- [Workstreams and dependencies](./validation-correspondence-implementation-plan/02-workstreams-and-dependencies.md)
- [Migration, validation gates, and completion](./validation-correspondence-implementation-plan/03-migration-validation-gates-and-completion.md)
- [Risks and unresolved planning decisions](./validation-correspondence-implementation-plan/04-risks-and-unresolved-planning-decisions.md)

## Relationships

- Feature-request root: #550.
- Governing planning issue: #568.
- Completed normative-specification issue: #561.
- Controlling planning contracts: `repo.implementation-plan`, `repo.development-document-base`, `repo.development-workflow`, and `repo.validation`.
- Controlling decomposition: `repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md`.
- Primary normative implementation authority: `repo.validation-correspondence` plus each workstream-specific accepted repository-specification set.
- Product-specific maintained-artifact realization: separate product-owned planning/implementation authority.

## Next authorized action

Review and merge corrected candidate planning content only. Candidate merge is not plan acceptance and does not authorize implementation. The next action after candidate merge is the explicit acceptance revision governed by #568.

## Discoverability

- [Repository plan root](./README.md)
- [Repository decomposition](../decompositions/REPOSITORY-DECOMPOSITION.md)
- [Repository functional set](../overview/REPOSITORY-FUNCTIONAL-SET.md)
