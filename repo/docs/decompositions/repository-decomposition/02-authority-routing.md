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

- **Level 0**: authority-routing capability contract;
- **Level 1**: routing decision model and authority invariants;
- **Level 2**: lifecycle routing relationships among audit, feature-development, and governed work;
- **Level 3**: profile-specific routing signals and externally visible state where needed.

## Successor work

Normative specifications must define accepted routing invariants and failure behavior before implementation planning.
