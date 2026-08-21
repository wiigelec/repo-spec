# Migration, validation gates, and completion

## Transition strategy

Migration shall preserve valid accepted revisions and the repository/product authority boundary.

The preferred repository-generic strategy is staged:

1. implement subordinate schema/parsing support without activating repository-wide completeness;
2. establish repository-generic source-local role/task identity mechanics;
3. populate canonical repository-owned packages in valid batches;
4. establish deterministic product-obligation discovery and handoff without product-owned mutation;
5. activate objective repository-scope enforcement after required repository-owned sources exist;
6. add repository/framework-owned propagation/freshness mechanics;
7. consume separately accepted product-owned realization evidence;
8. remove obsolete repository-owned duplicate mappings and enable final aggregate completeness only after both authority domains are ready.

Preparatory/non-active correspondence may be used only where accepted lifecycle authority permits it. The plan does not treat partial aggregate active completeness as valid unless controlling authority explicitly allows that state.

## Accepted-plan gate

This revision records `lifecycle_status: accepted` and is the explicit acceptance transition required by #568.

Before any implementation issue exists:

- this exact acceptance revision is validated, reviewed, and manually merged;
- merged `main` is verified;
- #568 remains open until a final read-only plan-acceptance audit confirms no unresolved authority gap;
- only after that final audit may #568 close and successor implementation issues be created.

## Product-authority gate

Before product-owned package population, product-spec correspondence mutation, product-specific validation-source mutation, or product-specific materialization occurs, separately governed product-owned planning/implementation authority must identify the exact applicable accepted product specifications.

Repository-generic VCP work may discover obligations and validate common invariants but may not substitute repository-only workstream authority for product-owned artifact mutation.

## Atomic checkpoint

Before any increment proposes an Atomic transition, its governing issue must prove:

- the exact invariant that makes the transition inseparable;
- why no valid intermediate accepted revision exists;
- the logical branch order required by `repo.development-workflow`;
- required plan impact/reaffirmation for the exact proposed revision.

If a staged inactive/preparatory or otherwise valid intermediate path exists, ordinary governed increments shall be used.

## Validation strategy

Every implementation increment shall use the strongest applicable combination of:

- focused schema/package/source metadata tests;
- validation-domain unit/self tests;
- deterministic fixture tests for positive, negative, boundary, and regression behavior where useful;
- product-authority evidence checks when aggregate completeness depends on product-owned work;
- `git diff --check`;
- generated-artifact freshness checks;
- `./scripts/validate`;
- exact-head CI;
- post-merge verification against the accepted default branch.

Validation evidence remains subordinate to accepted normative authority.

## Gate G1 — Schema readiness

VCP-I1 may exit only when the dedicated schema is present at the accepted path, structurally faithful to REPO-VC-012, exercised by focused tests, and does not independently define semantics.

## Gate G2 — Source auditability readiness

VCP-I2 may exit only when the selected repository-generic language mechanism is canonical across applicable framework-maintained validation domains and task metadata can be mechanically reconciled with canonical packages.

## Gate G3 — Repository population and product handoff readiness

VCP-I3 may exit only when repository-owned package ownership/lifecycle is mechanically distinguishable, repository-owned active population is complete for its selected scope, product-owned obligations are deterministically enumerable, and product-specific mutation is handed off rather than performed under repository-only authority.

## Gate G4 — Enforcement readiness

VCP-I4 may enable only those completeness/enforcement scopes whose required canonical package populations validly exist. Aggregate completeness across product-owned requirements remains disabled until accepted product-owned realization evidence exists.

## Gate G5 — Framework materialization readiness

VCP-I5 may exit only when every actual repository/framework-owned propagated/materialized surface has deterministic source equivalence and stale/missing/divergent correspondence is detectable. Product-specific surfaces remain outside this workstream's mutation authority.

## Gate G6 — Feature completion

VCP-I6 may exit only when:

- all active repository requirements in the accepted completeness domain have exactly one active package;
- required separately governed product-owned package/correspondence realization is accepted and present;
- all task/package/source invariants pass;
- product mappings agree with canonical packages;
- generated/materialized views are faithful and fresh;
- no obsolete competing correspondence registry remains;
- full repository validation and self-tests pass;
- any required migration/Atomic evidence is complete;
- all required repository-owned and product-owned successor implementation work is accepted and merged.

## Plan completion and acceptance

The plan content is complete: all workstreams have bounded authority, dependencies, entry/exit conditions, transition gates, validation strategy, unresolved planning decisions, product-authority handoff rules, and successor-issue boundaries sufficient to execute without inventing normative semantics.

This revision records the plan as accepted. Accepted planning authority becomes effective only after this exact revision is manually merged and verified and the final read-only acceptance audit passes.

Implementation completion remains separate from plan acceptance.

## Successor issue order

Default repository-generic issue order is VCP-I1, VCP-I2, VCP-I3, VCP-I4, VCP-I5, VCP-I6.

Product-owned planning/implementation proceeds separately under applicable product authority and must deliver accepted evidence before VCP-I6 may claim aggregate completion.
