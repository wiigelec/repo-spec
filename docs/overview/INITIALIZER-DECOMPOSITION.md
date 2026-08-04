# Repo-Spec Initializer Decomposition

## Status

Directional decomposition record for `docs/overview/INITIALIZER-OVERVIEW.md`.

This document is non-normative. It translates initializer product direction into bounded areas for later planning and specification work.

It does not define exact initializer behavior, input or output schemas, accepted specifications, implementation structure, or release readiness.

## Basis

- `docs/overview/INITIALIZER-OVERVIEW.md`
- `docs/overview/PRODUCT-OVERVIEW.md`
- `docs/overview/product-overview/02-decomposition-model.md`
- `docs/overview/product-overview/03-development-and-specifications.md`
- `docs/overview/product-overview/04-git-and-change-workflow.md`
- `docs/overview/product-overview/05-human-ai-continuity.md`
- `docs/overview/product-overview/06-governance-and-evolution.md`

## Role of this stage

Decomposition identifies bounded product areas, their dependencies, their exclusions, and the unresolved decisions that must be carried into later governed work.

It does not choose product semantics, settle implementation questions, or accept normative initializer behavior.

## Ordered dependency model

The areas below are ordered by dependency and authority flow, not by file layout.

| Order | Area | Primary concern |
| --- | --- | --- |
| 1 | Invocation and request boundary | What the initializer is asked to do and how the request is admitted |
| 2 | Source revision and authority | Which exact source revision and governing records control the run |
| 3 | Framework material selection | What reusable framework material may be reused or projected |
| 4 | Product-direction foundations | What starting product-direction records the initializer may establish |
| 5 | Product-specification foundations | What specification scaffolding the initializer may establish |
| 6 | Platform-profile installation | Which hosting-profile adapters or records are installed |
| 7 | Workspace isolation and safe execution | How initialization avoids destructive or ambiguous partial state |
| 8 | Deterministic generation and materialization | How bounded source material becomes an initialized repository |
| 9 | Validation and conformance evidence | How the initialized repository is checked and recorded |
| 10 | Handoff, packaging, and maintenance boundary | How the repository becomes independently governed after initialization |

## Stage boundary map

| Stage | Decision types |
| --- | --- |
| Product direction | Product identity, intended users, desired outcomes, broad non-goals |
| Decomposition | Bounded areas, dependencies, exclusions, unresolved questions, stopping criteria |
| Planning | Work ordering, transition conditions, artifact families, implementation sequencing |
| Specification | Exact contracts, schemas, authority rules, required behavior, evidence formats |
| Implementation | Code layout, adapters, generation mechanics, operational wiring |
| Validation | Checks, tests, conformance evidence, freshness and structural assertions |
| Release and maintenance | Packaging, versioning, publication, update policy, stewardship |

## Bounded areas

### 1. Invocation and request boundary

Purpose: define the entry boundary for an initialization request.

Responsibility: separate explicit user input from inferred or deferred input.

Boundary: request intake, destination selection, initial identity hints, and any explicit user-supplied overview material.

Depends on: product direction and governing authority records.

Excludes: exact command syntax, exact input schema, and final packaging choice.

Unresolved questions: whether invocation is CLI-only, library-only, or both; which inputs are required; how much can be deferred.

Likely successor work: implementation plan for the invocation surface and later specification of the admitted request model.

### 2. Source revision and authority

Purpose: anchor initialization to an exact accepted source state.

Responsibility: identify the governing issue, accepted base, and source revision identity used for initialization.

Boundary: source revision selection, authority rooting, and provenance-bearing records for the run.

Depends on: the invocation boundary and repository governance records.

Excludes: exact provenance format, release mechanics, and remote-hosting mutation.

Unresolved questions: whether initialization begins from a local checkout, a packaged release, or either; how exact initialized identity is represented before the first commit.

Likely successor work: provenance-oriented planning and later specifications for source identity recording.

### 3. Framework material selection

Purpose: define what reusable framework material can be carried into the initialized repository.

Responsibility: distinguish reusable repository material from bootstrap-only, profile-specific, and project-specific material.

Boundary: repository-generic specifications, derived repository documentation, validation support, and any reusable records needed to seed a new repository.

Depends on: source authority and the repository structure boundary.

Excludes: project semantics, product behavior, and profile-specific runtime decisions.

Unresolved questions: whether the canonical reusable source is a template tree, a declarative inventory, generated content, or a hybrid.

Likely successor work: artifact-inventory planning and later specification of reusable-source projection rules.

### 4. Product-direction foundations

Purpose: establish the initial product-direction records a new repository can carry.

Responsibility: create or seed overview-level material for product intent, product decomposition, and unresolved direction.

Boundary: candidate product-direction records and the minimum structure needed to begin governed product discussion.

