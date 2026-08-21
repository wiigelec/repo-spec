# Validation-domain ownership and product reconciliation

## Status

Directional decomposition content.

## Purpose

Define repository-constitutional ownership and applicability for normative validation correspondence across repository-owned, product-owned, and whole-checkout validation domains, including reconciliation with existing product correspondence authority.

## Responsibilities

- establish one repository-defined common correspondence contract applicable to active repo-owned and product-owned normative requirements;
- preserve product specifications as semantic owners of product requirements while preventing product authority from redefining repository-generic correspondence law;
- require repository-authorized structural representation of common correspondence roles across applicable root, repo, and product validation domains;
- preserve distinct domain ownership without creating duplicate canonical packages for the same requirement;
- define the responsibility boundary for inherently cross-domain or whole-checkout correspondence;
- explicitly reconcile the new validation-correspondence graph with accepted repo.product-correspondence so requirement-to-validation relationships are not independently authored twice.

## Boundaries

This area establishes constitutional ownership and reconciliation responsibilities. It does not authorize `validation/packages/`, `repo/validation/packages/`, or `product/validation/packages/`, select package placement, or choose the normalization strategy for repo.product-correspondence.

Structural symmetry means corresponding repository-authorized roles where the common concept applies, not byte-for-byte identical validation domains or duplicate package populations.

## Dependencies

Depends on Validation-correspondence Package Model and Validation-task Correspondence and Source Auditability.

Also depends on repo.validation, repo.repository-structure, repo.product-spec-base, repo.product-correspondence, artifact taxonomy, and repository authority delegation rules.

Feeds Correspondence Integrity, Propagation, and Migration.

## Exclusions

- no validation-domain directory creation;
- no exact package placement rule;
- no product-specification mutation;
- no exact repo.product-correspondence normalization;
- no transfer of repo-owned normative authority into product authority;
- no duplicate root-owned package solely because a task executes from root validation.

## Cross-cutting concerns

- repository constitutional consistency across source and initialized repositories;
- semantic ownership versus physical validation placement;
- default-deny structural envelopes;
- avoiding duplicate requirement-to-test registries;
- explicit delegation for any domain-specific exception.

## Unresolved decisions

- exact repository specification family that owns the common package contract;
- exact structural role selected for common correspondence;
- legitimate ownership semantics, if any, for whole-checkout canonical packages;
- exact normalization strategy for repo.product-correspondence;
- which existing product correspondence fields remain canonical for implementation or conformance after validation correspondence is introduced.

## Expected specification families

Directional expectation:

- **Repository validation-correspondence specification family**: constitutional applicability and domain ownership rules;
- **Repository validation/repository-structure specification families**: common validation-domain roles, explicit exceptions, and default-deny envelope changes;
- **Repository product-correspondence specification family**: normalization of existing product requirement/test correspondence to avoid duplicate validation ownership;
- **Repository product-specification-base relationship**: product authority remains semantic owner while conforming to repository-generic correspondence law.

## Successor work

After decomposition acceptance, coordinated repository specification work must establish the common correspondence ownership model and reconcile existing product correspondence before structure or product correspondence artifacts are migrated.
