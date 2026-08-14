# Platform validation integration

## Status

Directional decomposition content.

## Purpose

Define the directional responsibility boundary between repository-generic routing authority and hosting-platform-specific realization and hosted validation.

## Responsibilities

- keep GitHub-specific labels, comments, body updates, and issue events inside the platform-profile boundary;
- ensure ordinary unformatted intake is not subjected to governed-work field validation prematurely;
- ensure governed-work field validation becomes active only after governance-state promotion;
- preserve a valid observable state across promotion;
- distinguish repository-local validation from hosted issue-field policy.

## Boundaries

This area defines integration responsibilities and validation timing, not exact GitHub API calls, workflow YAML, or implementation architecture.

## Dependencies

Depends on Governed-work Promotion and Provenance.

Depends on:

- hosting-platform profiles;
- hosted field-policy validation;
- repository-local validation contracts;
- governing-issue structure.

## Exclusions

- no exact GitHub Actions trigger/event list;
- no exact API mutation sequence;
- no exact label colors or creation commands;
- no implementation code;
- no branch protection or unrelated hosting settings.

## Cross-cutting concerns

- fail-closed governance transitions;
- no invalid intermediate governed-work state;
- portability beyond GitHub;
- source-to-adapter authority for platform profiles;
- reproducible validation evidence;
- preservation of issue history and provenance.

## Unresolved decisions

- exact event ordering and trigger set for hosted validation;
- whether routing labels remain after promotion;
- how conflicts between platform state and repository authority are surfaced;
- which checks belong to repository-local validation versus hosted policy;
- whether promotion needs transactional or compensating behavior on platforms without atomic issue mutation.

## Expected specification families

Directional expectation:

- **Level 0**: platform integration scope for issue-routing governance;
- **Level 1**: repository-generic validation and state invariants;
- **Level 2**: profile boundary, event/state relationships, and failure semantics;
- **Level 3**: GitHub profile requirements for labels, comments, body updates, events, and field-policy integration.

Areas that may not require separate standalone specifications:
- purely documentary discoverability/index updates;
- non-semantic label presentation details unless later authority assigns meaning to them.

## Stopping criteria

This decomposition area is complete when downstream normative work can separately specify repository-generic lifecycle rules and GitHub-profile realization without architecture being prematurely chosen.

## Planning handoff

Implementation planning is not authorized until the required Level 0–3 specifications are accepted.

The next authorized lifecycle step is governed product-specification drafting and acceptance for the decomposed areas.

## Successor work

Create the required repository-owned and platform-profile specification artifacts, establish their dependency direction, accept them through governed review, and only then create an implementation plan.
