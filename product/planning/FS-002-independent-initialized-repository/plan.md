# FS-002 Plan — Independent Initialized Repository

## Technical Objective

Replace supplier-history fetch/checkout materialization with direct copying of the maintained installed-framework/root surfaces from the verified clean supplying checkout, followed by fresh target `git init`, one bootstrap commit, and repository-wide Validation.

## Installed Material

Copy the reusable framework and repository-root operational surfaces required by the installed framework. Do not copy initializer Product state. Remove `repo/planning/` from the installed framework snapshot. Preserve `repo/validation/framework-source.json` with the exact supplying revision.

## Git Bootstrap

The target shall contain a fresh `main` history with exactly one initialization commit and no supplier commit objects or ancestry required for ordinary operation.

## Validation

The initialized result shall validate through `scripts/validate`. Product regressions shall prove independent root history, absence of `repo/planning/`, exact source record retention, supplier-object absence, and continued validation after the source checkout is removed.

## Compatibility

Preserve the accepted-source check, clean-source requirement, destination safety, generic target Product seed, controlled pre-merge test seam, and existing CLI surface.

## Complexity Boundary

Use ordinary filesystem copy and Git initialization only. Do not introduce archive plumbing, object filtering, shallow-history tricks, grafts, replace refs, bundles, or generalized provenance machinery.
