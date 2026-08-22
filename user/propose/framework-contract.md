# Framework Contract Architecture Proposal

## Status

Design proposal for audit against the current repository.

This document is non-authoritative. Its purpose is to describe a candidate foundational architecture for the repository framework that can be compared against accepted repository authority, existing governance behavior, validation behavior, review practices, schemas, generated artifacts, implementation, and product-maintenance workflows before any normative change is proposed.

## Objective

The repository framework shall be organized around one foundational Framework Contract that defines and bounds three authorized keystone mechanisms:

- Governance;
- Conformance;
- Assurance.

The Framework Contract is the foundational authority model for the repository framework. It defines what the framework is, where framework authority resides, how authority is delegated, which responsibilities belong to each keystone, which responsibilities are prohibited to each keystone, and how the keystones collectively support construction and maintenance of the governed product.

The singular architectural goal is separation of responsibility under one explicit framework authority:

- Governance controls authoritative change;
- Conformance mechanically enforces accepted normative authority;
- Assurance evaluates semantic meaning, quality, and sufficiency where mechanical enforcement alone cannot decide the matter.

The three keystones shall operate under authority delegated by the Framework Contract and shall not independently define the bounds of their own authority.

## Foundational Model

The proposed foundational model is:

```text
repo/
  -> defines the repository framework
      -> defines the Framework Contract
          -> authorizes and bounds Governance
          -> authorizes and bounds Conformance
          -> authorizes and bounds Assurance
              -> collectively support construction and maintenance
                  -> of the governed product
```

The `repo/` tree is the authoritative framework-definition surface.

The product is governed by the framework but does not independently define the framework that governs it.

Governance, Conformance, and Assurance are framework mechanisms. They derive their authority from accepted repository framework authority and do not possess independent authority merely because supporting implementation exists.

## Established Design Truths

The proposal assumes the following truths.

1. `repo/` is the authoritative repository-framework definition surface.
2. The Framework Contract is defined by accepted normative authority under `repo/`.
3. The Framework Contract authorizes exactly three primary framework keystones: Governance, Conformance, and Assurance.
4. The Framework Contract defines the responsibility boundary of each keystone.
5. A keystone may exercise only authority explicitly delegated to it by accepted framework authority.
6. No keystone may independently expand its own authority.
7. Governance is the exclusive framework mechanism for controlled authoritative change.
8. Conformance is the exclusive framework mechanism for repository-local mechanical enforcement of accepted normative requirements.
9. Assurance is the framework mechanism for governed semantic review, interpretation, quality evaluation, and sufficiency judgment where objective mechanical conformance is not enough.
10. Conformance does not create normative semantics.
11. Assurance does not independently amend normative semantics.
12. Persistent changes to normative authority flow through Governance.
13. The maintained product is subordinate to accepted framework and product authority.
14. Product implementation does not become normative merely because it exists.
15. Validation behavior does not become normative merely because it exists.
16. Review findings do not become normative merely because they exist.
17. Generated or derived artifacts remain subordinate to their accepted source authority.
18. Framework mechanisms shall expose sufficient provenance to determine why governed artifacts exist and which authority authorizes them.
19. Framework authority shall remain distinguishable from product authority.
20. The framework shall be capable of governing changes to itself without treating current implementation accidents as independent authority.

## Framework Contract

The Framework Contract is the foundational normative contract that defines the repository framework's authority topology.

It shall define at minimum:

- the authoritative role of `repo/`;
- the distinction between framework authority and product authority;
- the existence and purpose of Governance, Conformance, and Assurance;
- the authority delegated to each keystone;
- the authority prohibited to each keystone;
- permitted dependency directions among framework authority, keystones, and product authority;
- the mechanism by which persistent normative changes are authorized;
- the relationship between objective mechanical enforcement and semantic review;
- the requirement that derived implementation remain subordinate to accepted authority;
- the requirement that framework artifacts expose provenance sufficient for human and machine audit;
- the relationship between the framework and the maintained product;
- the rules necessary for framework self-hosting and controlled framework evolution.

