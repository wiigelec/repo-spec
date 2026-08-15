# Derived-repository upgrade intake

## Provenance

This collection chunk records the feature-request intake from GitHub issue #418.

Original issue title:

`add derived repo upgrade capability`

Original unformatted issue body:

> when repo-spec adds new features, bug fixes, or security enhancements those need to be able to be propagated to previously derived repos.

The intake was classified `feature-request` and promoted in place to governed whiteboard-collection work after preserving the original issue content in the issue conversation.

This material is evidentiary and non-normative. It records requested repository/framework direction for later overview analysis and does not itself authorize requirements, decomposition, specifications, implementation planning, implementation, migration, or release behavior.

## Collected input

Repositories initialized from an earlier repo-spec revision should have some future capability through which later repo-spec changes can be propagated to them.

The stated classes of later repo-spec change are:

- new features;
- bug fixes;
- security enhancements.

The requested relationship is between a later repo-spec state and repositories that were previously derived from repo-spec.

No mechanism, compatibility policy, migration policy, or implementation form was specified by the intake.

## Unresolved intent

The following matters are deliberately unresolved and retained for later overview analysis:

- what subset of repo-spec changes should be eligible for propagation into an existing derived repository;
- how an existing derived repository identifies the repo-spec revision or framework state from which it originated;
- how a desired target repo-spec revision or framework state should be selected;
- how upgrades should distinguish framework-owned material from product-owned or repository-local customization;
- whether local modifications to framework-managed paths may be preserved, merged, rejected, or require explicit user resolution;
- what compatibility guarantees, if any, exist across repo-spec revisions;
- whether feature, bug-fix, and security changes use the same upgrade policy or different urgency and compatibility rules;
- whether an upgrade is atomic or may be staged;
- how generated artifacts and inventories participate in an upgrade;
- what validation is required before and after an upgrade;
- what failure, rollback, recovery, or partial-upgrade behavior is expected;
- whether upgrade provenance must record both source and target repo-spec identities;
- whether upgrades are initiated only locally or may also be proposed or coordinated through hosted repository workflows.

These questions are evidence for analysis, not decisions made by this collection stage.
