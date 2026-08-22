# Successor Concept Set Proposal

## Status

Design proposal for audit against the current repository.

This document is non-authoritative.

Its purpose is to identify concepts from the current repo-spec design that should be deliberately carried into, modified for, or superseded by a successor architecture built around the Framework Contract, Governance, Conformance, and Assurance proposals.

This proposal is intentionally concept-focused.

It does not preserve current implementation details merely because they exist.

It asks instead:

**Which ideas from the current repository are intrinsically valuable enough that a successor repo-spec should deliberately preserve them even if their present representation, workflow, schema, file layout, or implementation is replaced?**

The classification vocabulary is:

- **KEEP** — preserve the concept substantially as an architectural principle;
- **MODIFY** — preserve the underlying concept while changing its scope, ownership, terminology, or mandatory form; and
- **SUPERSEDE** — replace the concept with a stronger architectural model while preserving useful subordinate techniques where applicable.

## Relationship to the Four Architecture Proposals

This proposal is subordinate design input to:

1. Framework Contract Architecture Proposal;
2. Governance Architecture Proposal;
3. Conformance Architecture Proposal; and
4. Assurance Architecture Proposal.

The four architecture proposals define the target authority topology.

This document identifies reusable design concepts from the current repo-spec that should inform detailed successor Design without independently extending those proposals.

A retained concept shall not override a keystone boundary or create authority outside the four-proposal architecture.

## Primary Conceptual Invariant

**The successor repo-spec SHOULD preserve concepts that improve explicit authority, controlled refinement, traceability, bounded extension, and separation of evidence, interpretation, realization, and authority, while superseding current concepts that conflate Governance, Conformance, Assurance, implementation, or platform mechanics.**

## Concept Summary

| Concept | Disposition | Successor placement |
| --- | --- | --- |
| Default-deny maintained state | KEEP | Framework Contract / subordinate structure authority |
| Explicit governed extension points | KEEP | Framework Contract / subordinate structure authority |
| Framework and product authority domains | KEEP | Framework Contract |
| Enumerable authoritative registries | KEEP | Framework Contract / Governance |
| Stable identities and historical resolution | KEEP | Framework Contract / Governance |
| One controlling semantic owner | KEEP | Framework Contract |
| Derived artifacts subordinate to sources | KEEP | Framework Contract |
| Evidence before interpretation | KEEP | Governance Design |
| Analysis before commitment | KEEP | Governance Design |
| Capability-oriented functional sets | MODIFY | Governance Design technique |
| Directional decomposition | MODIFY | Governance Design technique |
| Product semantic Levels | MODIFY | Product normative refinement model |
| Realization planning distinct from normative semantics | KEEP | Governance Plan |
| Explicit predecessor and lineage relationships | KEEP | Governance |
| Explicit acceptance | KEEP | Governance |
| Exact-candidate evidence freshness | KEEP | Governance / Conformance / Assurance interface |
| Exploratory work isolation | KEEP | Governance boundary |
| Portable framework vs platform realization | KEEP | Framework Contract / subordinate profile design |
| Artifact classification | MODIFY | Cross-framework provenance model |
| Conformance ownership domains | MODIFY | Conformance subordinate design |
| Requirement-level correspondence | MODIFY | Independent Conformance and Assurance correspondence |
| Validation-task/callable correspondence | SUPERSEDE | Conformance assertion and primitive provenance |
| Combined validation dispositions | SUPERSEDE | Independent Conformance and Assurance applicability |
| Human semantic review | SUPERSEDE | Governed Assurance |
| Current multi-stage development lifecycle | SUPERSEDE | Governance Design → Plan → Build |
| GitHub issue/branch/PR workflow as governance semantics | SUPERSEDE | Platform realization of governed work |
| Atomic authority transition | MODIFY | Exceptional governed atomic realization |
| Bounded governed authorization | KEEP | Governance |
| Acyclic normative dependency/authorization | KEEP | Framework Contract |
| Observed vs desired external state | MODIFY | Governance / platform realization |

