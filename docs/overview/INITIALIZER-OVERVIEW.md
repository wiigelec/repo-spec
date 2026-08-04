# Repo-Spec Initializer Overview

## Status

Product-direction overview for the `repo-spec` initializer.

This document records the durable high-level intent of the initializer as a maintained product of `repo-spec`.

It is directional and non-normative. It provides the basis for decomposition, planning, specification, implementation, validation, review, acceptance, release, and maintenance work.

It does not:

* define exact initializer behavior;
* establish normative interfaces or data formats;
* authorize repository mutation;
* accept an implementation;
* replace accepted repository specifications;
* establish release readiness.

Exact behavior must be defined later through accepted product specifications developed under the governed workflow.

## Product identity

The initializer is the principal maintained product produced by `repo-spec`.

`repo-spec` defines a reusable governed-development framework for creating and maintaining product repositories. The initializer applies that framework to establish a new project repository in a valid initial governed state.

The initializer is not merely:

* a file copier;
* a project skeleton;
* a template renderer;
* a repository generator;
* a one-time bootstrap script.

It is a maintained product that creates the foundation from which another maintained product can be developed under the `repo-spec` governed workflow.

## Problem

Starting a maintained product repository requires more than creating directories and copying configuration files.

A project must begin with coherent foundations for:

* product direction;
* decomposition;
* implementation planning;
* repository authority;
* product specifications;
* artifact ownership;
* validation;
* review;
* acceptance;
* exact-revision evidence;
* human and AI continuity;
* hosting-platform integration;
* later release and maintenance.

Without a repeatable initialization mechanism, each new project must reconstruct these foundations manually.

Manual reconstruction creates several risks:

* required repository contracts may be omitted;
* authority relationships may be inconsistent;
* product semantics may be invented prematurely;
* generated artifacts may be mistaken for authoritative sources;
* hosting-provider assumptions may leak into the universal framework;
* project history may begin without a clear accepted base;
* implementation may begin before an overview, plan, or specifications exist;
* validation may be incomplete or dependent on external state;
* future human or AI sessions may lack sufficient repository-local context;
* generated projects may drift away from the framework’s intended development model.

The initializer must reduce these risks while preserving the distinction between reusable framework foundations and project-specific product decisions.

## Desired outcome

A user can use an accepted revision of the `repo-spec` initializer to establish a new repository that is ready to begin maintained product development through the `repo-spec` governed workflow.

The initialized repository must contain the repository-local authority, structure, tooling, records, and starting artifacts needed to proceed through:

```text
product idea
→ product overview
→ decomposition
→ implementation plan
→ candidate product specifications
→ accepted product specifications
→ product artifacts
→ validation
→ semantic review
→ exact-revision acceptance
→ merge
→ post-merge validation
→ release and maintenance
```

The initializer must create the foundation for this process without falsely claiming that unresolved product direction, plans, specifications, or implementation have already been accepted.

## Intended users

The initializer is intended for:

* individuals beginning a new maintained software or technical product;
* teams that want repository-local development authority and continuity;
* maintainers adopting the `repo-spec` framework for a new project;
* developers who want explicit correspondence among specifications, implementation, tests, and conformance evidence;
* human and AI collaborators working across multiple bounded sessions;
* framework maintainers validating that `repo-spec` can initialize more than one independent product repository.

The initial product may prioritize technically experienced users comfortable with:

* Git;
* command-line tools;
* structured repository artifacts;
* governed issue and review workflows;
* explicit product specifications.

A future user experience may simplify these concepts, but simplification must not erase the underlying authority boundaries.

## Primary user outcome

After successful initialization, the user has a self-contained repository that can answer:

* What product is being proposed?
* Which product-direction questions remain unresolved?
* What authority governs repository changes?
* What exact `repo-spec` revision established the repository?
* What repository specifications are installed?
* Which artifacts are authoritative, derived, generated, candidate, or accepted?
* What work is currently authorized?
* What validation commands apply?
* How should the next bounded change begin?
* Which hosting-platform behavior is installed?
* What remains explicitly outside the initialized scope?

The repository must provide these answers from repository-local records rather than requiring prior conversation history or access to the source `repo-spec` checkout.

## Product principles

### Governed creation

