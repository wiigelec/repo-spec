# Framework Architecture and Product-Specification System Plan

## Status

Current non-normative implementation plan. Stage 1 is complete; Stage 2 is complete; Stage 3 is complete; Stage 4 is complete; Stage 5 is complete; Stage 6 is complete; the reference repository is the next separately governed phase.

Accepted Stage 2 base:

```text
main at bb05dc4c52617abcc72cf793ed852ed2f3e195f9
```

Accepted Stage 3 base:

```text
main at 1234c646b3d85dd17e6121a955586ead663086bf
```

Accepted Stage 4 completion base and first Stage 5 base:

```text
main at 3f625406902a2170d345d510e111120d9f7c3e30
```

Accepted Stage 5 completion base and first Stage 6 base:

```text
main at e47474daa310cb8134b2cff16dbe0ac84b9a271b
```

Accepted Stage 6 completion base and first reference-repository base:

```text
main at f7fa9c51a88771599f9e908249a61d4353a436e9
```

This plan translates the accepted product overview into an ordered architecture and implementation roadmap for the reusable repository framework.

It does not define normative product behavior, replace accepted specifications, authorize repository mutation by itself, or establish acceptance of any future implementation. Each implementation stage requires separately governed work.

## Planning basis

This plan is based on:

- `repo/docs/overview/PRODUCT-OVERVIEW.md`
- `repo/docs/overview/product-overview/01-product-direction.md`
- `repo/docs/overview/product-overview/02-decomposition-model.md`
- `repo/docs/overview/product-overview/03-development-and-specifications.md`
- `repo/docs/overview/product-overview/04-git-and-change-workflow.md`
- `repo/docs/overview/product-overview/05-human-ai-continuity.md`
- `repo/docs/overview/product-overview/06-governance-and-evolution.md`

Accepted repository baseline at plan creation:

```text
main at 56ff01abfa2e32c0d45957525f697b75a1c6ae2a
```

The governing development sequence is:

```text
overview → plan → specifications → product artifacts
```

This document occupies the planning layer. It coordinates future governed work but cannot override accepted normative specifications.

## Purpose

The repository has completed its bootstrap, cleanup, maintainability, validation, and CI-readiness work.

The next development phase must define how the reusable framework will support product repositories that progress from a high-level idea to accepted specifications, conforming product artifacts, release, and maintenance.

The framework must support:

- explicit artifact roles and authority boundaries;
- repository and product specifications;
- the Level 0–3 product-specification model;
- deterministic validation;
- generated and derived artifacts;
- Git-native bounded development;
- hosting-platform profiles;
- human and AI continuity;
- initialization of more than one product repository;
- release and maintenance of exact revisions;
- separation between framework-generic behavior and product-specific semantics.

The immediate planning problem is therefore not to build a product runtime. It is to establish the architecture of the reusable framework and the product-specification system that initialized repositories will use.

## Stage 1 integration ownership matrix

This matrix records the current integration reading of the accepted Stage 1 records.

| Concept | Current authority owner | Notes |
| --- | --- | --- |
| Repository-specification source | `repo/specs/repo/` via `repo.manifest` | Governs repository-generic contracts only |
| Product-specification source | `product/specs/product/` via the future product manifest | Reserved, not yet introduced |
| Artifact taxonomy | `repo.artifact-taxonomy` | Classifies repository-local and framework-generic artifact roles |
| Platform profile boundary | `repo.platform-profiles` | Distinguishes Git-generic behavior from GitHub-specific behavior |
| Current GitHub adapters | Bootstrap-owned `.github/` files and `repo/scripts/github*` helpers | Operationally maintained now, not generated from profile source |
| Future GitHub profile source | `repo/profiles/github/` | Reserved for later reusable profile-source material |
| Validation | `repo.validation` plus repository-local validation code | Checks declared repository-local invariants only |
| Derived projections | Their declared source specifications | Must remain subordinate to source authority |

## Stage 2 integration ownership matrix

This matrix records the integrated Stage 2 authority reading after completion of the product manifest and base product-specification foundation.

