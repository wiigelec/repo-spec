# Workstreams and dependencies

## Status

Candidate implementation-plan content.

## IRP-I1 — Intake classification realization

**Controlling specifications**
- `repo.issue-routing-governance`
- `repo.issue-routing-classification`

**Entry conditions**
- both controlling specs remain accepted;
- ordinary issue intake exists on the target hosting profile;
- no implementation issue may treat classification as mutation authority.

**Planned implementation scope**
- represent `bug-fix` and `feature-request` routing classification;
- permit assignment at creation or after review;
- preserve separation from `governed-work`;
- surface unresolved conflicting authority directions and fail closed before routing proceeds.

**Exit conditions**
- focused tests demonstrate ordinary unformatted intake is permitted;
- classification may be applied without establishing governed-work;
- conflicting classifications that imply different authority paths cannot progress silently.

**Transition gate**
IRP-I2 may begin only when the classification representation and fail-closed conflict behavior are demonstrably available to authority routing.

## IRP-I2 — Authority routing realization

**Controlling specifications**
- `repo.issue-routing-governance`
- `repo.issue-routing-classification`
- `repo.issue-authority-routing`

**Dependencies**
- IRP-I1.

**Planned implementation scope**
- route `bug-fix` to audit;
- route `feature-request` to whiteboard/analysis/functional-set lifecycle;
- redirect claimed bugs that require missing/unaccepted behavior toward feature development;
- prevent routing metadata from authorizing mutation.

**Exit conditions**
- each supported classification has an explicit permitted authority outcome;
- ambiguous or conflicting authority direction fails closed;
- no direct intake-to-implementation path exists.

**Transition gate**
IRP-I3 may begin when routing outcomes are explicit and traceable.

## IRP-I3 — Provenance-preserving governed-work promotion

**Controlling specifications**
- `repo.issue-routing-governance`
- `repo.governed-work-provenance`
- `repo.issue-authority-routing`
- `repo.governed-work-promotion`

**Dependencies**
- IRP-I1 and IRP-I2.

**Planned implementation scope**
- preserve original unformatted body in an issue comment before destructive restructure;
- preserve pre-promotion routing-classification labels in traceable issue-comment provenance;
- install canonical governed issue body/state;
- support in-place or successor governed issue as bounded workflow mechanics;
- preserve a unique traceable governing issue for mutation.

**Exit conditions**
- promotion cannot destroy required provenance;
- bounded governed work is traceable to intake classification/evidence;
- neither in-place nor successor realization is globally hard-coded where the other remains conforming.

**Transition gate**
IRP-I4 may begin only when promotion can establish a canonical governed state without violating provenance.

## IRP-I4 — Hosted validation and platform integration

**Controlling specifications**
- `repo.issue-routing-governance`
- `repo.governed-work-provenance`
- `repo.governed-work-promotion`
- `repo.issue-routing-platform-validation`

**Dependencies**
- IRP-I3.

**Planned implementation scope**
- keep GitHub-specific mutation/event mechanics inside platform/profile ownership;
- ordinary intake must bypass governed-work field validation;
- canonical governed fields must be installed before governed validation observes governed-work state;
- hosted adapter state cannot create mutation authority.

**Exit conditions**
- ordinary intake survives hosted issue events without governed-field rejection;
- promoted governed issues are validated;
- no invalid intermediate governed-work state is observable by field policy;
- platform/profile source and installed adapters remain authority-consistent.

**Transition gate**
IRP-I5 begins after hosted integration satisfies all lower-level invariants.

## IRP-I5 — End-to-end integration and conformance

**Controlling specifications**
- all seven accepted Issue Intake and Governance Routing repository specifications.

**Dependencies**
- IRP-I1 through IRP-I4.

**Planned implementation scope**
- integrate ordinary intake, classification, authority routing, provenance, promotion, and validation activation;
- add end-to-end conformance evidence;
- verify failure paths for ambiguity, provenance failure, invalid promotion state, and authority conflict.

**Exit conditions**
- end-to-end successful outcomes leave explicit authority path, traceable evidence, and structurally governed work;
- all accepted failure conditions fail closed;
- maintained correspondence can truthfully identify implementation/tests/conformance for the accepted specs.

**Transition gate**
Capability implementation is complete only when IRP-I5 exit evidence is accepted through the separately governed implementation workflow; completion does not itself imply release or merge.
