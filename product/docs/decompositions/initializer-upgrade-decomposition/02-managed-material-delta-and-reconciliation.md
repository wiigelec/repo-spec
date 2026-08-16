# Initializer Upgrade Decomposition: Managed-Material Delta and Reconciliation

> Part 2 of 5 · [Initializer upgrade decomposition index](../INITIALIZER-UPGRADE-DECOMPOSITION.md) · [Previous](./01-request-identity-and-eligibility.md) · [Next](./03-staged-application-and-projections.md)

## Status

Directional decomposition content.

## Purpose

Bound the product responsibility that determines which initializer-managed material is eligible to change between the target's accepted framework state and the supplying framework state.

## Responsibilities

Resolve the target's currently accepted repo-spec revision to its repo-spec initialization manifest, resolve the supplying reconciliation-target repo-spec revision to its repo-spec initialization manifest, compare those two initializer-managed inventories through stable managed-material identity, classify managed material as unchanged, added, modified, removed, or retargeted where the later normative model supports those distinctions, and select the managed reconciliation set.

Preserve the approved authority boundary: upgrade may reconcile initializer-managed material but must not treat arbitrary repository paths or product-owned work outside that managed universe as upgrade-owned merely because files overlap operationally.

## Boundaries

This area covers source-owned upgrade qualification, baseline/target initialization-manifest resolution, old/new managed inventory comparison, stable material identity, managed authority classification, delta/reconciliation selection, and evidence needed to explain why a managed item is or is not selected. The baseline manifest is the initialization manifest for the target's currently accepted repo-spec revision; the target manifest is the initialization manifest for the supplying reconciliation repo-spec revision.

The approved functional set permits a source-owned upgrade manifest direction. That source-owned qualification may constrain which manifest-derived changes are legal or required, but it does not replace the two repo-spec initialization manifests as the managed-material inventory endpoints and does not create authority over material outside the initializer-managed universe. This decomposition does not define the upgrade-manifest schema, revision-selection semantics, dependency closure, or comparison algorithm.

## Dependencies

This area depends on valid target/source framework identity and target eligibility from the preceding area.

Staged application depends on the resulting selected managed reconciliation set and its authority classification.

## Exclusions

This area does not apply filesystem changes, define staging mechanics, reconcile generated projections operationally, re-anchor framework history, validate the complete staged target, or promote it.

It does not define exact conflict-resolution behavior for local changes to managed material.

## Unresolved decisions

Exact upgrade-manifest representation, material-key continuity rules across revisions, revision-range applicability, compatibility constraints, local managed-change classification, conflict policy, and the evidence model for source-owned upgrade qualification remain unresolved.

Later specification work must decide which existing material-manifest/output-inventory specifications can be reused and where upgrade-specific normative semantics are required.

## Successor work

Normative specification work should define managed-material identity and selection responsibilities, then hand the selected reconciliation set and authority evidence to staged application and projection reconciliation.