The Framework Contract should remain intentionally compact.

It should define the powers, boundaries, relationships, and primary invariants of the framework without absorbing the detailed internal mechanics of Governance, Conformance, or Assurance.

Detailed keystone behavior should be defined by separately governed normative specifications subordinate to the Framework Contract.

## Framework Authority

Framework authority is accepted normative authority that defines how the repository framework operates.

Framework authority shall reside under `repo/`.

Framework authority may define:

- repository structure;
- artifact classes;
- authority relationships;
- lifecycle rules;
- governance process;
- conformance architecture;
- assurance architecture;
- schema contracts;
- generation relationships;
- provenance relationships;
- product-governance relationships;
- framework self-hosting behavior.

Framework implementation outside normative specifications may realize framework authority but shall not independently establish it.

The existence of implementation behavior, historical convention, generated output, test behavior, workflow automation, validation code, issue templates, or review practice shall not by itself create framework authority.

## Product Authority

Product authority defines the accepted normative semantics of the maintained product.

Product authority is distinct from framework authority.

The Framework Contract defines how product authority is created, changed, enforced, reviewed, projected, and maintained, but product authority does not independently redefine those framework rules.

The proposed relationship is:

```text
framework authority
    -> defines Governance
        -> governs creation and change of product authority

product authority
    -> governs product implementation

framework authority
    -> defines Conformance
        -> enforces applicable framework and product authority

framework authority
    -> defines Assurance
        -> reviews applicable framework and product authority and evidence
```

## Keystone: Governance

Governance is the framework mechanism for controlled authoritative change.

Governance answers:

> What change is being considered, authorized, planned, built, and accepted?

The Framework Contract shall authorize Governance to manage the lifecycle through which proposed repository changes become accepted governed state.

The detailed Governance proposal is expected to define a workflow whose primary stages are:

```text
Design Proposal
    -> Design governed work
        -> Plan governed work
            -> Build governed work
```

Each primary stage is expected to be represented by a governed-work issue and to contain its own defined sub-stages and transition gates.

The Framework Contract should not define those detailed stage mechanics beyond the minimum necessary to establish Governance's authority and responsibility.

### Governance May

Governance may:

- receive detailed non-authoritative design proposals;
- audit candidate designs against accepted authority and repository state;
- normalize candidate design into proposed normative changes;
- authorize accepted normative changes through defined lifecycle rules;
- create and accept realization plans;
- authorize and track builds;
- manage lineage, supersession, acceptance, and governed change provenance;
- route discoveries back to earlier governed stages when design or planning defects are found;
- govern changes to framework authority and product authority within their respective authority boundaries.

### Governance Shall Not

Governance shall not:

- treat a non-authoritative proposal as accepted authority merely because it is detailed;
- treat implementation behavior as normative merely because it exists;
- treat passing validation as authority to invent requirements;
- bypass accepted authority-change rules to resolve ambiguity informally;
- use workflow state as a substitute for mechanical conformance;
- use workflow acceptance as a substitute for semantic assurance where assurance is required.

## Keystone: Conformance

Conformance is the framework mechanism for objective mechanical enforcement of accepted normative authority.

Conformance answers:

> Does observable repository state satisfy mechanically enforceable accepted normative requirements?

Conformance shall operate through a closed, governed validation hierarchy.

Validation is the implementation mechanism. Conformance is the architectural responsibility that validation establishes.

The Framework Contract shall authorize Conformance to reject repository states that mechanically violate accepted normative requirements.

### Conformance May

Conformance may:

- mechanically inspect repository state;
- evaluate objective predicates derived from accepted normative requirements;
- reject mechanically nonconforming states;
- produce deterministic conformance evidence;
- maintain validation packages and validation primitives where authorized by accepted authority;
- use shared implementation helpers where provenance and authority remain clear;
- validate its own correspondence, structure, execution, and evidence model;
- expose generated coverage and correspondence views subordinate to accepted authority.