| Concept | Current authority owner | Notes |
| --- | --- | --- |
| Product specification registry | `repo.product-manifest` | Governs the registered product-specification set |
| Product specification semantics | Individual accepted product specification | The governing product file remains normative for its own contract |
| Product manifest structure | `repo.product-manifest` | Defines manifest fields, registry behavior, and activation semantics |
| Common product file envelope | `repo.product-spec-base` | Defines the shared base envelope for product specifications |
| Product manifest schema | `product/schemas/product/product-manifest.schema.json` | Subordinate schema for the accepted product-manifest contract |
| Base product schema | `product/schemas/product/product-spec-base.schema.json` | Subordinate schema for the accepted base product-specification contract |
| Lifecycle source | Explicitly resolve manifest/file duplication | Manifest and file must agree on lifecycle status |
| Level source | Explicitly resolve manifest/file duplication | Manifest and file must agree on Level metadata |
| Derived artifact source | Individual accepted product specification | Manifest does not repeat derived artifacts; derived artifacts are owned by the product file |
| Validation | `repo.validation` plus implementation | Enforces repository/product separation and Stage 2 structural invariants |

## Stage 3 integration ownership matrix

This matrix records the integrated Stage 3 authority reading after reconciling the Level system, dependency rules, acyclicity, and structural completeness.

| Concept | Current authority owner | Notes |
| --- | --- | --- |
| Level purpose | `repo.product-levels` | Defines Level 0 kernel, Level 1 primitives, Level 2 components, and Level 3 orchestrations |
| Level metadata | `repo.product-manifest` and `repo.product-spec-base` | Manifest and file must agree on Level value; the base contract owns the common `level` field |
| Level/path correspondence | `repo.product-manifest` plus `repo.product-spec-base` | Each manifest entry must match exactly one product file under its reserved Level root |
| Level schema ownership | `product/schemas/product/product-level-0.schema.json` through `product/schemas/product/product-level-3.schema.json` | Level-specific schemas extend the base envelope rather than redefining common fields |
| Dependency lifecycle | `repo.product-spec-base` and `repo.validation` | Candidate specifications may target candidate or accepted specifications; accepted specifications may target only accepted specifications |
| Dependency direction | `repo.product-levels` plus `repo.validation` | Lower Levels must not depend on higher Levels |
| Same-Level dependencies | `repo.product-levels` plus `repo.validation` | Permitted only when explicit and acyclic |
| Graph acyclicity | `repo.validation` plus implementation | The full product dependency graph must remain acyclic |
| Structural completeness | `repo.product-levels` plus `repo.validation` | Machine-checkable structure only; semantic completeness remains review-owned |
| Validation ownership | `repo.validation` plus implementation | Enforces product/repository separation, schema boundaries, dependency rules, acyclicity, and completeness boundaries |

## Repository and product tree boundary

The staged repository-layout migration targets one Git repository with three classified content boundaries:

| Boundary | Ownership |
| --- | --- |
| `repo/` | Reusable framework and repository specifications, schemas, projections, tooling, validation, documentation, and profiles |
| `product/` | The `repo-spec` initializer product, including product specifications, product schemas and projections, source, tests, and initializer documentation |
| `reference/` | Separately classified reference-repository material, not part of either reusable or product-owned tree |

The approved root boundary retains `README.md`, `AGENTS.md`, `LICENSE`, and `.github/`. Additional root exceptions require explicit governed recording. Migration shall update authority, discovery, generation, validation, and initialization behavior before moving each affected path group.

## Intended outcome

Completion of this plan should leave the repository with an accepted roadmap that:

1. defines the target framework artifact model;
2. proposes a reusable repository layout;
3. defines how product specifications participate in manifests;
4. defines how Level 0–3 specifications are represented and validated;
5. chooses a product-specification schema strategy;
6. defines specification-to-implementation correspondence;
7. defines staged validation expansion;
8. separates Git-generic behavior from hosting-platform profiles;
9. defines an initialization and reference-repository strategy;
10. defines migration and cutover stages;
11. identifies decision gates between implementation phases;
12. preserves working bootstrap infrastructure until replacements are accepted.

## Explicit non-goals

This plan does not authorize or attempt to define:

- a final project name;
- a universal operation-processing runtime;
- governed operation dispatch;
- effects or execution records;
- authoritative-result semantics;
- product-specific identity families;
- one mandatory implementation language;
- one mandatory build system;
- one mandatory hosting platform;
- immediate removal of current bootstrap tooling;
- wholesale repository restructuring;
- immediate migration of every existing specification;
- implementation of all four product specification Levels;
- a universal repository initializer;
- final framework cutover;
- creation of the future derived product;
- automatic acceptance by AI;
- replacement of human semantic review.

