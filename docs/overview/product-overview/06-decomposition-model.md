# Product Overview: Decomposition Model

> Part 6 of 6 · [Product overview index](../PRODUCT-OVERVIEW.md) · [Previous](./05-governance-and-evolution.md)

This part defines the canonical decomposition model used by the framework to turn broad human intent into bounded AI-executable work.

## Status

Canonical decomposition model.

This document records the architectural reference for decomposition in repo-spec. It is directional only in the sense that it describes the framework's accepted decomposition principle; it does not replace accepted normative specifications.

## Purpose

repo-spec uses decomposition as its central engineering principle.

The goal is to reduce uncertainty, ambiguity, context size, decision freedom, and implicit assumptions before implementation begins.

## Core thesis

Complexity should be reduced before implementation rather than delegated to the implementation task.

The framework should progressively decompose a large human problem into smaller authoritative units until the remaining work is sufficiently bounded for reliable implementation.

## Decomposition pipeline

```text
human intent
  -> product understanding
  -> overview
  -> planning and decomposition
  -> accepted specifications
  -> bounded implementation tasks
  -> implementation
  -> tests and conformance evidence
  -> human review and acceptance
  -> maintained product
```

Each step should reduce uncertainty or strengthen authority.

## Bounded tasks

A bounded task has explicit:

- purpose;
- authority;
- inputs;
- outputs;
- scope;
- exclusions;
- dependencies;
- success criteria;
- validation;
- review boundary.

If a task cannot answer those questions, it is not sufficiently bounded.

## Stopping criteria

Decomposition should stop when additional subdivision no longer materially improves implementation reliability.

A candidate leaf task should have explicit purpose, authority, inputs, outputs, dependencies, success criteria, machine-verifiable checks, human-review boundaries, and no need to invent missing product semantics.

## AI reasoning boundaries

The framework should keep implementation work inside an AI assistant's bounded reasoning envelope.

A task is inside that envelope when its purpose is unambiguous, its authoritative sources are identifiable, its dependencies are available, its required context is small enough to hold, and its remaining decisions are already resolved or explicitly escalated.

## Architectural invariants

- Complex problems are decomposed before implementation.
- Each decomposition step should reduce meaningful uncertainty.
- Implementation tasks must have explicit authority.
- Implementation must not invent missing product semantics.
- Missing higher-level decisions are escalated rather than guessed.
- Conversation is not durable authority.
- Specifications preserve decisions and constrain realization.
- Generated artifacts do not become independent authority.
- Validation proves structural properties, not semantic correctness.
- Human review retains semantic authority.
- Every implementation artifact should be traceable to accepted product intent.
- Decomposition stops when work is reliably bounded.

## Terminology

- **Decomposition**: the process of reducing a large problem into smaller authoritative units.
- **Bounded task**: a task with explicit authority, scope, dependencies, outputs, and success criteria.
- **Authority**: the accepted source that controls a decision.
- **Reasoning envelope**: the set of conditions under which an AI assistant can complete a task without inventing major missing context.
- **Invariant**: a rule that remains true across decomposition and implementation.
- **Escalation**: the act of returning an unresolved decision to its owning authority.
- **Maintained product**: the final product realized and preserved through accepted work.
