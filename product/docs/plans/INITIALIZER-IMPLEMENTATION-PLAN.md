# Initializer Implementation Plan

## Status

Accepted; planning-authoritative; non-normative with respect to product semantics.

This document is non-normative with respect to product semantics. Issue #261
accepted this plan after revalidation against the synchronized accepted specification
set and repository planning contracts. The accepted plan provides planning authority
for governed successor work; it does not itself mutate product artifacts. B0 is the
next eligible governed successor, and I1-I5 remain gated by predecessor evidence and
separate governing issues. Issues #255 and #257 repaired the accepted provenance/handoff
specification conflicts and ordering gap, and issue #259 / PR #260 synchronized and
clean-room reviewed the plan before acceptance.

## Metadata

```json
{
  "artifact_id": "initializer-implementation-plan",
  "artifact_type": "implementation-plan",
  "document_slug": "initializer-implementation-plan",
  "filename_stem": "initializer-implementation-plan",
  "root_path": "product/docs/plans/",
  "title": "Repo-Spec Initializer Implementation Plan",
  "product_id": "repo-spec initializer",
  "authority_category": "planning",
  "lifecycle_status": "accepted",
  "governing_issue": "#243, #253, #255, #257, #259, #261",
  "controlling_documents": [
    "product/docs/overview/INITIALIZER-OVERVIEW.md",
    "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
  ],
  "predecessor_documents": [
    "product/docs/decompositions/INITIALIZER-DECOMPOSITION.md"
  ],
  "evidence": [
    "product/docs/overview/initializer-overview/01-product-identity-and-purpose.md",
    "product/docs/overview/initializer-overview/02-problem-and-outcome.md",
    "product/docs/overview/initializer-overview/03-users-principles-and-boundaries.md",
    "product/docs/overview/initializer-overview/04-capabilities-and-success.md",
    "product/docs/overview/initializer-overview/05-unresolved-questions.md",
    "product/docs/overview/initializer-overview/06-lifecycle-and-handoff.md",
    "product/docs/decompositions/initializer-decomposition/01-invocation-and-authority.md",
    "product/docs/decompositions/initializer-decomposition/02-framework-and-product-foundations.md",
    "product/docs/decompositions/initializer-decomposition/03-platform-and-execution.md",
    "product/docs/decompositions/initializer-decomposition/04-generation-validation-and-handoff.md"
  ],
  "required_content_areas": {
    "authority_and_basis": [
      "product/docs/plans/initializer-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "scope_and_exclusions": [
      "product/docs/plans/initializer-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "workstreams_and_dependencies": [
      "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md"
    ],
    "entry_and_exit_conditions": [
      "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md"
    ],
    "transition_gates": [
      "product/docs/plans/initializer-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "validation_strategy": [
      "product/docs/plans/initializer-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "risks_and_unresolved_decisions": [
      "product/docs/plans/initializer-implementation-plan/04-risks-and-unresolved-decisions.md"
    ],
    "completion_and_successor_work": [
      "product/docs/plans/initializer-implementation-plan/03-validation-gates-and-completion.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "product/docs/plans/initializer-implementation-plan/01-authority-scope-and-specification-map.md",
      "title": "Authority, scope, and specification map",
      "coverage": [
        "authority_and_basis",
        "scope_and_exclusions"
      ]
    },
    {
      "order": 2,
      "path": "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md",
      "title": "Implementation increments and dependencies",
      "coverage": [
        "workstreams_and_dependencies",
        "entry_and_exit_conditions"
      ]
    },
    {
      "order": 3,
      "path": "product/docs/plans/initializer-implementation-plan/03-validation-gates-and-completion.md",
      "title": "Validation, gates, and completion",
      "coverage": [
        "transition_gates",
        "validation_strategy",
        "completion_and_successor_work"
      ]
    },
    {
      "order": 4,
      "path": "product/docs/plans/initializer-implementation-plan/04-risks-and-unresolved-decisions.md",
      "title": "Risks and unresolved decisions",
      "coverage": [
        "risks_and_unresolved_decisions"
      ]
    }
  ],
  "successor_action": "Create a separately governed B0 evidence-classification issue against this accepted plan and the current accepted product specifications. B0 must complete before I1 work may be authorized; I1-I5 remain subject to their predecessor gates and separate governing issues.",
  "schema_version": "1"
}
```

## Planning basis

The accepted initializer product specifications are the normative authority for
future implementation planning. Repository governance and planning contracts
under `repo/` control the structure and lifecycle of this product plan. Product
artifacts may reference repository authority; this patch does not add any
repository-tree reference to product artifacts. The accepted initializer
overview and decomposition remain directional context only.

## Workstreams

The accepted plan defines six bounded increments in a single forward DAG:

| Rank | Increment | Purpose |
| --- | --- | --- |
| 0 | B0 | Existing-implementation conformance baseline across all 291 composite keys |
| 1 | I1 | Request intake, identity handling, source resolution, and destination preflight |
| 2 | I2 | Transactional staging, material realization, foundation seeding, and framework installation |
| 3 | I3 | Provenance, handoff, Git initialization, and repository-state assembly |
| 4 | I4 | Two-phase validation, report finalization, atomic promotion, and cleanup |
| 5 | I5 | End-to-end lifecycle orchestration, terminal outcomes, and whole-workflow conformance |

Issue #255 repaired the accepted provenance and handoff specification conflicts that
previously blocked I3-I5. The B0→I1→I2→I3→I4→I5 dependency order remains
unchanged. Plan acceptance makes B0 the next eligible governed successor; it does
not bypass the B0→I1→I2→I3→I4→I5 gates or the requirement for separate governing
issues before maintained product-artifact mutation.

## Chunk index

- [Authority, scope, and specification map](./initializer-implementation-plan/01-authority-scope-and-specification-map.md)
- [Implementation increments and dependencies](./initializer-implementation-plan/02-increments-and-dependencies.md)
- [Validation, gates, and completion](./initializer-implementation-plan/03-validation-gates-and-completion.md)
- [Risks and unresolved decisions](./initializer-implementation-plan/04-risks-and-unresolved-decisions.md)

## Relationships

- Governing issues: #243 (scaffold creation), #253 (specification mapping,
  increment definition, validation gates, risk register), the accepted
  provenance-conflict planning amendment recorded in issue #253 comment
  `#issuecomment-5222594632`, #255 (accepted provenance/handoff repair and
  plan impact review), #257 (handoff ordering repair and plan impact review),
  #259 (plan synchronization clean-room cycle), and #261 (separately governed plan-acceptance cycle)
- Controlling repository contracts: `repo.development-document-base`,
  `repo.implementation-plan`, `repo.development-workflow`, and applicable
  repository workflow and validation contracts
- Controlling overview: `product/docs/overview/INITIALIZER-OVERVIEW.md`
- Controlling decomposition: `product/docs/decompositions/INITIALIZER-DECOMPOSITION.md`
- Normative product authority: accepted initial-bounded-workflow product
  specifications registered in `product/specs/product/manifest.json`
- Predecessor plan: removed as obsolete by Patch 2 of issue #243; no
  predecessor plan content is incorporated into this scaffold

## Next authorized action

Issue #261 accepted this implementation plan after clean-room revalidation against
current accepted specifications and synchronized planning state. The next authorized
action is a separately governed B0 evidence-classification issue.

B0 must complete before I1 work may be authorized. I1-I5 remain gated by predecessor
evidence and separate governing issues.

## Discoverability

This is the canonical initializer implementation-plan entry point. Its
subordinate chunks are listed above.
