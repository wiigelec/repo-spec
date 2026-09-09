---
functional_set: FS-004
title: Structural Policy Integration
design_revision: 33b5dd3dc3512719d8ff4896df457412dc3a8cae
---

# FS-004 — Structural Policy Integration

## Purpose

Make the repo-spec initializer product consume the framework's configurable structural-policy contract correctly during repository initialization and repository upgrade.

## Selected Design

Planning consumes product Design at repository revision `33b5dd3dc3512719d8ff4896df457412dc3a8cae`.

Selected Design scope:

- DP-100 — Repo-Spec Initializer;
- DP-110 — Repository Initialization;
- DP-120 — Initialized Repository; and
- DP-130 — Repository Upgrade.

It also consumes the reviewed framework FS-005 structural-policy contract on this development branch as a required framework interface.

## Functional Set Boundary

FS-004 owns product behavior for:

- seeding the exact supplier structural policy during initialization;
- validating initialized candidates using the installed policy;
- preserving repository-specific schema-compatible policy authorization during upgrade;
- adding new framework-required authorization during upgrade; and
- failing rather than guessing when policy reconciliation is unsupported.

## Out of Scope

FS-004 does not define the structural-policy schema or framework enforcement semantics, which remain framework-owned.

It does not add product-specific structural meaning, generalized policy plugins, or arbitrary bypasses.

## Completion Criterion

After Acceptance, `repo-spec init` produces initialized repositories using the exact selected supplier policy, and `repo-spec upgrade` preserves compatible repository-specific authorization while reconciling prospective framework requirements and validating before promotion.

## Issue

This Functional Set supplies the initializer-product side of issue #15.
