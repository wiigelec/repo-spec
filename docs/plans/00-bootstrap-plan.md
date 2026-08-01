# Bootstrap Plan

## Status

Initial planning document for the repo-spec bootstrap process.

This plan is non-normative. It describes the staged path from human-authored Markdown to normalized normative JSON and then to derived Markdown documentation in a separate directory tree.

Temporary bootstrap authority: files under `specs/repo/` are the authoritative bootstrap source until the documented JSON cutover.

Bootstrap work follows the normal governed workflow: it begins from a governing issue and an isolated working branch.

## Purpose

Establish the bootstrap process that will make the separation between `repo specs` and `product specs` unmistakable to a fresh AI session and to human maintainers.

The immediate goal is not to build the final source product. The immediate goal is to make the repository structure, authority boundaries, and expected outcomes easy to discover without relying on prior conversation context.

## Bootstrap principles

- Start with simple Markdown artifacts.
- Use Markdown to clarify the split between repository-generic material and product-specific material.
- Promote stable structure into normalized JSON when the bootstrap is ready.
- Treat JSON as the normative source after the switch.
- Generate Markdown docs into a separate derived-docs directory.
- Keep authority visible at every step.

## Intended artifact progression

```text
Markdown bootstrap docs -> normalized JSON specs -> derived Markdown docs
```

During bootstrap, Markdown is the working authoring format. After the switch, Markdown becomes non-normative and derived from the JSON source.

## Planned bootstrap phases

### Phase 1: Boundary definition

Define the minimum set of Markdown docs needed to show:

- what belongs in `repo specs`;
- what belongs in `product specs`;
- how the two trees stay separate;
- how a chatbot should discover the repository shape;
- how bootstrap authority changes over time.

### Phase 2: Process clarity

Define the rudimentary workflow a fresh AI session must be able to infer, including:

- where to start reading;
- how to identify authoritative material;
- how to recognize the bootstrap state;
- how to avoid product leakage into template material and vice versa.

### Phase 3: Normalized JSON design

Define the first machine-readable spec shape and the closed artifact model.

The initial placeholder JSON set should land as one file per specification under `specs/repo/`.

Add JSON Schema definitions under `schemas/` to validate the structural properties of the artifact model.

The JSON should be:

- normalized for machine readability;
- explicit about authority;
- structured for validation;
- suitable for later schema enforcement;
- independent from Markdown presentation order.

### Phase 4: Derived documentation layout

Define the separate directory tree for non-normative Markdown projections.

`scripts/generate-docs` should write deterministic Markdown projections into `derived/specs/repo/`.

The derived docs should:

- be mechanically traceable to JSON sources;
- not override normative JSON;
- remain clearly separate from source specs.

### Phase 5: Validation gates

Define the closed validation set: JSON Schema conformance, manifest completeness, unique specification IDs, resolvable references, acyclic dependencies, generated-document freshness, and clean failure behavior.

The transition condition is user-triggered once a fresh AI session can reliably infer:

- the rudimentary process;
- the intended outcomes;
- the repo/product separation;
- the bootstrap-to-normative switch.

No new bootstrap check may be added without an accepted specification change.

## Open decisions

- exact derived-docs directory layout;
- initial JSON schema boundaries;
- validation commands and entry points;
- whether the plan itself becomes split into repo-spec and product-spec subplans.

## Current expectation

This plan is the first scaffold for the repository’s bootstrap workflow. It should be refined as the Markdown foundation becomes concrete and then translated into normalized JSON once the bootstrap threshold is reached.
