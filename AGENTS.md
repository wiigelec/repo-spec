# Agent and Contributor Guidance

This file is operational guidance. It does not create Design meaning or normative requirements and cannot override the reviewed Design, Planning artifacts, or normative specifications under `repo/`.

## Responsibility boundaries

- **Design owns semantic meaning.**
- **Planning owns Functional Set scope, consequential technical intent, normative requirements, and evaluation classification; the resulting normative specifications live under `repo/specs/`.**
- **Build owns implementation correctness, ordinary code-level decisions, and construction of required mechanical enforcement.**
- **Validation executes mechanically decidable checks; it does not create normative intent.**
- **Semantic Review identifies discrepancies without taking ownership of the decisions being reviewed.**

Route defects to the stage that owns the defective decision:

- missing, incorrect, ambiguous, or contradictory semantic meaning → **Design**;
- Functional Set, Plan, normative-requirement, or evaluation-classification defect → **Planning**;
- implementation or mechanical-enforcement-construction defect → **Build**.

Do not conceal an upstream defect by inventing intent, changing scope, or redefining an obligation downstream.

## Ownership and structure

- `repo/` is the reusable repository/framework ownership domain.
- `product/` is the generic product-owned domain; do not assume it means the repo-spec initializer or any other specific product.
- Closed architectural boundaries are default-deny. Do not create a new repository-root, `repo/`, or `product/` direct-child role merely for implementation convenience.
- Ordinary nested implementation structure remains allowed inside an authorized extensible role when it preserves that role and the governing upstream intent.
- If a required capability does not fit the accepted closed structure, return upstream for the Design and Planning decision rather than inventing a parallel namespace.

## Build discipline

Build consumes one reviewed Functional Set Planning result, its normative specification, and its bound Design revision.

Build may make ordinary implementation decisions that preserve Design meaning, Functional Set scope, Plan intent, normative requirements, and required agent control.

If a consequential semantic decision is missing, return to Design. If a consequential technical decision or requirement classification is missing or defective, return to Planning.

Prefer the simplest implementation that satisfies the reviewed Planning result. Do not add framework machinery merely because a similar mechanism existed historically.

## Validation

Use:

```bash
repo/scripts/validate
```

as the canonical mechanical Validation entry point.

Do not create a second normative validator in CI or workflow glue. CI may invoke the canonical entry point and report its result.

A passing Validation result proves only the mechanically checked conditions. It does not prove semantic fidelity, review convergence, or Acceptance.

## Semantic Review and Acceptance

After Build and required Validation, perform Build Review against the complete Planning result, the normative specification, and the Design revision it consumed.

Review should challenge scope drift, missing behavior, unintended additions, accidental architecture changes, and unnecessary complexity.

A satisfactory development candidate becomes accepted only through intentional integration into `main`.