## Architecture principles

### Authority remains layered

The framework must keep these roles distinct:

```text
idea
overview
plan
candidate specification
accepted normative specification
product artifact
validation evidence
review
acceptance
merge
release
```

No layer may silently substitute for another.

### Product artifacts do not define their own semantics

Source code, tests, generated files, and working implementations do not become normative merely because they exist or pass validation.

Accepted specifications remain the authority for required behavior.

### Generated artifacts remain subordinate

Every generated artifact must have:

- an identified authoritative source;
- a declared generator or derivation rule;
- deterministic output;
- freshness validation;
- reproducibility;
- an explicit statement that it does not override its source.

### Git records revisions, not semantic acceptance

Git commits, branches, diffs, merges, and tags provide exact revision evidence.

They do not independently establish semantic correctness, review, acceptance, or release.

### Framework behavior remains portable

Repository-generic behavior must not depend on:

- product-specific operation semantics;
- product-specific identity families;
- one hosting provider;
- prior chatbot conversations;
- one source layout;
- one language or build system.

### Development remains bounded

Each implementation change must use:

- a governing issue;
- an accepted default-branch base;
- an isolated branch;
- explicit scope and exclusions;
- an ordered patch plan;
- exact-head validation;
- review;
- explicit acceptance;
- merge;
- post-merge validation;
- completion-gate closure.

### Bootstrap infrastructure remains until replaced

Working bootstrap tooling may remain while the framework evolves.

It should be retired only after a replacement is:

- specified;
- implemented;
- validated;
- reviewed;
- accepted;
- proven on the default branch.

## Target artifact model

The framework should recognize these artifact families:

- discovery records;
- product overview;
- implementation plans;
- repository specifications;
- product specifications;
- schemas;
- manifests and indexes;
- derived projections;
- product artifacts;
- tests and conformance artifacts;
- platform profiles;
- release records.

For every artifact family, future specifications should identify:

- purpose;
- authority level;
- whether it is normative;
- source of truth;
- expected location;
- validation owner;
- whether it is generated;
- migration status from the current repository.

## Proposed reusable repository layout

```text
README.md
AGENTS.md

docs/
    overview/
    plans/

specs/
    repo/
        manifest.json
    product/
        manifest.json
        level-0/
        level-1/
        level-2/
        level-3/

schemas/
    repo/
    product/

derived/
    specs/
        repo/
        product/

product/src/
product/tests/
conformance/

repo/profiles/
    github/

repo/scripts/
.github/
```

### Mandatory framework paths

The reusable framework template should always provide:

```text
README.md
AGENTS.md
repo/docs/overview/
repo/docs/plans/
repo/specs/repo/
repo/schemas/repo/
repo/derived/specs/repo/
repo/scripts/
```

### Product paths created when needed

A product repository should introduce or activate:

```text
product/specs/product/
product/schemas/product/
product/derived/specs/product/
product/src/
product/tests/
conformance/
```

only when the applicable plan and specifications require them.

### Profile-specific paths

Hosting-provider-specific assets should be clearly identified, for example:

```text
repo/profiles/github/
.github/
```

The `.github/` directory remains the installed adapter location for current bootstrap-owned GitHub files while `repo/profiles/github/` is reserved for future reusable source material.

### Optional language-specific paths

The framework should not require one universal source layout beyond a declared implementation root.

Product-specific specifications may define language or build-system paths when needed.

## Manifest architecture

### Decision direction

Repository and product specifications should use separate manifests with shared validation infrastructure.

```text
repo/specs/repo/manifest.json
product/specs/product/manifest.json
```

### Rationale

Separate manifests preserve the distinction between contracts governing repository operation and contracts governing product behavior. They also reduce product leakage into the reusable framework.

### Product manifest responsibilities

A product manifest should register:

- `spec_id`;
- repository-relative path;
- Level;
- lifecycle state;
- version or revision metadata where applicable;
- dependencies;
- references;
- derived artifacts as declared and owned by the source product specification;
- implementation correspondence;
- test correspondence;
- conformance participation;
- supersession or retirement relationships.

