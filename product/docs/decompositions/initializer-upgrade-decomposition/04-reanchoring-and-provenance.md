# Initializer Upgrade Decomposition: Re-Anchoring and Provenance

> Part 4 of 5 · [Initializer upgrade decomposition index](../INITIALIZER-UPGRADE-DECOMPOSITION.md) · [Previous](./03-staged-application-and-projections.md) · [Next](./05-validation-promotion-and-outcomes.md)

## Status

Directional decomposition content.

## Purpose

Bound the transition from the target's prior accepted framework identity to the supplying framework identity while preserving historical initialization and upgrade provenance.

## Responsibilities

Represent the staged repository's intended new accepted framework anchor, preserve evidence of the original initialization relationship and relevant prior accepted framework state, and record enough upgrade provenance for later validation and future upgrade eligibility.

Ensure re-anchoring occurs before validation so validation evaluates the staged repository in the framework state it would claim after successful promotion.

## Boundaries

This area covers framework-anchor transition, provenance continuity, accepted-target identity, and the relationship among original initialization provenance, prior accepted framework state, supplying framework state, and the staged candidate state.

It defines responsibility boundaries only; exact history representation and storage mechanics remain normative-specification work.

## Dependencies

This area depends on a coherent staged managed state from staged application and projection reconciliation.

Complete staged validation depends on the new staged framework anchor and provenance state established here.

## Exclusions

This area does not decide Git-history topology, exact provenance schema, exact anchor storage format, rollback implementation, promotion mechanics, or hosted orchestration.

It does not erase or rewrite historical provenance merely to make the current framework identity convenient.

## Unresolved decisions

Exact accepted-anchor representation, provenance record extension or companion specification, multi-upgrade history model, relationship to Git object identity, retention of prior framework identities, rollback evidence, and security/integrity requirements remain unresolved.

Later specification work must determine whether current initializer provenance specifications can be extended compatibly or whether upgrade-specific normative records are required.

## Successor work

Normative specification work should define re-anchoring and provenance continuity, then hand the re-anchored staged repository to complete staged validation.
