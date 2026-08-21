# Risks and unresolved planning decisions

## Planning decisions intentionally delegated to repository-generic implementation mechanics

The following choices remain open but are not semantic authority gaps:

1. exact JSON Schema draft/features, definition factoring, and diagnostic wording;
2. exact repository-generic source metadata syntax for each maintained implementation language;
3. stable task-ID naming convention, provided identity stability and non-reuse semantics are preserved;
4. whether broad framework-maintained tests are split, wrapped, or retained behind parameterized task entry points;
5. repository-owned package-population batching strategy;
6. exact repository-generic validator module organization and discovery implementation;
7. exact aggregate generated coverage/report inventory and presentation;
8. exact propagation mechanism for each repository/framework-owned materialization surface;
9. freshness/equivalence algorithm for propagated or generated correspondence;
10. exact repository-generic migration batching/bootstrap sequence;
11. whether a later exact transition satisfies Atomic eligibility.

These decisions must be recorded in the governing implementation issue when they materially affect scope or acceptance evidence.

Product-specific realization choices are not delegated to this repository-owned plan; they belong to separately governed product-owned planning/implementation authority.

## Risk: candidate merge mistaken for acceptance

A merged candidate artifact could be incorrectly treated as accepted planning authority while its durable metadata still says `candidate`.

**Mitigation:** require a separate acceptance revision changing durable status to `accepted`, exact-revision validation/review/manual merge, and final read-only acceptance audit before implementation issues.

## Risk: repository/product authority collapse

Repository-generic correspondence law could be mistaken for authorization to mutate product-owned package, test, correspondence, or materialization artifacts.

**Mitigation:** repository workstreams may inspect product authority and define common invariants, but product-specific mutation requires separately governed product-owned planning/implementation with exact applicable accepted product specifications.

## Risk: completeness deadlock

Enabling aggregate completeness before both repository-owned and required product-owned canonical populations exist would make an otherwise valid intermediate revision fail.

**Mitigation:** keep aggregate completeness disabled/scoped until both authority domains are ready; use preparatory/non-active material where authorized; prove Atomic eligibility only if staging cannot produce a valid accepted revision.

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

Product correspondence could retain a second requirement-to-test mapping during separately governed product migration.

**Mitigation:** product-owned planning must migrate test evidence through `validation_package_refs`; repository-generic validation checks agreement without directly authorizing the product mutation.

## Risk: historical lifecycle loss

Migration could discard useful withdrawn/superseded provenance or accidentally count it as active coverage.

**Mitigation:** explicitly classify retained historical correspondence separately from active completeness and preserve canonical identity under REPO-VC-002/010.

## Risk: materialization overreach

Planning could invent initializer or product projection requirements for surfaces that do not actually need correspondence materialization.

**Mitigation:** inventory actual repository/framework-owned surfaces before VCP-I5 mutation; product-specific surfaces require product-owned authority.

## Authority escalation rule

If any implementation choice requires a new semantic rule rather than selecting mechanics within the accepted specification envelope, stop that workstream and return the question to specification governance.

If a proposed repository-generic implementation issue would mutate a product-owned artifact, stop and route that mutation through applicable product-owned planning/implementation authority instead of broadening the repository workstream ad hoc.
