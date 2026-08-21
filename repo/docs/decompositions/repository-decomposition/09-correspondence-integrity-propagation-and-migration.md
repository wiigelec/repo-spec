# Correspondence integrity, propagation, and migration

## Status

Directional decomposition content.

## Purpose

Define the repository-generic responsibility for validating correspondence integrity, deterministic projections, framework propagation/materialization, candidate preparation, and migration while preserving valid accepted states.

## Responsibilities

- require completeness and uniqueness checks across active normative requirements and canonical packages;
- require package ownership, task identity, source resolution, source-local role classification, and task-to-requirement metadata to remain mutually consistent;
- require withdrawn requirements to leave active coverage while preserving downstream-defined historical provenance;
- keep generated coverage/documentation as deterministic subordinate projections of canonical correspondence sources;
- preserve repo-owned correspondence identity and authority across repo-spec and initialized-repository materializations;
- detect stale, missing, duplicated, or divergent propagated correspondence;
- permit preparatory non-active correspondence for candidate authority without activating candidate semantics early;
- preserve valid accepted states during migration and route inseparable transitions through existing Atomic-transition authority when its eligibility conditions are actually met.

## Boundaries

This area defines integrity and transition responsibilities, not exact validator implementation, generated paths, initializer copy mechanics, candidate package representation, migration sequence, or a decision that an Atomic transition is required.

Propagation preserves repo-owned authority; constitutional applicability to independently authored product requirements remains the responsibility of Validation-domain Ownership and Product Reconciliation.

## Dependencies

Depends on all four preceding validation-correspondence areas.

Also depends on generated-artifact governance, repository structure, initializer/framework materialization authority, validation orchestration, development workflow, Atomic-transition rules, and withdrawn/superseded requirement provenance.

## Exclusions

- no generated validation-package outputs in this decomposition change;
- no initializer inventory changes;
- no validator implementation;
- no package population or migration;
- no preselection of Atomic transition;
- no CI or execution-orchestration change.

## Cross-cutting concerns

- fail-closed correspondence integrity;
- deterministic source/projection equivalence;
- repository authority preservation across materialization;
- accepted-state validity during staged migration;
- candidate-versus-active lifecycle separation;
- traceability through withdrawal and supersession.

## Unresolved decisions

- exact self-validation phases and diagnostics;
- generated projection inventory, paths, and formats;
- exact source-to-product and source-to-initialized-tree materialization mechanics;
- freshness/equivalence proof across propagated surfaces;
- candidate/pre-acceptance correspondence representation;
- migration sequencing, bootstrap strategy, and whether any final transition satisfies Atomic eligibility.

## Expected specification families

Directional expectation:

- **Repository validation-correspondence/validation specification families**: integrity invariants and enforcement ownership;
- **Repository generated-artifact specification family**: deterministic projection and freshness semantics;
- **Repository structure/initializer framework families**: authorized materialization roles and source-to-initialized-tree propagation;
- **Repository development-workflow family**: candidate activation, valid intermediate states, and Atomic-transition eligibility;
- **Cross-specification relationship**: all enforcement remains subordinate to normative authority and the canonical correspondence source model.

## Stopping criteria

The validation-correspondence decomposition is complete when identity/scope, package model, task/source auditability, constitutional domain ownership/product reconciliation, and integrity/propagation/migration each have stable responsibility boundaries; their dependencies and cross-specification relationships are explicit; unresolved exact mechanics remain visible; and downstream repository specification work can proceed without inferring semantics from this directional document.

## Planning handoff

Implementation planning is not authorized by this decomposition.

The next authorized lifecycle step after manual acceptance is governed repository-specification drafting and acceptance for the repository-generic validation-correspondence contract and required coordinated authority changes. Specification work must resolve ownership, structure, product-correspondence reconciliation, lifecycle, integrity, and migration semantics before implementation planning.

## Successor work

Create and accept the required owner-appropriate repository specification changes identified by areas 05–09, including their dependency direction and cross-specification reconciliation. Only after those normative changes are accepted may the feature-request workflow determine the authorized implementation-planning and migration path.