The initializer must itself be developed through the `repo-spec` governed workflow.

Its overview, plans, product specifications, implementation, tests, conformance evidence, reviews, acceptance records, releases, and maintenance changes must preserve the same authority boundaries it installs for other projects.

The initializer must demonstrate the workflow rather than bypass it.

### Overview before plan

Initializer development begins from durable product intent.

The implementation plan must be derived from an accepted overview direction. It must not become the source of product identity or silently establish normative behavior.

### Specifications before maintained behavior

Exact initializer behavior must be defined through accepted product specifications before it becomes maintained product behavior.

Implementation and tests may provide evidence, but they do not become normative merely because they exist or pass.

### Exact-revision evidence

Initialization must be attributable to exact revisions.

A generated repository should be able to identify:

* the exact initializer revision;
* the applicable specification revision;
* the selected reusable source material;
* the initialization inputs;
* the resulting initialized repository revision or content identity.

### Self-contained output

A successfully initialized repository must not require:

* the source `repo-spec` checkout;
* private framework history;
* prior chatbot conversations;
* ambient working-tree state;
* undeclared parent files;
* network access for its normal repository-local validation path.

### No invented product semantics

The initializer may establish structures for product direction and specification work.

It must not invent:

* users;
* required product behavior;
* architectural choices;
* interfaces;
* domain terminology;
* acceptance decisions;
* release claims.

Project-specific meaning must come from the project’s governed overview, plans, and accepted specifications.

### Lifecycle honesty

Generated artifacts must accurately represent their lifecycle state.

Candidate material must remain candidate.

Placeholder material must remain visibly incomplete.

Generated files must remain subordinate to declared sources.

No generated artifact may be represented as semantically accepted without the applicable governed acceptance process.

### Framework and project separation

The initializer must distinguish:

* reusable framework material;
* initializer-product behavior;
* hosting-platform profile material;
* initialized repository authority;
* project-specific product content;
* generated or derived artifacts.

The generated project becomes independently governed after initialization.

The initializer does not remain a hidden external authority over ordinary project development.

### Git compatibility

The universal initializer model must remain Git-compatible.

Hosting-provider features may be installed through explicit profiles, but GitHub-specific behavior must not define universal initializer semantics.

### Determinism and auditability

Equivalent accepted inputs should produce equivalent governed outputs except where nondeterminism is explicitly permitted and recorded.

The initialization process and result must be reviewable, reproducible, and auditable.

### Safe failure

Initialization must avoid destructive or ambiguous partial results.

Invalid input, conflicting paths, unsupported profiles, unresolved substitutions, or failed validation must produce clear failure rather than an apparently usable but incoherent project.

## Major capabilities

The initializer is expected to provide capabilities in the following areas.

### Initialization request

Accept a structured description of the repository to initialize.

The request should provide only information legitimately known at initialization time, such as:

* project identity;
* project title;
* brief stated purpose;
* destination;
* selected platform profile;
* requested product-activation mode;
* explicitly supplied initial overview material;
* exact initializer or framework revision where applicable.

The request must not be treated as an accepted product specification.

### Governed workspace establishment

Create an isolated workspace for producing and validating the initialized repository.

The process should establish:

* exact source revision;
* initialization authority;
* bounded scope;
* selected inputs;
* explicit exclusions;
* ordered initialization phases;
* validation expectations;
* completion conditions.

### Repository authority installation

Install the reusable repository-generic foundations required for governed work, including the applicable:

* repository manifest;
* repository specifications;
* schemas;
* derived documentation;
* governing-issue contract;
* review-proposal contract;
* development workflow;
* validation entry points;
* repository instructions.

### Product-direction foundation

Create a project-specific overview location and sufficient initial material to begin product-direction work.

The initializer may incorporate overview content explicitly provided by the user.

It must clearly distinguish:

* supplied statements;
* framework-provided structure;
* unresolved questions;
* candidate direction;
* accepted framework authority.

### Planning foundation

Provide the structure required to create an implementation plan after the project overview is sufficiently established.

The initializer may create an empty or candidate planning artifact, but must not fabricate a completed product roadmap.

### Product-specification foundation

Install the Level 0–3 product-specification framework and the structures needed for:

