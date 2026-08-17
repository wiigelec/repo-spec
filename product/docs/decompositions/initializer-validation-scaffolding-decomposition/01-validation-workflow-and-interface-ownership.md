# Initializer Validation Scaffolding Decomposition: Validation Workflow and Interface Ownership

> Part 1 of 4 · [Initializer validation scaffolding decomposition index](../INITIALIZER-VALIDATION-SCAFFOLDING-DECOMPOSITION.md) · [Next](./02-validation-self-test-ownership.md)

## Status

Directional decomposition content.

## Purpose

Bound the responsibility for a common validation workflow and the stable installed repository-relative interfaces through which repository/framework validation self-tests, product validation self-tests, and generic product implementation tests can participate without requiring repository-class-specific workflow forks.

## Responsibilities

Preserve the approved direction that repo-spec and initialized repositories share one common GitHub validation workflow while repository-class differences remain behind stable installed interfaces.

Keep production validation responsibilities distinct from validation self-tests and product implementation-test responsibilities. The analysis-selected interface direction includes `repo/scripts/test-validation`, `product/scripts/test-validation`, and `product/scripts/test-product`, but this decomposition does not define their exact runtime contracts.

Provide the upstream ownership boundary that later self-test, product-test, and initialized-output-closure areas depend on.

## Boundaries

This area covers workflow/interface responsibility, ownership separation, stable repository-relative surface direction, and the requirement that common CI depend on installed interfaces rather than source-development-only implementation details.

It does not decide workflow YAML structure, exact job or step order, shell versus Python wrappers, dispatcher topology, output formats, retry policy, platform-specific realization, or whether lower-level interfaces internally share implementation.

## Dependencies

This area depends on the approved validation-scaffolding functional set and accepted analysis direction.

Validation self-test ownership, product-test lifecycle, and initialized-output closure depend directionally on the stable interface boundary established here.

Likely downstream specification work may include minimal Level 0 shared lifecycle/authority semantics if genuinely required and Level 1 or Level 2 contracts for stable surface identity and common orchestration responsibility.

## Exclusions

This area does not modify `.github/workflows/validation.yml`, define exact commands, implement scripts, change production validation semantics, select implementation architecture, or authorize transport of repo-spec's complete source-development test tree.

It does not define product-test discovery or zero-applicable behavior beyond recognizing those as downstream responsibilities.

## Unresolved decisions

Exact workflow orchestration, invocation ordering, external/platform dependencies, wrapper/stub/dispatcher shape, command output and exit contracts, diagnostics, compatibility guarantees, and hosting-platform-specific realization remain unresolved.

Later normative specification work must decide whether stable interface identity is best represented as Level 1 primitives, Level 2 orchestration capabilities, or reused accepted specifications.

## Successor work

Create or revise and accept the owner-appropriate normative product specifications that define the common workflow/interface contract and its relationship to downstream self-test, product-test, and closure responsibilities.

Implementation planning and workflow/script mutation remain unauthorized until the necessary normative specifications are accepted.
