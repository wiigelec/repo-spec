# Initializer Upgrade Implementation Plan

## Status

Accepted; planning-authoritative; non-normative with respect to product semantics.

This plan sequences implementation of the accepted Repo-Spec Initializer derived-repository upgrade capability. It does not redefine product behavior, does not itself mutate product artifacts, and does not claim implementation completion.

## Metadata

```json
{
  "artifact_id": "initializer-upgrade-implementation-plan",
  "artifact_type": "implementation-plan",
  "document_slug": "initializer-upgrade-implementation-plan",
  "filename_stem": "initializer-upgrade-implementation-plan",
  "root_path": "product/docs/plans/",
  "title": "Repo-Spec Initializer Upgrade Implementation Plan",
  "product_id": "repo-spec initializer",
  "authority_category": "planning",
  "lifecycle_status": "accepted",
  "governing_issue": "#447",
  "controlling_documents": [
    "product/docs/overview/INITIALIZER-UPGRADE-FUNCTIONAL-SET.md",
    "product/docs/decompositions/INITIALIZER-UPGRADE-DECOMPOSITION.md"
  ],
  "predecessor_documents": [
    "product/docs/decompositions/INITIALIZER-UPGRADE-DECOMPOSITION.md"
  ],
  "evidence": [
    "product/docs/overview/initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md",
    "product/docs/overview/initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md",
    "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
    "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md",
    "product/docs/overview/initializer-upgrade-functional-set/05-boundaries-and-unresolved-direction.md",
    "product/docs/overview/initializer-upgrade-functional-set/06-decomposition-handoff.md",
    "product/docs/decompositions/initializer-upgrade-decomposition/01-request-identity-and-eligibility.md",
    "product/docs/decompositions/initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md",
    "product/docs/decompositions/initializer-upgrade-decomposition/03-staged-application-and-projections.md",
    "product/docs/decompositions/initializer-upgrade-decomposition/04-reanchoring-and-provenance.md",
    "product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"
  ],
  "applicable_accepted_specifications": [
    "product.initializer-level-0",
    "product.upgrade-request",
    "product.framework-reconciliation-lineage",
    "product.provenance-record",
    "product.managed-material-delta",
    "product.upgrade-set-resolution",
    "product.git-object-identity",
    "product.source-revision-identity",
    "product.local-git-repository",
    "product.material-classification",
    "product.material-manifest",
    "product.initializer-output-inventory-v1",
    "product.source-material-resolution",
    "product.staged-managed-reconciliation",
    "product.staging-workspace",
    "product.staging-state",
    "product.framework-reanchoring",
    "product.reconciliation-validation-promotion",
    "product.repository-validation",
    "product.validation-profile",
    "product.validation-report",
    "product.execution-report",
    "product.derived-repository-upgrade"
  ],
  "workstream_authority": [
    {
      "id": "UP1",
      "controlling_product_specifications": [
        "product.initializer-level-0",
        "product.upgrade-request",
        "product.framework-reconciliation-lineage",
        "product.provenance-record",
        "product.managed-material-delta",
        "product.upgrade-set-resolution",
        "product.git-object-identity",
        "product.source-revision-identity",
        "product.local-git-repository",
        "product.material-classification",
        "product.material-manifest",
        "product.initializer-output-inventory-v1",
        "product.source-material-resolution"
      ]
    },
    {
      "id": "UP2",
      "controlling_product_specifications": [
        "product.initializer-level-0",
        "product.managed-material-delta",
        "product.upgrade-set-resolution",
        "product.staged-managed-reconciliation",
        "product.material-manifest",
        "product.initializer-output-inventory-v1",
        "product.staging-workspace",
        "product.staging-state"
      ]
    },
    {
      "id": "UP3",
      "controlling_product_specifications": [
        "product.initializer-level-0",
        "product.framework-reconciliation-lineage",
        "product.staged-managed-reconciliation",
        "product.framework-reanchoring",
        "product.source-revision-identity",
        "product.git-object-identity"
      ]
    },
    {
      "id": "UP4",
      "controlling_product_specifications": [
        "product.initializer-level-0",
        "product.framework-reconciliation-lineage",
        "product.framework-reanchoring",
        "product.reconciliation-validation-promotion",
        "product.repository-validation",
        "product.validation-profile",
        "product.validation-report",
        "product.execution-report"
      ]
    },
    {
      "id": "UP5",
      "controlling_product_specifications": [
        "product.initializer-level-0",
        "product.upgrade-request",
        "product.framework-reconciliation-lineage",
        "product.provenance-record",
        "product.managed-material-delta",
        "product.upgrade-set-resolution",
        "product.staged-managed-reconciliation",
        "product.framework-reanchoring",
        "product.reconciliation-validation-promotion",
        "product.derived-repository-upgrade"
      ]
    }
  ],
  "required_content_areas": {
    "authority_and_basis": [
      "product/docs/plans/initializer-upgrade-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "scope_and_exclusions": [
      "product/docs/plans/initializer-upgrade-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "workstreams_and_dependencies": [
      "product/docs/plans/initializer-upgrade-implementation-plan/02-workstreams-dependencies-and-conditions.md"
    ],
    "entry_and_exit_conditions": [
      "product/docs/plans/initializer-upgrade-implementation-plan/02-workstreams-dependencies-and-conditions.md"
    ],
    "transition_gates": [
      "product/docs/plans/initializer-upgrade-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "validation_strategy": [
      "product/docs/plans/initializer-upgrade-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "completion_and_successor_work": [
      "product/docs/plans/initializer-upgrade-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "risks_and_unresolved_decisions": [
      "product/docs/plans/initializer-upgrade-implementation-plan/04-risks-decisions-and-successor-work.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "product/docs/plans/initializer-upgrade-implementation-plan/01-authority-scope-and-specification-map.md",
      "title": "Authority, scope, and specification map",
      "coverage": [
        "authority_and_basis",
        "scope_and_exclusions"
      ]
    },
    {
      "order": 2,
      "path": "product/docs/plans/initializer-upgrade-implementation-plan/02-workstreams-dependencies-and-conditions.md",
      "title": "Workstreams, dependencies, and conditions",
      "coverage": [
        "workstreams_and_dependencies",
        "entry_and_exit_conditions"
      ]
    },
    {
      "order": 3,
      "path": "product/docs/plans/initializer-upgrade-implementation-plan/03-validation-gates-and-completion.md",
      "title": "Validation, gates, and completion",
      "coverage": [
        "transition_gates",
        "validation_strategy",
        "completion_and_successor_work"
      ]
    },
    {
      "order": 4,
      "path": "product/docs/plans/initializer-upgrade-implementation-plan/04-risks-decisions-and-successor-work.md",
      "title": "Risks, decisions, and successor work",
      "coverage": [
        "risks_and_unresolved_decisions"
      ]
    }
  ],
  "successor_action": "After this plan is accepted and post-merge validated, governed Product-artifact implementation issues may be created for UP1-UP5 only when each issue cites the exact workstream ID(s), accepted implementation-plan authority, applicable accepted product specifications, accepted default-branch base, and predecessor completion evidence required by this plan.",
  "schema_version": "1"
}
```

