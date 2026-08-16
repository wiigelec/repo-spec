# Initializer Upgrade Decomposition: Validation, Promotion, and Outcomes

> Part 5 of 5 · [Initializer upgrade decomposition index](../INITIALIZER-UPGRADE-DECOMPOSITION.md) · [Previous](./04-reanchoring-and-provenance.md)

## Status

Directional decomposition content.

## Purpose

Bound the terminal upgrade lifecycle from validation of the complete re-anchored staged repository through promotion or non-promotion failure and finalization.

## Responsibilities

Validate the complete staged repository after managed reconciliation and re-anchoring, prevent promotion when required validation fails, promote only a validated complete target, and produce deterministic terminal evidence describing success or failure.

Define the stopping boundary for decomposition: after this area, remaining exact semantics belong to normative product specifications, and implementation planning remains blocked until those specifications are accepted.

## Boundaries

This area covers the complete staged validation gate, promotion eligibility, non-promotion on validation failure, terminal failure/recovery evidence, successful promotion outcome, cleanup/finalization responsibility, and the user-visible lifecycle completion boundary.

It coordinates the complete upgrade outcome without defining primitive/component semantics that belong in lower-Level specifications.

## Dependencies

This area depends on request/identity/eligibility, managed reconciliation selection, staged managed application/projection reconciliation, and re-anchored provenance.

A future Level 3 complete-upgrade specification is expected to coordinate accepted lower-Level responsibilities needed for the observable lifecycle outcome.

## Exclusions

This area does not define exact repository-validation command sets, exact rollback mechanism, filesystem atomic-promotion algorithm, CLI presentation, hosted orchestration, release policy, or implementation architecture.

It does not authorize implementation planning or implementation before the required normative product specification set is accepted.

## Unresolved decisions

Exact validation profile, validation-result contract, promotion atomicity, failure classification, recovery/rollback guarantees, cleanup guarantees, user-visible result schema, resumability, interruption handling, hosted execution, and release/compatibility policy remain unresolved.

Later specification work must identify which existing repository-validation, staging, execution-report, and lifecycle specifications can be reused and which upgrade-specific Level 0-3 specifications are required.

## Successor work

Create or revise and accept the owner-appropriate normative product specification set for the five decomposition areas. Likely families include minimal Level 0 upgrade-wide identity/authority/lifecycle semantics if needed; Level 1 request/identity/material/provenance/outcome primitives; Level 2 managed-selection, staged-reconciliation, re-anchoring/provenance, and validation/promotion capabilities; and a Level 3 complete derived-repository upgrade lifecycle.

Exact specification identifiers, boundaries, dependency edges, and reuse decisions remain for that governed successor work. Implementation planning is not authorized until the necessary controlling specifications are accepted.
