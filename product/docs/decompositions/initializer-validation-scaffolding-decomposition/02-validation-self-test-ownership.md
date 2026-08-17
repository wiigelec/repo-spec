# Initializer Validation Scaffolding Decomposition: Validation Self-Test Ownership

> Part 2 of 4 · [Initializer validation scaffolding decomposition index](../INITIALIZER-VALIDATION-SCAFFOLDING-DECOMPOSITION.md) · [Previous](./01-validation-workflow-and-interface-ownership.md) · [Next](./03-product-test-lifecycle.md)

## Status

Directional decomposition content.

## Purpose

Bound repository/framework validation self-test and product validation self-test responsibilities behind the stable validation/test surfaces used by common CI.

## Responsibilities

Assign repository/framework validation self-test responsibility to the repository-owned validation domain and product validation self-test responsibility to the product-owned validation domain.

Preserve the analysis-selected direction for `repo/scripts/test-validation` and `product/scripts/test-validation` as stable installed interfaces while leaving exact implementation and command semantics unresolved.

Ensure initialized repositories receive enough portable self-test capability to exercise their installed validation responsibilities without implying that repo-spec's full source-development-only test harness must be transported.

Keep validation self-tests distinct from production validation (`repo/scripts/validate` and `product/scripts/validate`) and from generic product implementation tests.

## Boundaries

This area covers self-test ownership, portability responsibility, installed-versus-source-development boundary, and the relationship between self-tests and stable common-CI interfaces.

It does not decide exact self-test cases, fixtures, test framework, packaging layout, execution engine, invocation ordering, diagnostic text, or whether repository and product self-tests share internal libraries.

## Dependencies

This area depends on the stable workflow/interface ownership area for the interfaces through which self-tests participate.

The initialized-output closure area depends on this area to identify which self-test surfaces and supporting material must be present when common CI references them.

Likely downstream specification work may include Level 1 self-test identity/applicability primitives and Level 2 portable self-test ownership/execution capabilities where independently useful.

## Exclusions

This area does not change production validation behavior, implement validators or self-tests, define exact test inventories, require transport of repo-spec's complete source-development test tree, or define product implementation-test semantics.

It does not establish exact compatibility or upgrade propagation behavior.

## Unresolved decisions

Exact portable self-test inventory, fixtures, discovery, support-library installation, execution mechanism, result schema, exit semantics, diagnostics, compatibility, and the boundary between installed portable tests and repo-spec-only development tests remain unresolved.

Later normative specification work must determine reuse of existing validation specifications and whether separate repository-owned and product-owned product specifications are needed for all details.

## Successor work

Create or revise and accept normative product specifications that define portable validation self-test ownership and the installed capability required by common CI while preserving repository/framework versus product authority boundaries.

Implementation of self-test scripts, fixtures, or transported test support remains unauthorized until those specifications are accepted.
