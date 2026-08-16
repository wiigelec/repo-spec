# Upgrade capability boundary and outcome

## Capability boundary

The functional set covers one end-to-end product capability: perform an in-place re-initialization of an existing repository previously derived from repo-spec so its initializer-managed material is reconciled to a later accepted repo-spec framework revision while repository content outside the initializer-managed material universe is preserved.

The public user-facing entry point is:

`repo-spec upgrade --repo <existing-repo>`

The capability begins when an existing derived repository is supplied for upgrade and ends only when either a validated upgraded repository has been promoted and success finalized, or the upgrade terminates without promotion and produces sufficient failure/recovery evidence.

## Included outcome

A successful upgrade leaves the existing repository on a later accepted repo-spec framework state while preserving all repository content outside the initializer-managed material universe.

Upgrade mutation authority is bounded by initializer installation capability: material is eligible for upgrade only when the initializer is capable of installing that managed material into a derived repository. Repository path alone does not establish eligibility.

Within that eligible universe, reconciliation may add, modify, remove, or retarget managed material as the target moves from its currently accepted framework state to the supplying framework state. Current initializer-managed material is concentrated in `repo/` but also includes installed projections, root support, and selected `product/` framework/validation material such as product level-spec schemas.

## End-to-end usability

The user should not need to manually reconstruct a repo-spec diff, identify framework files, or perform an ad hoc migration sequence.

One upgrade command owns the lifecycle from target/source identification through managed selection, staging, validation, promotion, and final outcome reporting.

This chunk does not define exact command output, prompts, exit codes, or error schemas.
