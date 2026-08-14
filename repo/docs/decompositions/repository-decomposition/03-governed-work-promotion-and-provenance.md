# Governed-work promotion and provenance

## Status

Directional decomposition content.

## Purpose

Define the directional responsibility for transitioning from intake/provenance state into a bounded governed operation while preserving original evidence.

## Responsibilities

- establish `governed-work` as governance state distinct from intake classification;
- require a canonical governed issue structure before governed-work validation is active;
- preserve original intake evidence before body replacement or restructuring;
- maintain traceability between intake intent and bounded governed mutations;
- support successor governed issues when lifecycle separation requires them.

## Boundaries

This area defines responsibility and invariants for promotion and provenance.

It does not define the exact governing-issue schema or exact hosting-platform API sequence.

## Dependencies

Depends on Authority Routing.

Depends on the canonical governing-issue contract and existing bounded development workflow.

Feeds Platform Validation Integration.

## Exclusions

- no exact comment/body/label operation ordering beyond necessary invariants;
- no exact successor-issue count or naming convention;
- no CI workflow syntax;
- no implementation code.

## Unresolved decisions

- exact point at which a feature-request becomes or spawns `governed-work`;
- whether the original intake issue can itself serve as every downstream governed issue;
- exact routing-label lifecycle after promotion;
- exact minimum provenance payload required at promotion;
- whether title preservation is required in addition to body/classification evidence.

## Expected specification families

Directional expectation:

- **Level 0**: governed-work promotion and provenance capability contract;
- **Level 1**: promotion invariants and provenance requirements;
- **Level 2**: lifecycle transition model between intake, routed state, and governed operations;
- **Level 3**: platform-profile issue/comment/body/label requirements needed to realize promotion safely.

## Successor work

Normative specifications must define accepted promotion, provenance, and traceability behavior before implementation planning.
