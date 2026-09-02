# FS-004 Plan — Portable History and Validation Composition

## Technical Objective

Remove the accidental local-Git-object dependency from generic Functional Set Design binding validation and add the smallest repository-wide Validation composition mechanism needed by repositories containing framework-owned and product-owned Validation.

## Design Binding

`design_revision` remains exactly one 40-character lowercase Git revision identifier. Generic framework Validation shall validate that representation and any explicitly fixed revision value required by an existing normative requirement, but shall not generally require the referenced commit object to resolve in the current repository.

## Root Operational Role

Planning authorizes one new maintained repository-root namespace: `scripts/`.

For FS-004 its only authorized maintained entry is `scripts/validate`.

## Validation Composition

`scripts/validate` shall run `repo/scripts/validate`, stop on framework failure, then run `product/scripts/validate` when that path exists. If the product path exists it must be executable. Product failure fails repository-wide Validation. Absence of product Validation is valid before a product establishes mechanical obligations.

The root entry point coordinates domain validators and shall not implement their normative checks itself.

## Framework Validation

Framework Validation shall authorize only `scripts/validate` in the new root role, verify root-entrypoint delegation, preserve the framework-domain validator, allow non-local well-formed Design revision identifiers, preserve explicit exact-value checks, regression-test portable Design bindings and root composition, validate docs, and require CI to delegate to `./scripts/validate`.

## Documentation

README and AGENTS shall document root Validation composition, domain ownership, and portable retained Design revisions. AGENTS shall prohibit moving normative predicates into root composition or assuming retained Design revisions imply local ancestry.

## CI

`.github/workflows/validation.yml` shall invoke `./scripts/validate` and shall not directly select framework or product validators.

## Validation

Before Acceptance run `./scripts/validate`, `./repo/scripts/validate`, `./product/scripts/validate`, and `git diff --check`; confirm this Functional Set binds the Design-only commit created before Planning; then perform Build Review for scope and unnecessary complexity.
