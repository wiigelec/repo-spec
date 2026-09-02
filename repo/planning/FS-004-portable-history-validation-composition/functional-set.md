---
functional_set: FS-004
title: Portable History and Validation Composition
design_revision: 15475e3b13790380850c1e890284cc6eeb7b7ebc
---

# FS-004 — Portable History and Validation Composition

## Purpose

Make the reusable framework compatible with repositories whose Git history is independent from the framework-supplying repository, and establish the narrow repository-root Validation composition surface authorized by Design.

## Selected Design

Planning consumes framework Design at repository revision `15475e3b13790380850c1e890284cc6eeb7b7ebc`.

Selected Design scope:

- DP-013 — Repository Ownership and Structural Boundaries;
- DP-021 — Functional Set Architecture; and
- DP-040 — Validation Architecture.

## Functional Set Boundary

FS-004 establishes portable retained Design bindings, minimal installed framework snapshots that may omit `repo/planning/`, repository-root `scripts/` operational composition, `scripts/validate`, framework/product Validation composition, CI delegation, and active README/AGENTS alignment.

## Out of Scope

FS-004 does not change the initializer's Git materialization strategy, create fresh target history, import supplier commits, add Git grafts/replace refs/bundles, or create generalized provenance, lineage, plugin, or validation-discovery systems.

## Completion Criterion

After Acceptance, framework Validation can operate with well-formed retained Design revision identifiers whose originating Git objects are absent, while repository-wide mechanical Validation is invoked through `scripts/validate` and delegates to domain-owned validators.
