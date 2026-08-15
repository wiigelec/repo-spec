# Authority, scope, and specification map

## Status

Candidate implementation-plan content. Planning authority only after plan acceptance; non-normative with respect to repository semantics.

## Authority and basis

The accepted Issue Intake and Governance Routing repository specifications provide the complete normative repository basis for this plan. `repo.implementation-plan` and `repo.development-document-base` control plan structure and lifecycle.

The plan must not redefine:
- routing classification versus governance state;
- bug-fix versus feature-request authority routing;
- provenance minimums;
- in-place versus successor governed-issue permissibility;
- hosted validation-state boundaries;
- end-to-end success/failure semantics.

## Specification-complete scope

The planned capability is specification-complete for:
- ordinary pre-governed intake classification;
- fail-closed authority routing;
- audit routing for `bug-fix`;
- whiteboard/analysis/functional-set routing for `feature-request`;
- original-body and pre-promotion classification-label preservation in issue comments;
- governed-work promotion;
- hosted validation activation only after canonical governed fields/state exist;
- end-to-end integration/conformance.

## Implementation-authorized scope after plan acceptance

After separate acceptance, implementation issues may realize the five workstreams exactly through their declared controlling accepted specification sets.

## Deferred implementation decisions

The following are implementation mechanics, not unresolved repository semantics:
- exact GitHub mutation/API/event ordering consistent with accepted invariants;
- whether live routing-classification labels are retained, removed, or transformed after promotion;
- concrete criteria for choosing in-place versus successor issue where both conform;
- exact internal split between repository-owned implementation/test/conformance evidence and repository/profile-owned helper and adapter mechanics, provided maintained implementation/test/conformance evidence never substitutes repository/framework tooling for the repository-owned evidence required to claim covered `product.*` requirements;
- rollout treatment for existing issues.

The ownership class itself is not deferred: implementation/test/conformance artifacts cited as maintained correspondence for the seven controlling `repo.*` specifications are repository-owned. GitHub profile source, installed `.github` adapters, and repository/framework helpers remain governed by their existing repository/profile ownership boundaries and may support the product implementation without becoming implementation/test/conformance evidence.

## Explicit exclusions

This candidate plan does not authorize:
- implementation issues;
- source/executable changes;
- GitHub Actions, labels, templates, platform-profile mutation, or audit mutation;
- repository specification changes;
- title-preservation semantics;
- universal live routing-label retention;
- universal in-place or successor promotion.

## Semantic gap rule

If implementation planning discovers a requirement that cannot be derived from accepted specifications without choosing new repository behavior, the affected workstream stops and returns to specification governance.