# Concepts to Keep

## 1. Default-Deny Maintained State

### Disposition

**KEEP**

### Current Concept

The current repository uses a default-deny structural authorization model: maintained artifacts and namespaces require positive authorization rather than being permitted merely because no rule forbids them.

### Successor Concept

Default deny should be generalized beyond filesystem layout.

A successor framework should treat maintained governed state as unauthorized unless its role is established by accepted authority or by an explicitly governed extension point.

Conceptually:

**maintained state**
→ **accepted authorization or governed extension point**
→ **permitted**

Absence of authorization should be a defect rather than implied permission.

### Why Keep It

Default deny prevents implementation drift from silently extending the framework.

It is especially valuable when automated or AI actors can create new files, metadata, schemas, validators, review mechanisms, generated outputs, or workflow conventions faster than a human reviewer can recognize their architectural consequences.

### Successor Placement

Framework-level invariant with detailed structural realization delegated to subordinate authority.

---

## 2. Explicit Governed Extension Points

### Disposition

**KEEP**

### Current Concept

The current repository combines closed boundaries with explicitly extensible namespaces and contracts.

### Successor Concept

The successor should preserve the pair:

**default deny + explicit extensibility**

The framework should not attempt to enumerate every future artifact, primitive, finding type, profile, or generated view.

Instead, accepted authority should identify where extension is allowed and what constraints govern extension.

### Why Keep It

This avoids two bad extremes:

- permissive implicit extension; and
- brittle closed-world enumeration requiring foundational changes for ordinary growth.

### Successor Placement

Framework Contract principle with subordinate realization by Governance, Conformance, Assurance, structure, and profile authority.

---

## 3. Explicit Framework and Product Authority Domains

### Disposition

**KEEP**

### Current Concept

Repository/framework semantics and product semantics occupy distinct authority domains.

### Successor Concept

Framework authority should continue to define how the repository operates, while product authority should define maintained product semantics within the framework-defined boundary.

Product authority and implementation must remain unable to redefine framework authority independently.

### Why Keep It

This prevents product-specific needs from becoming accidental framework policy and prevents framework mechanics from absorbing product semantics.

### Successor Placement

Framework Contract.

---

## 4. Enumerable Authoritative Registries

### Disposition

**KEEP**

### Current Concept

Authoritative specification sets are explicitly enumerated through manifests rather than discovered through naming convention or directory scanning alone.

### Successor Concept

Accepted authority and authority-bearing relationships should be enumerable and machine-resolvable.

The successor should preserve the broader principle:

**authority should be declared, not inferred.**

This principle may apply to:

- accepted specifications;
- normative requirements;
- delegated authority;
- Governance lineage;
- Conformance correspondence;
- Assurance correspondence; and
- governed extension registries.

### Why Keep It

Explicit registries create deterministic joins and allow tooling to prove completeness rather than merely search for likely artifacts.

### Successor Placement

Framework Contract and subordinate Governance/keystone mechanisms.

---

## 5. Stable Identity and Historical Resolution

### Disposition

**KEEP**

### Current Concept

Published normative identities remain stable, are not reused for unrelated semantics, and remain historically resolvable after movement, merger, supersession, or withdrawal.

### Successor Concept

Stable identity should remain foundational for:

- normative requirements;
- Governance work and accepted results;
- Conformance assertions and other identity-bearing primitives;
- Assurance review obligations, cases, and findings; and
- historical authority lineage.

### Why Keep It

Stable identity makes provenance durable across refactors and prevents current structure from erasing historical meaning.

### Successor Placement

Framework Contract identity principle with lifecycle mechanics in Governance and keystone-specific identity rules in Conformance and Assurance.

---

## 6. One Controlling Semantic Owner

### Disposition

**KEEP**

### Current Concept

A semantic invariant should have one controlling normative owner rather than multiple independently maintained restatements.

