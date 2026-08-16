# Initializer Upgrade Decomposition: Re-Anchoring and Provenance

> Part 4 of 5 · [Initializer upgrade decomposition index](../INITIALIZER-UPGRADE-DECOMPOSITION.md) · [Previous](./03-staged-application-and-projections.md) · [Next](./05-validation-promotion-and-outcomes.md)

## Status

Directional decomposition content.

## Purpose

Bound the transition from the target's prior accepted framework identity to the supplying framework identity while preserving historical initialization and upgrade provenance.

## Responsibilities

Represent the staged repository's intended new accepted framework anchor and maintain a durable ordered reconciliation lineage beginning with the exact repo-spec revision used for original initialization and appending every repo-spec revision whose reconciliation is subsequently accepted. Each accepted lineage entry must retain enough identity/provenance to resolve that revision's repo-spec initialization manifest for audit and future reconciliation.

Ensure re-anchoring occurs before validation so validation evaluates the staged repository in the framework state it would claim after successful promotion.

## Boundaries

This area covers framework-anchor transition, provenance continuity, accepted-target identity, and the relationship among original initialization provenance, the ordered sequence of accepted reconciliation repo-spec revisions, the currently accepted active baseline, the supplying framework state, and the staged candidate state. Historical accepted entries remain durable provenance even though only the most recent accepted entry is the active baseline for the next reconciliation.

It defines responsibility boundaries only; exact history representation and storage mechanics remain normative-specification work.

## Dependencies

This area depends on a coherent staged managed state from staged application and projection reconciliation.

Complete staged validation depends on the new staged framework anchor and provenance state established here.

## Exclusions

This area does not decide Git-history topology, exact provenance schema, exact anchor storage format, rollback implementation, promotion mechanics, or hosted orchestration.

It does not erase or rewrite historical provenance merely to make the current framework identity convenient.

## Unresolved decisions

Exact accepted-anchor representation, provenance/history record schema, manifest-resolution representation, relationship to Git object identity, rollback evidence, and security/integrity requirements remain unresolved. The requirement to retain original initialization identity plus every successfully accepted reconciliation identity is resolved at this decomposition level; only its exact representation remains open.

Later specification work must determine whether current initializer provenance specifications can be extended compatibly or whether upgrade-specific normative records are required.

## Successor work

Normative specification work should define re-anchoring and provenance continuity, then hand the re-anchored staged repository to complete staged validation.