### Conformance Shall Not

Conformance shall not:

- create normative requirements;
- extend a normative requirement beyond accepted semantics;
- use historical implementation behavior as substitute authority;
- silently convert implementation preference into normative enforcement;
- place normative enforcement behavior outside the governed conformance hierarchy;
- claim semantic certainty where accepted authority requires interpretation or judgment;
- permit validation primitives with no human- and machine-resolvable provenance to accepted normative authority.

### Conformance Provenance Principle

Every maintained derived validation primitive shall be human- and machine-traceable to the accepted normative requirement or requirements that authorize its existence.

Every mechanically enforceable accepted normative requirement shall resolve to its maintained conformance primitives.

This relationship shall be bidirectionally closed.

The detailed Conformance proposal is expected to define validation-package identity, validation-primitive identity, closed hierarchy rules, direct and transitive provenance, executable assertions, unit tests, self-tests, fixtures, mutation evidence, runners, helpers, and correspondence integrity.

## Keystone: Assurance

Assurance is the framework mechanism for governed semantic review, interpretation, quality evaluation, and sufficiency judgment where mechanical conformance alone cannot decide the matter.

Assurance answers:

> Is the accepted authority, realization, evidence, or interpretation semantically adequate and sufficiently justified?

Assurance may be performed by qualified humans, AI agents operating under governed instructions, or a defined combination of both.

The Framework Contract shall distinguish Assurance from both Governance and Conformance.

Assurance does not gain normative authority merely because a reviewer reaches a conclusion.

### Assurance May

Assurance may:

- review proposed normative requirements for clarity, atomicity, consistency, and semantic quality;
- identify ambiguity, contradiction, overlap, omission, or implementation leakage in normative authority;
- interpret accepted authority for a bounded review case;
- review whether conformance evidence is sufficient for the claim being made;
- review partially mechanical requirements;
- review requirements for which meaningful conformance depends on semantic judgment;
- inspect implementation and conformance behavior for divergence from accepted intent;
- issue governed findings;
- recommend remediation;
- route findings requiring persistent semantic change back into Governance.

### Assurance Shall Not

Assurance shall not:

- silently amend normative requirements;
- establish persistent normative semantics solely through a review finding;
- replace Governance as the authority-change mechanism;
- replace Conformance for objective mechanical enforcement;
- convert reviewer preference into framework or product authority;
- treat AI-generated interpretation as authoritative merely because it is plausible.

### Assurance Escalation Principle

When Assurance determines that accepted normative authority is ambiguous, contradictory, incomplete, or otherwise requires persistent semantic change, the remedy shall flow through Governance.

A bounded interpretation may support disposition of the case under review, but persistent framework or product semantics shall be changed only through authorized Governance.

## Separation of Keystone Responsibilities

The keystones exist to prevent one framework mechanism from silently assuming the responsibilities of another.

The proposed separation is:

| Keystone | Primary responsibility | May create persistent normative authority? | May mechanically reject state? | May issue semantic findings? |
| --- | --- | --- | --- | --- |
| Governance | controlled authoritative change | yes, through governed acceptance | not as a substitute for Conformance | may consume findings but is not Assurance |
| Conformance | objective mechanical enforcement | no | yes | no, except reporting inability to decide mechanically |
| Assurance | semantic review and sufficiency judgment | no | no, except where Governance delegates a review gate rather than a mechanical predicate | yes |

The exact mechanics of review gates and acceptance consequences remain subject to the Assurance and Governance proposals.

## Cross-Keystone Relationships

The Framework Contract shall define explicit permitted interactions among the keystones.

### Governance to Conformance

Governance may create or change accepted normative authority that changes conformance obligations.

Conformance shall consume accepted authority, not draft intent, as the semantic basis for persistent mechanical enforcement.

A Build may include planned Conformance changes, but those changes shall remain traceable to accepted normative authority and an accepted realization plan.