### Successor Concept

Dependent authority may specialize, apply, sequence, enforce, review, or realize an invariant without becoming a second independent semantic owner when reference to the controlling authority is sufficient.

### Why Keep It

This prevents semantic drift and supports clean delegation between the Framework Contract and the three keystones.

### Successor Placement

Framework Contract.

---

## 7. Derived Artifacts Remain Subordinate

### Disposition

**KEEP**

### Current Concept

Generated projections, schemas, adapters, implementation, tests, validation behavior, and other derived artifacts do not become authority merely because they exist or execute successfully.

### Successor Concept

Every derived framework behavior should remain subordinate to accepted authority and preserve resolvable provenance.

Generated views may improve usability but must never become competing semantic owners.

### Why Keep It

This is central to preventing authority inversion.

### Successor Placement

Framework Contract, with stronger provenance closure in Conformance and Assurance.

---

## 8. Evidence Before Interpretation

### Disposition

**KEEP**

### Current Concept

The current functional-set process preserves raw user statements, discovered evidence, provenance, and unresolved intent before interpretation into requirements or design structure.

### Successor Concept

Design should preserve a distinction between:

**evidence / stated intent**
→ **analysis**
→ **directional synthesis**
→ **candidate normative semantics**

A Design process should not silently rewrite raw evidence into accepted meaning.

### Why Keep It

It reduces accidental semantic invention and keeps unresolved or deferred intent visible.

### Successor Placement

Governance Design, primarily Design Audit.

---

## 9. Analysis Before Commitment

### Disposition

**KEEP**

### Current Concept

Analysis identifies capabilities, dependencies, ambiguity, boundaries, and alternatives before directional or normative commitment.

### Successor Concept

Governance Design should explicitly distinguish discovery and semantic analysis from normative production and acceptance.

### Why Keep It

It prevents the first plausible interpretation from becoming authority merely because work has begun.

### Successor Placement

Governance Design Audit.

---

## 10. Realization Planning Is Distinct from Normative Semantics

### Disposition

**KEEP**

### Current Concept

Implementation plans coordinate realization and sequencing but do not redefine accepted repository or product semantics.

### Successor Concept

This distinction should become the defining boundary of Governance Plan:

**Design owns what must be true.**
**Plan owns how accepted authority will be realized.**

### Why Keep It

The concept already expresses the same separation now formalized by the Governance proposal.

### Successor Placement

Governance Plan.

---

## 11. Explicit Predecessor and Lineage Relationships

### Disposition

**KEEP**

### Current Concept

Development and implementation artifacts preserve predecessor relationships, controlling authority, evidence, and authorized next work.

### Successor Concept

Every governed stage and realization work item should remain traceable to the accepted result or authority that authorizes it.

Lineage should support both forward and reverse resolution.

### Why Keep It

Lineage makes authority flow auditable and prevents downstream work from becoming self-authorizing.

### Successor Placement

Governance.

---

## 12. Explicit Acceptance

### Disposition

**KEEP**

### Current Concept

Validation success, review, implementation completion, merge, and issue closure do not independently constitute acceptance.

### Successor Concept

Acceptance remains a distinct governed decision that promotes only the candidate result belonging to the stage in which acceptance occurs.

### Why Keep It

This concept is now foundational to Design, Plan, and Build separation.

### Successor Placement

Governance.

---

## 13. Exact-Candidate Evidence Freshness

### Disposition

**KEEP**

### Current Concept

Validation and review evidence used for acceptance is revision-specific and becomes stale when the candidate materially changes.

### Successor Concept

Evidence used to disposition a governed candidate should resolve to the candidate state for which the evidence is claimed.

This concept should not depend on Git commits specifically.

It applies to any identity-bearing candidate result.

### Why Keep It

A successful check or review against an earlier candidate does not prove anything about an unreviewed later candidate.

### Successor Placement

Governance acceptance with interfaces to Conformance evidence and Assurance findings.

