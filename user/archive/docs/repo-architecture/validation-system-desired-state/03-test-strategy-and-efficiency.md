# Test strategy and efficiency

## 1. Test layers

The desired system has three distinct layers.

### Production validation

Answers:

> Is this repository state valid now?

Run through the leaf and aggregate production entry points.

### Validation self-tests

Answer:

> Does the validation implementation correctly accept and reject representative states
> for each current invariant?

Run through the repository/product validation self-test entry points and their aggregate.

### Subsystem tests

Answer:

> Does the product or subsystem implementation behave correctly?

Examples include initializer unit tests. They are not validator self-tests even when
validator changes can affect them.

CI may execute all three layers. Their orchestration remains distinct.

## 2. Functional self-test ownership

Each maintained semantic validator or coherent validator phase should have one primary
functional self-test suite.

That suite should contain:

- a minimal valid case where useful;
- one representative rejection for each materially distinct failure mode;
- boundary cases that distinguish the invariant from adjacent invariants;
- regression cases only when they add a distinct semantic edge.

A large catch-all suite should not duplicate cases already owned by dedicated functional
suites.

## 3. Integration tests

Integration coverage is intentionally small.

Top-level integration tests should prove:

- leaf composition invokes required phases;
- public wrappers invoke the intended implementation;
- aggregate production validation invokes both leaves and no self-tests;
- aggregate validation self-tests invoke both validation self-test domains;
- clean failure behavior is preserved.

Integration tests do not need to repeat every mutation already proven by functional
suites.

## 4. Mutation tests

Mutation testing is valuable when each mutation corresponds to a current invariant.

A mutation is stale when:

- the invariant no longer exists;
- the mutation protects only a completed transition;
- an equivalent mutation is already owned by another functional suite;
- the expected failure message depends on an obsolete implementation path rather than the
  invariant;
- the mutation only proves that a historical artifact still has historical structure.

Stale mutations should be removed rather than renamed.

## 5. Fixture policy

Fixtures exist to make a functional invariant easy to express.

Desired fixture properties:

- small;
- purpose-specific;
- named by semantic state;
- reused only when reuse remains clear;
- free of irrelevant historical content.

A fixture should not become a miniature frozen copy of the repository unless the
invariant genuinely requires whole-repository context.

If many tests repeatedly build nearly identical repositories, common fixture construction
should be factored into semantic builders rather than duplicating setup blocks.

## 6. Assertion policy

Self-tests should assert on stable invariant-level diagnostics.

Prefer:

```text
product dependency direction failed
duplicate product specification id
generated document is stale
undeclared JSON content under product specification root
```

Avoid assertions coupled to:

- line numbers;
- incidental call order;
- temporary variable names;
- patch/milestone identifiers;
- large complete error strings when a stable invariant fragment is sufficient.

## 7. Efficiency goals

Routine production validation should be cheap enough to run reflexively before commit and
during local iteration.

The desired system therefore follows these rules:

- no validator self-tests inside production validation;
- no subsystem unit suites inside validator self-tests;
- no repeated full-tree clone/mutation work in production validation;
- parse stable repository inputs once per leaf run where practical;
- use schema validation for local shape instead of equivalent Python rechecks;
- avoid repeated rendering of the same generated artifact within one run;
- avoid network access in repository-local validation;
- use deterministic local state only.

No fixed runtime budget is established by this candidate plan because current repository
authority does not provide one. A future acceptance cycle may add a measured budget if
needed. Until then, audits should compare cost qualitatively and with measured before/after
timings rather than inventing a threshold.

## 8. Coverage standard

The target is not maximum test count.

The target is **complete coverage of required invariant classes with minimal redundant
paths**.

Removing duplicate tests is correct when:

1. the same invariant and relevant boundary are already proven in its owning functional
   suite;
2. the removed case does not exercise a distinct failure mode;
3. the remaining suite still fails if the owning validator is deliberately broken.

Adding another test is correct when it protects a distinct required semantic boundary,
not merely because a past issue once had a regression test.