### Governance to Assurance

Governance may require Assurance review at defined lifecycle gates.

Governance may consume Assurance findings as evidence or as triggers for additional governed work.

Assurance findings requiring persistent semantic change shall return to Governance.

### Conformance to Governance

Conformance failures may block governed progression where accepted Governance rules require conformance.

Conformance may identify missing correspondence or an inability to mechanically enforce a requirement, but it shall not repair such problems by inventing new authority.

Required authority changes return to Governance.

### Conformance to Assurance

Conformance may expose evidence for Assurance review.

Conformance may identify requirements whose semantics cannot be completely established mechanically.

Assurance may evaluate whether remaining semantic obligations are adequately satisfied.

### Assurance to Governance

Assurance findings may trigger a new Design Proposal, reopen governed Design, or otherwise route through a Governance mechanism defined by accepted authority.

### Assurance to Conformance

Assurance may identify that a conformance primitive misinterprets accepted authority or that objective portions of a requirement should be mechanically enforceable.

Assurance shall not directly redefine the enforcement rule. Persistent correction shall follow accepted Governance and Conformance rules.

## Permitted Dependency Direction

The proposed authority dependency direction is:

```text
Framework Contract
    -> Governance definition
    -> Conformance definition
    -> Assurance definition

Framework authority
    -> keystone mechanisms

Governance
    -> accepted framework or product authority changes

accepted authority
    -> Conformance enforcement
    -> Assurance review basis

Conformance evidence
    -> Assurance review input
    -> Governance gate input where defined

Assurance finding
    -> Governance input when persistent change is required
```

Implementation dependencies may differ from authority dependencies, but implementation structure shall not obscure or invert normative authority.

## Forbidden Authority Inversions

The framework should mechanically or semantically guard against authority inversion.

Examples of forbidden authority inversion include:

```text
validation implementation
    -> treated as normative because it already rejects something
```

```text
review interpretation
    -> treated as persistent normative semantics without governed change
```

```text
product implementation
    -> treated as framework authority because existing behavior depends on it
```

```text
workflow convention
    -> treated as accepted governance authority without normative ownership
```

```text
generated documentation
    -> treated as independent source authority
```

```text
bootstrap accommodation
    -> promoted into permanent target semantics solely to make the current repository self-conforming
```

## Normative Requirement Quality

The Framework Contract should require the framework to define a governed quality model for normative requirements.

Normative requirements are the root semantic inputs to Governance, Conformance, and Assurance. Poorly factored requirements therefore propagate ambiguity and coarse correspondence throughout the framework.

The detailed quality model may be defined by subordinate framework authority, but the Framework Contract should establish the principle that normative authority must be suitable for deterministic identification, review, realization, and conformance mapping.

A normative requirement should represent one primary obligation wherever practical.

Explanatory rationale, examples, migration notes, implementation guidance, and contextual prose should remain distinguishable from the normative statement itself.

Mechanical requirement-quality checks may reject structural defects and detect strong ambiguity indicators.

Assurance should evaluate semantic properties that cannot be established mechanically, including atomicity, clarity, contradiction, overlap, and inappropriate implementation leakage.

## Framework Artifacts and Provenance

Every maintained framework artifact shall have a defined authority relationship.

The repository should be able to determine for a governed artifact:

- what class of artifact it is;
- whether it is normative, implementation, evidence, derived output, proposal, or historical provenance;
- which accepted authority authorizes its existence;
- which keystone owns its lifecycle or use;
- whether it may influence normative semantics;
- what upstream artifact or authority it derives from;
- what downstream artifacts or behavior it authorizes or supports.

No artifact should acquire semantic authority merely because its purpose is unclear.

The absence of provenance should be treated as a framework defect rather than as permission for an agent to infer authority.

## AI Agent Boundary

The framework shall be designed for operation by AI agents as well as humans.