---

## 14. Exploratory Work Isolation

### Disposition

**KEEP**

### Current Concept

Exploratory experiments may exist without claiming maintained, accepted, or conforming status and require later governed adoption before becoming maintained implementation.

### Successor Concept

Exploration should be allowed without forcing premature authority, while promotion from exploration into maintained governed state must be explicit.

Conceptually:

**exploration**
→ may produce evidence or candidate design input
→ does not implicitly promote
→ Governance required for maintained adoption

### Why Keep It

This allows experimentation without making prototypes de facto specifications.

### Successor Placement

Governance boundary and subordinate workflow design.

---

## 15. Portable Framework vs Platform Realization

### Disposition

**KEEP**

### Current Concept

Portable framework semantics are distinguished from hosting-platform-specific profiles and installed adapters.

### Successor Concept

GitHub, GitLab, another forge, or local tooling should realize Governance/Conformance/Assurance contracts without becoming the source of those contracts.

### Why Keep It

A framework should not accidentally define GitHub behavior as universal repository governance.

### Successor Placement

Framework Contract with subordinate platform/profile authority.

## 16. Bounded Governed Authorization

### Disposition

**KEEP**

### Current Concept

The current governed-work model distinguishes authorized scope from adjacent or successor work. Material scope expansion must be made explicit, exclusions matter, and completion of one governed work item does not independently authorize unrelated follow-on work.

### Successor Concept

Governed authorization should remain explicitly bounded.

Conceptually:

**governed work**
→ **explicit authorized scope**
→ **explicit exclusions**
→ **no authority beyond that boundary**

Acceptance or completion of one governed result should not silently expand authorization into neighboring or successor work.

### Why Keep It

Bounded authorization prevents scope drift from becoming de facto Governance authority.

It also makes delegation safer for automated and AI actors because possession of a valid governed-work identity does not imply permission to perform any adjacent useful work.

### Successor Placement

Governance.

---

## 17. Acyclic Normative Dependency and Authorization

### Disposition

**KEEP**

### Current Concept

The current repository requires key authority and product dependency graphs to remain directed and acyclic rather than permitting requirements to become authoritative through circular dependency.

### Successor Concept

The successor should distinguish ordinary bidirectional traceability from normative dependency.

Historical cross-reference, reverse provenance lookup, and many-to-many evidence relationships may be cyclic as graph navigation.

The normative basis by which authority depends on other authority should not be circular.

Conceptually:

**Authority A**
→ depends normatively on **Authority B**
→ depends normatively on **Authority C**

must not return to **Authority A** as a condition of A's own authority.

### Why Keep It

Resolvable circularity is still circularity.

This principle complements Governance's candidate-acceptance anti-circularity rule by addressing static normative dependency topology rather than only temporal self-authorization during acceptance.

### Successor Placement

Framework Contract.

---

# Concepts to Modify

## 18. Capability-Oriented Functional Sets

### Disposition

**MODIFY**

### Current Concept

A functional set is a bounded capability-oriented directional unit suitable for downstream decomposition and intentionally avoids becoming exact product semantics or implementation architecture.

### Successor Concept

Capability-oriented functional grouping should remain available as a Design technique for sufficiently large or ambiguous work.

It should not remain a mandatory constitutional stage for every Governance lifecycle.

A small framework correction may move from Design Proposal through Audit and Normalize without requiring a separate functional-set artifact.

A large product initiative may benefit greatly from explicit functional-set formation.

### What Changes

The successor preserves:

- capability orientation rather than technical-layer slicing;
- bounded directional units;
- multiple candidates before commitment; and
- explicit separation from normative semantics.

It supersedes mandatory use as a universal lifecycle gate.

### Successor Placement

Optional or conditionally required Governance Design technique.

---

## 19. Directional Decomposition

### Disposition

**MODIFY**

### Current Concept