## Planning basis

The approved initializer-upgrade functional set and accepted initializer-upgrade decomposition provide controlling directional context. The accepted product specifications cited in `applicable_accepted_specifications` and in each `workstream_authority` entry are the normative product authority. This plan coordinates implementation only within those accepted semantics.

This plan was revalidated under governing Issue #449 after the accepted upgrade specifications were corrected for first-reconciliation legacy-lineage bootstrap and for validation/promotion/lineage acceptance atomicity, and was synchronized under governing Issue #451 so the workstream authority and subordinate planning text fully reflect those corrected semantics. Those specification corrections do not alter the UP1-UP5 workstream boundaries or execution order; implementation remains constrained by the current accepted specifications listed in this metadata.

The accepted base for this planning cycle is `0d72ad21d1628d4761dd89d2a931a6589d6090a7`. The historical `INITIALIZER-IMPLEMENTATION-PLAN.md` remains separate authority for the original initializer workflow and is not modified, superseded, or incorporated into this upgrade plan.

## Workstreams

| Workstream | Purpose | Dependency |
| --- | --- | --- |
| UP1 | Request, baseline, and upgrade-set resolution | None |
| UP2 | Staged managed reconciliation | UP1 |
| UP3 | Framework re-anchoring and prospective lineage state | UP2 |
| UP4 | Validation, promotion, and lineage acceptance by commit | UP3 |
| UP5 | End-to-end upgrade orchestration and conformance | UP4 |

Canonical execution order: `UP1 -> UP2 -> UP3 -> UP4 -> UP5`.

## Chunk index

- [Authority, scope, and specification map](./initializer-upgrade-implementation-plan/01-authority-scope-and-specification-map.md)
- [Workstreams, dependencies, and conditions](./initializer-upgrade-implementation-plan/02-workstreams-dependencies-and-conditions.md)
- [Validation, gates, and completion](./initializer-upgrade-implementation-plan/03-validation-gates-and-completion.md)
- [Risks, decisions, and successor work](./initializer-upgrade-implementation-plan/04-risks-decisions-and-successor-work.md)

## Relationships

- Governing issue: #447
- Controlling overview: `product/docs/overview/INITIALIZER-UPGRADE-FUNCTIONAL-SET.md`
- Controlling decomposition: `product/docs/decompositions/INITIALIZER-UPGRADE-DECOMPOSITION.md`
- Normative product authority: the accepted product specifications registered in `product/specs/product/manifest.json` and listed in this plan's workstream metadata
- Predecessor normative-specification acceptance: Issue #445 / PR #446
- Historical original initializer plan: `product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md` remains unchanged and distinct

## Next authorized action

After this plan is accepted, manually merged, and post-merge validated, successor governed Product-artifact implementation issues may be created for UP1-UP5. No runtime implementation is authorized merely by drafting or reviewing this plan.

## Discoverability

This is the canonical initializer-upgrade implementation-plan entry point. Its subordinate chunks are listed in the Chunk index above, and the plan-root `README.md` links this controller alongside the separate historical initializer implementation plan. The UP1-UP5 Workstreams summary and machine-readable `workstream_authority` metadata define the canonical planning index for successor governed implementation work.
