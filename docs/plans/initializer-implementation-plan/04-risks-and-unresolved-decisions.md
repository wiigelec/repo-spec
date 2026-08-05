# Initializer Implementation Plan: Risks and Unresolved Decisions

> Part 4 of 4 · [Initializer plan index](../INITIALIZER-IMPLEMENTATION-PLAN.md) · [Previous](./03-validation-and-completion.md)

## Status

Accepted planning content.

## Risks

### Semantic drift

Implementation convenience may pressure the project to invent input defaults or product content not present in the accepted direction.

**Control:** require traceability to accepted source material and reject or defer unsupported decisions.

### Framework and instance coupling

Reusable `repo-spec` framework material may become coupled to repository-specific content.

**Control:** maintain explicit selection, rendering, and instance boundaries with dedicated tests.

### Platform leakage

Hosting-platform behavior may become embedded in the initializer core.

**Control:** require a Git-generic core and explicit platform-profile interfaces.

### Partial-output ambiguity

A failed initialization may leave plausible-looking but invalid repository content.

**Control:** use isolated staging, explicit status, and validation-gated handoff.

### Source revision ambiguity

Generated output may not identify the exact source revision from which it was created.

**Control:** make exact-revision provenance an exit requirement.

### Validation circularity

Initializer tests may validate only the initializer process and not the repository it produces.

**Control:** run the initialized repository's own validation as part of end-to-end acceptance.

### Unsupported compatibility expansion

Implementation may grow into an open-ended matrix of operating systems, Git providers, invocation modes, or migration cases.

**Control:** require each supported profile or environment to be explicitly governed, implemented, and tested.

## Unresolved decisions

Unresolved decisions remain open until a governed implementation issue requires and resolves them. A decision record must identify:

* the workstream requiring the decision;
* accepted directional evidence;
* alternatives considered;
* the selected boundary;
* validation consequences;
* compatibility consequences; and
* any successor work intentionally deferred.

Decisions that would change accepted product direction or decomposition must not be resolved as implementation details.

## Residual risks and unresolved decisions

Residual risks and unresolved decisions must remain visible in implementation issues, review proposals, maintained documentation, or explicit successor issues.

A residual item may be deferred beyond initializer completion only when:

* it does not invalidate the declared supported behavior;
* its effect and limitation are documented;
* validation demonstrates the supported boundary;
* the deferral does not create false success or authority; and
* successor work is explicitly identified.

## Successor work

After this plan is accepted, successor work proceeds through separately governed implementation issues in dependency order.

After the initializer implementation program satisfies its completion gate, possible successor work may include:

* packaging or distribution work;
* additional platform profiles;
* additional supported invocation adapters;
* broader compatibility fixtures;
* release preparation; or
* governed development inside repositories created by the initializer.

None of that successor work is authorized merely by acceptance of this plan.

## Plan closure

This implementation plan remains the controlling planning record until it is superseded through governed change.

The plan must not be marked complete merely because all planned patches have been written. Closure requires accepted evidence that the completion conditions and governed review requirements have been met.