Decomposition identifies bounded areas, dependencies, unresolved decisions, specification families, and responsibility boundaries without itself becoming normative authority.

### Successor Concept

Directional decomposition remains a valuable bridge between broad design intent and atomic normative requirements.

It should be available when semantic complexity requires explicit problem-space partitioning but should not be mandatory ceremony for trivial Design work.

### What Changes

Decomposition becomes a Design normalization technique rather than an independent top-level Governance stage.

### Successor Placement

Governance Design Audit/Normalize.

---

## 20. Product Semantic Levels

### Disposition

**MODIFY**

### Current Concept

Product authority is refined through Level 0–3 semantics, roughly from intent/scope through observable behavior and architecture to implementation-constraining detail.

### Successor Concept

The principle of controlled semantic refinement should remain distinct from the Governance lifecycle.

Governance Design → Plan → Build answers how authority changes and is realized.

Product semantic Levels answer how accepted product meaning is organized by abstraction depth.

The successor should preserve that orthogonality.

### What Changes

The exact four-Level vocabulary and boundary definitions should be re-audited rather than treated as foundational simply because they exist today.

Intermediate Levels should remain optional when unnecessary.

### Successor Placement

Subordinate product-authority design.

---

## 21. Artifact Classification

### Disposition

**MODIFY**

### Current Concept

The artifact taxonomy classifies artifacts by authority category, role, source-of-truth behavior, mutability, generation mode, validation ownership, portability, and manifest participation.

### Successor Concept

Artifact classification remains valuable, but authority role, keystone role, ownership, derivation, lifecycle, and portability should be treated as distinct dimensions rather than one large ontology where possible.

A successor classification might distinguish concepts such as:

- normative;
- governed decision/result;
- derived primitive;
- evidence;
- generated projection;
- external observation; and
- non-authoritative convenience.

Separately, an artifact may serve Governance, Conformance, Assurance, product, platform, or no keystone role.

### What Changes

The taxonomy should become smaller, orthogonal, and provenance-oriented.

### Successor Placement

Framework/subordinate cross-cutting design.

---

## 22. Conformance Ownership Domains

### Disposition

**MODIFY**

### Current Concept

Validation is separated into whole-checkout, repository/framework, and product-owned domains.

### Successor Concept

The ownership distinction should remain:

- cross-domain/whole-system Conformance responsibility;
- framework Conformance responsibility; and
- product Conformance responsibility.

### What Changes

The successor should preserve ownership semantics without treating the current exact directory envelope, duplicated filenames, or runner layout as foundational architecture.

### Successor Placement

Subordinate Conformance design.

---

## 23. Requirement-Level Correspondence

### Disposition

**MODIFY**

### Current Concept

Every active normative requirement has one canonical validation-correspondence relationship.

### Successor Concept

Every active normative requirement should instead have independent canonical relationships to both keystones:

**normative requirement**
→ **Conformance correspondence**
→ **Assurance correspondence**

The two applicability dimensions remain independent.

### What Changes

The useful one-requirement/one-canonical-record discipline survives independently in both keystones.

The shared mixed validation disposition does not.

### Successor Placement

Conformance and Assurance.

---

## 24. Atomic Realization

### Disposition

**MODIFY**

### Current Concept

An Atomic authority transition permits logically ordered authority, plan, and implementation synchronization to become externally accepted as one exact revision when no valid intermediate accepted revision exists.

### Successor Concept

The successor should preserve the underlying principle:

**logical authority sequencing may remain strict even when physical state transition must be atomic.**

### What Changes

Atomic realization must remain exceptional and must satisfy Governance's non-circular acceptance rule.

Candidate authority cannot authorize its own acceptance.

Any atomic mechanism must be authorized by authority accepted before the atomic candidate acquires its new authority.

### Successor Placement

Subordinate Governance transition design.

## 25. Observed vs Desired External State

### Disposition

**MODIFY**

### Current Concept

