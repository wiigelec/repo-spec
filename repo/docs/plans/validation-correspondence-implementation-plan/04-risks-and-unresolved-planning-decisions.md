# Risks and unresolved planning decisions

## Planning decisions intentionally delegated to implementation mechanics

The following choices remain open but are not semantic authority gaps:

1. exact JSON Schema draft/features, definition factoring, and diagnostic wording;
2. exact source metadata syntax for each maintained implementation language;
3. stable task-ID naming convention, provided identity stability and non-reuse semantics are preserved;
4. whether broad existing tests are split, wrapped, or retained behind parameterized task entry points;
5. package-population batching strategy;
6. exact validator module organization and discovery implementation;
7. exact aggregate generated coverage/report inventory and presentation;
8. exact propagation mechanism for each actual maintained materialization surface;
9. freshness/equivalence algorithm for propagated or generated correspondence;
10. exact migration batching/bootstrap sequence;
11. whether a later exact transition satisfies Atomic eligibility.

These decisions must be recorded in the governing implementation issue when they materially affect scope or acceptance evidence.

## Risk: completeness deadlock

Enabling repository-wide completeness before canonical package population exists would make an otherwise valid intermediate revision fail.

**Mitigation:** keep completeness enforcement disabled or scoped until the required accepted-state population exists; use preparatory/non-active material where authorized; prove Atomic eligibility only if staging cannot produce a valid accepted revision.

## Risk: duplicate correspondence authority

Source annotations, product mappings, generated indexes, or propagated copies could become independent mutable registries.

**Mitigation:** packages remain canonical; source metadata and product mappings mechanically agree with packages; generated/materialized copies are deterministic subordinate representations.

## Risk: artificial task decomposition

Forcing every fixture, parameter case, helper, or broad historical test into a separate correspondence task could distort implementation.

**Mitigation:** use the accepted task/helper boundary, stable externally identified task wrappers where needed, and preserve parameterized/shared internal implementation.

## Risk: incorrect domain ownership

Execution from root validation could tempt package duplication or root ownership.

**Mitigation:** derive package ownership from normative authority only; root packages require explicit inherently cross-domain/whole-checkout ownership.

## Risk: semantic drift during schema implementation

JSON Schema implementation could accidentally make optional semantic choices mandatory or introduce undeclared fields.

**Mitigation:** treat REPO-VC-004/005/008/012 as the semantic contract; schema enforcement is subordinate only.

## Risk: product reconciliation regression

Product correspondence could retain a second requirement-to-test mapping during migration.

**Mitigation:** migrate test evidence through `validation_package_refs` and validate conformance agreement before removing predecessor mappings.

## Risk: historical lifecycle loss

Migration could discard useful withdrawn/superseded provenance or accidentally count it as active coverage.

**Mitigation:** explicitly classify retained historical correspondence separately from active completeness and preserve canonical identity under REPO-VC-002/010.

## Risk: materialization overreach

Planning could invent initializer or projection requirements for surfaces that do not actually need correspondence materialization.

**Mitigation:** inventory actual maintained surfaces first; implement propagation only where an accepted framework surface requires it.

## Authority escalation rule

If any implementation choice requires a new semantic rule rather than selecting mechanics within the accepted specification envelope, stop that workstream and return the question to specification governance. Do not encode the choice first in schema, validator, package population, source metadata, or migration behavior.
