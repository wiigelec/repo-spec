# Purpose, authority, and boundaries

## 1. Purpose

The validation system exists to reject repository states that violate current accepted,
machine-checkable repository or product invariants assigned to repository-local
validation.

Validation is not a general quality framework. It is not intended to prove that prose is
good, code is correct, a feature works end-to-end, GitHub is configured correctly except
where a repository-local contract explicitly assigns such a check, or historical
implementation evidence remains unchanged.

The primary design objective is **high-value structural enforcement with the smallest
maintained validation surface that preserves required coverage**.

## 2. Authority hierarchy

Validation behavior shall be traceable to current accepted authority.

The order of precedence is:

1. accepted normative repository specifications;
2. accepted normative product specifications for product-owned invariants;
3. this accepted desired-state plan, once accepted, for architectural organization and
   audit criteria;
4. maintained validation implementation and tests as evidence of realization;
5. historical plans, issues, patches, migration evidence, and prior implementation
   structure as historical evidence only.

No test becomes permanent authority merely because it once caught a bug.

## 3. Validation domains

The maintained validation system has two production domains:

### Repository domain

Owned by `repo/scripts/validate`.

It enforces repository-owned structural invariants, including the repository specification
root, repository manifests and identity, repository references and lineage, repository
development-document contracts, repository-generated artifacts, repository root
boundaries, and repository-local platform/profile contracts assigned by accepted
authority.

### Product domain

Owned by `product/scripts/validate`.

It enforces product-owned structural invariants, including the product specification
root, product manifests and identity, product dependency semantics, product lineage,
product correspondence where assigned, product development-document contracts, product
projection declarations and freshness, and other product-local structural requirements
assigned by accepted authority.

### Aggregate production domain

Owned by `scripts/validate`.

It composes the repository and product production validators and adds no independent
semantic validation of its own. Its responsibility is orchestration and clean aggregate
failure behavior.

## 4. Explicit non-goals

Routine production validation shall not permanently own:

- validator regression or mutation tests;
- initializer, application, or subsystem unit tests;
- historical milestone evidence integrity;
- one-time migration compatibility checks after their transition is complete;
- issue-number, patch-number, or implementation-increment-specific checks;
- remote GitHub issue-body inspection or other remote state unless accepted authority
  explicitly assigns a repository-local representation to a leaf validator;
- prose quality, style, formatting taste, or source-code behavioral correctness unless an
  accepted validation requirement explicitly assigns a machine-checkable structural
  contract;
- generated Markdown as a source of authority over its source specification.

## 5. Structural rules for adding validation

A new production validation rule is justified only when all of the following are true:

1. a current accepted requirement assigns the invariant to repository-local validation;
2. the invariant is machine-checkable and deterministic;
3. the owning validation domain is unambiguous;
4. the invariant is not already fully enforced by a lower-cost authoritative mechanism,
   such as JSON Schema;
5. the rule can fail with a specific diagnostic tied to the violated invariant;
6. the rule does not encode development history as architecture.

If any condition is not met, the proposed rule belongs elsewhere or requires an authority
change before implementation.

## 6. Schema versus semantic validation

JSON Schema owns local document shape whenever the invariant can be expressed clearly and
stably in schema.

Semantic validation owns relationships that require repository context, such as:

- manifest-to-file correspondence;
- cross-file identity agreement;
- reference resolution;
- dependency and lineage graphs;
- lifecycle-dependent relationships;
- exact inventory coverage;
- generated-output freshness;
- repository-root boundaries;
- cross-document development-document relationships.

A semantic validator shall not reimplement schema checks merely to produce another path
to the same rejection.

## 7. Historical material

Historical plans, evidence packages, migration artifacts, and completed implementation
increments may remain in the repository for provenance.

Their continued presence does not imply active validation ownership.

If historical material requires integrity preservation for archival reasons, that
requirement must be explicit and function-based, such as archival inventory integrity. It
shall not be retained under a milestone-specific validator name merely because the
material originated in a milestone.
