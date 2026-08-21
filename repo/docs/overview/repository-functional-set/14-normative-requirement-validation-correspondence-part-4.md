# functional-set lifecycle: Normative Requirement Validation Correspondence — Part 4

This part defines the repository-constitutional validation-domain rules, product applicability, and structural correspondence symmetry for **Normative Requirement Validation Correspondence**.

## Repository validation authority

Accepted repository specifications are the controlling repository-local authority for repository-generic validation structure, ownership, correspondence, lifecycle, and enforcement boundaries.

Product specifications operate inside that repository-defined validation system.

A product specification may define product-specific normative semantics and product-specific validation intent, but it does not independently redefine:

- the existence or role of validation correspondence;
- validation-correspondence cardinality rules;
- validation-correspondence lifecycle rules;
- repository-generic validation artifact classes;
- repository-generic validation-domain structure;
- correspondence integrity requirements;
- the authority relationship between normative requirements and validation evidence.

Any exception or specialization to those repository-generic rules must be explicitly delegated by accepted repository authority.

## Applicability to product-owned normative requirements

The normative validation-correspondence contract applies to every active identified normative requirement in an accepted repository or accepted product specification governed by the repository framework.

Therefore an active product-owned normative requirement is subject to the same repository-defined correspondence invariants as an active repo-owned normative requirement, including:

- one durable active correspondence package per active identified normative requirement;
- one unambiguous canonical normative-requirement reference per package;
- explicit validation disposition;
- stable externally identified validation-task ownership where tasks exist;
- one-package/one-requirement task correspondence;
- active/withdrawn lifecycle handling;
- correspondence integrity and completeness validation;
- subordinate deterministic generated projections.

Product ownership changes the normative semantic owner of the requirement. It does not opt the requirement out of repository-generic validation law.

## Validation-domain structural symmetry

Repository authority defines the validation-domain layout contract for root, repository-owned, and product-owned validation surfaces.

When accepted repository authority introduces a validation-correspondence structural element as a common validation-domain concept, the corresponding element must exist in every validation domain to which that concept applies.

For the proposed package architecture, structural symmetry is conditional on the package namespace later selected by accepted repository authority.

If accepted repository specification ultimately authorizes `repo/validation/packages/` as the repository-owned package namespace for the common validation-correspondence capability, then repository authority must also authorize corresponding `product/validation/packages/` and root `validation/packages/` roles for product-owned and whole-checkout correspondence unless it explicitly defines a domain-specific exception.

The functional set does not independently choose `packages/` as the final namespace. It establishes that a common validation-correspondence role selected for one applicable validation domain must have repository-authorized corresponding representation in the other applicable domains.

This is structural correspondence, not a claim that every validation-domain directory must be byte-for-byte identical.

Repository authority may define domain-specific differences where the role itself differs. Existing examples include root/repository GitHub-validation support that is not necessarily a product-domain concern.

But a common correspondence role may not exist only in `repo/validation/` while product-owned normative requirements remain subject to the same correspondence contract.

Structural symmetry does not require identical package population in every domain.

A normative requirement still has exactly one canonical active correspondence package according to its normative owner. A validation task executed from root `validation/` may therefore be referenced by a repository-owned or product-owned canonical package without creating a duplicate root-owned package for the same requirement.

If a root `validation/packages/` role is later authorized, downstream authority must define what canonical correspondence may legitimately be owned there without violating one-package-per-requirement cardinality.

## Domain ownership

Whatever package namespace is later selected, repository authority must preserve distinct ownership roles while applying one repository-defined correspondence model:

- repository/framework correspondence belongs to the repository-owned validation domain;
- product correspondence belongs to the product-owned validation domain;
- inherently cross-domain or whole-checkout correspondence belongs to the root validation domain when repository authority assigns it there.

If downstream specification selects `packages/` as the common structural role, these ownership roles correspond directionally to `repo/validation/packages/`, `product/validation/packages/`, and `validation/packages/`.

A package belongs in the domain that owns the normative validation responsibility.

Physical placement does not change normative ownership and must not create a second semantic owner for the referenced requirement.

## Existing product-correspondence reconciliation

Accepted `repo.product-correspondence` already defines product-specification correspondence among requirements, implementation mappings, test mappings, and conformance records.

The new normative validation-correspondence capability must not create a second independently maintained requirement-to-test authority beside that existing contract.

Downstream decomposition and specification must explicitly determine how the existing product correspondence system is revised, narrowed, referenced, or otherwise normalized so that:

- product specification semantics remain owned by product authority;
- repository-generic validation correspondence has one controlling semantic owner;
- requirement-to-validation-task relationships are not independently authored in two registries;
- retained product implementation/conformance correspondence remains compatible with the canonical validation-correspondence graph;
- transition preserves existing accepted product-specification lifecycle semantics until successor authority is accepted.

The functional set does not select the exact normalization strategy.

## Repo-spec source and initialized repositories

The repo-spec source repository is itself governed by the repository specifications it defines.

The same repository-level validation law also governs repositories derived or initialized from the framework.

Accordingly:

- repo-spec `repo/` requirements use the repository-owned correspondence domain;
- repo-spec `product/` requirements use the product-owned correspondence domain;
- derived or initialized repositories remain governed by the same repository-generic correspondence rules, with any framework materialization preserving canonical ownership;
- their own product normative requirements are governed by the same repository-defined normative validation-correspondence contract;
- whole-checkout correspondence remains governed by the repository-defined root validation domain.

The framework must not produce initialized repositories with weaker correspondence obligations than the repo-spec source repository unless accepted repository authority explicitly defines such a lifecycle distinction.

## Propagation versus independent ownership

Repository-generic framework material that is propagated or installed into another repository remains governed by repo-owned normative authority; materialization does not move that authority into the product domain.

Product-owned requirements created within a derived repository are not copies of repo-owned requirements; they are independent product authority within the product domain.

They nevertheless remain bound by the same repository-generic validation-correspondence contract.

Thus two distinct mechanisms coexist:

1. propagation preserves repo-owned authority and its correspondence across materialized framework surfaces;
2. repository constitutional authority imposes the correspondence contract on independently authored product-owned normative requirements.

Neither mechanism permits a product specification or generated artifact to redefine repository-generic correspondence law.

## Structural acceptance boundary

This functional set establishes the required symmetry and applicability direction but does not itself mutate the validation-domain structure.

If downstream accepted authority selects a `packages/` structural role, repository decomposition and specification must define the accepted structure revision that introduces that role consistently across the applicable validation domains, subject to explicitly authorized domain-specific differences.

That downstream work must also reconcile the new common package role with the current default-deny validation envelopes and their domain-specific differences.

No `packages/` directory is authorized merely by this functional-set document.

## Decomposition handoff

Repository decomposition must treat constitutional validation applicability as a first-class responsibility, including:

1. the repository-owned common correspondence contract;
2. product-owned requirement conformance to that contract;
3. root/repo/product validation-domain structural symmetry for common correspondence roles;
4. domain ownership rules for package placement;
5. propagation into repo-spec product materializations and initialized repositories;
6. validation that no applicable normative requirement escapes correspondence because of ownership domain.

This responsibility must remain distinct from exact schema design, path population, tagging syntax, or implementation mechanics.