* product manifest participation;
* dependency declarations;
* lifecycle states;
* schemas;
* implementation correspondence;
* test correspondence;
* conformance correspondence;
* derived projections.

Product specification content should remain empty, candidate, or explicitly incomplete until governed product work defines it.

### Platform-profile installation

Install selected hosting-platform adapters without making them universal framework requirements.

The initial maintained product may support GitHub first, while preserving a profile boundary that allows:

* no hosting profile;
* future alternative profiles;
* profile-specific validation;
* clear adapter ownership.

### Validation

Validate both:

* the initialization process; and
* the initialized repository.

Validation should confirm mechanically demonstrable properties such as:

* required artifact presence;
* manifest completeness;
* schema conformance;
* path containment;
* source and derived-artifact correspondence;
* deterministic generation;
* profile isolation;
* repository-local command operation;
* absence of parent-checkout dependencies;
* expected invalid-case failure.

Validation does not replace semantic review or acceptance.

### Provenance

Record enough initialization provenance to audit the generated repository’s origin.

Provenance should identify:

* exact initializer revision;
* initialization contract version;
* selected source/template identity;
* selected profile;
* normalized request identity;
* generated artifact inventory;
* completion status.

Provenance must remain subordinate to the initialized repository’s installed authority.

### Maintained-project handoff

Conclude initialization with a repository-local handoff that identifies:

* current authority;
* exact initialized state;
* lifecycle status of overview, plan, and specifications;
* validation evidence;
* unresolved decisions;
* the next authorized action.

After handoff, ordinary development proceeds through the initialized repository’s own governed workflow.

## Initial product modes

The product direction anticipates at least two initialization modes.

### Framework foundation

Create a governed repository prepared to begin product discovery and overview work.

This mode should avoid generating product semantics or pretending a product specification already exists.

### Product-starting foundation

Create the same governed repository foundation while also establishing candidate product-direction and product-specification structures from explicitly supplied user material.

This mode may reduce setup work, but it must preserve lifecycle honesty and must not automatically accept generated product content.

The exact modes, names, inputs, and behavior remain specification decisions.

## Relationship to the reference repository

The Stage 7 reference repository is evidence that a minimal initialized repository can be:

* represented as repository content;
* copied into isolation;
* validated from its own root;
* operated without parent-checkout dependencies;
* structured around repository and product authority boundaries.

The reference repository is not automatically the initializer template.

It may provide evidence and reusable candidates, but Stage 8 must explicitly determine:

* which artifacts are reusable framework material;
* which are reference-only evidence;
* which are bootstrap-only;
* which are example-product-specific;
* which must be generated;
* which must be omitted;
* which must be selected through a platform profile.

Reference-product semantics must not leak into initialized projects.

## Relationship to `repo-spec`

`repo-spec` has two related product roles:

1. it defines the reusable governed-development framework; and
2. it maintains the initializer that applies that framework.

The initializer is governed by repository specifications and future initializer product specifications stored in `repo-spec`.

The initialized repository receives the applicable reusable framework foundations but does not become a subordinate working tree of `repo-spec`.

The source repository remains the producer and maintainer of the initializer.

The initialized repository becomes the authority for its own product after handoff.

## Human and AI collaboration

The initializer should support repository-first continuity for both human and AI contributors.

A newly initialized repository must provide enough local evidence for a later session to determine:

* what the repository is;
* what lifecycle stage it is in;
* which records are authoritative;
* what work is currently authorized;
* what has been validated;
* which questions remain unresolved;
* what action may occur next.

No essential project authority should exist only in transient conversation context.

AI assistance may help:

* collect initialization inputs;
* draft candidate overview material;
* identify unresolved questions;
* execute deterministic initialization;
* inspect generated output;
* run validation;
* prepare review evidence.

AI assistance must not silently:

* invent product semantics;
* grant acceptance;
* expand authorized scope;
* override accepted specifications;
* conceal uncertainty;
* replace human semantic judgment.

## Success conditions

The initializer product succeeds when it can repeatedly demonstrate that:

