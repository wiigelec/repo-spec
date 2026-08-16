# Boundaries and unresolved direction

## Exclusions

This functional set does not establish exact upgrade-manifest schema, source/target revision-range rules, compatibility policy, local-modification conflict behavior, security-update policy, framework-anchor storage format, upgrade-history format, projection-generation mechanism, promotion/rollback algorithm, CLI diagnostics, machine-readable result schema, hosted orchestration semantics, or release readiness.

It does not authorize arbitrary replacement of product-owned content.

It does not convert repo-spec source history into a raw Git-patch migration contract.

## Preserved unresolved direction

Later decomposition and specification must retain explicit treatment of compatibility and skipped revisions, managed-entry dependency closure, removal/retirement/rename behavior, target-local modifications, provenance/current framework anchoring, exceptional product-validation eligibility, managed projections outside `repo/`, failure/rollback/indeterminate promotion, and security-sensitive update behavior.

These questions are intentionally not silently resolved by candidate functional-set formation.
