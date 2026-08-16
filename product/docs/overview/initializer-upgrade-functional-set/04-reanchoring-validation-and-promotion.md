# Re-anchoring, validation, and promotion

## Framework re-anchoring

A staged upgraded repository must be re-anchored to the repo-spec revision that supplies the accepted upgraded framework before repository validation.

This replaces the assumption that the original repository root commit is the permanent framework baseline.

Original initialization provenance remains preserved while the repository gains a current accepted framework identity suitable for later upgrades and validation.

## Staged validation gate

The complete prospective repository is validated while still staged.

Validation covers the upgraded repository framework, managed projections, and exceptional product-validation support when included.

Promotion is not available unless staged repository validation succeeds.

## Promotion and finalization

After successful validation, the upgrade lifecycle promotes the complete prospective result and then finalizes success.

The capability includes deterministic failure and recovery evidence when promotion does not complete normally.

Exact anchor artifact, digest model, transactional replacement mechanism, rollback guarantees, and indeterminate-promotion recovery mechanics remain later specification concerns.