1. it is itself developed and maintained through the `repo-spec` governed workflow;
2. an accepted initializer revision can create a new repository from explicit inputs;
3. the initialized repository has clear local authority and lifecycle state;
4. reusable framework material is separated from project-specific content;
5. no reference-product semantics leak into the output;
6. the generated repository is independent of the source checkout;
7. repository-local generation and validation pass;
8. required invalid initialization cases fail safely;
9. generated candidate material is not misrepresented as accepted;
10. the repository identifies its exact initialization provenance;
11. the repository reports the next authorized product-development action;
12. a subsequent bounded change can be performed through the installed governing workflow;
13. the initializer can be released and maintained as an exact product revision;
14. more than one distinct product repository can be initialized without modifying universal framework semantics.

## Explicit non-goals

The initial initializer product is not intended to:

* design a product automatically;
* replace product discovery;
* decide product requirements;
* produce complete accepted product specifications;
* automatically accept generated artifacts;
* automatically approve or merge changes;
* create a product release;
* guarantee long-term compatibility with future initializer versions;
* upgrade existing initialized repositories;
* migrate repositories from unrelated frameworks;
* merge framework changes into maintained projects automatically;
* support arbitrary hosting platforms in the first release;
* execute arbitrary project-supplied code during initialization;
* provide a universal build system;
* require a universal implementation language;
* require network access for core initialization;
* hide the governed workflow behind an unverifiable one-step process.

Upgrade, migration, compatibility, release, and long-term maintenance behavior require later planning and specification.

## Important constraints

### Authority must remain layered

The initializer must preserve the distinction among:

```text
overview
plan
candidate specification
accepted specification
product artifact
validation evidence
semantic review
acceptance
merge
release
```

### Generated output must remain subordinate

Generated artifacts must identify their source and must not override it.

### Installed projects must remain portable

Initialized repositories must not depend on private or out-of-tree state for their declared local operations.

### Scope must remain bounded

Each initializer development change must use a governing issue and authorize one coherent body of work.

### Bootstrap tooling must remain until replaced

Existing working infrastructure should remain until its replacement is:

* specified;
* implemented;
* validated;
* reviewed;
* accepted;
* proven on the default branch.

### Initial output must be maintainable

The initializer must optimize for continued governed development, not merely successful first creation.

## Unresolved product-direction questions

The following questions require decomposition and later planning or specification:

* Is the initializer primarily a command-line application, a library with a command adapter, or both?
* Does initialization always begin from a local accepted `repo-spec` checkout, a packaged release, or either?
* What constitutes the canonical reusable source: a template tree, a declarative artifact inventory, generated content, or a hybrid?
* What project identity information is required at initialization?
* How much initial overview content may be supplied in the initialization request?
* Should the initializer create only candidate overview material, or support importing separately accepted overview content?
* What exact product-activation modes are needed?
* What is the minimum repository state required to begin governed work?
* Which repository specifications are copied, generated, referenced, or transformed?
* How is framework provenance recorded without retaining ongoing external authority?
* Which artifacts remain managed by the initializer after creation, if any?
* How are local-only governing records represented when no hosting profile is selected?
* Is initialization complete before a remote repository exists?
* How is exact initialized-repository identity recorded before its first commit?
* Does the initializer create the first commit, or leave commit creation to a separate governed adapter?
* Which GitHub artifacts belong to the initial GitHub profile?
* What behavior is universal versus GitHub-specific?
* How are failed or interrupted initializations cleaned up?
* Which nondeterministic values, if any, are permitted?
* What conformance suite proves that independently initialized repositories behave consistently?
* What conditions define the first releasable initializer revision?
* Where does Stage 8 end and Stage 9 release and maintenance work begin?

These questions are not answered by this overview merely because they are listed here. They become inputs to bounded decomposition and implementation planning.

## Directional product lifecycle

The intended initializer development sequence is:

```text
initializer overview
→ initializer decomposition
→ initializer implementation plan
→ initializer product specifications
→ initializer product artifacts
→ initializer conformance evidence
→ exact-revision review and acceptance
→ initializer release
→ initializer maintenance
```

The initializer then applies the framework to establish a new project’s starting sequence:

```text
initialization request
→ initialized project foundation
→ project overview
→ project decomposition
→ project implementation plan
→ project product specifications
→ project product artifacts
→ project release and maintenance
```

The initializer supports the second sequence because it was itself developed through the first.
