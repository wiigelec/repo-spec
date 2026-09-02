---
functional_set: FS-002
title: Independent Initialized Repository
design_revision: 790d8204f545c7759f22f4f34f53dd34e206ab6a
---

# FS-002 — Independent Initialized Repository

## Purpose

Refine repository initialization so the derived repository begins independent Git history, installs only the framework state needed for ordinary lifecycle use, and omits supplier framework-development Planning history.

## Selected Design

Planning consumes Product Design at repository revision `790d8204f545c7759f22f4f34f53dd34e206ab6a`.

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
