---
functional_set: FS-003
title: Repository Ownership and Structural Boundaries
design_revision: a5d566041958481286325f671393405b900a7141
---

# FS-003 — Repository Ownership and Structural Boundaries

## Purpose

Complete the portable repository framework for product work by establishing the generic `repo/` and `product/` ownership domains and mechanically protecting the shallow architectural boundaries that separate them.

This Functional Set responds to a concrete need exposed by beginning product development: the accepted lifecycle did not yet define where generic product-owned lifecycle and implementation state belongs relative to reusable framework state.

## Selected Design

Planning consumes Design at repository revision `a5d566041958481286325f671393405b900a7141`.

Selected Design scope:

- DP-001 — Repository Development Lifecycle
- DP-010 — Design Architecture
- DP-012 — Design Corpus Architecture
- DP-013 — Repository Ownership and Structural Boundaries
- DP-020 — Planning Architecture
- DP-023 — Normative Requirements Architecture
- DP-030 — Build Architecture
- DP-031 — Mechanical Enforcement Construction Architecture
- DP-040 — Validation Architecture
- DP-051 — Stage Review Architecture

## Functional Set Boundary

FS-003 establishes `repo/` as the reusable framework domain, `product/` as the generic product-owned domain, shallow default-deny structural boundaries for the repository root and both ownership trees, ordinary extensibility beneath authorized roles, project-native mechanical enforcement, and operational guidance preventing accidental parallel namespaces.

## Out of Scope

FS-003 does not define product identity or semantics, make `product/` initializer-specific, recursively close nested implementation structure, create a structure registry or artifact taxonomy, recreate v0 governance machinery, generalize framework-side lifecycle discovery or parsing to product-owned artifacts, or change Acceptance semantics.

## Completion Criterion

After Acceptance, product Design and subsequent product lifecycle work may begin under `product/` without another framework Functional Set merely to establish generic product ownership or placement. FS-003 establishes structural readiness; it does not claim that every framework-side lifecycle tool already operates generically on product-owned artifacts.

## Issue #12 Bug-Fix Amendment

This accepted Functional Set is corrected in place to realize the canonical product Validation substrate now made explicit by DP-013.

The existing generic `product/` role set remains unchanged. The correction makes `product/design/`, `product/specs/`, `product/scripts/`, and `product/validation/` required baseline roles whenever the maintained product ownership domain is present; `product/planning/` and `product/src/` remain optional until product work needs them.

No new architectural namespace is introduced.
