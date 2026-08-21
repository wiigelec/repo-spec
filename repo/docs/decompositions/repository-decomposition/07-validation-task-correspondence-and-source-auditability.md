# Validation-task correspondence and source auditability

## Status

Directional decomposition content.

## Purpose

Define the repository-generic responsibility for validation-task identity, source-local role auditability, task-to-requirement correspondence, and separation of task purpose from execution level.

## Responsibilities

- require each externally identified validation task to belong through one canonical package to exactly one canonical normative requirement;
- require every maintained validation callable defined in governed validation implementation source to be source-locally classifiable as exactly one validation-task callable or helper;
- require validation-task callables to expose exactly one canonical normative-requirement correspondence directly from source;
- keep helpers explicitly non-owning and mutually exclusive with validation-task ownership at the same revision;
- require package ownership and source-local task metadata to agree without creating an independent task-to-requirement registry;
- distinguish source-level validation-task callables from public validation entry points governed by repo.validation;
- separate validation purpose or coverage intent from execution-level metadata.

## Boundaries

This area defines auditability and correspondence responsibilities, not exact task identifiers, decorator/attribute syntax, metadata vocabulary, task granularity, parameterization mechanics, discovery implementation, or orchestration.

Source-local metadata remains subordinate traceability metadata; the canonical package set remains the correspondence source model.

## Dependencies

Depends on Normative-reference Identity and Active Requirement Scope and Validation-correspondence Package Model.

Also depends on existing validation implementation organization and the accepted public-entry-point boundary in repo.validation.

Feeds correspondence integrity and later validator/test migration planning.

## Exclusions

- no source annotation or decorator selection;
- no validator/test tagging in this decomposition change;
- no task-ID format;
- no requirement to register fixtures, assertions, or parameter cases as separate tasks;
- no source refactor or test migration;
- no new public validation entry point.

## Unresolved decisions

- stable task identity granularity and accepted uniqueness scope;
- exact source-local helper/task role representation;
- exact normative-reference annotation mechanism;
- purpose/coverage and execution-level vocabularies and cardinalities;
- parameterized-task and shared-helper treatment;
- source movement and task-identity stability rules.

## Expected specification families

Directional expectation:

- **Repository validation-correspondence specification family**: task ownership, source-local auditability, task/helper exclusivity, and package/source agreement;
- **Repository validation specification family**: relationship between source-level task callables, helper implementation, runners, and public validation entry points;
- **Cross-specification relationship**: task correspondence must remain subordinate to the package model and normative authority while executable validation organization remains implementation detail unless explicitly governed.

## Successor work

After decomposition acceptance, repository specifications must define task identity and source-local correspondence semantics before any maintained validation source is tagged or migrated.
