# Validation-package feature request

## Provenance

This collection chunk records feature-request intent from GitHub issue #550, `install normative requirement based validation packages`, together with read-only audit observations made against the accepted repository state before any implementation authority was inferred.

Issue #550 is ordinary intake classified `feature-request`. Its body is non-authoritative design input. This chunk preserves that input as evidentiary whiteboard material for later repository overview analysis.

The governing operation that records this evidence is issue #551. Issue #551 authorizes collection only; it does not approve the proposed architecture or downstream implementation.

## Requested direction

The feature request proposes reorganizing repository validation around stable normative requirement identifiers so accepted normative authority and executable validation evidence can be traced in both directions.

The requested end-state concept is:

- every active identified normative requirement has exactly one validation package;
- every validation package identifies exactly one active normative requirement;
- every maintained externally identified validation task belongs through exactly one validation package to exactly one active normative requirement;
- validation packages remain subordinate correspondence/evidence artifacts and do not restate or replace normative requirement semantics;
- validation package structure is schema-governed;
- each package declares a validation disposition describing the relationship between the requirement and mechanical validation;
- validation task references identify stable task identity, source location, and functional entry point;
- maintained validation entry points carry machine-readable requirement correspondence metadata;
- withdrawn requirement identifiers do not retain active validation-package ownership;
- package-derived Markdown and repository-wide coverage views are deterministic subordinate projections rather than independent authority.

## Proposed validation dispositions

Issue #550 proposes the following disposition vocabulary:

- `mechanical`;
- `partial`;
- `semantic-review`;
- `not-applicable`.

The proposal expects non-mechanical dispositions to carry rationale and explicitly distinguishes package completeness from mechanical task population.

These values remain requested design input only. This collection does not accept the vocabulary or assign dispositions to existing requirements.

## Proposed validation-task model

Issue #550 proposes six named validation-task categories:

- `positive`;
- `negative`;
- `boundary`;
- `regression`;
- `unit`;
- `integration`.

It also proposes stable repository-unique validation task identifiers and a canonical machine-readable mechanism associating each externally identified validation function entry point with exactly one active normative requirement identifier.

The exact taxonomy, task identity rules, and tagging mechanism remain unresolved.

## Proposed correspondence and integrity checks

The feature request asks the validation system to establish correspondence invariants including:

- exactly one package for every active identified normative requirement;
- no active package for an unknown or withdrawn requirement;
- package ownership agreeing with the requirement's owning specification;
- repository-unique validation task identifiers;
- every referenced source file and functional entry point resolving;
- every validation task appearing in exactly one package;
- function-level requirement metadata agreeing with package ownership;
- deterministic canonical package location;
- deterministic package-derived Markdown;
- stale or divergent generated correspondence views being rejected.

The proposal also asks aggregate execution surfaces to consume or verify the canonical correspondence model rather than maintain a second independent requirement-to-validator registry.

## Read-only audit evidence

A read-only audit of issue #550 against the accepted repository state identified the following material evidence for later analysis.

### Requirement identifier uniqueness is not yet an established global join-key invariant

Accepted authority preserves normative requirement identifier stability and reserves withdrawn identifiers, but the current repository validator's generic uniqueness pass checks `normative_requirements[].id` within each specification independently.

The current accepted repository state therefore does not yet provide evidence that a bare normative requirement identifier is mechanically guaranteed to be repository-global across all relevant authority domains.

This collection does not decide whether global uniqueness is required or which accepted specification should own that invariant.

### The proposed package source layout is not currently structurally authorized

Issue #550 illustrates a `validation/packages/...` source layout.

The accepted repository validation structural envelope is closed and currently authorizes the existing validation-domain entries without a `packages/` direct child.

The illustrated location therefore cannot be treated as an already-authorized implementation path. Any later accepted design must either select an already-authorized representation or govern the necessary structural change before package artifacts are installed.

### Package correspondence semantics are proposed rather than accepted

The current accepted validation specification defines validation ownership, delegated enforcement, entry points, structural responsibilities, and orchestration, but it does not currently establish the complete package-to-requirement and task-to-package contract proposed by issue #550.

Schemas, tests, validators, manifests, generated output, or implementation must not manufacture those missing semantics.

## Unresolved analysis questions

The following questions are intentionally preserved for successor overview analysis:

- Should normative requirement identifiers be explicitly repository-global, or should correspondence use a composite identity such as specification plus requirement identifier?
- Which accepted authority should own requirement identity semantics if an additional invariant is required?
- What artifact class should a durable validation package use?
- Which source namespace should own repository, product, and whole-checkout validation packages?
- Which accepted specification should own package cardinality, package lifecycle, disposition vocabulary, task identity, and function correspondence semantics?
- Should `positive`, `negative`, `boundary`, and `regression` be treated as behavioral-intent categories while `unit` and `integration` form a separate execution-level dimension?
- If task classifications are multidimensional, which dimensions are required and which may contain multiple values?
- What is the canonical machine-readable requirement-tagging mechanism for maintained validation entry points?
- How should shared internal validation helpers relate to requirement-specific externally identified tasks?
- How should current broad validation phases and tests be inventoried, split, wrapped, or retained without creating duplicate correspondence registries?
- Where should deterministic package-derived Markdown and aggregate coverage views live?
- If accepted authority eventually requires exactly one package for every active requirement, does migration require an Atomic authority transition because the present structural envelope forbids the proposed artifacts before the authority change while the new invariant would forbid an incomplete post-authority intermediate state?
- Which existing validators encode behavior that lacks a clear accepted normative owner, and how should such cases be handled without elevating implementation into authority?
- Which withdrawn requirement identifiers still have active validation behavior that should be reassigned to surviving normative owners?
- Which validation obligations are mechanical, partial, semantic-review based, or not applicable?

## Collection boundary

This chunk does not:

- approve a validation-package architecture;
- establish global requirement-ID uniqueness;
- establish package or task cardinality;
- accept a schema or path convention;
- accept the proposed disposition vocabulary;
- accept a validation-task taxonomy;
- choose a tagging mechanism;
- revise repository structure;
- create packages, schemas, generated projections, validators, or tests;
- perform overview analysis;
- form or approve a functional set;
- authorize decomposition, specification, planning, or implementation.

Its sole role is to preserve issue #550 and the audit evidence as traceable non-normative input for the next overview-analysis stage.
