# Product Overview: Development and Specifications

> Part 3 of 6 · [Product overview index](../PRODUCT-OVERVIEW.md) · [Previous](./02-decomposition-model.md) · [Next](./04-git-and-change-workflow.md)

This part defines the development layers and the four-Level template used to organize normative product specifications.

## Development layers

### Overview

The overview records the durable high-level intent of the product.

It describes:

- the problem being addressed;
- intended users;
- desired outcomes;
- important constraints;
- major capabilities;
- explicit non-goals;
- success conditions;
- unresolved product-direction questions.

The overview is directional and non-normative. It provides the basis for decomposition and specification work but does not define exact product behavior.

An accepted overview must exist before product decomposition may proceed to acceptance.

### Decomposition

Decomposition turns product direction into bounded questions, expected specification families, and dependency boundaries before implementation planning begins.

The decomposition identifies:

- expected Level 0–3 specification families;
- responsibility boundaries;
- intended dependency direction;
- known cross-specification relationships;
- unresolved semantic decisions;
- specification work required before implementation planning;
- areas that do not require separate specification artifacts.

Decomposition is directional and non-normative. It identifies what must be specified without prematurely defining normative product semantics.

An accepted decomposition must exist before the controlling product-specification set is finalized.

### Plan

The implementation plan organizes how the intended product will be constructed against accepted product specifications.

It describes:

- major work areas;
- controlling accepted product specifications for each workstream;
- dependency order;
- construction stages;
- expected artifact families;
- validation strategy;
- transition conditions;
- risks;
- unresolved design decisions;
- specification-complete and specification-work-still-required scope boundaries.

Plans are non-normative. They coordinate development but cannot override accepted specifications or silently define product behavior.

An implementation plan may not become accepted without its required controlling product specifications being accepted and structurally valid.

### Specifications

Specifications define the authoritative contracts for the repository and product.

They may define:

- repository structure;
- artifact roles;
- authority and precedence;
- product concepts;
- interfaces and data contracts;
- required behavior;
- identity and versioning;
- source layout;
- validation;
- conformance;
- generated projections;
- release and maintenance rules.

Candidate specifications remain proposals until accepted through the applicable governed process.

Accepted normative specifications control maintained product artifacts. No specification at a given Level may be accepted until its required lower-Level dependencies satisfy the product-level contract. Higher-Level specification drafting may begin while lower-Level specifications remain candidate, provided the dependency targets and unresolved authority are explicit, but a higher-Level specification may not be accepted until its required lower-Level dependencies are accepted.

Repository decomposition and product decomposition are related but distinct: repository decomposition governs how work is represented and authorized, while product decomposition governs what the product must do.

### Product artifacts

Product artifacts realize the accepted specifications.

They may include:

- source code;
- libraries;
- command-line tools;
- services;
- schemas;
- configuration;
- templates;
- generators;
- tests;
- conformance artifacts;
- generated documentation;
- packaging;
- release automation;
- repository-maintenance tooling.

Existing implementation does not become product authority merely because it exists. Product artifacts must be evaluated against accepted specifications.

Product-artifact synthesis must not begin until the applicable accepted product specifications and the corresponding implementation plan are accepted. Product artifacts realize accepted specifications; they do not define their own semantics.

## Product specification Level template

The framework defines a fixed four-Level format for normative product specifications:

```text
Level 0 — kernel
Level 1 — primitives
Level 2 — components
Level 3 — orchestrations
```

The framework repository defines the meaning, structure, dependency rules, validation requirements, and expected artifact relationships for these Levels.

The framework repository is not required to contain its own product Level 0–3 specification documents. Instead, repositories created from the framework use the Level template to organize their product specifications.

The Level model is not the complete decomposition process. It is a reusable structure for organizing one part of product decomposition, the normative specification graph. Governing issues, implementation plans, requirements, and source changes may require additional decomposition within or across Levels.

Within that decomposition dimension, Level 0 constrains universal foundations, Level 1 isolates atomic concepts, Level 2 isolates reusable responsibilities, and Level 3 limits end-to-end orchestration. The dependency direction prevents an allegedly small lower-level task from requiring hidden higher-level context.

### Level 0 — Kernel

Level 0 defines minimal product-wide semantics that govern the interpretation, identity, authority, lifecycle, or common constraints of otherwise independent product areas.

It may define:

- core terminology;
- universal invariants;
- authority and precedence rules;
- identity and versioning foundations;
- common data constraints;
- error and failure principles;
- lifecycle foundations;
- extension boundaries.

Level 0 must remain minimal and foundational. It must not depend on higher Levels.

### Level 1 — Primitives

Level 1 defines an independently meaningful product concept or elementary contract that can be understood without coordinating multiple coherent product responsibilities.

It may define:

- entities;
- values;
- records;
- interfaces;
- elementary operations;
- state definitions;
- validation primitives;
- reusable product concepts.

Level 1 may depend on Level 0 but must not depend on Levels 2 or 3.

### Level 2 — Components

Level 2 defines a reusable capability that composes primitives into one coherent product responsibility but does not itself establish a complete product outcome.

It may define:

- services;
- processors;
- validators;
- adapters;
- repositories;
- subsystems;
- coordinated state machines;
- reusable component contracts.

Level 2 may depend on Levels 0 and 1 but must not depend on Level 3.

### Level 3 — Orchestrations

Level 3 defines a complete product outcome, use case, or lifecycle transition by coordinating one or more independently meaningful responsibilities, including observable success and failure behavior.

