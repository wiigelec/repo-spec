# Product Overview: Development and Specifications

> Part 2 of 5 · [Product overview index](../PRODUCT-OVERVIEW.md) · [Previous](./01-product-direction.md) · [Next](./03-git-and-change-workflow.md)

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

The overview is directional and non-normative. It provides the basis for planning but does not define exact product behavior.

### Plan

The implementation plan organizes how the intended product will be constructed.

It describes:

- major work areas;
- dependency order;
- construction stages;
- expected artifact families;
- validation strategy;
- transition conditions;
- risks;
- unresolved design decisions.

Plans are non-normative. They coordinate development but cannot override accepted specifications or silently define product behavior.

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

Accepted normative specifications control maintained product artifacts.

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

### Level 0 — Kernel

Level 0 defines the product-wide foundations that all higher Levels depend upon.

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

Level 1 defines atomic product concepts and contracts built upon the kernel.

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

Level 2 defines reusable compositions of primitives that provide coherent product responsibilities.

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

Level 3 defines complete workflows and externally meaningful product behavior.

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

Same-Level dependencies may be permitted only when they are explicit, justified, and acyclic.

### Level artifact structure

The framework should define a predictable product-specification layout, such as:

```text
specs/
    levels/
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
overview
    ↓
plan
    ↓
Level 0 kernel
    ↓
Level 1 primitives
    ↓
Level 2 components
    ↓
Level 3 orchestrations
    ↓
product artifacts
```

The overview establishes product direction. The plan sequences specification and implementation work. The Level specifications define the accepted product contracts. Product artifacts implement those contracts.

The framework should make the Level model available to every initialized product repository without requiring the framework itself to instantiate product-specific Level documents.
