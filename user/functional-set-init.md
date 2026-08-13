# functional-set lifecycle Whiteboard — Initial Functional-Set Discussion

Status: working collection evidence  
Authority: non-normative  
Phase: overview phase 1 — collection  
Purpose: durably capture user-supplied product-direction observations before functional-set analysis

## WB-0001 — Conversational overview development

functional-set lifecycle development is expected to begin conversationally between the user and an AI agent.

The user may describe the desired product incrementally, informally, and without a predetermined structure.

## WB-0002 — Unorganized input is expected

User-supplied product descriptions are likely to be unordered and may mix behaviors, constraints, goals, implementation concerns, examples, and future ideas.

The workflow must not require the user to organize this material before supplying it.

## WB-0003 — Overview has two distinct phases

The overview stage should contain two distinct phases:

1. collection;
2. analysis.

These phases have different purposes and should not be conflated.

## WB-0004 — Collection precedes interpretation

Overview phase 1 is data collection.

During collection, user comments should be itemized and durably recorded in a whiteboard document or whiteboard document set.

Collection should preserve the supplied product direction without prematurely converting every comment into a requirement, specification, implementation decision, or functional-set assignment.

## WB-0005 — Whiteboard is durable working evidence

The whiteboard is a durable record of evolving product intent.

It should survive beyond the originating conversation so subsequent AI sessions and human reviewers can recover the accumulated product direction without depending on conversation history.

## WB-0006 — Whiteboard content remains non-normative

Recording a statement in the whiteboard does not make that statement an accepted product specification.

Whiteboard content is evidence and input to later overview analysis.

## WB-0007 — Analysis is overview phase 2

Overview phase 2 analyzes the accumulated whiteboard material.

Its purpose is to identify coherent functional groupings, relationships, dependencies, ambiguities, and candidate functional-set boundaries.

## WB-0008 — Functional sets are capability-oriented

A functional set is an easily decomposed subset of the overall product functionality.

Functional sets should be organized around coherent product capability rather than technical architecture layers such as database, backend, frontend, or authentication in isolation.

## WB-0009 — Functional Set 0 is required

The initialization-era overview process requires identification of Functional Set 0, also called the Core Functional Set.

FS0 is selected during overview analysis rather than during raw collection.

## WB-0010 — FS0 establishes a minimally usable scaffold

The purpose of FS0 is to permit end-to-end development of a minimally usable product scaffold.

That scaffold should provide a usable product capability and enough integration structure for later functional sets to be added incrementally.

## WB-0011 — FS0 is an integration foundation

FS0 should establish the fundamental product surfaces required for subsequent functional sets to integrate without requiring replacement of the product's basic structure.

FS0 is therefore both a functional capability boundary and an integration foundation.

## WB-0012 — FS0 should be a vertical slice

The core functional set should represent an end-to-end usable capability rather than a collection of isolated technical layers.

A valid FS0 may cross multiple implementation concerns when necessary to produce a minimally usable product.

## WB-0013 — FS0 candidates precede acceptance

Overview analysis may identify multiple possible FS0 candidates.

Candidate identification and comparison should occur before one core functional set is accepted.

The workflow should distinguish candidate FS0 material from an accepted FS0.

## WB-0014 — User acceptance establishes the core

Overview phase 2 culminates in an accepted Core Functional Set.

The AI agent may synthesize, organize, compare, and recommend candidate boundaries, but the accepted core remains subject to user direction and correction.

## WB-0015 — Decomposition follows accepted functional-set identification

Functional-set development is part of the overview stage.

Detailed decomposition should begin only after the applicable functional set has been accepted.

For initialization, the first such transition is from accepted FS0 into FS0 decomposition.

## WB-0016 — Future functional-set candidates remain in the whiteboard

Analysis does not need to fully identify or accept all future functional sets before FS0 development begins.

Potential future capabilities and candidate functional sets should remain represented in the whiteboard until later overview iterations are ready to analyze and accept them.

## WB-0017 — Overview remains iterative after FS0

The overview stage is not exhausted when FS0 is accepted.

New user direction and previously deferred whiteboard material may be analyzed in later iterations to identify and develop subsequent functional sets.

## WB-0018 — Whiteboard survives functional-set acceptance

Whiteboard material should not be discarded when a functional set is accepted.

The whiteboard remains the durable evidence base for future analysis, clarification, additional functional-set discovery, and product evolution.

## WB-0019 — Functional sets are development boundaries

An accepted functional set provides a bounded unit for downstream decomposition, specification, planning, implementation, validation, and integration.

This allows product realization to proceed piecewise rather than requiring full-product decomposition before implementation begins.

