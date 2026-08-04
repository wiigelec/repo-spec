# Product Overview: Decomposition Model

> Part 2 of 6 · [Product overview index](../PRODUCT-OVERVIEW.md) · [Previous](./01-product-direction.md) · [Next](./03-development-and-specifications.md)

This part defines the canonical decomposition model used by the framework to turn broad human intent into bounded AI-executable work.

## Status

Canonical decomposition model.

This document records the architectural reference for decomposition in repo-spec. It is directional only in the sense that it describes the framework's accepted decomposition principle; it does not replace accepted normative specifications.

## Purpose

repo-spec uses decomposition as its central engineering principle.

The goal is to reduce uncertainty, ambiguity, context size, decision freedom, and implicit assumptions before implementation begins, and again whenever implementation exposes unresolved higher-level decisions that exceed the bounded task's authority.

## Failure modes addressed

| Failure mode | Mitigation |
| --- | --- |
| Context drift | Keep decisions and boundaries in repository records rather than conversation memory. |
| Semantic drift | Preserve traceability from intent to overview, specifications, implementation, and tests. |
| Authority drift | Keep each decision in its owning layer and prevent lower layers from inventing higher-level behavior. |
| Scope drift | Require explicit scope, exclusions, dependencies, and bounded task boundaries. |
| Hallucination | Require accepted authority for missing decisions and escalate unresolved gaps instead of guessing. |

## Core thesis

Complexity should be reduced before implementation rather than delegated to the implementation task.

The framework should progressively decompose a large human problem into smaller, more explicit representations whose authority increases or becomes more precisely defined as decisions move toward accepted specifications until the remaining work is sufficiently bounded for reliable implementation.

Decomposition does not make every child artifact normative.

## Decomposition dimensions

repo-spec uses multiple compatible decomposition views rather than one canonical tree.

| Dimension | Question |
| --- | --- |
| Authority | Which artifact owns the decision? |
| Product structure | Which capability or component owns the behavior? |
| Dependency | What must exist first? |
| Work | What can be implemented as one bounded change? |
| Evidence | How is each requirement demonstrated? |

## Recursive decomposition

Decomposition may occur within plans, specifications, governing issues, and implementation tasks.

Any resulting unit may itself be decomposed again if it remains too large or too ambiguous to support reliable implementation.

```text
problem
├── capability
│   ├── component
│   │   ├── requirement
│   │   └── requirement
│   └── component
└── capability
```

The number of layers is determined by complexity, not by a fixed template.

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

Decomposition is shown beside planning for readability; in practice it recurs at every later stage until implementation work is sufficiently bounded.

```text
bounded task encounters missing authority
        |
        v
identify owning layer
        |
        v
revise and accept higher-level artifact
        |
        v
resume decomposition or implementation
```

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

Decomposition should not continue merely to make tasks smaller; excessive subdivision can fragment context and create coordination overhead without improving reliability.

A candidate leaf task should have explicit purpose, authority, inputs, outputs, dependencies, success criteria, machine-verifiable checks, human-review boundaries, and no need to invent missing product semantics.

A leaf task should change one coherent responsibility, have a reviewable diff, be independently validatable, avoid coupling unrelated decisions, and avoid requiring simultaneous acceptance of multiple architectural changes.

## AI reasoning boundaries

The framework should keep implementation work inside an AI assistant's bounded reasoning envelope.

A task is inside that envelope when its required context is finite and identifiable, its product and architectural decisions are resolved or explicitly escalated, it has a limited number of interacting responsibilities, its file and behavior boundaries are explicit, and its completion and review criteria are objective.

Context-window size alone does not determine boundedness.

## Traceability

```text
human intent
  -> accepted overview direction
  -> accepted specification requirement
  -> governing issue scope
  -> implementation mapping
  -> test mapping
  -> conformance record
  -> accepted revision
```

Machine verification may establish the presence, structure, and referential validity of the specification requirement, governing issue scope, implementation mapping, test mapping, and conformance record.

Human review remains responsible for determining whether those links correctly preserve the intended semantics, including the relationship between accepted overview direction and accepted revision.

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

- **Decomposition**: the process of reducing a large problem into smaller, more explicit units with defined roles, boundaries, dependencies, and authority.
- **Conversation**: a discovery and clarification medium that may produce candidate understanding, expose intent, identify uncertainty, test interpretations, and discover constraints; decisions required for later work must be recorded in the repository artifact that owns them.
- **Bounded task**: a task with explicit authority, scope, dependencies, outputs, and success criteria.
- **Authority**: the accepted source that controls a decision.
- **Reasoning envelope**: the set of conditions under which an AI assistant can complete a task without inventing major missing context.
- **Invariant**: a rule that remains true across decomposition and implementation.
- **Escalation**: the act of returning an unresolved decision to its owning authority.
- **Maintained product**: the final product realized and preserved through accepted work.
