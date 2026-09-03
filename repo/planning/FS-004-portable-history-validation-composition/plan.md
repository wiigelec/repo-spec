# FS-004 Plan — Portable History and Validation Composition

## Technical Objective

Remove the accidental local-Git-object dependency from generic Functional Set Design binding validation and add the smallest repository-wide Validation composition mechanism needed by repositories containing framework-owned and product-owned Validation.

## Design Binding

`design_revision` remains exactly one 40-character lowercase Git revision identifier. Generic framework Validation shall validate that representation and any explicitly fixed revision value required by an existing normative requirement, but shall not generally require the referenced commit object to resolve in the current repository.

## Installed Framework Snapshot

`repo/validation/framework-source.json` is the existing installed-framework source record. Its presence is sufficient to identify an installed framework snapshot; FS-004 adds no mode field, state machine, or second validator.

An installed snapshot may omit `repo/planning/`. When the source record exists, framework Validation shall skip checks whose subject is framework-development Planning history and shall derive requirement classification/state needed for manifest validation directly from `repo/specs/`. All other applicable framework Validation remains active.

## Root Operational Role

Planning authorizes one new maintained repository-root namespace: `scripts/`.

For FS-004 its only authorized maintained entry is `scripts/validate`.

## Validation Composition

`scripts/validate` shall run `repo/scripts/validate`, stop on framework failure, then require and run executable `product/scripts/validate` whenever the maintained `product/` ownership domain is present. Product Validation failure fails repository-wide Validation. A product with no current mechanical obligations is represented by an empty valid product manifest and a passing canonical product validator, not by omission of the product Validation substrate.

The root entry point coordinates domain validators and shall not implement their normative checks itself.

## Framework Validation

Framework Validation shall authorize only `scripts/validate` in the new root role, verify root-entrypoint delegation, preserve the framework-domain validator, allow non-local well-formed Design revision identifiers, preserve explicit exact-value checks, regression-test portable Design bindings and root composition, validate docs, and require CI to delegate to `./scripts/validate`.

## Documentation

README and AGENTS shall document root Validation composition, domain ownership, and portable retained Design revisions. AGENTS shall prohibit moving normative predicates into root composition or assuming retained Design revisions imply local ancestry.

## CI

`.github/workflows/validation.yml` shall invoke `./scripts/validate` and shall not directly select framework or product validators.

## Validation

Before Acceptance run `./scripts/validate`, `./repo/scripts/validate`, `./product/scripts/validate`, and `git diff --check`; confirm this Functional Set binds the Design-only commit created before Planning; then perform Build Review for scope and unnecessary complexity.

## Issue #12 Product Validation Contract

Framework Validation shall enforce the following generic product Validation contract when maintained `product/` exists:

- `product/scripts/validate` is executable and is the canonical product-domain entry point;
- the entry point is a narrow launcher that delegates to `product/validation/validate_product.py` and forwards arguments unchanged;
- `product/validation/requirement-evaluation.json` exists and has the same versioned `bindings` shape used by framework Validation;
- product normative requirement identity and mechanical classification are derived from maintained `product/specs/`;
- every active product requirement classified `M` or `B` has exactly one manifest binding with at least one task;
- active `S` requirements and inactive requirements have no mechanical binding;
- every manifest requirement exists in product specifications;
- task lists are non-empty, contain unique task identities, and every referenced task resolves through the canonical product validator;
- `product/scripts/validate --list-tasks` prints the available product validation task identities, one per line;
- `product/scripts/validate --task <task>` executes one named task and fails for an unknown task;
- `product/scripts/validate` with no task argument executes the distinct tasks required by the active product manifest and fails if any required task fails.

The standardized launcher and task interface exist only to make framework-owned structural and traceability checks reliable. Product task implementation may invoke project-native tools and remains owned by `product/validation/`.

Framework Validation shall not execute a product task merely to determine whether the task identity resolves. Product-specific predicates are executed by product Validation.

Regression coverage shall include missing product entry point, non-executable entry point, launcher drift, missing or malformed product manifest, unbound mechanical product requirements, impermissible semantic-only bindings, unknown requirements, duplicate bindings/tasks, unresolved task identities, product Validation failure propagation, and the valid empty-manifest state.
