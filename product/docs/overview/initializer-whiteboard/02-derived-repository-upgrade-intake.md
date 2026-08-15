# Derived-repository upgrade intake

## Provenance

This collection chunk records the product feature-request intake from GitHub issue #418.

Original issue title:

`add derived repo upgrade capability`

Original unformatted issue body:

> when repo-spec adds new features, bug fixes, or security enhancements those need to be able to be propagated to previously derived repos.

The user clarified during governed collection that this capability belongs in the product lifecycle rather than the repository/framework lifecycle. Under the current product overview structure, this evidence is recorded in the Repo-Spec Initializer whiteboard.

This material is evidentiary and non-normative. It records requested product direction for later overview analysis and does not itself authorize requirements, decomposition, specifications, implementation planning, implementation, migration, or release behavior.

## Collected input

Repositories initialized from an earlier repo-spec revision should have some future product capability through which later repo-spec changes can be propagated to them.

The stated classes of later repo-spec change are:

- new features;
- bug fixes;
- security enhancements.

No upgrade mechanism, compatibility policy, migration policy, or implementation form was specified by the intake.

## Unresolved intent

The following matters remain unresolved for later product overview analysis:

- what subset of repo-spec changes is eligible for propagation;
- how source and target repo-spec revisions are identified;
- how managed repo-spec material is distinguished from local customization;
- how local modifications and conflicts are handled;
- what compatibility guarantees exist;
- whether feature, bug-fix, and security updates use distinct policies;
- whether upgrades are atomic or staged;
- how generated artifacts participate;
- what validation is required before and after upgrade;
- what rollback, recovery, or partial-upgrade behavior is expected;
- what provenance must be recorded;
- whether upgrade orchestration is local-only or may involve hosted workflows.

These questions are evidence for product analysis, not decisions made by this collection stage.