AI agents are especially likely to infer plausible behavior from surrounding implementation, create helpful-looking validation outside the intended hierarchy, preserve accidental historical behavior, merge multiple normative obligations into one implementation abstraction, or treat an implementation shortcut as a design rule.

The Framework Contract should therefore require explicit boundaries that minimize implicit authority inference.

An AI agent should be able to determine mechanically or from authoritative documentation:

- which artifacts are authoritative;
- which artifacts are proposals;
- which keystone currently owns the work being performed;
- which normative requirement authorizes a derived enforcement primitive;
- whether it is permitted to change authority in the current workflow stage;
- whether an ambiguity requires Assurance;
- whether a persistent semantic correction requires Governance;
- where conformance code is legally permitted to exist;
- what evidence is required before governed completion.

When no accepted authority supports a proposed enforcement behavior, an agent shall not create that enforcement behavior merely because it appears useful.

## Maintained Product Relationship

The purpose of the framework is to build and maintain the governed product.

The three keystones collectively support that purpose:

```text
Governance
    -> authorizes product change

Conformance
    -> mechanically enforces applicable accepted authority

Assurance
    -> reviews semantic adequacy and sufficiency

all under
    -> Framework Contract authority
```

The product may contain product-specific normative authority and implementation, but framework powers remain defined by `repo/`.

Product-specific mechanisms shall not silently redefine the Framework Contract.

## Framework Self-Governance

The framework must be capable of changing itself through the mechanisms it defines.

Self-governance does not mean that every intermediate bootstrap repository state must already satisfy every target-state invariant.

The framework should distinguish:

- target architecture;
- transitional migration state;
- bootstrap accommodations.

Bootstrap accommodations should remain explicit, bounded, and removable.

They should not redefine target semantics solely to make the current implementation pass its own checks.

A framework change that modifies Governance, Conformance, Assurance, or the Framework Contract itself shall preserve sufficient provenance to show:

- which prior authority permitted the change process;
- which proposal motivated the change;
- which governed work authorized the change;
- which accepted normative requirements resulted;
- which implementation and conformance changes realized the result;
- which assurance findings, if any, affected the result.

## Self-Hosting

The desired mature framework is self-hosting.

A self-hosting `repo-spec` should be capable of using accepted framework authority from an existing generation to construct a new repository generation whose Governance, Conformance, and Assurance mechanisms are derived from and subordinate to the accepted framework model.

The intended bootstrap progression is:

```text
existing repo-spec generation
    -> accepted repo/ framework authority
        -> authorized Governance
        -> authorized Conformance
        -> authorized Assurance
            -> governed construction of new repo-spec generation
                -> independently coherent framework
                    -> capable of repeating the process
```

A new generation should not be produced by blindly copying historical implementation merely because the historical implementation exists.

Bootstrap-only structures should migrate only when the accepted target model requires them.

## Framework Contract Versus Keystone Specifications

The Framework Contract should define the existence, purpose, authority, prohibition, and interaction boundaries of the three keystones.

It should not define detailed keystone mechanics that belong in subordinate proposals and specifications.

Examples expected to remain outside the Framework Contract include:

### Governance Details

- exact Design, Plan, and Build sub-stage names;
- governed-work issue schema fields;
- exact transition-state machine;
- proposal promotion mechanics;
- plan document schema details;
- build evidence details.

### Conformance Details

- validation package schema shape;
- validation primitive taxonomy;
- metadata syntax;
- fixture metadata representation;
- runner implementation;
- exact evidence taxonomy;
- exact assertion-to-test cardinality.

### Assurance Details

- review artifact schema;
- review assignment model;
- human-versus-agent review policy;
- exact finding classes;
- adjudication mechanics;
- interpretation lifetime;
- review evidence representation.

The Framework Contract may establish invariants that those details must satisfy.

## Candidate Foundational Invariants

The following are candidate Framework Contract invariants subject to audit and normative decomposition.

### Framework Authority Invariant

> Accepted framework authority SHALL reside under the authoritative `repo/` framework-definition surface.

