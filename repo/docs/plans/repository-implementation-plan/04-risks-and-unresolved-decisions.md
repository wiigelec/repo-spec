# Risks and unresolved decisions

## Status

Candidate implementation-plan content.

## Planning risks

### Hosted non-atomic mutations
GitHub issue comments, body edits, labels, and events are separate operations. The implementation must choose an order or compensating approach that satisfies accepted provenance and validation invariants without presenting an invalid governed-work state.

### Legacy issue states
Existing ordinary and governed issues may predate the new routing model. Rollout must avoid silently reclassifying historical intent or creating false provenance.

### Adapter authority drift
GitHub profile source must remain authoritative over installed `.github/` adapters. Direct installed-file edits would create drift.

### Cross-lifecycle coupling
Bug-fix routing depends on audit and feature-request routing depends on whiteboard/analysis/functional-set authority. Implementation must integrate with those lifecycles without redefining them.

### Correspondence overclaim
Accepted specs currently may have empty implementation/test/conformance correspondence. Implementation work must not claim coverage until evidence exists.

## Unresolved implementation-planning decisions

These remain candidate plan choices until plan acceptance:
1. exact GitHub mutation/API/event sequence satisfying provenance-before-restructure and valid governed-work activation;
2. live routing-classification label lifecycle after promotion;
3. concrete selection criteria for in-place versus successor governed issue;
4. exact source ownership split among profile YAML/data, helper scripts, field-policy workflow logic, and focused tests;
5. rollout behavior for existing intake/governed issues;
6. whether any narrow experimental spike is required to prove hosted event ordering before committing implementation mechanics.

## Decision boundary

These questions are implementation mechanics only while every permitted choice satisfies the accepted repository specifications.

If resolving any question requires introducing a new product invariant, the plan cannot decide it. The affected workstream must return to governed specification work before implementation proceeds.

## Candidate acceptance review focus

Plan acceptance should explicitly confirm:
- IRP-I1 through IRP-I5 are the correct bounded execution partition;
- each workstream's controlling accepted spec set is complete and no broader than necessary;
- dependency and transition gates are sufficient;
- listed implementation decisions remain mechanics rather than hidden semantic gaps;
- the rollout and hosted-event risks are sufficiently bounded for implementation issues.
