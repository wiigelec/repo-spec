# Intake classification

## Status

Directional decomposition content.

## Purpose

Define the directional responsibility for recognizing and classifying ordinary issue intake before governance is established.

## Responsibilities

- accept that an issue may begin as unformatted intake;
- distinguish routing classification from governance state;
- represent `bug-fix` and `feature-request` as routing concepts;
- preserve enough classification context for later authority routing;
- fail closed when classification is ambiguous enough to affect authority selection.

## Boundaries

This area identifies classification responsibility but does not define exact label APIs, automation, UI, schema, or enforcement mechanics.

It does not authorize mutation.

## Dependencies

This area depends on ordinary issue intake existing on the selected hosting-platform profile and feeds the Authority Routing area.

## Exclusions

- no audit semantics;
- no whiteboard or functional-set semantics;
- no governed-work promotion mechanics;
- no CI behavior;
- no concrete GitHub implementation.

## Unresolved decisions

- whether `bug-fix` and `feature-request` must be mutually exclusive;
- whether additional routing classifications are permitted;
- how classification conflicts are represented;
- whether classification state is repository-generic or entirely profile-specific.

## Expected specification families

Directional expectation:

- **Repository specification family**: repository-generic issue-intake/routing purpose, scope, classification concepts, invariants, state relationships, and allowed transitions;
- **Hosting-platform profile boundary**: profile-specific realization requirements only where labels or issue metadata carry classification.

Repository-generic classification requirements shall not be forced into product-specification levels. Exact repository-specification partitioning and profile realization remain subject to later governed specification work.

## Successor work

Owner-appropriate normative specifications must define the accepted classification semantics and invariants before implementation planning. Repository-generic requirements belong under repository specification authority.