### Delegation Invariant

> Governance, Conformance, and Assurance SHALL exercise only authority delegated by accepted framework authority.

### Governance Invariant

> Persistent changes to accepted normative authority SHALL occur only through the authorized Governance mechanism.

### Conformance Invariant

> Mechanical normative enforcement SHALL occur only through the authorized Conformance mechanism and SHALL remain traceable to accepted normative authority.

### Assurance Invariant

> Semantic review and interpretation SHALL occur through the authorized Assurance mechanism and SHALL NOT independently create persistent normative authority.

### Separation Invariant

> No keystone SHALL independently exercise authority reserved to another keystone.

### Product-Subordination Invariant

> Product implementation and product-local behavior SHALL remain subordinate to accepted framework and product authority and SHALL NOT independently redefine framework authority.

### Provenance Invariant

> Every maintained derived framework primitive SHALL possess human- and machine-resolvable provenance to the accepted authority that authorizes its existence or use.

### No-Implicit-Authority Invariant

> Implementation behavior, validation behavior, review findings, generated artifacts, workflow convention, and historical repository state SHALL NOT independently create normative authority.

### Bootstrap Invariant

> Bootstrap or transitional accommodations SHALL NOT redefine target framework semantics solely to make an intermediate repository state self-conforming.

## Mechanical Validation of the Framework Contract

The Framework Contract should delegate mechanical enforcement of objectively decidable contract properties to Conformance.

Potential mechanically enforceable properties include:

- required authoritative framework locations exist;
- forbidden authority locations are rejected;
- declared keystone artifacts reside within governed locations;
- conformance primitives do not exist outside the governed conformance hierarchy;
- required provenance metadata resolves to accepted authority;
- forbidden dependency directions are absent where mechanically observable;
- generated artifacts do not masquerade as source authority;
- accepted normative requirement identifiers are unique and structurally valid;
- derived artifacts resolve to their source authority;
- framework and product authority remain distinguishable by structure and metadata.

Mechanical Conformance shall not pretend to establish semantic properties that require Assurance.

## Assurance of the Framework Contract

The Framework Contract should delegate semantic framework review to Assurance.

Potential Assurance responsibilities include:

- whether a proposed normative requirement is sufficiently atomic;
- whether two accepted requirements contradict or overlap;
- whether a keystone specification has exceeded its delegated authority;
- whether an implementation is exploiting a loophole while technically passing mechanical checks;
- whether a bootstrap accommodation has improperly hardened into target architecture;
- whether framework behavior remains faithful to the purpose of the Framework Contract;
- whether a proposed authority decomposition is understandable to a human or AI agent without relying on undocumented historical context.

## Derived Views

Human-readable framework views should be generated from accepted authority where practical rather than manually maintained as independent semantic sources.

Potential derived views include:

- framework authority map;
- keystone responsibility matrix;
- allowed dependency graph;
- forbidden authority-inversion report;
- framework-to-product authority map;
- normative requirement quality report;
- conformance provenance report;
- assurance findings summary;
- self-hosting lineage view.

Derived views shall remain evidence and navigation aids, not independent normative authority.

## Migration from Current repo-spec

The current repository is a bootstrapping and dogfooding implementation whose present structure includes target architecture, historical implementation choices, transitional accommodations, and newly introduced self-validation machinery.

Migration should not assume that all current behavior belongs in the target Framework Contract.

The current repository should be audited by classifying relevant behavior and artifacts as:

- target Framework Contract semantics;
- Governance semantics;
- Conformance semantics;
- Assurance semantics;
- product semantics;
- implementation detail;
- generated evidence;
- bootstrap accommodation;
- obsolete historical residue;
- currently unauthorized behavior requiring either removal or new accepted authority.

Migration should prefer semantic simplification over preservation of accidental complexity.

The intended result is not a renamed current repository. It is a normalized framework capable of constructing a new `repo-spec` generation from explicit accepted authority.

## Desired End State

The repository should expose one understandable authority model:

