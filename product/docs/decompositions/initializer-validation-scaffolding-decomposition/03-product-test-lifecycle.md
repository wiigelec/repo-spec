# Initializer Validation Scaffolding Decomposition: Product-Test Lifecycle

> Part 3 of 4 · [Initializer validation scaffolding decomposition index](../INITIALIZER-VALIDATION-SCAFFOLDING-DECOMPOSITION.md) · [Previous](./02-validation-self-test-ownership.md) · [Next](./04-initialized-output-closure-and-installation.md)

## Status

Directional decomposition content.

## Purpose

Bound the lifecycle for generic product-owned implementation testing, including the legitimate zero-applicable state of a fresh initialized repository and the later transition to governed applicable product tests.

## Responsibilities

Preserve `product/scripts/test-product` as the analysis-selected generic product-owned implementation-test surface rather than naming repo-spec's initializer as the universal product.

Represent an honest zero-applicable product-test state when a repository truly has no governed applicable product implementation tests yet.

Distinguish that legitimate state from missing required commands, missing dependencies, broken discovery, or an expected-but-undiscovered governed test suite.

Provide direction for later transition from zero applicable tests to one or more governed applicable product tests without requiring common CI to be rewritten for each product.

## Boundaries

This area covers product-test applicability, ownership, lifecycle state, generic surface direction, and the distinction between honest absence and failure.

It does not define exact discovery, registry format, test selection algorithm, activation event, output wording, exit codes, test runner, test framework, or product-specific test semantics.

## Dependencies

This area depends on stable workflow/interface ownership and is distinct from validation self-test ownership.

The initialized-output closure area depends on this area because the generic `product/scripts/test-product` interface must remain resolvable even when the applicable governed product-test count is zero.

Likely downstream specification work may include Level 1 applicable-test-state or product-test-surface primitives and Level 2 product-test lifecycle resolution. A Level 3 complete validation-scaffolding lifecycle is needed only if lower-Level contracts cannot fully coordinate the observable outcome.

## Exclusions

This area does not implement initializer tests, define any concrete product test suite, make zero-applicable equivalent to success when expected tests are missing, or choose discovery/registration architecture.

It does not authorize weakening validation or silently suppressing failures.

## Unresolved decisions

Exact applicability model, governed test registration, discovery paths, activation triggers, expected-suite evidence, zero-applicable diagnostics, exit semantics, missing-test classification, deterministic ordering, compatibility, and user-facing result reporting remain unresolved.

Later normative specification work must define how the system can prove that zero applicable tests is legitimate rather than accidental absence.

## Successor work

Create or revise and accept normative product specifications for generic product-test surface identity, applicability/lifecycle semantics, honest zero-applicable behavior, and failure distinction.

Implementation of `product/scripts/test-product`, product-test discovery, or zero-state reporting remains unauthorized until the necessary specifications are accepted.
