---
functional_set: FS-002
title: Independent Initialized Repository
design_revision: a5d566041958481286325f671393405b900a7141
---

# FS-002 — Independent Initialized Repository

## Purpose

Refine repository initialization so the derived repository begins independent Git history, installs only the framework state needed for ordinary lifecycle use, and omits supplier framework-development Planning history.

## Selected Design

Planning consumes Product Design at repository revision `a5d566041958481286325f671393405b900a7141`.

Selected Product Design scope:

- DP-110 — Repository Initialization
- DP-120 — Initialized Repository

FS-002 also consumes the installed-framework portability behavior established by framework FS-004.

## Functional Set Boundary

FS-002 changes only initialized-repository materialization and the regression/mechanical validation necessary to prove the resulting history and installed framework payload.

## Out of Scope

FS-002 does not add upgrade behavior, archive/distribution formats, generalized provenance, supplier-history imports, grafts, replace refs, bundles, remote creation, target-product semantics, or new normal CLI arguments.

## Completion Criterion

A successful initialization produces one independently rooted target repository whose installed framework validates without `repo/planning/` or supplier Git objects, while retaining the exact supplying revision in `repo/validation/framework-source.json`.

## Issue #12 Bug-Fix Amendment

This accepted Functional Set is corrected in place so every newly initialized independent repository receives the canonical generic product Validation scaffold required by the installed framework.

The scaffold carries no target-product semantics. It provides only product lifecycle ownership surfaces, starter guidance, an empty Requirement Evaluation Manifest, and a no-op-until-bound product Validation mechanism.
