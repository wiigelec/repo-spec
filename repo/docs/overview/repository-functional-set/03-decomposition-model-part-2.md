# functional-set lifecycle: Decomposition Model — Part 2

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
- **Product understanding**: the provisional shared interpretation of human intent produced through discovery and clarification before it is recorded as durable overview direction; it is explicitly non-authoritative until recorded and accepted in the proper artifact.
- **Bounded task**: a task with explicit authority, scope, dependencies, outputs, and success criteria.
- **Authority**: the accepted source that controls a decision.
- **Reasoning envelope**: the set of conditions under which an AI assistant can complete a task without inventing major missing context.
- **Invariant**: a rule that remains true across decomposition and implementation.
- **Escalation**: the act of returning an unresolved decision to its owning authority.
- **Maintained product**: the final product realized and preserved through accepted work.
