# Risks, decisions, and successor work

## Purpose

Record implementation risks, bounded planning decisions, unresolved matters, and the exact boundary for successor governed work.

## Planning decisions

- Use five implementation workstreams UP1-UP5 rather than the analysis-stage U1-U8 candidate methodology.
- Preserve the original initializer implementation plan as separate historical authority.
- Reuse existing accepted initializer primitives and capabilities without broadening their semantics.
- Require exact predecessor exit evidence before successor workstreams proceed.
- Treat the accepted product specifications as the only source of product semantics.

## Risks

### Inventory-version availability

Upgrade requires the target's accepted lineage entries to resolve framework inventory authority for historical repo-spec revisions. Implementation must fail closed if required historical inventory evidence cannot be resolved.

### Managed local divergence

Target-local changes inside initializer-managed authority can conflict with reconciliation. Accepted semantics forbid silent overwrite but do not authorize generalized automatic merge behavior.

### Projection consistency

Managed projections must remain consistent with their governing source material. Implementation must avoid creating a staged state where source and managed projection authorities disagree.

### Promotion uncertainty

An indeterminate or finalization-error promotion outcome must not be misreported. Accepted lineage state and terminal evidence must agree on whether promotion committed.

### Specification drift

A material change to any controlling accepted specification invalidates affected workstream planning authority until this plan is revised or explicitly reaffirmed.

## Unresolved planning decisions

The following may be selected by implementation issues without redefining product semantics:

- internal module boundaries;
- helper function/class names;
- exact test file organization;
- evidence file locations where not normatively prescribed;
- implementation language/library choices within repository conventions;
- internal staging mechanics that satisfy accepted isolation and promotion behavior.

The following are not planning decisions and must return to specification work if required:

- new conflict-resolution semantics;
- new compatibility/range semantics;
- remote framework retrieval semantics;
- different lineage acceptance rules;
- different mutation authority boundaries;
- different success/failure semantics.

## Successor work boundary

After this plan is accepted and post-merge validated, a successor Product-artifact implementation issue must cite:
- one or more exact workstream IDs from UP1-UP5;
- this accepted implementation plan;
- the workstream's exact controlling accepted product specifications;
- accepted default-branch base;
- predecessor completion evidence required by the workstream entry conditions.

No implementation issue may silently combine unrelated workstreams or bypass predecessor gates.