```text
repo/
    -> Framework Contract
        -> Governance
            -> controlled authoritative change
        -> Conformance
            -> mechanical normative enforcement
        -> Assurance
            -> semantic review and sufficiency judgment

Governance
    -> creates and changes accepted framework/product authority

accepted authority
    -> governs maintained product implementation
    -> authorizes Conformance obligations
    -> provides Assurance review basis

Conformance evidence
    -> demonstrates objective satisfaction or violation

Assurance findings
    -> evaluate semantic adequacy
    -> return persistent semantic changes to Governance
```

A human or AI agent should be able to inspect repository state and determine:

- what is authoritative;
- why it is authoritative;
- which keystone owns a responsibility;
- what derived behavior is authorized by which normative requirement;
- whether a finding is mechanical or semantic;
- whether a semantic change requires Governance;
- whether an artifact is source authority or subordinate evidence;
- whether the framework is operating within its declared bounds.

## Proposed Primary Design Invariant

The Framework Contract should be evaluated against the following invariant:

> The authoritative `repo/` framework shall explicitly define and bound Governance, Conformance, and Assurance such that persistent authority is changed only through Governance, objective normative requirements are mechanically enforced only through Conformance, semantic sufficiency and interpretation are handled only through Assurance, and every maintained derived framework primitive remains subordinate and traceable to accepted authority.

All framework structure, lifecycle, validation, review, generation, provenance, migration, and self-hosting decisions should preserve this invariant.

## Audit Questions

The current repository should be audited against this proposal by determining:

1. Which current `repo/` specifications already define foundational Framework Contract semantics.
2. Which current framework semantics exist only in implementation, workflow automation, validation, documentation, or historical convention.
3. Which current specifications mix Framework Contract, Governance, Conformance, Assurance, and product concerns within the same normative requirement.
4. Which current normative requirements are too prose-heavy or compound to serve as clean authority anchors.
5. Which current requirements should be split, merged, clarified, superseded, or withdrawn during normalization.
6. Which current governance mechanisms independently perform functions that should belong to Conformance or Assurance.
7. Which current validation mechanisms enforce semantics with no accepted normative owner.
8. Which current validation primitives exist outside the intended closed Conformance hierarchy.
9. Which current validation helpers, runners, tests, self-tests, fixtures, schemas, and metadata lack complete provenance to accepted normative requirements.
10. Which current semantic-review or not-applicable dispositions actually represent missing Assurance architecture.
11. Which current review practices produce interpretations that function as de facto authority without governed normalization.
12. Which current generated or derived artifacts risk being mistaken for independent authority.
13. Which current product artifacts improperly define framework behavior.
14. Which current framework artifacts depend on product-specific behavior in a way that inverts authority.
15. Which current bootstrap accommodations have become embedded in normative architecture only to keep the dogfooding repository self-conforming.
16. Which current structures are necessary only for the bootstrap generation and should not migrate into the self-hosted generation.
17. Which objective Framework Contract properties can be mechanically enforced by Conformance.
18. Which Framework Contract properties require Assurance rather than mechanical validation.
19. What provenance model is required so both human and AI agents can distinguish authority, implementation, evidence, proposal, and historical context.
20. What minimum accepted authority is required for the current repo-spec generation to build a clean self-hosted successor.
21. Whether `Framework Contract` is the correct durable software-engineering term for this foundational concept or whether audit identifies a more precise term.
22. Which normative requirements must exist in the Framework Contract before the separate Governance, Conformance, and Assurance design proposals can be normalized without circular authority.

## Follow-On Design Proposals

This proposal intentionally leaves detailed keystone mechanics to three follow-on design proposals:

1. Governance Architecture Proposal;
2. Conformance Architecture Proposal;
3. Assurance Architecture Proposal.

Those proposals should be audited against the accepted Framework Contract and should not assume powers that the Framework Contract does not delegate.

The Framework Contract proposal should therefore be audited and normalized first.
