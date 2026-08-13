# functional-set lifecycle: Development and Specifications — Part 1

> Part 3 of 6 · [functional-set lifecycle index](../functional-set-process.md) · [Previous](./02-decomposition-model.md) · [Next](./04-git-and-change-workflow.md)

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

Candidate product specifications may depend on candidate or accepted product specifications. Accepted product specifications may depend only on accepted product specifications, so the accepted dependency graph remains entirely normative.

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
