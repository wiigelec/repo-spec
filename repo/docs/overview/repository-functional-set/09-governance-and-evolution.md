# functional-set lifecycle: Governance and Evolution

> Part 6 of 6 · [functional-set lifecycle index](../functional-set-process.md) · [Previous](./05-human-ai-continuity.md)

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

Substantive completeness for GitHub issue and pull-request forms may be enforced by a separate hosted policy checker, not by repository-local validation.

Validation evidence should identify the exact repository state or Git revision tested.

## Authority model

The framework must keep these roles distinct:

```text
idea
overview
decomposition
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
- decomposition is not a specification;
- a plan is not product authority;
- code is not authority merely because it works;
- tests do not define semantics unless accepted specifications assign them that role;
- validation is not review;
- review is not acceptance;
- acceptance is not merge;
- merge is not release;
- completion of one issue does not authorize unrelated successor work.

Correspondence and traceability connect decomposition, implementation, and tests so that accepted work can be followed back to its owning requirement.

## Specification-change impact on plans

A material change to an accepted product specification (revision, supersession, or retirement) that an implementation plan relies upon must trigger an implementation-plan impact review. The affected plan sections must be revised or explicitly reaffirmed before implementation under the changed authority may proceed. Implementation must pause where the accepted specification and plan no longer agree.

## Plan-change impact on governing issues

A material implementation-plan change (sequencing or scope change) must be reflected in the controlling plan before affected open governing issues are updated. Completed implementation must be audited when controlling authority changes materially, and the audit results must be recorded before successor implementation proceeds.

## Exploratory experiments

The repository may classify explicitly non-product exploratory experiments. An exploratory experiment shall be isolated from maintained product paths where practical, shall not claim conformance, acceptance, release, or product status, shall not silently become maintained implementation, shall require a later governed specification and implementation process before adoption, and shall have explicit disposal, archival, or adoption criteria. Adoption of experimental work shall require accepted product specifications and an accepted implementation plan before maintained implementation may begin.

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

## Migration guidance for existing implementation

Repositories or projects whose product artifacts were implemented before the corresponding Level 0–3 product specifications were accepted may continue to operate, but the following remediation expectations apply:

- Existing implementation artifacts (code, tests, schemas, generated output) do not become normative product authority merely because they exist.
- Before new feature work may proceed on maintained product artifacts, the governing lifecycle must be satisfied: the applicable product specifications must be drafted, accepted through governed review, and referenced by an implementation plan.
- Existing implementation should be audited against accepted specifications once those specifications exist. Nonconformance found during audit should be governed as separate remediation work.
- Implementation plans created before the corrected lifecycle was established remain non-normative planning records. They should be revised or superseded under the corrected lifecycle before authorizing new implementation work.
- The corrected lifecycle does not automatically invalidate or require reversion of existing implementation. It governs only forward work and specification acceptance.

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

The decomposition invariants live with the canonical decomposition model, while this part preserves the governance boundaries that keep those invariants enforceable.