The current platform-profile model distinguishes live observed external state from desired state, separates inspection from apply, records intended mutation, and requires post-change verification.

### Successor Concept

The successor should preserve the more general state-management discipline:

**observe external state**
→ **compare with governed desired state**
→ **Plan the authorized mutation**
→ **Build/apply the mutation**
→ **verify resulting state**

Repository content, desired external state, and actual external state should not be treated as interchangeable.

### What Changes

This concept should not be GitHub-specific and should not become a fourth authority system.

Governance owns authorization of the change, Conformance may mechanically verify observable properties, Assurance may review semantic sufficiency where required, and a platform profile may define provider-specific representation and mutation mechanics.

### Successor Placement

Subordinate Governance and platform/profile design.

---

# Concepts to Supersede

## 26. Validation-Task and Callable-Centric Correspondence

### Disposition

**SUPERSEDE**

### Current Concept

The existing model gives stable identity primarily to validation tasks and associates those identities with maintained callables.

### Replacement Concept

Conformance should identify independently governed mechanical predicates as assertions.

Conceptually:

**normative requirement**
→ **assertion identity**
→ **implementation callable**

Multiple assertions may share a callable when their semantic identities and provenance remain distinct.

All maintained Conformance primitives, not just callables, participate in provenance closure.

### Useful Subordinate Idea Retained

Stable implementation-task identities may remain useful where they represent durable execution responsibilities, but they should no longer be the foundational semantic unit of enforcement correspondence.

### Successor Placement

Conformance.

---

## 27. Combined Validation Dispositions

### Disposition

**SUPERSEDE**

### Current Concept

The current correspondence vocabulary combines mechanical and semantic responsibility through values such as:

- `mechanical`;
- `partial`;
- `semantic-review`; and
- `not-applicable`.

### Replacement Concept

The successor should represent two independent questions:

**Conformance applicability**

- `mechanical`
- `none`

**Assurance applicability**

- `required`
- `none`

For example, old `partial` typically becomes:

**Conformance = mechanical**
**Assurance = required**

### Why Supersede It

The combined vocabulary conflates separate keystone responsibilities and prevents clean closure in either subsystem.

### Successor Placement

Conformance + Assurance with Governance-owned cross-keystone disposition.

---

## 28. Human Semantic Review as an Informal Architecture

### Disposition

**SUPERSEDE**

### Current Concept

The current repository distinguishes human semantic review from mechanical validation and acceptance, often directing semantic attention through review proposals and reviewer judgment.

### Replacement Concept

Semantic review should become governed Assurance:

**accepted authorizing authority**
→ **Assurance correspondence**
→ **review obligation**
→ **review case**
→ **evidence**
→ **finding**

Actor type is separate from authority.

Humans, AI agents, automated semantic systems, or combinations may perform Assurance where authorized.

### Useful Subordinate Idea Retained

The existing recognition that semantic review is distinct from validation and acceptance is preserved and strengthened.

### Successor Placement

Assurance.

---

## 29. Current Multi-Stage Development Lifecycle as the Primary Governance Model

### Disposition

**SUPERSEDE**

### Current Concept

The current repository defines a universal lifecycle including collection, analysis, functional set, decomposition, normative specification, implementation plan, implementation issues, and maintained artifacts.

### Replacement Concept

The primary Governance lifecycle should be:

**Design Proposal**
→ **Design**
→ **Plan**
→ **Build**

Useful current techniques move beneath those stages rather than disappearing.

For example:

**Design** may use collection, analysis, functional sets, and decomposition.

**Plan** may use implementation-plan decomposition and sequencing.

**Build** may use bounded implementation work and verification.

### Why Supersede It

The current lifecycle elevates one detailed development methodology into constitutional Governance structure and makes small changes carry unnecessary ceremony.

### Successor Placement

Governance.

---

## 30. GitHub Issue/Branch/PR Mechanics as Governance Semantics

### Disposition

**SUPERSEDE**

### Current Concept

