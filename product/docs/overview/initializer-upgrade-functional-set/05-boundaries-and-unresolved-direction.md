# Boundaries and unresolved direction

## Exclusions

This functional set does not establish exact upgrade-manifest schema, source/target revision-range rules, compatibility policy, local-modification conflict behavior, security-update policy, framework-anchor storage format, upgrade-history format, projection-generation mechanism, promotion/rollback algorithm, CLI diagnostics, machine-readable result schema, hosted orchestration semantics, or release readiness.

It does not authorize mutation of any material outside the initializer-managed material universe, regardless of whether that material exists in repo-spec or happens to reside beside managed material in the target repository.

It does not convert repo-spec source history into a raw Git-patch migration contract.

## Preserved unresolved direction

Later decomposition and specification must retain explicit treatment of compatibility and skipped revisions, initializer-managed eligibility, managed-entry dependency closure, add/modify/remove/retarget reconciliation, target-local modifications, provenance/current framework anchoring, installed product-framework eligibility, managed projections outside `repo/`, failure/rollback/indeterminate promotion, and security-sensitive update behavior.

These questions are intentionally not silently resolved by candidate functional-set formation.
