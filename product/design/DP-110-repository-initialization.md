---
doc_id: DP-110
title: Repository Initialization
depends_on:
  - DP-100
---

# Repository Initialization

## Purpose

Repository initialization is the transformation performed by the repo-spec initializer from a user's request for a new repository and a selected repo-spec source into a repository ready to begin independent product development.

This document defines the meaning and boundaries of that transformation without prescribing its implementation.

## Initialization Inputs

Initialization requires a destination selected by the user and a repo-spec source from which the reusable framework is supplied.

The destination identifies the repository the user intends to establish.

The initializer may derive information mechanically when that information is already inherent in the destination or selected source rather than requiring the user to restate it.

The initializer shall not require target-product semantics merely to initialize the repository.

## Supplying Source

The supplying repo-spec state must identify the framework revision that initialization is actually using.

Initialization shall not silently substitute a different framework revision while representing the result as having been supplied by the selected source.

If the initializer cannot determine the supplying framework state accurately enough to construct a truthful result, initialization is not successful.

Whether the supplying source must be a local checkout, installed distribution, archive, or another representation is not fixed by Design unless a later semantic need requires that restriction.

## Destination Meaning

The destination is user-owned input to initialization.

The initializer may create repository state within that destination as required to establish the initialized repository, but it shall not treat arbitrary existing material as disposable merely because that would simplify implementation.

When existing destination state makes correct initialization ambiguous, destructive, or semantically unclear, the initializer should reject the operation unless current Design and Planning explicitly define a safe interpretation.

Detailed filesystem predicates for destination admissibility belong to Planning when they can be derived without additional product meaning.

## Framework Establishment

Initialization establishes the reusable repo-spec framework within the new repository.

Framework-owned state in the result shall remain distinguishable from product-owned state.

The initialized repository shall preserve the framework's generic `product/` ownership meaning rather than importing the initializer product's own semantics as the target repository's product.

The supplying repository therefore has:

    repo/       reusable framework
    product/    repo-spec initializer

while the initialized repository has:

    repo/       reusable framework
    product/    target repository's product domain

The second `product/` does not mean repo-spec initializer unless that repository later independently chooses to develop such a product.

## Product Readiness

Initialization establishes the generic repository state necessary for later product Design and subsequent product lifecycle work.

It may establish empty directories, initial operational guidance, or other generic product-development surfaces when those are required to make that ownership and lifecycle usable.

It shall not populate those surfaces with invented target-product intent.

A newly initialized repository may therefore be structurally ready for product development while having no current product Design beyond the generic ownership domain supplied by the framework.

## Product Validation Scaffold

Product readiness includes establishment of the generic product surfaces required to use the installed lifecycle rather than leaving each target repository to reconstruct those mechanics independently.

Initialization shall establish the canonical product Design surface, normative-specification surface, product Validation entry point, and product Validation implementation surface required by the installed framework.

The initialized product Validation substrate includes a Requirement Evaluation Manifest in the product Validation ownership domain. Before product normative requirements exist, that manifest represents a valid empty binding set.

The product Validation entry point is a narrow executable interface to product-owned Validation. Initialization shall not populate that entry point with initializer-specific or target-product-specific validation predicates merely to make the scaffold executable.

These surfaces establish lifecycle mechanism and ownership only. Their presence does not define the target product, create product Design meaning, create normative product requirements, or imply that target-product implementation has begun.

## Repository Bootstrap

Where Git repository state is necessary for the initialized repository to use the framework correctly, initialization may establish that state.

The semantic requirement is that the resulting repository can participate in the lifecycle expected by the installed framework.

Design does not prescribe specific Git commands, object layouts, bootstrap commit construction, branch-manipulation algorithms, or low-level repository plumbing unless those details later become consequential product meaning.

The initialized repository is a new repository in its own right. Its ordinary Git history shall not inherit the supplying repo-spec repository's commit ancestry merely as a consequence of framework installation. Exact source identity may be retained as maintained information without importing supplier commit objects into the initialized repository.

Framework-development Planning history from the supplying repository is not required in an installed framework snapshot when the installed framework can operate from its Design, normative specifications, validation bindings, and source record without that history.

## Validation

Before reporting successful initialization, the initializer shall cause the resulting repository state to be mechanically evaluated to the extent required by the installed framework and the initializer's mechanically decidable product obligations.

Validation shall evaluate the actual candidate result rather than merely assume that generation succeeded because initializer execution completed.

Passing mechanical Validation means only that mechanically decidable initialization obligations were satisfied.

## Atomic Meaning

Initialization has two user-visible semantic outcomes:

- a successfully initialized repository; or
- initialization failure.

The initializer shall not knowingly report success for a partially established repository that does not satisfy the conditions required of an initialized repository.

Implementation may use staging, temporary directories, rollback, direct construction, or another reliable technique. Design requires the observable success/failure boundary, not a particular transaction mechanism.

## Repeatability and Determinism

Equivalent initialization requests using the same relevant source state should not acquire unexplained semantic differences from incidental execution conditions.

Exact byte-for-byte output, Git object identity, timestamps, ordering, or other low-level determinism is required only where Planning can derive a concrete need for it from current Design.

The product should not introduce elaborate reproducibility machinery merely to maximize theoretical determinism.

## Exclusions

Repository initialization does not inherently include:

- defining the target product;
- implementing target-product features;
- approving target-product Functional Sets;
- making target-product Acceptance decisions;
- publishing or releasing the target product;
- upgrading an already initialized repository to a later framework revision;
- configuring a particular hosting provider;
- establishing generalized migration, reconciliation, provenance, or evidence systems.

Any of these may become separate product capabilities if later Design establishes that need.