The current workflow contains repository-generic normative requirements directly describing governing issues, branch naming, push, PR creation, and hosted state inspection.

### Replacement Concept

Governance should define generic governed-work semantics:

- identity;
- stage;
- predecessor;
- scope;
- candidate result;
- evidence;
- state;
- explicit acceptance or rejection; and
- provenance.

A GitHub profile may realize those semantics using issues, branches, PRs, checks, labels, or other platform facilities.

### Useful Subordinate Idea Retained

The current operational discipline around bounded work, isolated changes, exact bases, and review remains useful as profile realization guidance.

### Successor Placement

Governance + subordinate platform profile.

# Cross-Cutting Successor Principles

The retained and modified concepts suggest several broader design principles that should guide successor normalization.

## Explicitness Over Inference

Authority, ownership, provenance, applicability, extension, candidate state, evidence, and acceptance should be machine-resolvable wherever practical.

The framework should not require actors to infer control from file proximity, convention, implementation behavior, or conversation history.

## Default Deny With Governed Extension

Unknown maintained state should not automatically be accepted.

Growth should occur through explicit extension points rather than accidental precedent.

## Evidence Is Not Interpretation, and Interpretation Is Not Authority

The successor should preserve clear distinctions:

**evidence**
≠ **analysis**
≠ **directional design**
≠ **normative authority**
≠ **realization intent**
≠ **implementation**
≠ **Conformance result**
≠ **Assurance finding**
≠ **Governance acceptance**

Each may inform another without silently becoming it.

## Layer Before Commitment

Where complexity warrants it, Design should move from evidence through analysis and decomposition before producing normative requirements.

The framework should discourage direct conversion of raw user intent into implementation or persistent normative semantics.

## Refinement Without Authority Inversion

Lower-level product specifications, Plans, Conformance assertions, Assurance interpretations, generated artifacts, and implementation may refine, realize, evaluate, or explain upstream authority without independently redefining it.

## One Semantic Owner

Each independently governed semantic invariant should have one controlling normative owner.

Other artifacts should reference or derive from that owner rather than maintain competing semantic copies.

## Explicit Promotion

Exploration, candidate design, analysis, review, successful execution, merge, repeated use, and historical convention should not silently promote an artifact or conclusion into maintained authority.

Promotion should occur only through the governed mechanism appropriate to the target role.

# Candidate Normalization Targets

The statements below are non-authoritative normalization targets, not a fifth parallel normative requirement set.

They identify candidate semantics for incorporation into their controlling Framework Contract, Governance, Conformance, Assurance, product-authority, or subordinate specifications.

Where a target overlaps an existing candidate requirement, later Design should normalize it into the single controlling semantic owner rather than preserve a duplicate requirement.

### SC-01 — Default-Deny Maintained State

**Maintained governed state SHALL require accepted authorization or an explicitly governed extension point.**

### SC-02 — Explicit Extension

**Framework extensibility SHALL occur only through extension points authorized by accepted authority.**

### SC-03 — Declared Authority

**Accepted authority and authority-bearing relationships SHALL be machine-resolvable without relying solely on convention or implementation discovery.**

### SC-04 — Semantic Ownership

**Each independently governed semantic invariant SHALL have one controlling normative owner.**

### SC-05 — Evidence Preservation

**Governance Design SHALL preserve material source evidence and unresolved intent without silently converting them into accepted normative semantics.**

### SC-06 — Layered Design

**Governance Design SHALL distinguish analysis and directional decomposition from normative semantic acceptance.**

### SC-07 — Optional Design Decomposition

**Governance MAY require capability grouping or directional decomposition where necessary to produce coherent normative authority, but those techniques SHALL NOT constitute mandatory primary Governance stages.**

### SC-08 — Refinement Boundary

**A subordinate refinement, realization, enforcement, review, or projection SHALL NOT independently redefine the controlling normative semantics from which it derives.**

### SC-09 — Evidence Freshness

