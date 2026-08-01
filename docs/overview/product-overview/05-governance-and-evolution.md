# Product Overview: Governance and Evolution

> Part 5 of 5 · [Product overview index](../PRODUCT-OVERVIEW.md) · [Previous](./04-human-ai-continuity.md)

This part defines validation and authority boundaries, generated artifacts, portability, derived-product separation, and development continuity.

## Validation model

The framework should provide stable repository-local validation entry points.

Validation should eventually cover:

- repository structure;
- artifact placement;
- specification structure;
- schemas;
- references;
- manifests;
- identity rules where applicable;
- conformance artifacts;
- source layout;
- generated artifacts;
- projection freshness;
- product tests;
- packaging;
- text and diff hygiene.

Validation establishes only the properties it is designed to check. A passing validation result is not semantic review or acceptance.

Validation evidence should identify the exact repository state or Git revision tested.

## Authority model

The framework must keep these roles distinct:

```text
idea
overview
plan
candidate specification
accepted normative specification
product artifact
validation evidence
review
acceptance
merge
release
```

No role silently substitutes for another.

In particular:

- an overview is not a specification;
- a plan is not product authority;
- code is not authority merely because it works;
- tests do not define semantics unless accepted specifications assign them that role;
- validation is not review;
- review is not acceptance;
- acceptance is not merge;
- merge is not release;
- completion of one issue does not authorize unrelated successor work.

## Generated and derived artifacts

The framework may support deterministic generated or derived artifacts, including Markdown projections, schemas, indexes, manifests, and documentation.

Every generated artifact should have:

- an identified source;
- a declared generator or derivation rule;
- deterministic output;
- reproducibility checks;
- freshness validation;
- a clear statement that it does not independently override its source authority.

Hand editing a generated projection must not silently revise normative authority.

## Portability

A completed framework should be usable to initialize more than one product repository.

Portable behavior should not depend on:

- product-specific identity families;
- product operation or result contracts;
- maintained runtime modules;
- one product’s source structure;
- one hosting provider’s APIs;
- prior chatbot conversations.

Repository-generic mechanisms must be separable from product-specific profiles.

## Relationship to the derived product

A future product may be derived from this framework.

A future derived repository may define:

- governed operation descriptions;
- operation dispatch;
- effects;
- execution records;
- authoritative results;
- validation;
- repository and remote mutations;
- publication;
- failure and recovery behavior.

Those concepts will be governed by the future product’s own overview, plan, specifications, implementation, and acceptance records.

Bootstrap development infrastructure may remain in this repository while the framework evolves. Its existence does not define the desired reusable product outcome.

## Development continuity

The repository contains accepted specifications and implementation that support the current framework.

The framework must:

- identify which artifacts remain reusable;
- identify which artifacts belong only to the future product;
- identify which artifacts require revision or supersession;
- preserve working bootstrap development infrastructure until a replacement is accepted;
- avoid product leakage into repository-generic authority;
- use bounded governed issues;
- keep the repository valid while changes are made;
- avoid combining product redefinition, renaming, authority replacement, implementation removal, and final cutover into one change.

This overview establishes direction only. Detailed sequencing belongs in the current governing issue for active bounded work. Historical plans provide context only and do not authorize new work.