The product manifest records the governed registry and projection inventory; the source product specification owns each `derived_artifacts` declaration.

### Product manifest completeness

Validation should eventually prove:

- every product specification is registered;
- every registered path exists;
- every registered `spec_id` is unique;
- every path is unique;
- every Level declaration is valid;
- every dependency target exists;
- every reference resolves;
- every declared derived artifact is unique and fresh;
- every lifecycle relation is valid;
- every required implementation or conformance mapping exists.

## Product specification Level model

```text
Level 0 — kernel
Level 1 — primitives
Level 2 — components
Level 3 — orchestrations
```

### Level 0 — Kernel

Defines minimal product-wide semantics that govern the interpretation, identity, authority, lifecycle, or common constraints of otherwise independent product areas.

Dependency rule: Level 0 must not depend on Levels 1–3.

### Level 1 — Primitives

Defines an independently meaningful product concept or elementary contract that can be understood without coordinating multiple coherent product responsibilities.

Dependency rule: Level 1 may depend on Level 0 but must not depend on Levels 2 or 3.

### Level 2 — Components

Defines a reusable capability that composes primitives into one coherent product responsibility but does not itself establish a complete product outcome.

Dependency rule: Level 2 may depend on Levels 0 and 1 but must not depend on Level 3.

### Level 3 — Orchestrations

Defines a complete product outcome, use case, or lifecycle transition by coordinating one or more independently meaningful responsibilities, including observable success and failure behavior.

Dependency rule: Level 3 may depend on Levels 0, 1, and 2.

### Definition impact review

Issue #211 revises the Level definitions without changing dependency direction, same-Level dependency rules, lifecycle requirements, structural rules, or validation ownership. The framework architecture plan remains applicable without sequencing or scope changes; its Level-model section is reaffirmed against the revised `repo.product-levels` authority.

### Same-Level dependencies

Same-Level dependencies may be permitted only when they are explicit, acyclic, and do not hide prohibited upward dependencies or redefine another artifact's authority.

### Required dependency validation

Validation should detect:

- cycles;
- missing targets;
- upward dependencies;
- hidden cross-Level dependencies;
- same-Level cycles;
- duplicate dependency declarations;
- structurally detectable higher-Level redefinition of lower-Level semantics.

## Product specification structure

Every product specification should contain a stable common envelope. A candidate shape is:

```json
{
  "spec_id": "product.example",
  "title": "Example Product Specification",
  "level": 1,
  "status": "accepted",
  "purpose": "...",
  "normative_requirements": [],
  "dependencies": [],
  "references": [],
  "derived_artifacts": [],
  "implementation": {
    "paths": [],
    "tests": [],
    "conformance": []
  }
}
```

The exact schema remains subject to future governed specification work.

## Schema strategy

### Preferred architecture

Use a base product-specification schema plus Level-specific schemas:

```text
product/schemas/product/product-manifest.schema.json
product/schemas/product/product-spec-base.schema.json
product/schemas/product/product-level-0.schema.json
product/schemas/product/product-level-1.schema.json
product/schemas/product/product-level-2.schema.json
product/schemas/product/product-level-3.schema.json
```

### Base schema responsibilities

The base schema should define:

- common identity fields;
- lifecycle fields;
- purpose;
- requirement records;
- dependencies;
- references;
- derived artifacts;
- implementation correspondence;
- lineage.

### Level-specific schema responsibilities

Level-specific schemas should constrain:

- permitted Level value;
- dependency directions;
- Level-specific required sections;
- Level-specific prohibited sections where needed.

### Schema implementation decision gate

Before expanding product schemas, governed work must decide whether the current in-repository JSON Schema subset supports the required features.

Possible outcomes:

1. retain the current deliberately small schema dialect;
2. extend the internal interpreter;
3. adopt a standard validator as a development dependency;
4. support both a bootstrap subset and an optional full validator.

The decision must preserve deterministic repository-local validation and a low-friction bootstrap path.

## Specification-to-implementation correspondence

The framework should define explicit correspondence between accepted specifications and maintained artifacts.

Candidate fields:

```json
{
  "implementation": {
    "paths": ["product/src/example.py"],
    "tests": ["product/tests/test_example.py"],
    "conformance": ["conformance/example/"]
  }
}
```

