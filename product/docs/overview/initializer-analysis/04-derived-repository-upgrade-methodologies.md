# Derived-repository upgrade methodology analysis

## Considered methodologies

### Raw Git diff application

Rejected as primary methodology because repo-spec history mixes source-only product work, initializer implementation, tests, repository framework, generated references, validation support, and session artifacts.

### Cherry-pick repo-spec commits

Rejected because source and derived repositories have independent histories and source commits may mix distributable and non-distributable material.

### Reinitialize and replace target

Rejected because it would overwrite subsequent product work.

### Blind `repo/` replacement

Insufficient because it does not reconcile managed projections, exceptional validation support, local modifications, framework re-anchoring, or revision-aware deletion.

### Separate hand-maintained upgrade manifest

Not preferred because it duplicates existing initializer inventory knowledge and risks drift.

## Preferred methodology

Use a revision-aware material-key delta plus staged reconstruction of the existing target.

### Phase 1 — resolve identities

Read the target's accepted framework anchor and resolve the exact repo-spec revision supplying the upgrade.

### Phase 2 — reconcile inventories

Load inventories for the old and new repo-spec revisions from Git objects and reconcile by stable `material_key`.

Classify unchanged, changed, added, removed/retired, and destination-retargeted entries.

### Phase 3 — select applicable entries

Apply upgrade eligibility policy and dependency closure.

Normal entries are repository-framework material. Exceptional `product/` entries are validation support unless later authority expands that boundary.

### Phase 4 — seed staging from target

Unlike initialization, upgrade staging starts from the existing target state so the complete prospective repository can be validated before any live replacement.

### Phase 5 — apply managed changes

Apply selected source-side entries while distinguishing managed framework material, user-owned product material, locally modified managed content, and generated/projected outputs.

### Phase 6 — reconcile managed projections

Regenerate or reconcile managed outputs such as `.github/` adapters from their authoritative repository-profile sources.

### Phase 7 — re-anchor framework

Record the new repo-spec framework revision before validation while preserving original initialization provenance and later upgrade history.

### Phase 8 — validate staged repository

Run full repository validation against the prospective upgraded state. Promotion stays closed on failure.

### Phase 9 — promote and finalize

Promote only the validated complete target and emit deterministic recovery/provenance evidence.

## Architectural fit

This methodology reuses exact Git source resolution, stable material keys, output inventory, staging isolation, repository validation, promotion gating, and success finalization. Upgrade becomes a sibling Initializer workflow instead of a parallel migration engine.
