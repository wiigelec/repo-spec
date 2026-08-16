# Initializer Upgrade Decomposition: Request, Identity, and Eligibility

> Part 1 of 5 · [Initializer upgrade decomposition index](../INITIALIZER-UPGRADE-DECOMPOSITION.md) · [Next](./02-managed-material-delta-and-reconciliation.md)

## Status

Directional decomposition content.

## Purpose

Bound the upgrade request and establish the identities and eligibility facts needed before any initializer-managed material can be selected for reconciliation.

## Responsibilities

Identify the requested target repository, the target's currently accepted framework identity, the supplying repo-spec framework revision, and whether the target is eligible for the initializer upgrade lifecycle.

Separate explicit request input from facts resolved from durable repository state or the supplying framework. Preserve uncertainty when exact eligibility, revision compatibility, or provenance evidence is not yet normatively defined.

## Boundaries

This area covers the public upgrade-request boundary, source and target framework identity, target preflight, existing initialization/provenance evidence needed to recognize an initialized target, and the boundary between initializer-managed authority and unrelated target content.

It establishes facts needed by later areas but does not decide the exact schema, compatibility algorithm, or conflict policy used to resolve those facts.

## Dependencies

This area depends on the approved upgrade functional set and accepted existing initializer identity/provenance concepts where later normative review determines they are reusable.

Downstream managed-material reconciliation depends on the identities and eligibility outcome established here.

## Exclusions

This area does not compute a managed-material delta, mutate the target, stage changes, re-anchor framework state, validate a staged repository, or promote an upgrade.

It does not define exact revision-range semantics, compatibility policy, security policy, request schema, or CLI result schema.

## Unresolved decisions

Exact target-eligibility rules, supported source/target revision relationships, treatment of incomplete or stale historical provenance, security-sensitive eligibility constraints, and the exact public request/result contract remain for normative specification work.

Whether existing accepted initializer identity/request specifications can be reused unchanged, require revision, or need upgrade-specific companions also remains open.

## Successor work

Normative specification work should define the independently meaningful request, identity, provenance, and eligibility concepts needed by the upgrade lifecycle and then hand the resolved identities to managed-material delta and reconciliation.
