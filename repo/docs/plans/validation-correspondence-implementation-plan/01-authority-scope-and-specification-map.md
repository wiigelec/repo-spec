# Authority, scope, and specification map

## Purpose

Define the implementation-planning authority basis, bounded realization scope, and specification map for the validation-correspondence capability.

## Authority and basis

Feature request #550 progressed through collection (#551), analysis (#555), functional-set approval (#557 / PR #558), decomposition (#559 / PR #560), and complete normative specification (#561 / PRs #562–#567). The final specification-stage audit found zero material normative gaps.

Implementation must therefore realize accepted semantics rather than the literal non-authoritative design proposal where the accepted lifecycle normalized it.

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

## Scope

This plan coordinates implementation of:

1. the dedicated subordinate package JSON Schema already authorized by `repo.validation-correspondence`;
2. canonical package parsing/structural validation support;
3. source-local role/correspondence metadata realization for maintained validation callables;
4. stable validation-task identity and source resolution;
5. canonical package population for active repository and product requirements;
6. product correspondence reconciliation through canonical package references;
7. mechanical correspondence integrity validation in repository/product/root responsibilities;
8. deterministic generated/reporting projections where useful;
9. propagation/materialization and freshness/equivalence checking where required by maintained framework surfaces;
10. staged migration from the pre-correspondence state while preserving valid accepted revisions.

## Explicit exclusions

The plan does not authorize new repository semantics, duplicate correspondence registries, bare global requirement-ID joins, package ownership based only on execution location, or a mandatory per-package Markdown projection.

The plan does not itself create or modify schema, package, source-tagging, validation, initializer, generated-report, or migration artifacts.

Product semantic ownership remains with accepted product specifications. Validation correspondence supplies repository-generic correspondence law only.

## Specification map

| Concern | Primary controlling specifications |
| --- | --- |
| semantic package/reference/task/lifecycle contract | `repo.validation-correspondence` |
| subordinate/generated authority boundary | `repo.authority-model` |
| package artifact classification | `repo.artifact-taxonomy` |
| package/schema/validation-domain structural envelopes | `repo.repository-structure` |
| delegated enforcement and public validation boundaries | `repo.validation` |
| product test mapping/conformance reconciliation | `repo.product-correspondence` |
| product specification registration/lifecycle | `repo.product-manifest`, `repo.product-spec-base` |
| valid intermediate states and Atomic eligibility | `repo.development-workflow` |

Every implementation issue must use its workstream's exact authority set rather than treating this table as a substitute for `workstream_authority`.
