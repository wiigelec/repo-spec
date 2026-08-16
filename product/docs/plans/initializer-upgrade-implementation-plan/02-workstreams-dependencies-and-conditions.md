# Workstreams, dependencies, and conditions

## Purpose

Define implementation sequencing, entry conditions, exit conditions, and predecessor evidence for UP1 through UP5.

## Dependency order

`UP1 -> UP2 -> UP3 -> UP4 -> UP5`

No later workstream may claim completion before its predecessor exit evidence exists and the successor entry conditions are satisfied.

## UP1 — Request, baseline, and upgrade-set resolution

### Entry conditions

- this implementation plan is accepted and post-merge validated;
- governing implementation issue cites `UP1`;
- accepted product specifications required by UP1 remain accepted and unchanged or the plan is revalidated;
- target implementation work is based on an accepted default-branch revision recorded by the issue.

### Implementation scope

Implement request handling, target repository identification, accepted-lineage resolution, active-baseline selection, supplying local repo-spec identity, baseline/target initialization inventory resolution, managed-material delta classification, and source-owned upgrade qualification.

### Exit conditions

- focused conformance tests cover accepted UP1 requirements;
- deterministic evidence identifies baseline revision, reconciliation-target revision, inventory endpoints, material-key comparison results, qualification decisions, and legal reconciliation set;
- ambiguity or invalid authority fails closed before staged mutation;
- no UP2 mutation is required to demonstrate UP1 completion.

## UP2 — Staged managed reconciliation

### Entry conditions

- UP1 exit evidence is complete;
- legal reconciliation set is deterministic and accepted by the UP2 implementation issue as predecessor evidence;
- unresolved target-local managed conflicts are represented according to accepted fail/defer semantics.

### Implementation scope

Create isolated staged target state, apply only selected initializer-managed changes, preserve content outside managed authority, reconcile managed projections, and expose conflicts without silent overwrite.

### Exit conditions

- staged state contains only authorized managed changes plus preserved target content;
- unmanaged/product-owned content preservation is demonstrated;
- add/modify/remove/retarget operations are covered;
- unresolved managed-state conflicts produce non-destructive failure/defer evidence;
- staged output is ready for re-anchoring.

## UP3 — Framework re-anchoring and lineage candidate

### Entry conditions

- UP2 exit evidence identifies a coherent staged managed state;
- target accepted lineage and supplying framework identity are resolvable.

### Implementation scope

Write the candidate framework anchor and candidate lineage evidence while preserving original initialization and every prior accepted reconciliation identity.

### Exit conditions

- staged candidate resolves to the exact supplying framework revision;
- accepted historical lineage is preserved;
- target revision is still candidate-only before promotion;
- complete staged validation can evaluate the candidate framework state.

## UP4 — Validation, promotion, and accepted-lineage commit

### Entry conditions

- UP3 exit evidence proves re-anchored staged candidate state;
- required validation profile and reporting surfaces are available;
- no unresolved managed-state conflict remains.

### Implementation scope

Run complete staged repository validation, enforce promotion gating, commit promotion, update accepted lineage only after promotion, and preserve deterministic terminal evidence.

### Exit conditions

- validation failure prevents promotion;
- successful promotion yields exactly one new accepted lineage entry;
- failed/non-promoted attempts leave accepted lineage unchanged;
- terminal evidence distinguishes promoted success, rejection/failure, indeterminate promotion, and promoted-with-finalization-error where technically applicable;
- resulting repository is suitable for UP5 end-to-end orchestration.

## UP5 — End-to-end upgrade orchestration and conformance

### Entry conditions

- UP1-UP4 focused implementation and exit evidence are complete;
- the complete accepted Level-3 workflow remains unchanged or this plan has been revalidated.

### Implementation scope

Compose the public local upgrade operation and all lower-level responsibilities into one end-to-end lifecycle.

### Exit conditions

- `repo-spec upgrade --repo <existing-repo>` or accepted equivalent drives the complete lifecycle;
- end-to-end conformance covers initial reconciliation and at least one subsequent reconciliation using the latest accepted lineage entry as baseline;
- success, rejection, pre-promotion failure, and non-promotion lineage invariants are covered;
- whole-workflow evidence maps implementation/tests back to accepted product requirements;
- no known blocker remains for the accepted local upgrade capability.
