# Migration, validation gates, and completion

## Transition strategy

Migration shall preserve valid accepted revisions.

The preferred strategy is staged:

1. implement subordinate schema/parsing support without activating repository-wide completeness;
2. establish source-local role/task identity metadata;
3. populate canonical packages in valid batches;
4. reconcile product mappings;
5. activate objective enforcement after the governed source population required by that enforcement exists;
6. add propagation/freshness mechanics for actual maintained materialization surfaces;
7. remove obsolete duplicate mappings and enable final end-to-end completeness.

Preparatory/non-active correspondence may be used only where accepted lifecycle authority permits it. The plan does not treat partial active completeness as valid unless controlling specifications explicitly allow that state.

## Atomic checkpoint

Before any increment proposes an Atomic transition, its governing issue must prove all of the following from current accepted authority:

- the exact invariant that makes specification/plan/artifact synchronization inseparable;
- why no valid intermediate accepted revision exists;
- the logical branch order required by `repo.development-workflow`;
- plan impact or reaffirmation for the exact proposed revision.

If a staged inactive/preparatory or otherwise valid intermediate path exists, ordinary governed increments shall be used instead.

## Validation strategy

Every implementation increment shall use the strongest applicable combination of:

- focused schema/package/source metadata tests;
- validation-domain unit/self tests;
- deterministic fixture tests for positive, negative, boundary, and regression behavior where useful;
- `git diff --check`;
- generated-artifact freshness checks;
- `./scripts/validate`;
- exact-head CI;
- post-merge verification against the accepted default branch.

Validation evidence remains subordinate to accepted normative authority.

## Gate G1 — Schema readiness

VCP-I1 may exit only when the dedicated schema is present at the accepted path, structurally faithful to REPO-VC-012, exercised by focused tests, and does not independently define semantics.

## Gate G2 — Source auditability readiness

VCP-I2 may exit only when the selected language mechanism is canonical across applicable validation domains, all migrated callables are classifiable task/helper, and task metadata can be mechanically compared to package records.

## Gate G3 — Population readiness

VCP-I3 may exit only when package ownership and active/historical/preparatory lifecycle are mechanically distinguishable, product mappings no longer duplicate requirement-to-test ownership, and the intended completeness population can be computed deterministically.

## Gate G4 — Enforcement readiness

VCP-I4 may enable active completeness enforcement only when the corresponding accepted-state package population already exists in the same valid revision path or when a separately proven Atomic transition is eligible.

## Gate G5 — Materialization readiness

VCP-I5 may exit only when every actual propagated/materialized surface has deterministic source equivalence and stale/missing/divergent correspondence is detectable without network authority.

## Gate G6 — Feature completion

VCP-I6 may exit only when:

- all active requirements in the accepted completeness domain have exactly one active package;
- all task/package/source invariants pass;
- product mappings agree with canonical packages;
- generated/materialized views are faithful and fresh;
- no obsolete competing correspondence registry remains;
- full repository validation and self-tests pass;
- any required migration/Atomic evidence is complete;
- all successor implementation issues are accepted and merged.

## Plan completion

This plan is complete as a planning artifact when all six workstreams have bounded authority, dependencies, entry/exit conditions, transition gates, validation strategy, unresolved planning decisions, and successor-issue rules sufficient to execute without inventing normative semantics.

Implementation completion is separate from plan acceptance. Acceptance of this plan authorizes creation of governed implementation issues; it does not claim the implementation is already complete.

## Successor issue order

Default issue order is VCP-I1, VCP-I2, VCP-I3, VCP-I4, VCP-I5, VCP-I6.

A successor issue may cover multiple adjacent workstreams only if doing so improves validity/reviewability and its exact controlling specification union and predecessor evidence are explicit.
