# Reference Repository Plan

## Status

Current non-normative implementation plan. The reference repository uses the in-repository isolated-copy model.

Accepted reference-repository base:

```text
main at f7fa9c51a88771599f9e908249a61d4353a436e9
```

## Planning basis

This plan is based on:

- `docs/overview/product-overview/04-git-and-change-workflow.md`
- `docs/overview/product-overview/06-governance-and-evolution.md`
- `docs/plans/01-framework-architecture-plan.md`
- `specs/repo/artifact-taxonomy.json`
- `specs/repo/repository-structure.json`
- `specs/repo/platform-profiles.json`
- `specs/repo/validation.json`
- `specs/repo/product-manifest.json`
- `specs/repo/product-spec-base.json`
- `specs/repo/product-levels.json`

## Purpose

The reference repository proves the framework with a minimal initialized repository snapshot that can live inside this repository as a checked-in isolated copy.

The reference copy is a proof artifact, not a replacement for the framework plan, the repository specifications, or the validation contract.

## Issue 1 - Decide the reference form and artifact inventory

### Scope

- accept the in-repository isolated-copy model;
- classify required and optional initialized-repository artifacts;
- identify reusable, bootstrap-only, and product-specific files;
- define reference validation boundaries.

### Accepted reference form

The reference repository is an in-repository isolated copy of a minimal initialized repository.

The copy must be self-contained, reviewable as checked-in content, and valid without any dependence on private history, ambient working-tree state, or remote-only hosting state.

### Artifact inventory

The reference repository inventory is organized by authority and purpose.

#### Required initialized-repository artifacts

- repository-generic specification source and derived documentation;
- repository structure, artifact taxonomy, platform-profile, workflow, validation, manifest, and correspondence records;
- deterministic validation entry points;
- minimal product activation records needed to show an initialized product repository;
- reference validation evidence.

#### Optional initialized-repository artifacts

- Level 2 and Level 3 product specifications;
- product-specific tests and implementation beyond the minimum proof set;
- additional derived product projections;
- release and maintenance artifacts;
- non-essential documentation or examples that do not change the reference boundary.

#### Reusable files

- accepted repository specifications;
- repository schemas;
- derived repository documentation;
- validation scripts and their repository-local support code;
- product-agnostic overview and plan documents;
- deterministic generators that remain subordinate to their sources.

#### Bootstrap-only files

- GitHub issue and pull-request templates;
- GitHub workflow adapters that remain under bootstrap ownership until profile-source material exists;
- field-policy helpers and their mutation tests;
- remote-state inspection and deployment scaffolding that is not yet profile-source managed.

#### Product-specific files

- product manifest entries and product-specification files under `specs/product/`;
- product schemas under `schemas/product/`;
- product-derived documentation under `derived/specs/product/`;
- product implementation and tests that exist only to prove the initialized product repository.

### Validation boundaries

Reference validation is limited to repository-local evidence for the reference copy.

It shall cover:

- repository-local path and root separation;
- schema conformance for declared files;
- manifest completeness and registration consistency;
- reference-path resolution;
- product Level and dependency rules where product files exist;
- deterministic derived-document freshness;
- clean validation failure behavior.

It shall not cover:

- remote GitHub mutation;
- pull-request or issue lifecycle execution;
- general initializer behavior;
- private history inspection;
- out-of-tree repository state;
- product semantics beyond the accepted specification contracts.

### Expected outcome

The reference repository becomes a checked-in proof that the framework can describe a minimal initialized repository, classify its artifact inventory, and validate the boundary between reusable, bootstrap-only, and product-specific content.

### Acceptance gate

A fresh reference repository passes all required validation without relying on private history or prior chatbot context.

### Completion gate

The reference form and complete artifact inventory are accepted.

## Issue 5 - Add isolated validation and mutation tests

### Scope

- implement clean temporary-copy validation;
- run reference generation, validation, mutation tests, and product tests;
- add portability and parent-dependency checks;
- integrate the reference test into complete repository validation or CI.

### Completion gate

A clean isolated copy passes, and all required invalid mutations fail.
