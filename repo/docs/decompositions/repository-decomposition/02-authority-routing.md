# Authority routing

## Status

Directional decomposition content.

## Purpose

Define the directional responsibility for selecting the correct authority lifecycle after intake classification.

## Responsibilities

- route `bug-fix` intake toward audit;
- route `feature-request` intake toward governed whiteboard, analysis, and functional-set development;
- preserve the rule that routing classification alone does not authorize mutation;
- preserve authority boundaries between defect correction and new-direction development;
- expose routing failure or ambiguity rather than silently choosing an authority path.

## Boundaries

This area decides lifecycle direction at the responsibility level.

It does not redefine audit, whiteboard, analysis, or functional-set semantics.

## Dependencies

Depends on Intake Classification.

External dependencies:

- audit lifecycle;
- repository whiteboard lifecycle;
- repository analysis lifecycle;
- functional-set lifecycle.

Feeds Governed-work Promotion and Provenance when a bounded governed operation becomes appropriate.

## Exclusions

- no detailed audit rules;
- no functional-set approval mechanics;
- no exact issue-closing or successor-issue policy;
- no GitHub automation;
- no implementation architecture.

## Unresolved decisions

- what evidence threshold is sufficient for bug-fix versus feature-request classification;
- what happens when audit discovers missing product intent;
- whether original intake remains the parent/provenance surface through all downstream stages;
- how routing ambiguity is surfaced to humans and agents.

## Expected specification families

Directional expectation:

- **Repository specification family**: repository-generic authority-routing capability, routing decision model, authority invariants, and lifecycle relationships among audit, feature-development, and governed work;
- **Hosting-platform profile boundary**: profile-specific routing signals and externally visible state only where needed for realization.

Repository-generic authority-routing requirements shall not be forced into product-specification levels.

## Successor work

Owner-appropriate normative specifications must define accepted routing invariants and failure behavior before implementation planning. Repository-generic requirements belong under repository specification authority.
