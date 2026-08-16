# Authority, scope, and specification map

## Purpose

Define the exact authority basis, implementation scope, exclusions, and accepted-specification mapping for the initializer upgrade implementation plan.

## Authority and basis

This plan is product-owned planning authority under `repo.implementation-plan`. It is controlled by the approved initializer-upgrade functional set and accepted initializer-upgrade decomposition. Product semantics remain governed exclusively by accepted product specifications.

The plan does not inherit implementation authority from the historical original initializer plan. Reusable accepted initializer specifications may be cited by an upgrade workstream only where their current accepted semantics already apply.

## Specification-complete scope

The upgrade implementation is specification-complete for the product behavior represented by:

- `product.upgrade-request`
- `product.framework-reconciliation-lineage`
- `product.managed-material-delta`
- `product.upgrade-set-resolution`
- `product.staged-managed-reconciliation`
- `product.framework-reanchoring`
- `product.reconciliation-validation-promotion`
- `product.derived-repository-upgrade`

Reusable accepted initializer specifications are cited per workstream in the controller metadata.

## Implementation-authorized scope after plan acceptance

After the plan completion gate is satisfied, implementation issues may be created only for the UP1-UP5 workstreams and only under their exact controlling specification sets.

## Deferred implementation

The following remain outside this plan unless later accepted authority explicitly adds them:

- remote framework retrieval;
- caller-selected arbitrary framework revisions;
- hosted orchestration;
- generalized automatic conflict resolution;
- automatic rollback or retry after indeterminate promotion;
- release/go-live policy;
- unrelated initializer features.

## Unresolved semantic decisions

This plan does not create missing semantics. If implementation encounters behavior that cannot be determined from accepted specifications, the affected workstream must stop and route the gap back to governed specification work.

## Scope exclusions

This plan does not authorize modification of the original initializer implementation plan, the upgrade functional set, decomposition, accepted product specifications, or repository governance contracts.
