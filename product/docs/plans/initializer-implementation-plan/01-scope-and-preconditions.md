# Initializer Implementation Plan: Scope and Preconditions

> Part 1 of 3 · [Initializer plan index](../INITIALIZER-IMPLEMENTATION-PLAN.md) · [Next](./02-workstreams-and-dependencies.md)

## Status

Accepted planning content.

## Authority and basis

This plan is authorized by issue #187 and is grounded in:

* the accepted initializer overview;
* the accepted initializer decomposition;
* the accepted repository specifications applicable to governed development, repository structure, implementation plans, validation, product overviews, and product decomposition; and
* the accepted default-branch base recorded by issue #187.

The overview defines the initializer’s direction and success conditions. The decomposition defines its bounded product areas and dependencies. This plan may order and gate implementation of those areas, but it may not revise their semantics.

## Implementation scope

The implementation program covers the maintained initializer product needed to:

* receive and bound an initialization request;
* establish the authority and workspace boundary for initialization;
* select and install reusable repository-framework material;
* establish project-specific product-direction, planning, and specification foundations;
* distinguish Git-generic behavior from hosting-platform behavior;
* apply selected platform profiles;
* generate repository content deterministically;
* validate the initialized repository;
* preserve source and revision provenance; and
* hand the initialized repository off for governed development.

The program includes implementation code, tests, fixtures, user-facing invocation support, deterministic generation behavior, validation integration, provenance records, and documentation directly required to operate and maintain the initializer.

Every implementation change must trace to an accepted capability, boundary, responsibility, dependency, or successor obligation in the initializer overview or decomposition.

## Explicit exclusions

This plan does not authorize:

* changes to accepted initializer product direction;
* changes to accepted initializer decomposition boundaries;
* new initializer capabilities not already represented in the accepted documents;
* changes to repository specifications merely to accommodate implementation choices;
* weakening or bypassing repository validation;
* implementation of unrelated `repo-spec` products;
* automatic acceptance, merge, publication, or release of generated repositories;
* assumptions that a hosting platform is always present;
* silent invention of missing product semantics or user intent;
* irreversible modification of an existing destination without an explicitly governed and validated execution path; or
* successor product development inside the generated repository.

Any need for excluded work must be raised as a separate governed decision rather than absorbed into an initializer implementation issue.

## Program entry conditions

Initializer implementation may begin only when:

1. this implementation plan is accepted;
2. the governing implementation issue identifies the workstream and bounded deliverables it implements;
3. the issue names the accepted overview, decomposition, plan, and base revision;
4. required predecessor workstream evidence is available;
5. unresolved decisions that block the proposed work are either resolved by governed authority or explicitly deferred without making the work unsafe or semantically ambiguous;
6. the validation commands and expected evidence for the proposed change are stated; and
7. the change can be completed without modifying excluded artifacts.

## Common implementation constraints

All workstreams must preserve the following constraints:

* **Explicit authority:** initialization begins from explicit request material and does not infer authority that was not granted.
* **Workspace isolation:** generation and validation occur within a bounded destination or staging workspace.
* **Determinism:** equivalent accepted inputs and source revisions produce equivalent governed repository content, except for explicitly defined variable data.
* **Traceability:** generated authority and product foundations remain traceable to their source material and exact revision.
* **Layer separation:** reusable repository framework, project-specific product content, Git behavior, and platform-specific behavior remain distinguishable.
* **Failure safety:** partial failure does not falsely present the destination as a successfully initialized repository.
* **Local validation:** the initialized repository can execute its required validation without depending on undocumented external state.
* **Governed handoff:** initializer completion ends at a repository ready for governed development; it does not perform that successor development.

## Initial unresolved planning decisions

The accepted documents intentionally leave some implementation choices open. These include:

* the concrete initializer invocation interface;
* the representation of initialization-request input;
* the internal staging and transaction model;
* the exact boundary between copied, rendered, and generated artifacts;
* the concrete profile model for hosting-platform integration;
* the provenance-record representation;
* the minimum fixture and compatibility matrix; and
* the packaging or distribution mechanism for the maintained initializer.

These decisions may be resolved during separately governed implementation work when the decision is required, remains within accepted product boundaries, and is recorded with its rationale and validation consequences.

No unresolved decision may be silently treated as settled by this plan.

