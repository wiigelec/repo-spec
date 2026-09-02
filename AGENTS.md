# Agent and Contributor Guidance

This file is operational guidance. It does not create Design meaning or normative requirements and cannot override reviewed Design, Planning artifacts, or normative specifications under `repo/`.

## Responsibility boundaries

- **Design owns semantic meaning.**
- **Planning owns Functional Set scope, consequential technical intent, normative requirements, and evaluation classification; normative specifications live under `repo/specs/`.**
- **Build owns implementation correctness, ordinary code-level decisions, and construction of required mechanical enforcement.**
- **Validation executes mechanically decidable checks; it does not create normative intent.**
- **Semantic Review identifies discrepancies without taking ownership of reviewed decisions.**

Route defects to the stage that owns the defective decision:

- missing, incorrect, ambiguous, or contradictory semantic meaning → **Design**;
- Functional Set, Plan, normative-requirement, or evaluation-classification defect → **Planning**;
- implementation or mechanical-enforcement-construction defect → **Build**.

Do not conceal an upstream defect by inventing intent, changing scope, or redefining an obligation downstream.

## Ownership and structure

- `repo/` is the reusable repository/framework ownership domain.
- `product/` is the generic product-owned domain; do not assume it means the repo-spec initializer or another specific product.
- `scripts/` is the narrow repository-root operational composition role. It coordinates domain entry points but owns no framework or product semantics.
- Closed architectural boundaries are default-deny. Do not create a new repository-root, `repo/`, or `product/` direct-child role merely for implementation convenience.
- FS-004 authorizes `scripts/validate`; do not add other root `scripts/` entries unless later Design and Planning authorize them.
- If required behavior does not fit accepted closed structure, return upstream for Design and Planning rather than inventing a parallel namespace.

## Build discipline

Build consumes one reviewed Functional Set Planning result, its normative specification, and its bound Design revision.

A retained `design_revision` identifies the exact Design state consumed by Planning. Do not assume the originating Git object or supplier ancestry must exist in the current repository merely because the identifier is retained.

Build may make ordinary implementation decisions that preserve Design meaning, Functional Set scope, Plan intent, normative requirements, and required agent control.

If a consequential semantic decision is missing, return to Design. If a consequential technical decision or requirement classification is missing or defective, return to Planning.

Prefer the simplest implementation that satisfies the reviewed Planning result. Do not add framework machinery merely because a similar mechanism existed historically.

## Validation

Use:

```bash
scripts/validate
```

as the repository-wide mechanical Validation entry point.

The root entry point coordinates domain-owned Validation:

- `repo/scripts/validate` remains authoritative for framework mechanical checks.
- `product/scripts/validate` remains authoritative for product mechanical checks when present.

Do not place framework or product normative predicates into `scripts/validate`. Do not create an independent predicate set in CI or workflow glue. CI should invoke the root entry point and report its result.

A passing Validation result proves only mechanically checked conditions. It does not prove semantic fidelity, review convergence, or Acceptance.

## Portable history

Framework state may be installed into a repository whose Git history is independent from the supplying repo-spec repository.

Preserve exact source and Design identifiers required by accepted artifacts, but do not introduce imported ancestry, grafts, replace refs, hidden remotes, bundles, or generalized provenance machinery unless controlling Design and Planning explicitly require them.

## Semantic Review and Acceptance

After Build and required Validation, perform Build Review against the complete Planning result, normative specification, and Design revision it consumed.

Review should challenge scope drift, missing behavior, unintended additions, accidental architecture changes, and unnecessary complexity.

A satisfactory development candidate becomes accepted only through intentional integration into `main`.