## WB-0020 — Functional sets are integration boundaries

Each accepted functional set should have an explicit relationship to the existing product scaffold.

Subsequent functional sets should be integrated incrementally with the realized core and previously accepted functionality.

## WB-0021 — Functional sets provide traceability

Functional sets should provide a durable traceability boundary connecting:

- accepted overview intent;
- decomposition;
- normative specifications;
- implementation planning;
- implementation;
- tests and validation;
- integration state.

A functional-set identifier may become a useful traceability key across these downstream artifacts.

## WB-0022 — Functional sets provide an audit surface

Functional sets should provide a stable bounded surface for the repository audit workflow.

An audit should be able to target a specific accepted functional set and examine whether its downstream artifacts and implementation remain consistent with controlling authority.

## WB-0023 — Audit workflow remains subordinate to accepted authority

The audit workflow handoff is non-normative operational convenience material.

It does not establish product or repository authority.

Accepted repository and product specifications remain controlling authority during an audit.

## WB-0024 — Functional sets can bound audit scope

A functional set can provide a traversal root for an audit through:

accepted functional-set overview → decomposition → specifications → plan → implementation → tests and validation.

This should reduce ambiguity about what constitutes the audit subject and its controlling artifact set.

## WB-0025 — Audit findings must not create unauthorized product scope

If an audit discovers desirable product functionality that is not part of the accepted functional set being audited, that discovery should not automatically become an implementation correction.

Unaccepted product intent should return to the whiteboard for future overview analysis.

## WB-0026 — Existing audit deferral semantics align with the whiteboard

The audit workflow already requires unrelated discoveries to be deferred rather than allowing a governed patch to become a catch-all.

The whiteboard provides a natural durable destination for deferred observations that concern unaccepted or future product functionality.

## WB-0027 — Overview documents must remain machine-context bounded

Whiteboard, analysis, and functional-set material should follow the repository's existing document chunking rules.

The overview system should not introduce indefinitely growing monolithic documents that require excessive machine context.

## WB-0028 — Indexes should support selective loading

Chunked overview material should provide compact indexes or navigation surfaces so an AI agent can locate the active or relevant chunks without loading the entire overview history.

## WB-0029 — Overview capability belongs to the repository framework

The whiteboard, overview-analysis, and functional-set workflow is reusable repository-framework behavior.

It should therefore be represented in the `repo/` tree and distributed to initialized repositories through the repo-spec initialization product.

## WB-0030 — Initialized repositories need usable overview scaffolding

An initialized repository should receive the generic overview structure and workflow needed to begin product-direction collection and functional-set development.

Initialization should not require the product to already have a complete overview, decomposition, or functional-set inventory.

## WB-0031 — Framework scaffolding must not contain repo-spec-specific product intent

Because the `repo/` tree is transported into initialized repositories, repo-spec's own working discussion about developing the overview framework must not be embedded in transported framework-instance content.

Generic overview capability and repository-specific overview evidence must remain distinguishable.

## WB-0032 — Dogfooding requires a source-only working instance

Repo-spec should be able to use the same overview concepts to develop the overview framework itself.

The current discussion therefore needs a durable source-repository working whiteboard that is not automatically transported into initialized repositories.

## WB-0033 — Whiteboard, analysis, and accepted functional sets have distinct roles

The emerging model distinguishes three kinds of overview material:

- whiteboard — collected product-direction evidence;
- analysis — synthesis, grouping, candidate identification, and reasoning;
- accepted functional sets — deliberately accepted bounded product structure.

These should not be treated as interchangeable authority levels.

## WB-0034 — Functional-set acceptance creates a downstream handoff point

Once a functional set is accepted, it becomes suitable for handoff into decomposition and later product-artifact development.

The accepted functional set should provide enough bounded context and traceability for downstream work to proceed without reconstructing the original conversation.

## WB-0035 — Functional sets may support future framework upgrades

A durable functional-set model may provide a useful structure for future framework upgrades.

An upgrader could reason about accepted and realized functional sets, preserve product intent and traceability, migrate framework representation, and continue product development without reconstructing product state from arbitrary files.

## WB-0036 — Upgrade support is successor analysis material

The relationship between functional sets and framework upgrades is promising but is not yet an accepted design.

It should remain available for later analysis rather than being treated as an already-defined upgrade mechanism.

## WB-0037 — Immediate next stage

The immediate purpose of this document is collection only.

The next overview phase should analyze these whiteboard observations, identify coherent capability groupings, identify candidate core-functional-set boundaries, and culminate in an accepted FS0 before decomposition, specification updates, planning, or implementation proceeds.
