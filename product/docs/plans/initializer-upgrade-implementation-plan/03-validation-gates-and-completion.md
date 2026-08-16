# Validation, gates, and completion

## Purpose

Define transition gates, validation strategy, implementation-completion evidence, and successor authorization boundaries.

## Transition gates

### Plan acceptance gate

No UP1-UP5 Product-artifact implementation issue is authorized until this plan is accepted, merged, and post-merge validated.

### UP1 -> UP2

Requires deterministic accepted baseline/target inventory endpoint evidence and a legal reconciliation set. Ambiguous identity or invalid qualification blocks transition.

### UP2 -> UP3

Requires isolated staged managed reconciliation with unmanaged-content preservation and no silently overwritten unresolved managed conflict.

### UP3 -> UP4

Requires candidate re-anchor and lineage evidence that preserve accepted history while keeping the target revision non-accepted before promotion.

### UP4 -> UP5

Requires focused validation/promotion conformance and deterministic accepted-lineage behavior.

### Completion gate

UP5 may be considered complete only when focused UP1-UP4 evidence and whole-workflow conformance all pass against the exact accepted implementation revision.

## Validation strategy

Each implementation issue shall run repository-required validation plus focused tests for its controlling product-spec requirements. Validation evidence must identify the exact revision tested.

At minimum, whole-upgrade conformance shall cover:

- valid existing initialized target request;
- invalid/non-initialized target rejection;
- clean supplying framework revision resolution;
- baseline and reconciliation-target inventory endpoint resolution;
- unchanged/add/modify/remove/retarget managed-material classification;
- source-owned qualification that constrains but does not expand authority;
- unmanaged/product-owned preservation;
- local managed conflict fail/defer behavior;
- candidate re-anchoring before complete validation;
- required validation failure prevents promotion;
- successful promotion appends exactly one accepted lineage entry;
- failed/non-promoted attempts do not advance lineage;
- second successful reconciliation uses the latest accepted lineage revision as baseline.

## Completion evidence

Each UP workstream should produce maintained implementation/test correspondence and issue/PR validation evidence sufficient to audit requirement coverage. The exact evidence artifact paths may be chosen by the governed implementation issue when not already prescribed by accepted contracts.

## Successor work

Completion of a workstream authorizes only its declared successor dependency in this plan. Completion of UP5 establishes implementation completion evidence for the accepted local upgrade capability but does not itself declare release, deployment, or go-live.
