# Target architecture and ownership

## 1. Public entry points

The desired public surface is intentionally small.

```text
scripts/validate
    repo/scripts/validate
    product/scripts/validate

scripts/test-validation
    repo/scripts/test-validation
    product/scripts/test-validation
```

Subsystem tests, including initializer tests, remain independently runnable under their
own subsystem ownership.

Public shell wrappers stay thin. Python modules contain implementation.

## 2. Production validator architecture

Each leaf validator should read as a short ordered composition of functional phases.
Phase names describe invariants, not implementation history.

A target repository validator is conceptually:

```text
repository validation
    repository boundary
    schema conformance
    manifest and inventory integrity
    identity and uniqueness
    references and lineage
    repository development documents
    repository-local platform/profile contracts
    generated-output freshness
```

A target product validator is conceptually:

```text
product validation
    schema conformance
    manifest and inventory integrity
    identity and correspondence
    dependencies and completeness
    dependency acyclicity
    lineage
    product development documents
    product projections
    generated-output freshness
```

The exact phase list remains subordinate to accepted `repo.validation`. A phase may be
split when its invariants are materially distinct, or combined when a shared context
makes that clearer, but the ownership model remains functional.

## 3. Phase ownership

Every production invariant has one primary owning phase.

Supporting utilities may be shared, but two phases shall not independently implement the
same semantic rule.

Examples:

- JSON type, enum, required-field, and pattern constraints → schema conformance;
- manifest entry corresponds to one existing artifact → manifest/inventory integrity;
- manifest status agrees with document status → identity/correspondence;
- accepted product may not depend on candidate product → dependency policy;
- graph has no dependency cycle → dependency acyclicity;
- supersedes/superseded_by reciprocal and acyclic → lineage;
- generated Markdown matches source → generated-output freshness.

Integration may cause one validator invocation to encounter several phases, but test
ownership should still identify the specific invariant under test.

## 4. Validation context

A leaf validator should load and normalize repository state once where practical, then
pass a stable context to functional phases.

Repeated parsing of the same manifests, schemas, specifications, or development-document
registries should be treated as an efficiency smell unless isolation is required for
correctness.

The context is an implementation optimization, not a second source of authority. It
should contain normalized facts, not hidden policy.

## 5. Shared utilities

Shared utilities are appropriate for mechanics that are genuinely common across domains,
including:

- JSON loading;
- schema-subset evaluation;
- path normalization and root containment;
- generated-output comparison;
- graph traversal primitives;
- deterministic failure helpers;
- mutation-fixture construction.

Shared utilities shall not erase domain ownership. Repository policy does not become a
generic utility merely because product policy has similar syntax.

## 6. Composition rules

Top-level `validate_repo()` and `validate_product()` functions should be composition
functions, not secondary implementations of leaf rules.

They should:

1. build the required context;
2. execute each current functional phase exactly once in a stable order;
3. emit concise success/failure information;
4. return or fail cleanly.

They should not contain duplicate fallback logic, historical branches, patch-era alternate
phase lists, or one-off compatibility checks whose transition has ended.

## 7. Naming rules

Maintained production code and self-tests use names based on invariant or capability.

Preferred:

- `manifest_integrity`
- `dependency_policy`
- `dependency_acyclicity`
- `generated_freshness`
- `development_documents`
- `repository_boundary`
- `projection_rendering`

Not preferred:

- `patch_3`
- `b0`
- `i4`
- `issue_318`
- `legacy_fix`
- `phase_from_migration`

Historical names may remain in archival evidence and completed historical plans. They
shall not define active validation ownership.

## 8. No milestone-shaped architecture

The desired architecture is independent of the order in which features were developed.

A future developer should be able to delete the repository's issue and PR history and
still understand why every active validation module exists from:

- accepted specifications;
- this desired-state plan;
- module/function names;
- current self-tests.

If understanding a validator requires knowing which development milestone introduced it,
the architecture has drifted from this desired state.
