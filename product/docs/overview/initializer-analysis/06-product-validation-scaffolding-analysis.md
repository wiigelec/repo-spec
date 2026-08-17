# Product validation scaffolding analysis

> Part 6 of 6 · [Repo-Spec Initializer analysis](../INITIALIZER-ANALYSIS.md) · [Previous](./05-derived-repository-upgrade-handoff.md)

## Status

Candidate analysis. Directional and non-normative.

## Source evidence

The collected product-validation-scaffolding intake requests useful validation support in newly initialized repositories during design and planning, with obvious product-owned extension points for later product-specific validation.

Accepted initializer direction already treats validation and a locally valid, self-contained initialized repository as core outcomes. Current implementation and fresh-derived-repository audit evidence also show that transported CI can reference repository-relative test commands that exist in repo-spec but are absent from initialized output. Production validation can therefore pass while the common CI contract fails.

Existing code, workflow text, generated output, and prior behavior remain evidence rather than authority.

## Candidate capability grouping

A strong candidate direction is one common GitHub validation workflow for repo-spec and initialized repositories. Repository-class differences should stay behind stable repository-local entrypoints rather than workflow forks.

Candidate stable surfaces are:

- `repo/scripts/test-validation` for repository validator self-tests;
- `product/scripts/test-validation` for product validator self-tests;
- `product/scripts/test-product` for broader product-owned implementation tests.

Within repo-spec, the Repo-Spec Initializer is the product, so its full implementation test suite can run behind `product/scripts/test-product`. In a fresh derived repository, that same surface can initially have zero applicable product tests until governed product development establishes product behavior and corresponding tests.

The generic `test-product` name keeps the common CI contract product-owned instead of encoding repo-spec's current product identity as an initializer.

## Zero-applicable-test state

A new repository can legitimately have no governed product implementation tests yet. Later normative stages should therefore distinguish:

- zero applicable tests for the current lifecycle/product state; from
- missing required tests, entrypoints, or transported dependencies.

A zero-applicable result may succeed only because no governed tests apply, not because expected tests are silently absent. Exact diagnostics, discovery, activation, and exit semantics remain unresolved.

## Dependencies and ownership

This direction depends on initializer generation, framework installation, validation, and maintained-project handoff.

Candidate ownership is:

- repository production validation behind `repo/scripts/validate`;
- product production validation behind `product/scripts/validate`;
- repository validation self-tests behind `repo/scripts/test-validation`;
- product validation self-tests behind `product/scripts/test-validation`;
- broader product tests behind `product/scripts/test-product`;
- initializer installation responsible for making every installed common-CI repository-relative command resolvable.

This preserves the distinction between stable framework interfaces and repo-spec's complete source-development test implementation. Derived repositories need not receive the entire source test tree merely to satisfy the common CI interface.

## Ambiguities

Successor stages must still decide:

- wrapper/stub/dispatcher representation;
- exact zero-applicable semantics and diagnostics;
- which self-tests are portable framework scaffolding;
- how `test-product` discovers later product tests;
- exact common-CI orchestration;
- how output inventory proves executable-reference closure;
- upgrade compatibility when common entrypoints evolve.

No exact runtime implementation, schema, plugin/hook system, inventory mutation, or release behavior is selected here.

## Candidate functional-set and core implications

This direction belongs with original initializer validation/generation rather than derived-repository upgrade because the demonstrated failure exists immediately after generation.

A successor candidate should preserve these outcomes:

- fresh initialized repositories can execute their unchanged common validation workflow;
- every required repository-relative CI executable resolves in initialized output or through an accepted external/platform dependency;
- stable repository- and product-owned validation/test entrypoints exist from initialization onward;
- product implementation testing uses the generic `product/scripts/test-product` surface;
- zero-applicable product-test state is explicit and honest;
- source-only repo-spec development tests are not transported merely to preserve the interface.

These remain candidate conclusions. Functional-set approval, decomposition, specifications, planning, initializer/runtime mutation, and release behavior require separately governed successor work.

## Successor handoff

Later approved specifications should define the exact common-CI command contract, `test-product` behavior, zero-applicable semantics, installation inventory, executable-reference closure checks, compatibility, and failure diagnostics before implementation.

A useful eventual acceptance condition, subject to later approval, is that a fresh initialization from an accepted repo-spec revision produces a repository whose transported GitHub validation workflow passes in full on its first push without manual post-initialization additions.