Future specifications must determine:

- whether correspondence is declared by the specification, a separate index, or both;
- whether one implementation artifact may correspond to multiple specifications;
- whether every accepted specification must have implementation evidence;
- how specification-only repositories represent intentionally unimplemented contracts;
- how generated implementation artifacts are declared;
- how implementation ownership is validated;
- how stale correspondence is detected;
- how moved or retired source paths are handled.

The initial direction is to keep correspondence in product specifications or their manifest rather than introducing a separate generalized graph database.

## Validation architecture expansion

The framework should add support for:

- product manifest completeness;
- product schema conformance;
- Level validity;
- dependency direction;
- same-Level acyclicity;
- cross-reference resolution;
- lineage;
- generated product projections;
- implementation correspondence;
- test correspondence;
- conformance correspondence;
- product source layout;
- product tests;
- packaging;
- text and diff hygiene;
- release evidence.

The framework must keep these layers separate:

```text
repository-local deterministic validation
hosting-platform policy validation
semantic review
exact-revision acceptance
merge
post-merge validation
release validation
```

Validation phases should remain named and composable. The architecture should permit future support for scoped or structured output without changing the currently accepted public interfaces.

## Generated product projections

The product-specification system should support deterministic human-readable projections under:

```text
product/derived/specs/product/
```

Each projection should:

- identify its authoritative JSON source;
- identify the generator;
- include no independent normative content;
- be reproducible;
- be checked for freshness;
- be declared by its source or manifest;
- be removed when orphaned.

## Hosting-platform profile architecture

### Git-generic core

The reusable core may assume Git repositories, commits, branches, refs, tags, object identities, ancestry, merge bases, diffs, exact-revision validation, and merge-based integration.

### GitHub profile

GitHub-specific behavior may include:

- issue forms;
- pull-request templates;
- labels;
- protected branches;
- rulesets;
- Actions workflows;
- hosted policy checks;
- review comments;
- merge queues;
- release records.

GitHub should be the first fully supported profile, but current bootstrap-owned GitHub behavior must remain distinguishable from framework-generic behavior until reusable profile source material exists.

### Hosting-state mutations

Any automation that mutates hosting-platform rules should record:

- governing issue;
- accepted repository revision;
- target repository;
- ruleset or protection identifier;
- previous value;
- new value;
- execution evidence;
- rollback procedure;
- post-change verification.

## Human and AI continuity

Repositories initialized from the framework should preserve:

- product intent;
- active plan;
- normative authority roots;
- governing issue;
- scope and exclusions;
- accepted base;
- intended branch;
- dependencies;
- implementation decisions;
- validation requirements;
- exact revision evidence;
- unresolved decisions;
- successor boundaries.

A new session should be able to read the discovery documents, identify the active plan and governing issue, discover normative manifests, inspect Git and hosting state, identify the next bounded action, and stop when authority is missing or conflicting.

## Initialization strategy

The framework should first prove a static reusable layout before implementing a general initializer.

Recommended sequence:

1. define the artifact model;
2. define product manifests and schemas;
3. implement product validation;
4. create a minimal reference repository or fixture;
5. validate the reference repository;
6. identify real configuration variability;
7. specify initialization behavior;
8. implement an initializer or template-generation mechanism.

No universal initializer should be implemented until the reference repository proves required files, optional files, profile boundaries, generated artifacts, default validation behavior, configuration variability, and upgrade needs.

## Reference initialized repository

The reference should demonstrate:

```text
product overview
implementation plan
product manifest
one Level 0 specification
one Level 1 specification
derived projections
minimal source correspondence
minimal test correspondence
validation
```

It should remain intentionally small and generic.

## Migration strategy

### Preserve

- accepted repository specifications;
- repository manifest;
- repository schemas;
- validation entry points;
- deterministic generation;
- hosted policy separation;
- governing issue and review contracts;
- Git-native bounded workflow;
- AI initialization guidance.

### Generalize incrementally

- repository model loading;
- manifest handling;
- schema loading;
- projection generation;
- dependency validation;
- lineage validation;
- correspondence checks;
- profile handling.

### Retain temporarily

- bootstrap scripts;
- current GitHub workflow layout;
- existing repository-specific projections;
- compatibility behavior required by accepted interfaces.

