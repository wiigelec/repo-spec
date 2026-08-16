# Upgrade capability boundary and outcome

## Capability boundary

The functional set covers one end-to-end product capability: upgrade an existing repository previously derived from repo-spec to a later accepted repo-spec framework revision without overwriting subsequent product-owned work.

The public user-facing entry point is:

`repo-spec upgrade --repo <existing-repo>`

The capability begins when an existing derived repository is supplied for upgrade and ends only when either a validated upgraded repository has been promoted and success finalized, or the upgrade terminates without promotion and produces sufficient failure/recovery evidence.

## Included outcome

A successful upgrade leaves the existing repository on a later accepted repo-spec framework state while preserving repository-local product development outside the managed upgrade boundary.

The upgrade is repository-first. Its normal managed scope is the target repository's `repo/` framework tree.

The capability may also propagate explicitly managed support outside `repo/` where repository framework behavior projects into installed surfaces, and may exceptionally propagate validation-focused `product/` framework support.

## End-to-end usability

The user should not need to manually reconstruct a repo-spec diff, identify framework files, or perform an ad hoc migration sequence.

One upgrade command owns the lifecycle from target/source identification through managed selection, staging, validation, promotion, and final outcome reporting.

This chunk does not define exact command output, prompts, exit codes, or error schemas.
