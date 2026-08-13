# functional-set lifecycle: Product Direction

> Part 1 of 6 · [functional-set lifecycle index](../functional-set-process.md) · [Next](./02-decomposition-model.md)

This part defines the framework’s intended outcome, audience, success conditions, and explicit boundaries.

## Status

Product-direction overview.

This document records the intended outcome and development model for this repository. It is directional and non-normative.

It does not replace accepted normative specifications, authorize repository mutations, or define detailed implementation requirements. Normative behavior remains governed by accepted specifications until those specifications are explicitly revised, superseded, or retired through bounded governed work.

The project name is intentionally unresolved. A separate future product derived from this repository framework may choose its own name.

## Product vision

repo-spec is a top-down engineering framework for AI-assisted software development. It progressively reduces complex conversational human intent into smaller units whose role and authority become increasingly explicit and more precisely governed until each remaining task is sufficiently bounded for reliable AI implementation.

Its delivery mechanism is a reusable, Git-native repository framework and template for developing a high-level product idea into a specified, validated, released, and maintainable product.

The framework is designed for collaboration between human maintainers and AI chatbots. It preserves enough durable context in the repository and its Git-compatible development records for an independent AI session to understand the product, recover current work, propose bounded changes, validate results, and continue development without depending on prior conversation history.

The framework uses decomposition to reduce ambiguity before implementation.

The central product-development loop is:

```text
overview → plan → specifications → product artifacts
```

The loop is iterative rather than strictly one-way. Discoveries made during specification, implementation, validation, review, or maintenance may require revisions at an earlier layer.

Changes must be made at the layer that owns the affected decision. Product code must not silently resolve an ambiguity owned by a specification, a specification must not silently invent direction absent from the overview or plan, and a plan must not silently become normative product authority.

## Desired outcome

A repository created from this framework should be capable of progressing from an uncertain high-level idea to a maintained product through explicit, reviewable, and recoverable stages.

The framework should provide:

- a predictable repository structure;
- clear artifact roles and authority boundaries;
- a durable functional-set lifecycle;
- non-normative implementation planning;
- normative repository and product specifications;
- maintained product artifacts;
- schemas and conformance artifacts where appropriate;
- deterministic validation;
- generated and derived artifact handling;
- Git-based change isolation and revision evidence;
- issue- and review-based bounded development;
- independent AI-session recovery;
- explicit acceptance, release, and maintenance boundaries.

The framework itself is not primarily a universal operation-processing runtime.

A governed execution product may later be created as a separate repository derived from this template. Its operation, effect, execution-record, and authoritative-result semantics will belong to that product rather than to the reusable framework.

## Intended users

The framework is intended for:

- human product owners defining outcomes and approving material decisions;
- human developers implementing and validating product behavior;
- AI chatbots performing repository orientation, analysis, planning, implementation support, validation review, and bounded development work;
- reviewers evaluating exact proposed revisions;
- maintainers evolving a released product over time.

The framework should support small projects without requiring unnecessary ceremony while remaining capable of supporting large, long-lived, specification-driven products.

## Success conditions

The framework succeeds when a repository initialized from it can:

- begin from a high-level product idea;
- record a useful overview;
- produce a dependency-aware implementation plan;
- develop and accept normative specifications;
- implement conforming product artifacts;
- validate repository and product state deterministically;
- support bounded Git-based development;
- support independent AI chatbot sessions;
- preserve durable authority and decision context;
- distinguish generic framework behavior from product-specific behavior;
- release and maintain exact product revisions;
- evolve through reviewable governed changes.

The framework should ultimately be capable of being used to construct a separate product without importing product-specific semantics into the template itself.

## Explicit non-goals

This overview does not define:

- the final project name;
- the final repository layout;
- final specification schemas;
- final identity families;
- final manifest or sealing behavior;
- a universal product architecture;
- one mandatory programming language;
- one mandatory build system;
- one mandatory hosting platform;
- automatic acceptance by AI;
- replacement of human product judgment;
- immediate removal of the bootstrap executor;
- immediate migration of existing product specifications;
- the future product contract;
- final framework cutover.

Those decisions require the revised implementation plan and separately governed issues.
