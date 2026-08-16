# Initializer Upgrade Decomposition: Staged Application and Projections

> Part 3 of 5 · [Initializer upgrade decomposition index](../INITIALIZER-UPGRADE-DECOMPOSITION.md) · [Previous](./02-managed-material-delta-and-reconciliation.md) · [Next](./04-reanchoring-and-provenance.md)

## Status

Directional decomposition content.

## Purpose

Bound the isolated application of selected initializer-managed changes to a staged copy of the existing target while preserving content outside upgrade authority.

## Responsibilities

Seed an isolated upgrade workspace from the existing target, apply selected managed additions/modifications/removals/retargets, and reconcile initializer-managed projections that must remain consistent with their managed source material.

Preserve product-owned work and unrelated repository content outside the initializer-managed universe. Surface local changes inside managed authority rather than silently overwriting them when later normative conflict policy requires intervention.

## Boundaries

This area covers existing-target staging, managed mutation application, managed projection reconciliation, and isolation of incomplete upgrade work from the accepted target.

Projection handling is included only where the projection is initializer-managed under accepted authority; path location alone is insufficient to establish ownership.

## Dependencies

This area depends on the managed reconciliation set and authority evidence from the preceding area.

Re-anchoring and provenance depend on a coherent staged managed state produced here.

## Exclusions

This area does not define exact conflict-resolution policy, promotion mechanics, rollback implementation, public CLI presentation, or the final validation contract.

It does not make the analysis-stage revision-aware material-key/staged-reconstruction candidate a mandatory implementation architecture; staging and managed reconciliation are directional product responsibilities, while exact realization remains later authority.

## Unresolved decisions

Exact workspace mechanics, local managed-change handling, projection dependency representation, conflict outcomes, rollback/recovery mechanics during application, atomicity details, and security-sensitive mutation constraints remain unresolved.

Later normative specification work must separate reusable staging/transaction concepts from upgrade-specific managed reconciliation semantics.

## Successor work

Normative specification work should define the staged managed-application and projection-reconciliation responsibilities and hand a coherent staged state to re-anchoring and provenance.
