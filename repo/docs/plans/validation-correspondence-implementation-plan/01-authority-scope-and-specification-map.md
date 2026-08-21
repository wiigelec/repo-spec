# Authority, scope, and specification map

## Purpose

Define the repository-generic implementation-planning authority basis, bounded realization scope, cross-domain handoff boundary, and specification map for the validation-correspondence capability.

## Authority and basis

Feature request #550 progressed through collection (#551), analysis (#555), functional-set approval (#557 / PR #558), decomposition (#559 / PR #560), and complete normative specification (#561 / PRs #562–#567). The final specification-stage audit found zero material normative gaps.

Implementation must realize accepted semantics rather than the literal non-authoritative design proposal where the accepted lifecycle normalized it.

The controlling accepted semantic model includes:

- composite canonical normative references using `spec_id` plus `requirement_id`;
- one active canonical package per active requirement in accepted repository and product authority;
- package ownership by normative domain rather than execution location;
- explicit validation disposition independent of task population;
- stable task identity separated from mutable source coordinates;
- source-local validation-task/helper role auditability;
- one canonical source metadata mechanism per implementation language across validation domains;
- product test mappings resolving through canonical `validation_package_refs`;
- deterministic subordinate projections and authority-preserving materialization;
- lifecycle-valid preparatory and historical correspondence;
- Atomic eligibility only when no valid intermediate accepted revision exists.

## Repository-generic scope

This plan coordinates implementation of:

1. the dedicated subordinate package JSON Schema authorized by `repo.validation-correspondence`;
2. repository-generic package parsing/structural validation support;
3. repository-generic source-local role/correspondence metadata mechanism and stable task identity rules;
4. canonical repository-owned package population;
5. framework mechanics for discovering product-owned correspondence obligations and validating repository-generic invariants without mutating product-owned artifacts under repository-only authority;
6. mechanical correspondence integrity validation in repository/product/root responsibility boundaries;
7. deterministic repository-generic generated/reporting projections where useful;
8. repository-generic propagation/materialization and freshness/equivalence checking for actual framework-owned maintained surfaces;
9. staged repository-generic migration while preserving valid accepted revisions;
10. explicit handoff requirements for product-owned realization.

## Product-owned handoff

This plan does not authorize direct mutation of product-owned validation packages, product-specification `correspondence` declarations, product test-artifact mappings, product-specific implementation/test/conformance artifacts, or product-specific materialization surfaces.

After this plan is explicitly accepted, product-owned realization shall proceed through separately governed product-owned planning/implementation authority that cites the exact applicable accepted product specifications for the product scope being changed.

Repository-generic work may enumerate or inspect accepted product specifications to compute obligations and may validate common correspondence invariants, but inspection or common-law enforcement does not convert product-owned mutation into repository-owned implementation authority.

## Explicit exclusions

The plan does not authorize new repository or product semantics, duplicate correspondence registries, bare global requirement-ID joins, package ownership based only on execution location, or a mandatory per-package Markdown projection.

The plan does not itself create or modify schema, package, source-tagging, validation, initializer, generated-report, product, or migration artifacts.

Candidate-plan merge does not constitute acceptance.

## Specification map

| Concern | Primary controlling specifications |
| --- | --- |
| semantic package/reference/task/lifecycle contract | `repo.validation-correspondence` |
| subordinate/generated authority boundary | `repo.authority-model` |
| package artifact classification | `repo.artifact-taxonomy` |
| package/schema/validation-domain structural envelopes | `repo.repository-structure` |
| delegated enforcement and public validation boundaries | `repo.validation` |
| repository-generic product correspondence law | `repo.product-correspondence` |
| product specification registry/lifecycle discovery | `repo.product-manifest`, `repo.product-spec-base` |
| valid intermediate states and Atomic eligibility | `repo.development-workflow` |
| product-specific maintained-artifact realization | separately governed accepted product specifications and product-owned plan authority |

Every repository-generic implementation issue must use its workstream's exact authority set rather than treating this table as a substitute for `workstream_authority`.