**Evidence used for governed disposition SHALL resolve to the candidate state for which that evidence is claimed.**

### SC-10 — Exploratory Isolation

**Exploratory work SHALL NOT acquire maintained or authoritative status without explicit governed promotion.**

### SC-11 — Platform Subordination

**Hosting-platform realization SHALL remain subordinate to portable framework authority and SHALL NOT independently define framework Governance, Conformance, or Assurance semantics.**

### SC-12 — Bounded Governed Authorization

**A governed work item SHALL authorize only its explicitly governed scope and SHALL NOT independently authorize unrelated or successor work.**

### SC-13 — Acyclic Normative Dependency

**Normative authority SHALL NOT depend for its authority on a cycle of normative dependencies.**

### SC-14 — Observed and Desired External State

**Governed external-state mutation SHALL distinguish observed state, desired state, authorized mutation, and post-mutation verification.**

## Audit Questions

The successor Design should determine:

1. Which retained concepts belong in the Framework Contract itself and which should remain subordinate.
2. Whether default deny should apply only to maintained artifacts or to all maintained governed relationships and roles, and which generalized rule belongs in the Framework Contract.
3. What extension-point properties must be governed to prevent implicit authority creation.
4. Whether the current manifest model is the appropriate successor representation for all enumerable authority or only for specifications.
5. Which current semantic-owner rules should become Framework Contract requirements, including whether one controlling semantic owner should be foundational.
6. Which current functional-set semantics are generally useful Design principles and which are product-development-specific techniques.
7. Whether directional decomposition should have a standardized artifact or remain a technique with multiple possible representations.
8. Whether the current Level 0–3 product model remains the best abstraction-depth model for successor product authority.
9. Which artifact-taxonomy dimensions remain necessary after keystone roles and provenance are explicit.
10. Which current platform-independent workflow concepts remain after GitHub mechanics are moved to profile realization.
11. Which exact-revision evidence rules generalize to candidate-result identity beyond Git commits.
12. What conditions justify atomic physical realization without weakening logical Design → Plan → Build sequencing.
13. Which current validation ownership concepts should become Conformance ownership-domain semantics.
14. Which current semantic-review practices can be transformed into Assurance obligations and cases.
15. Whether any concept classified here as KEEP would create unnecessary foundational coupling if placed too high in the authority hierarchy.
16. How bounded governed authorization should be represented independently of any specific issue or platform mechanism.
17. Which normative dependency edges must be acyclic and which non-authoritative traceability graphs may legitimately contain cycles.
18. How observed, desired, planned, applied, and verified external state should be represented without creating platform-specific framework authority.

## Explicitly Deferred Concerns

This proposal intentionally does not define:

- successor repository directory layout;
- exact manifest representation;
- exact Design Proposal format;
- mandatory Design supporting artifacts;
- exact functional-set schema;
- exact decomposition schema;
- final product-Level vocabulary;
- exact artifact taxonomy;
- exact Conformance directory topology;
- exact correspondence schema;
- exact Assurance schema;
- exact GitHub profile realization;
- migration sequencing;
- bootstrap mechanics; or
- implementation language.

Those concerns belong to later Design and Plan after the successor concept set is accepted or otherwise incorporated into controlling architecture.

## Relationship to Successor Design

The intended conceptual hierarchy is:

**Framework Contract**
→ defines foundational authority and separation

**Governance**
→ controls persistent change and Design → Plan → Build progression

**Conformance**
→ provides closed mechanical enforcement

**Assurance**
→ provides governed semantic review

**Successor Concept Set**
→ preserves useful design lessons from the current repo-spec as non-authoritative Design input for detailed successor normalization and does not become an independent normative authority source

The successor should therefore be neither a clean-sheet rejection of the current repository nor a mechanical preservation of its current contracts.

It should retain strong concepts, relocate concepts whose authority is currently misplaced, and supersede concepts whose responsibilities are now better expressed by the four-part target architecture.