### Exclude from the reusable framework

- product-specific operation semantics;
- effect execution;
- authoritative result contracts;
- maintained runtime modules belonging only to a future product;
- product-specific identity families.

### Retire only after replacement

No accepted artifact should be removed until its replacement has been specified, implemented, validated, reviewed, accepted, merged, and proven on the default branch.

## Implementation stages

### Stage 1 — Framework artifact taxonomy

Goal: define normative artifact classes and authority relationships.

Candidate outputs:

- revised repository-structure specification;
- artifact-role specification;
- product-specification root definition;
- platform-profile boundary definition;
- manifest relationship decision.

Acceptance gate: accepted definitions exist for repository specifications, product specifications, plans, overviews, product artifacts, tests, conformance artifacts, generated artifacts, and profiles.

### Stage 2 — Product manifest and base specification model

Goal: define how product specifications are identified, registered, and governed.

Candidate outputs:

- `product/specs/product/manifest.json`;
- product manifest schema;
- base product-specification schema;
- lifecycle rules;
- reference and lineage rules.

Acceptance gate: a minimal product-specification set can be represented and validated structurally.

### Stage 3 — Level 0–3 schemas and dependency validation

Goal: implement the Level model.

Candidate outputs:

- Level-specific schemas;
- Level metadata;
- dependency-direction validation;
- same-Level acyclicity validation;
- Level-specific generated projections.

Acceptance gate: validation rejects missing or invalid Levels, upward dependencies, cycles, unresolved targets, and duplicate identities.

### Stage 4 — Product projection and freshness support

Goal: generate deterministic human-readable product-specification projections.

Candidate outputs:

- product projection renderer;
- product-derived artifact declarations;
- freshness validation;
- orphan detection;
- mutation tests.

Acceptance gate: stale or orphaned projections fail validation.

Ownership model: product specifications declare their own `derived_artifacts`; the product manifest does not independently author those declarations.

### Stage 5 — Implementation, test, and conformance correspondence

Goal: connect accepted product specifications to maintained artifacts.

Stage 5 begins from `main at 3f625406902a2170d345d510e111120d9f7c3e30`.

Stage 5 authority model:

- accepted product specifications own their correspondence declarations;
- the product manifest remains a governed registry and does not author correspondence;
- validation owns structural correspondence checks;
- semantic correctness remains review-owned;
- product projections must render accepted correspondence fields deterministically.

Stage 5 integrated ownership matrix:

| Concept | Current authority owner | Notes |
| --- | --- | --- |
| Correspondence declaration source | accepted product specification | Product file owns implementations, tests, and conformance |
| Product manifest registry | `repo.product-manifest` | Registry only; no correspondence authoring |
| Correspondence contract | `repo.product-correspondence` | Canonical lifecycle and completeness rules |
| Base envelope and level inheritance | `repo.product-spec-base` and `repo.product-levels` | Common envelope plus extension boundaries |
| Projection rendering | `repo/scripts/docgen.py` | Deterministic rendering from product JSON |
| Structural validation | `repo.validation` plus implementation | Path, ownership, and completeness checks |
| Semantic correctness | review | Remains outside repository-local validation |

Ordered Stage 5 issue sequence:

1. Define correspondence authority and declaration contracts.
2. Implement correspondence schemas and projection support.
3. Validate implementation and test artifact correspondence.
4. Enforce requirement-level conformance completeness.
5. Integrate Stage 5 and record the first Stage 6 base.

Candidate outputs:

- correspondence schema;
- correspondence validation;
- source ownership rules;
- test mapping;
- conformance mapping.

Acceptance gate: validation proves declared correspondence paths exist and satisfy accepted completeness rules.

Completion gate: the final Stage 5 integration issue may record the first Stage 6 base only after post-merge validation passes on the exact final Stage 5 revision.

### Stage 6 — GitHub profile formalization

Goal: separate GitHub-specific behavior from the Git-generic framework.

Stage 6 integrated ownership matrix:

| Concept | Current authority owner | Notes |
| --- | --- | --- |
| GitHub profile source layout | `repo/profiles/github/` via `repo.platform-profiles` | Source-authoritative profile material |
| Installed adapters | `.github/` via `repo.platform-profiles` | Installed/generated output |
| Issue and PR templates | `repo/profiles/github/` | Lowest-risk managed adapters |
| Workflow adapters | `repo/profiles/github/workflows/` | Source-authoritative installed/generated workflow family |
| Remote-state deployment contract | `repo/profiles/github/manifest.json` and `repo.platform-profiles` | Desired-state, inspection, apply, rollback, verification |
| Freshness validation | `repo/scripts/github_profile.py` plus `repo.validation` | Confirms source/adapter sync and orphan detection |
| Bootstrap scripts | `repo/scripts/github-field-policy`, `repo/scripts/github_field_policy.py`, `repo/scripts/github_field_policy_mutation_test.py` | Remain bootstrap-owned support infrastructure |
| Reference repository base | `main at f7fa9c51a88771599f9e908249a61d4353a436e9` | First accepted reference-repository base |

Candidate outputs:

- GitHub profile specification;
- profile source layout;
- deterministic adapter installation or generation;
- ruleset and branch-protection deployment procedure;
- profile validation.

Acceptance gate: GitHub-specific behavior is identifiable and does not define universal framework semantics.

Completion gate: the Stage 6 integrated ownership matrix is recorded, the adapter inventory is current, source/adapter freshness validation passes, the remote-state procedure is reviewed, and the exact reference-repository base is captured.

### Reference repository

Goal: prove the architecture with a minimal initialized product repository.

The reference implementation uses the in-repository isolated-copy model: a checked-in repository snapshot inside this repository that can be validated as a self-contained initialized repository without depending on private history or out-of-tree state.

Stage 7 ownership findings:

- the reference repository owns the minimal product manifest, Level 0 and Level 1 product specifications, source behavior, tests, correspondence records, derived projections, and isolated-copy validation harness;
- repository-generic authority remains with the accepted repository specifications and plans;
- product semantics remain constrained to the accepted product specifications and their correspondence records.

Stage 7 portability findings:

- the reference repository can be copied to a clean temporary location and run generation, validation, mutation tests, and product tests through repository-local scripts from its own repository root under a minimal environment;
- the reference validator applies schema-driven conformance checks to the declared repository and product files before the semantic assertions;
- the portability harness checks for missing product manifest, missing initialization document, invalid JSON, invalid product-root placement, symlink escape, parent-checkout text references, deterministic tree inventory or digest, and broken product tests;
- the copied reference tree does not require parent-checkout state or private history for the validated command paths.

Candidate outputs:

- reference form decision;
- initialized-repository artifact inventory;
- reusable, bootstrap-only, and product-specific classification;
- validation boundaries;
- validation evidence.

Acceptance gate: a fresh reference repository passes all required validation without relying on private history or prior chatbot context.

### Stage 8 — Initialization mechanism

Goal: create a repeatable way to initialize new product repositories.

First Stage 8 accepted base:

```text
main at 88524d68b6bd25746cc5891163b86deb4dba344d
```

Fixed inputs:

- the accepted reference repository and its isolated-copy validation evidence;
- the accepted product-manifest, product-spec-base, product-levels, and product-correspondence contracts;
- the repository-local generation, validation, and mutation-test entry points;
- the Stage 7 ownership and portability findings;
- the exact accepted Stage 8 base above.

Variable inputs:

- initialization specification;
- template source;
- initializer implementation;
- profile selection;
- generated starter artifacts;
- initialization conformance tests.

Candidate outputs:

- initialization specification;
- template source;
- initializer implementation;
- profile selection;
- generated starter artifacts;
- initialization conformance tests.

Acceptance gate: a new repository can be initialized, validated, and used to begin governed planning and specification work.

### Stage 9 — Release and maintenance model

Goal: define exact-revision release, migration, upgrade, and maintenance boundaries.

Candidate outputs:

- release specification;
- release record format;
- packaging checks;
- migration planning rules;
- compatibility policy;
- upgrade procedure.

Acceptance gate: an initialized repository can release and maintain an exact accepted product revision.

## Decision gates

### Gate A — Manifest separation

Decide whether repository and product specifications use separate manifests.

Preferred direction: separate manifests with shared infrastructure.

### Gate B — Schema validator capability

Decide whether the existing schema subset is sufficient before Level-specific schemas require unsupported features.

### Gate C — Correspondence ownership