It may define:

- end-to-end use cases;
- multi-component workflows;
- user-facing operations;
- lifecycle orchestrations;
- cross-system coordination;
- release or deployment flows;
- complete product interactions.

Level 3 may depend on Levels 0, 1, and 2.

### Level dependency rules

The framework should require dependencies to flow upward through the Level hierarchy:

```text
Level 0 → Level 1 → Level 2 → Level 3
```

Higher Levels may depend on lower Levels. Lower Levels must not depend on higher Levels.

The Level model should also prevent:

- circular dependencies;
- hidden upward dependencies;
- higher Levels redefining lower-Level semantics;
- orchestrations inventing missing primitive behavior;
- implementation artifacts becoming undocumented sources of specification semantics.

Same-Level dependencies may be permitted only when they are explicit and acyclic.

### Classification matrix

The following examples are illustrative guidance for applying the accepted `repo.product-levels` contract. They are not additional normative requirements. When an example spans boundaries, classify it by the responsibility and outcome it actually defines, not by its implementation name.

| Example | Classification | Reason | Boundary or edge case |
| --- | --- | --- | --- |
| Authority and precedence rules shared by all product areas | Level 0 | Product-wide governance foundation | A rule limited to one feature is not Level 0. |
| Product-wide identity and versioning foundation | Level 0 | Common identity semantics | A feature-specific identifier belongs to that feature's lower-level contract. |
| Universal lifecycle invariant | Level 0 | Product-wide lifecycle semantics | A workflow-specific transition belongs to Level 2 or Level 3. |
| Feature-specific pricing value or discount-code contract | Level 1 | Independently meaningful concept | It is not Level 0 merely because the feature uses it broadly. |
| User or account record definition | Level 1 | Atomic product concept | Coordinating account creation and notification is not a primitive. |
| Elementary input-validation contract | Level 1 | Standalone contract requiring no responsibility coordination | A validator service coordinating persistence and policy is Level 2. |
| Standalone operation interface or state definition | Level 1 | Independently understandable elementary contract | A complete operation using it may be Level 3. |
| Reusable authentication-token validator | Level 2 | Coherent capability composed from primitive contracts | It remains Level 2 when it validates without completing a user outcome. |
| Persistence adapter over entity and storage primitives | Level 2 | Reusable responsibility composed from primitives | The adapter does not become Level 3 because it has side effects. |
| Import processor coordinating parsing, validation, and staging | Level 2 | One reusable coherent responsibility | Importing plus publishing and reporting a completed result is Level 3. |
| Reusable coordinated state machine | Level 2 | Component-level responsibility | A full user lifecycle that drives it is an orchestration. |
| Complete checkout use case | Level 3 | Complete outcome coordinating independent responsibilities | It remains Level 3 even when one component performs most of the work. |
| Account onboarding lifecycle | Level 3 | Complete lifecycle transition with observable outcome | The individual account record remains Level 1. |
| Cross-system deployment or release flow | Level 3 | Complete outcome coordinating systems and responsibilities | A deployment adapter alone is Level 2. |
| User-facing validation-and-submission operation | Level 3 | Complete product outcome with success and failure behavior | A reusable validation capability alone is Level 2. |
| Component that redefines primitive or component semantics | Not a valid Level 3 classification | Higher Levels must not redefine lower-Level authority | Clarify or move the semantics to the owning lower Level. |

### Level schema extension mechanics

Each Level-specific product schema extends `schemas/product/product-spec-base.schema.json` with a two-member `allOf` composition:

1. The first member references the common base schema.
2. The second member is an object schema that narrows `level` to the Level constant and declares that Level's extension fields at the product-specification root.

The extension object must not redefine common envelope fields other than the `level` narrowing. The Level-specific schema must set root `unevaluatedProperties: false`, and every nested object introduced by the extension must set `additionalProperties: false`. This makes the base envelope and explicitly declared Level fields the complete accepted schema surface.

### Level artifact structure

The framework should define a predictable product-specification layout, such as:

```text
specs/
    product/
        level-0/
        level-1/
        level-2/
        level-3/
```

The exact subordinate structure may evolve, but the framework should define:

- Level roots;
- artifact naming;
- manifest participation;
- schema requirements;
- cross-reference rules;
- dependency declarations;
- derived projection rules;
- source correspondence;
- conformance participation;
- validation ownership;
- completeness requirements.

A product repository may contain multiple specification artifacts within each Level. The framework should define how those artifacts collectively form the product specification system.

### Relationship to product development

The Level template governs normative product specifications within the broader development lifecycle:

```text
accepted overview
    ↓
accepted decomposition
    ↓
accepted Level specifications
    (Level 0 → Level 1 → Level 2 → Level 3,
     or direct valid dependencies across Levels)
    ↓
accepted implementation plan
    ↓
governed implementation issues
    ↓
product artifacts
```

The overview establishes durable product direction. The decomposition identifies the expected specification families, responsibility boundaries, and dependency direction. The Level specifications define the accepted product contracts in valid dependency order. The implementation plan sequences artifact construction against those accepted contracts. Governed implementation issues carry out the planned work within the accepted specification authority. Product artifacts realize the accepted specifications.

Decomposition precedes specification drafting. Implementation planning follows accepted normative contracts. A plan cannot substitute for missing specifications or redefine accepted product semantics.

The framework should make the Level model available to every initialized product repository without requiring the framework itself to instantiate product-specific Level documents.
