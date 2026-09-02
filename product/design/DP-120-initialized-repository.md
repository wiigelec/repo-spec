---
doc_id: DP-120
title: Initialized Repository
depends_on:
  - DP-100
  - DP-110
---

# Initialized Repository

## Purpose

An initialized repository is the successful product result of repository initialization.

It is a new repository containing the reusable repo-spec development framework and the generic ownership state necessary for an independently defined product to begin development.

This document defines the semantic properties of that result and the handoff from initialization to later product work.

## Ownership

The initialized repository preserves the framework's separation between reusable framework state and repository-specific product state.

`repo/` owns the reusable repository-development framework.

`product/` owns the independently developed product of the initialized repository.

The initializer may establish both ownership domains structurally, but initializer-specific product meaning from the supplying repo-spec repository shall not become target-product meaning in the initialized repository.

Repository-root operational surfaces and user-owned material may exist according to the installed framework Design.

## Framework State

The initialized repository contains the reusable framework state necessary to use the repo-spec lifecycle.

That framework state shall correspond to the framework supplied by the selected repo-spec revision rather than being an undocumented hybrid of unrelated revisions or historical implementations.

The result may contain generated or mechanically adapted material when required for operation, but generation does not give such material independent normative authority.

## Independent Operation

After successful initialization, ordinary use of the new repository's development lifecycle shall not require the source repo-spec working tree that performed initialization to remain available.

The repository should contain or otherwise possess the framework-owned material required for its own Design, Planning, Build, Validation, Semantic Review, and Acceptance work.

This independence does not prohibit intentionally obtaining a later repo-spec revision for a separately designed future upgrade capability.

## Product State at Handoff

Initialization does not define the repository's eventual product.

At handoff, the product domain is available for product Design, but its identity and semantics remain to be established by the user through the repository lifecycle.

The first substantive product decision therefore occurs after initialization rather than being smuggled into bootstrap parameters or generated defaults.

The initialized repository should make that boundary understandable to both human and AI collaborators.

## Design and Planning Readiness

The result shall provide the structural and operational foundation necessary to begin product Design.

Once sufficient product Design exists, the repository shall be capable of proceeding through Planning, Build, Validation, Semantic Review, and Acceptance according to the installed framework.

Initialization need not pre-create speculative Planning or normative requirements for a product that has not yet been designed.

Generic empty or starter ownership surfaces may exist when useful, but they carry no product semantics merely by existing.

## Mechanical Validity

A successfully initialized repository shall satisfy all mechanically decidable framework and initialization obligations applicable to its initialized state.

It shall provide the canonical mechanical Validation behavior required by the installed framework.

A successful initialization report shall not substitute for running or otherwise obtaining the required mechanical evaluation of the resulting repository.

## Semantic Validity

Mechanical validation cannot establish that a future target product has been designed correctly because initialization intentionally does not define that product.

The initialized repository is semantically successful when it faithfully establishes the generic development environment promised by the initializer without introducing unauthorized product meaning or disguising initializer-specific behavior as reusable framework behavior.

## Source Relationship

Where necessary for correct future interpretation or maintenance, the initialized repository shall retain sufficient information to determine the repo-spec framework revision from which its installed reusable framework state originated.

That information exists to preserve an accurate source relationship.

It does not create a separate authority system, acceptance ledger, provenance architecture, or historical evidence hierarchy.

Git and ordinary repository state should carry this information when they can do so adequately.

The source relationship does not make supplier commits part of the initialized repository's ancestry. A successfully initialized repository begins independent Git history while retaining the exact supplying revision as source information. An installed framework snapshot need not retain the supplying repository's framework-development `repo/planning/` history when ordinary lifecycle operation does not require it.

## Handoff

Successful initialization ends when the new repository is valid and ready for its user to begin defining the actual product.

The conceptual transition is:

    accepted repo-spec source
              ↓
        initialization
              ↓
       initialized repository
              ↓
          Product Design
              ↓
           Planning
              ↓
            Build
              ↓
          Validation
              ↓
       Semantic Review
              ↓
          Acceptance

Initialization owns the transition into the initialized repository.

It does not own the product-development decisions after that handoff.

## Historical Reference

Previous repo-spec implementations may provide useful evidence about initializer capabilities, failure cases, and operational experience.

Historical presence alone does not require an equivalent mechanism in the current initialized repository.

Current product behavior is derived through current Design and Planning.
