---
doc_id: DP-100
title: Repo-Spec Initializer
depends_on: []
---

# Repo-Spec Initializer

## Purpose

The repo-spec initializer is the maintained product developed by this repository.

Its purpose is to use an accepted repo-spec revision to establish a new repository that contains the reusable repository-development framework and is ready for subsequent development of an independently defined product.

The initializer applies the framework; it is not itself part of the reusable framework meaning.

## Product Identity

The initializer is a repository initialization product.

It is more than a file copier, project skeleton, template renderer, or directory generator. Its successful result is a repository with a coherent framework-owned development environment from which product Design, Planning, Build, Validation, Semantic Review, and Acceptance can proceed.

The initializer product belongs to this repository's `product/` ownership domain.

The reusable framework under `repo/` remains product-independent. Nothing in framework Design shall require another repository using the framework to develop the repo-spec initializer or any other specific product.

## User Intent

A user chooses to create a new repository using a particular accepted repo-spec source.

The initializer turns that request into a correctly established repository without requiring the user to manually reconstruct the framework's internal structure or lifecycle machinery.

Initialization should require only information that belongs to repository initialization itself.

Information about the product that will eventually be developed in the initialized repository belongs to that product's later Design and is not an initializer input merely because the product will use the initialized repository.

## Product Boundary

The initializer owns the act of establishing a new repository and the correctness of the repository state produced by that act.

It may establish framework-owned state, generic product-development surfaces, necessary repository-root operational state, and other material required for the initialized repository to begin using the repo-spec lifecycle.

The initializer shall not invent the target repository's product identity, product meaning, architecture, feature set, implementation plan, acceptance decisions, or release claims.

Initialization ends with a repository prepared for product development. Product development itself is successor work.

## Framework Relationship

The initialized repository receives the reusable repository-development framework represented by the selected repo-spec source revision.

Initializer-specific Design, Planning, implementation, validation, documentation, and other product-owned state from the supplying repo-spec repository are not part of the reusable framework merely because the initializer uses them to perform initialization.

The distinction between reusable framework state and initializer-product state shall remain observable in both the supplying repository and the initialized result.

## Source Revision

Initialization is performed from an identifiable repo-spec source revision.

The initialized result shall not falsely represent which framework revision supplied its reusable framework state.

Where later operation of the initialized repository depends on knowing the framework revision from which its reusable state originated, that relationship shall remain recoverable by the simplest mechanism sufficient for that purpose.

This Design does not require a provenance database, evidence graph, lineage system, or other generalized historical architecture.

## Result

Successful initialization produces a repository that is self-contained enough to begin and continue its own product-development lifecycle without depending on the continued presence of the source repo-spec working tree that performed initialization.

The resulting repository shall be capable of evaluating the mechanical obligations necessary to determine that its initialized framework state is internally valid.

Mechanical validity does not establish future product meaning or future product Acceptance.

## Failure

The initializer shall fail rather than knowingly claim successful initialization when it cannot establish the required repository state accurately and unambiguously.

Failure shall not intentionally destroy or silently reinterpret pre-existing user-owned repository material merely to obtain a superficially valid result.

Specific destination admissibility rules, staging techniques, rollback mechanisms, command interfaces, and implementation strategies belong to Planning and Build unless further Design meaning is required.

## Simplicity

The initializer should perform the minimum work necessary to establish a correct repository ready for subsequent product development.

Capabilities from historical implementations are not part of the current product merely because they previously existed.

Additional initializer capabilities should be added only when current Design establishes their product meaning and bounded Planning selects them for realization.

## Further Design

Repository initialization semantics are defined by DP-110.

The intended properties and lifecycle handoff of the initialized repository are defined by DP-120.

Repository upgrade semantics for an already initialized repository are defined by DP-130.
