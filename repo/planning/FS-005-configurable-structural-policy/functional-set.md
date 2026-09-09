---
functional_set: FS-005
title: Configurable Structural Policy
design_revision: 33b5dd3dc3512719d8ff4896df457412dc3a8cae
---

# FS-005 — Configurable Structural Policy

## Purpose

Separate repository structural-policy data from reusable framework Validation implementation while preserving the closed, default-deny structural-boundary semantics established by DP-013.

## Selected Design

Planning consumes framework Design at repository revision `33b5dd3dc3512719d8ff4896df457412dc3a8cae`.

Selected Design scope:

- DP-001 — Repository Development Lifecycle;
- DP-013 — Repository Ownership and Structural Boundaries;
- DP-031 — Mechanical Enforcement Construction Architecture; and
- DP-040 — Validation Architecture.

## Functional Set Boundary

FS-005 establishes one canonical repository-local structural-policy configuration, the framework-owned schema and enforcement semantics for that configuration, current default policy compatibility, and the ability for an installed repository to intentionally carry repository-specific concrete authorization without modifying reusable Validation code.

## Out of Scope

FS-005 does not define initializer or repository-upgrade product behavior. Those behaviors belong to product Planning.

FS-005 also does not:

- introduce a generalized plugin or policy engine;
- make arbitrary paths exempt from structural Validation;
- add wildcard or pattern-based structural authorization;
- change ownership semantics of `repo/`, `product/`, `scripts/`, or `user/`;
- change the currently accepted default authorized entries merely because the policy becomes data;
- make Validation configuration normative authority independent from Design and Planning; or
- define product-specific repository structure.

## Completion Criterion

After Acceptance, canonical framework Validation obtains concrete structural authorization from one strict repository-local policy file rather than hardcoded allowlists, the accepted default policy preserves current behavior, and an installed repository may intentionally carry different concrete authorization while undeclared structure remains denied.

## Issue

This Functional Set supplies the framework side of issue #15.