Depends on: framework material selection and source authority.

Excludes: accepted product behavior, implementation choices, and product tests.

Unresolved questions: how much initial overview content may be supplied; whether accepted overview content may be imported or only candidate material may be created.

Likely successor work: implementation plan for product-direction seeding and later specification of the created overview artifacts.

### 5. Product-specification foundations

Purpose: establish the initial structure for later product specifications without accepting product semantics.

Responsibility: create or reserve the product-specification roots, manifest context, and Level-oriented scaffolding needed for later specification work.

Boundary: specification foundations only, not the exact product contract set.

Depends on: product-direction foundations and reusable framework material.

Excludes: accepted Level contents, exact required behavior, and implementation details.

Unresolved questions: which product-specification levels are activated at initialization; what minimum specification scaffolding is needed; which artifacts are candidate-only versus empty placeholders.

Likely successor work: product-specification planning and the first accepted initializer product specifications.

### 6. Platform-profile installation

Purpose: separate Git-generic behavior from installed hosting-platform behavior.

Responsibility: install explicit profile-specific adapters or records without turning a platform profile into universal authority.

Boundary: GitHub or other profile material that belongs to the initialized repository, plus any declared local-only records for profile-specific behavior.

Depends on: source authority, framework material selection, and repository structure boundaries.

Excludes: remote mutation, hosting-provider assumptions as universal behavior, and profile-independent product semantics.

Unresolved questions: which profiles are installed by default; which GitHub artifacts belong in the initial profile set; what remains bootstrap-owned versus profile-source-owned.

Likely successor work: hosting-profile planning and later profile-specific specifications or adapter work.

### 7. Workspace isolation and safe execution

Purpose: keep initialization from producing destructive or ambiguous partial state.

Responsibility: constrain the execution environment so failures, interruptions, or conflicts do not leave a misleading repository state.

Boundary: temporary workspace handling, cleanup behavior, conflict detection, and safe failure paths.

Depends on: invocation boundary, source authority, and selected material.

Excludes: the exact generation engine, exact validation suite, and release packaging.

Unresolved questions: how interrupted initializations are cleaned up; which operations must occur in isolation; what ambient state, if any, may be consulted.

Likely successor work: execution-safety planning and later implementation details for failure handling.

### 8. Deterministic generation and materialization

Purpose: turn selected source material into a consistent initialized repository shape.

Responsibility: define the generation or projection boundary that produces the repository-local files and structure from accepted source material.

Boundary: deterministic file creation, stable ordering, and reproducible materialization of repository-local artifacts.

Depends on: framework material selection, platform-profile installation, and safe execution.

Excludes: validation policy, release policy, and any claim that generated content becomes authority over its source.

Unresolved questions: whether nondeterminism is permitted at all; which values, if any, may vary between runs; whether the initializer creates the first commit or leaves that to another adapter.

Likely successor work: generation and materialization planning, then specific generation-related product specifications.

### 9. Validation and conformance evidence

Purpose: show that the initialized repository is structurally ready for governed work.

Responsibility: define how the initialized repository is checked, what evidence is recorded, and how exact-revision correspondence is demonstrated.

Boundary: repository-local checks, freshness checks, structural correspondence, and exact-revision evidence capture.

Depends on: deterministic generation and the installed validation boundary.

Excludes: semantic review, acceptance, release, and implementation beyond the validation contract.

Unresolved questions: the exact validation suite, the evidence record shape, and whether a conformance suite includes mutation-style checks.

Likely successor work: validation specification and test planning for the initializer product.

### 10. Handoff, packaging, and maintenance boundary

Purpose: define how initialization ends and ordinary governed project development begins.

Responsibility: ensure the initialized repository becomes independently governed and no longer depends on hidden initializer authority.

Boundary: the handoff point, retained repository-local records, and any packaging or invocation boundary that remains outside the initialized project.

Depends on: validation and provenance evidence.

Excludes: later project release work, ongoing maintenance tooling, and final decisions about the initializer product form.

Unresolved questions: which artifacts remain managed after creation, whether packaging is part of the initializer product boundary, and what the first releasable initializer revision requires.

Likely successor work: handoff-oriented planning, release boundary specification, and maintenance planning.

## Stopping criteria

Decomposition stops when each area has a clear purpose, responsibility, boundary, dependency relation, exclusion set, unresolved-question set, and likely successor work.

It should also stop when further subdivision would not materially reduce uncertainty or improve planning reliability.

If a proposed split would only rename a concern without changing authority boundaries or sequencing, the decomposition stage is complete for that concern.

## Next authorized planning action

The next authorized development step is the initializer implementation plan.

That plan may order the bounded areas further, but it must not define normative initializer behavior or accept product specifications.

## Discoverability

- [Initializer overview](./INITIALIZER-OVERVIEW.md)