Decide where implementation, test, and conformance mappings live before Stage 5.

### Gate D — Profile source and installation model

Decide whether reusable profile sources live under `repo/profiles/` and generate installed hosting artifacts before Stage 6; current bootstrap-owned adapters remain the operational source of truth until that transition is governed.

### Gate E — Reference repository form

Use the in-repository isolated-copy model for the reference implementation, with the exact initialized-repository artifact inventory recorded before any implementation work begins.

### Gate F — Initialization mechanism

Choose template, command, or hybrid initialization only after reference-repository evidence exists.

### Gate G — Framework cutover

Define conditions under which bootstrap tooling may be removed or replaced only after replacement tooling has been accepted and proven.

## Risks and mitigations

### Premature product leakage

Mitigation: separate repository and product manifests, explicit profile and product boundaries, and portability-focused review.

### Premature initializer design

Mitigation: prove the reference repository first.

### Schema interpreter growth

Mitigation: isolate schema behavior and establish a capability gate before adding advanced features.

### Excessive ceremony

Mitigation: permit minimal repositories, require only needed artifact families, and preserve simple public entry points.

### Hidden hosting-platform authority

Mitigation: treat hosting mutations as governed deployment state and record before/after values with exact revision evidence.

### Big-bang migration

Mitigation: follow staged work, preserve bootstrap infrastructure, and require accepted replacements before retirement.

### Duplicate sources of truth

Mitigation: define one authoritative source for each relationship, generate projections, and validate completeness and freshness.

## Validation strategy

Each implementation stage should include:

- schema validation where applicable;
- focused repository-local checks;
- complete `repo/scripts/validate`;
- complete `repo/scripts/validate --mutation-tests`;
- generated artifact freshness checks;
- exact-head CI;
- changed-file inventory review;
- semantic review against the governing issue;
- post-merge validation on `main`.

New validators should include mutation tests proving that invalid states fail cleanly.

## Transition conditions

### Planning complete

This plan is complete when:

- the architecture and stage sequence are accepted;
- major decision gates are explicit;
- scope and exclusions are clear;
- the first implementation stage can be governed independently.

### Stage transition

A stage may begin only when predecessor acceptance gates are satisfied, required decisions are closed, and a governing issue records accepted base, scope, exclusions, and patch order.

### Initialization work may begin

Initialization work may begin only after product manifest support, Level validation, product projections, sufficiently defined correspondence, and a passing reference repository exist.

### Future derived-product work may begin

A separate derived product repository may begin only after the framework can initialize or provide a validated product repository, framework-generic and product-specific authority are separated, and the future product has its own overview and plan.

## First implementation phase

The first implementation phase after acceptance of this plan should be:

```text
Framework artifact taxonomy and product-specification foundation
```

It should establish:

- normative product-specification roots;
- repository and product manifest relationship;
- common product-specification identity and lifecycle fields;
- Level metadata;
- initial schema boundaries;
- validation ownership.

It should not yet implement complete Level 0–3 product semantics, correspondence enforcement, general initialization, release automation, or future product runtime behavior.

## Recommended governing issue sequence

### Issue 1 — Accept this plan

Expected bounded output:

```text
repo/docs/plans/01-framework-architecture-plan.md
```

### Issue 2 — Define artifact taxonomy

Introduce or revise normative repository specifications for artifact roles, product-specification roots, and profile boundaries.

### Issue 3 — Define product manifest and base schema

Create the first normative product-specification representation.

### Issue 4 — Implement Level validation

Enforce Level declarations and dependency rules.

Further issues should follow the stages in this plan rather than being pre-authorized by this document.

## Completion criteria

This planning phase is complete when:

- the plan is reviewed and accepted through governed work;
- no unresolved contradiction remains with the product overview;
- the first implementation phase is bounded and independently reviewable;
- successor work is explicit but not automatically authorized;
- the repository remains valid and CI-clean on the accepted default-branch revision.

## Successor work not authorized by this plan

Acceptance of this plan does not itself authorize:

- creation of product manifests;
- creation of product schemas;
- repository restructuring;
- migration of current specifications;
- profile installation changes;
- initializer implementation;
- reference repository creation;
- runtime implementation;
- release tooling;
- future product development.

Each requires a separate governing issue and accepted implementation scope.
