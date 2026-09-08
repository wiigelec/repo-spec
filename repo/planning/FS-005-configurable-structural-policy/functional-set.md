---
functional_set: FS-005
title: Configurable Structural Policy
design_revision: 33b5dd3dc3512719d8ff4896df457412dc3a8cae
---

# FS-005 — Configurable Structural Policy

## Purpose

Separate repository structural-policy data from the reusable framework Validation implementation while preserving the existing closed, default-deny structural-boundary semantics established by DP-013.

## Selected Design

Planning consumes framework Design at repository revision `33b5dd3dc3512719d8ff4896df457412dc3a8cae`.

Selected Design scope:

- DP-001 — Repository Development Lifecycle;
- DP-013 — Repository Ownership and Structural Boundaries;
- DP-031 — Mechanical Enforcement Construction Architecture;
- DP-040 — Validation Architecture; and
- accepted initialized-repository and repository-upgrade product Design where initialization and upgrade consume the reusable framework.

## Functional Set Boundary

FS-005 establishes one canonical repository-local structural-policy configuration, framework-owned schema and enforcement semantics for that configuration, initializer seeding of the default policy, and upgrade reconciliation of framework-required policy with repository-specific authorized entries.

FS-005 preserves the Design-declared closed root, `repo/`, and `product/` boundaries and keeps their enforcement default-deny.

## Out of Scope

FS-005 does not:

- introduce a generalized plugin or policy engine;
- make arbitrary paths exempt from structural Validation;
- add wildcard or pattern-based structural authorization;
- change ownership semantics of `repo/`, `product/`, `scripts/`, or `user/`;
- change the currently accepted default authorized entries merely because the policy becomes data;
- make Validation configuration normative authority independent from Design and Planning; or
- define product-specific repository structure.

## Completion Criterion

After Acceptance, canonical framework Validation obtains concrete structural authorization from one strict repository-local policy file rather than hardcoded allowlists, initialized repositories receive the current default policy, derived repositories may intentionally modify that policy through their own lifecycle without patching reusable Validation code, and repository upgrade preserves compatible target-specific authorization while reconciling framework-required policy changes.

## Issue

This Functional Set resolves issue #15: `Externalize closed structural allowlist into repository-owned config`.
