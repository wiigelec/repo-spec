# functional-set lifecycle: Normative Requirement Validation Correspondence — Part 2

This part defines the directional package, validation-disposition, validation-task, and entry-point correspondence model.

## Validation-correspondence package

A validation-correspondence package is the durable source artifact that binds one in-scope active normative requirement to its maintained validation disposition and externally identified validation evidence.

The package is analytically distinct from:

- the normative specification;
- executable validation code;
- validation orchestration;
- test helper internals;
- generated Markdown or aggregate coverage output.

The package should remain small enough to express correspondence without duplicating normative semantics or executable implementation detail.

## Package cardinality

The directional cardinality is:

- one active correspondence package per in-scope active identified normative requirement;
- one normative requirement reference per active package;
- zero or more externally identified validation tasks per package.

Package completeness and executable task population are separate concerns.

A requirement may legitimately have an active package with no executable task when its accepted validation disposition explains why mechanical validation is absent.

This prevents the correspondence model from inventing meaningless executable checks merely to satisfy package cardinality.

## Validation disposition

The collected request proposed these dispositions:

- `mechanical`;
- `partial`;
- `semantic-review`;
- `not-applicable`.

The functional-set direction accepts the need for explicit validation disposition metadata and accepts these names as the current directional vocabulary.

Downstream specification must still define:

- exact meaning of each disposition;
- whether the vocabulary is exhaustive;
- allowed transitions;
- rationale requirements;
- how mixed mechanical and non-mechanical coverage is represented;
- how disposition affects completeness and reporting.

Non-mechanical or incomplete mechanical validation should remain explainable rather than silently appearing as missing coverage.

## Externally identified validation tasks

The correspondence model needs stable identity for maintained validation tasks that are represented as correspondence evidence.

It does not require every helper function, fixture, parameter case, assertion, or internal implementation unit to become a separately registered task.

An externally identified validation task should be a maintained executable validation responsibility that downstream tooling can identify, resolve, and report.

Exact task-granularity rules remain downstream specification work.

## Task ownership and uniqueness

Each externally identified validation task should:

- have stable identity within the accepted correspondence scope;
- resolve to a maintained source location or executable entry point;
- belong to exactly one active correspondence package;
- thereby correspond to exactly one canonical normative-requirement reference;
- avoid duplicate registration in an independent aggregate registry.

Shared helpers may support many tasks without becoming independent correspondence entries unless they themselves are deliberately exposed as maintained validation responsibilities.

## Task classification dimensions

The original proposal listed:

- positive;
- negative;
- boundary;
- regression;
- unit;
- integration.

The analysis found that these values mix different dimensions.

The functional-set direction therefore separates at least:

- **purpose or coverage intent**, such as positive, negative, boundary, or regression;
- **execution level**, such as unit or integration.

The exact vocabulary, multiplicity, and cardinality of each dimension remain downstream specification decisions.

A validation task may legitimately be, for example, both negative in coverage intent and integration-level in execution.

## Entry-point correspondence

Machine-readable entry-point metadata should agree with package ownership.

The directional invariant is that executable validation entry points are resolvable from the canonical correspondence model without creating a second independently maintained mapping of requirements to tasks.

The exact realization may use source annotations, decorators, manifests, generated adapters, or another mechanism selected downstream.

This functional set does not select that syntax.

## Source-of-truth boundary

The durable correspondence package set is the source model.

Aggregate coverage tables, Markdown summaries, indexes, and similar views should be deterministic subordinate projections.

Generated views must not become independent editing surfaces for correspondence authority.

If generated output diverges from canonical package sources, the generated output is stale and should be regenerated or rejected.

## Broad and parameterized tests

Existing tests may exercise multiple cases, boundaries, or contract aspects.

The functional set does not require every current test file or test function to map one-to-one with a package.

Downstream migration may:

- split broad tests;
- introduce explicit externally identified task wrappers;
- retain parameterized execution behind one stable task identity;
- preserve shared helpers outside the correspondence registry.

The selected migration must keep correspondence truthful without forcing artificial implementation structure.
