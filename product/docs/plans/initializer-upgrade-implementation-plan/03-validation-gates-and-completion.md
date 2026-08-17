# Validation, gates, and completion

## Purpose

Define transition gates, validation strategy, implementation-completion evidence, and successor authorization boundaries.

## Transition gates

### Plan acceptance gate

No UP1-UP5 Product-artifact implementation issue is authorized until this plan is accepted, merged, and post-merge validated.

### UP1 -> UP2

Requires deterministic accepted baseline/target inventory endpoint evidence, exact repository-local accepted-lineage authority when governed by the transportable representation, exact legacy authority/backfill eligibility when applicable, and a legal reconciliation set. Ambiguous, missing, unanchored, or unresolvable authority/identity or invalid qualification blocks transition.

### UP2 -> UP3

Requires isolated staged managed reconciliation with unmanaged-content preservation and no silently overwritten unresolved managed conflict.

### UP3 -> UP4

Requires the prospective framework anchor and reconciliation-target lineage entry to be present in the staged repository in the exact serialized form intended for acceptance, while preserving accepted history, together with the prospective target framework-authority bundle and any required exact historical backfill anchored to their lineage Git identities; the prospective lineage/authority state remains non-accepted until promotion commits the validated state.

### UP4 -> UP5

Requires focused validation/promotion conformance, deterministic accepted-lineage and accepted framework-authority behavior, and proof that the promoted repository can perform routine framework-managed integrity validation from committed repository-local authority without the originating repo-spec checkout or remote retrieval.

### Completion gate

UP5 may be considered complete only when focused UP1-UP4 evidence and whole-workflow conformance all pass against the exact accepted implementation revision.

## Validation strategy

Each implementation issue shall run repository-required validation plus focused tests for its controlling product-spec requirements. Validation evidence must identify the exact revision tested.

At minimum, whole-upgrade conformance shall cover:

- valid existing initialized target request;
- invalid/non-initialized target rejection;
- clean supplying framework revision resolution;
- accepted-lineage baseline resolution through exact repository-local framework-authority evidence when governed by the transportable representation or, for the first reconciliation of a lineage-predating target, valid `product.provenance-record` bootstrap of the exact original framework/inventory authority plus exact locally resolvable historical backfill eligibility;
- invalid, incomplete, ambiguous, unanchored, tampered, or unresolvable accepted/legacy authority or provenance fails closed without guessing;
- baseline and reconciliation-target inventory endpoint resolution;
- unchanged/add/modify/remove/retarget managed-material classification;
- source-owned qualification that constrains but does not expand authority;
- unmanaged/product-owned preservation;
- local managed conflict fail/defer behavior;
- prospective re-anchoring and reconciliation-target lineage entry serialized in final intended form before complete validation;
- prospective target framework-authority bundle and any required exact historical backfill are materialized deterministically and cryptographically anchored before complete validation;
- complete staged validation verifies required framework-authority Git objects by repository-local identity traversal and rejects missing, incomplete, inconsistent, unanchored, or tampered authority;
- required validation failure prevents promotion;
- successful promotion commits the exact validated lineage-and-framework-authority staged state and thereby makes exactly one prospective reconciliation-target lineage entry and its required authority accepted, without a separate post-promotion maintained-repository lineage/authority mutation;
- failed/non-promoted attempts do not advance lineage or accepted framework-authority state;
- a promoted repository performs routine framework-managed integrity validation after the originating repo-spec checkout is unavailable and without remote retrieval;
- second successful reconciliation uses the latest accepted lineage revision and repository-local framework-authority bundle as baseline.

## Completion evidence

Each UP workstream should produce maintained implementation/test correspondence and issue/PR validation evidence sufficient to audit requirement coverage. The exact evidence artifact paths may be chosen by the governed implementation issue when not already prescribed by accepted contracts.

## Successor work

Completion of a workstream authorizes only its declared successor dependency in this plan. Completion of UP5 establishes implementation completion evidence for the accepted local upgrade capability but does not itself declare release, deployment, or go-live.
