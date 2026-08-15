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

- **Repository specification family**: repository-generic governed-work promotion/provenance capability, promotion invariants, provenance requirements, and lifecycle transition relationships between intake, routed state, and governed operations;
- **Hosting-platform profile boundary**: issue/comment/body/label realization requirements needed to perform promotion safely on a supported platform.

Repository-generic promotion and provenance requirements shall not be forced into product-specification levels.

## Successor work

Owner-appropriate normative specifications must define accepted promotion, provenance, and traceability behavior before implementation planning. Repository-generic requirements belong under repository specification authority.
