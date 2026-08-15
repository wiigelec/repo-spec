# Derived-repository upgrade decomposition handoff

## Analysis conclusion

The architecture audit supports one primary capability:

**Upgrade an existing repo-spec-derived repository from its currently accepted framework revision to a later repo-spec revision without overwriting subsequent product-owned work, and promote the result only after staged validation succeeds.**

Public invocation:

`repo-spec upgrade --repo <existing-repo>`

## Candidate decomposition boundaries

These are analysis-derived boundaries for later decomposition ingestion after functional-set approval.

### U1 — Upgrade request and target preflight

Command intake, target recognition, safety preconditions, and current framework-anchor resolution.

### U2 — Source revision and upgrade inventory resolution

Exact supplying revision, source-side manifest loading, inventory reconciliation, delta classification, applicable-entry selection, and dependency closure.

### U3 — Existing-repository staging

Protected staging, reproduction of current target into the candidate, transaction separation, and deterministic candidate identity.

### U4 — Managed framework application

Normal `repo/` updates, exceptional validation-focused `product/` updates, added/changed/removed entries, local modification detection, and conflict surfacing.

### U5 — Managed projection reconciliation

Reconcile repository-owned outputs outside `repo/`, including `.github/` adapters.

### U6 — Framework re-anchoring and provenance

Preserve original initialization provenance, record the new accepted framework revision, and expose the anchor required by validation.

### U7 — Staged validation gate

Validate the prospective repository and framework anchor/content correspondence. Close promotion on failure.

### U8 — Promotion, failure, and finalization

Transactional promotion of the existing repository, recovery evidence, indeterminate-promotion handling, cleanup, and final reporting.

## Cross-cutting concerns

Compatibility, local customization, source/target identity, manifest evolution, security policy, managed versus product-owned material, deterministic provenance, rollback/recovery, and generated/projected outputs.

## Recommended functional-set shape

Use one end-to-end functional set containing U1-U8. Narrower identity-only or application-only alternatives do not independently satisfy the original request.

## Required gate before decomposition

This chunk is formatted for decomposition ingestion but does not authorize decomposition by itself.

The next lifecycle action is to form/update the candidate Repo-Spec Initializer functional set from this analysis, obtain explicit user approval, and only then create the product decomposition using these boundaries as predecessor evidence.
