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

Implement request handling, target repository identification, accepted-lineage resolution, and active-baseline selection. For accepted lineage governed by `product.transportable-framework-authority`, resolve the active baseline and its initialization inventory/source authority from the exact repository-local framework-authority evidence anchored to the recorded lineage identity. For the first reconciliation of a target that predates accepted lineage representation, establish the exact original framework baseline only from valid, unambiguous `product.provenance-record` evidence with resolvable initialization inventory authority, and determine exact locally resolvable historical authority/backfill eligibility without guessing; invalid, incomplete, ambiguous, or unresolvable provenance/inventory/authority evidence fails closed before staged mutation. Then resolve the supplying local repo-spec identity, baseline/target initialization inventories, managed-material delta classification, and source-owned upgrade qualification. UP1 resolves authority and eligibility only; it does not materialize bundles or broaden mutation authority.

### Exit conditions

- focused conformance tests cover accepted UP1 requirements;
- deterministic evidence identifies baseline revision, reconciliation-target revision, inventory endpoints, material-key comparison results, qualification decisions, and legal reconciliation set;
- accepted-lineage baseline authority resolves through the exact required repository-local framework-authority evidence when governed by the transportable representation;
- first-reconciliation legacy provenance resolves the exact original framework/inventory authority and exact local historical backfill eligibility, or fails closed without guessing before staged mutation;
- no framework-authority bundle materialization and no UP2 mutation is required to demonstrate UP1 completion.

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

## UP3 — Framework re-anchoring and prospective lineage state

### Entry conditions

- UP2 exit evidence identifies a coherent staged managed state;
- target accepted lineage and supplying framework identity are resolvable.

### Implementation scope

Write the prospective framework anchor and reconciliation-target lineage entry into the staged repository in the exact serialized form intended for the prospective accepted repository, while preserving original initialization and every prior accepted reconciliation identity. Materialize the prospective reconciliation-target repository-local framework-authority bundle and any exact historical bundle backfill required for accepted lineage portability, anchored to the corresponding exact lineage Git identities. Presence in staging remains prospective rather than accepted until promotion commits that exact validated state.

### Exit conditions

- staged candidate resolves to the exact supplying framework revision;
- accepted historical lineage is preserved;
- the reconciliation-target lineage entry is present in staging in its final serialized form but remains prospective/non-accepted before promotion;
- the prospective target framework-authority bundle and any required exact historical backfill are present, deterministically represented, and anchored to their exact lineage Git identities;
- complete staged validation can evaluate the candidate framework state using the staged repository-local authority.

## UP4 — Validation, promotion, and lineage acceptance by commit

### Entry conditions

- UP3 exit evidence proves re-anchored staged candidate state;
- required validation profile and reporting surfaces are available;
- no unresolved managed-state conflict remains.

### Implementation scope

Run complete staged repository validation over the lineage-bearing prospective repository state, including repository-local Git-object traversal that verifies all required transportable framework-authority evidence and fails closed on missing, incomplete, unanchored, inconsistent, or tampered authority. Enforce promotion gating, commit that exact validated staged lineage-and-authority state, and preserve deterministic terminal evidence. The prospective reconciliation-target lineage entry and its validated framework-authority state become accepted together by virtue of the committed promotion; UP4 shall not perform a separate post-promotion maintained-repository lineage or authority rewrite to establish acceptance.

### Exit conditions

- validation failure prevents promotion;
- successful promotion commits the exact validated lineage-and-framework-authority staged state, causing exactly one prospective reconciliation-target lineage entry and its required local authority to become accepted without a later maintained-repository lineage/authority mutation;
- the promoted repository can perform routine framework-managed integrity validation from committed lineage and repository-local framework-authority evidence without the originating repo-spec checkout or remote retrieval;
- failed/non-promoted attempts leave accepted lineage and accepted framework-authority state unchanged;
- terminal evidence distinguishes promoted success, rejection/failure, indeterminate promotion, and promoted-with-finalization-error where technically applicable;
- resulting repository is suitable for UP5 end-to-end orchestration.

## UP5 — End-to-end upgrade orchestration and conformance

### Entry conditions

- UP1-UP4 focused implementation and exit evidence are complete;
- the complete accepted Level-3 workflow remains unchanged or this plan has been revalidated.

### Implementation scope

Compose the public local upgrade operation and all lower-level responsibilities into one end-to-end lifecycle, including repository-local framework-authority production, exact authorized legacy backfill, complete local-object validation, promotion, and transported-repository validation.

### Exit conditions

- `repo-spec upgrade --repo <existing-repo>` or accepted equivalent drives the complete lifecycle;
- end-to-end conformance covers a first reconciliation of a lineage-predating target using valid legacy provenance bootstrap plus exact locally resolvable authority backfill, fail-closed invalid/ambiguous/unresolvable legacy provenance or authority, and at least one subsequent reconciliation using the latest accepted lineage entry and repository-local framework-authority bundle as baseline;
- promoted-repository conformance demonstrates routine framework-managed integrity validation after the originating repo-spec checkout is unavailable and without remote retrieval;
- success, rejection, pre-promotion failure, non-promotion lineage, and non-promotion framework-authority invariants are covered;
- whole-workflow evidence maps implementation/tests back to accepted product requirements;
- no known blocker remains for the accepted local upgrade capability.
