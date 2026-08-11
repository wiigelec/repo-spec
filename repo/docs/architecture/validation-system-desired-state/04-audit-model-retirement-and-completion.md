# Audit model, retirement, and completion

## 1. Audit purpose

Future validation audits compare current `main` against this desired state and accepted
normative authority. They are bounded architecture audits, not invitations for general
cleanup. Findings must identify concrete deltas and evidence.

## 2. Audit inventory

Inspect at minimum:

- production and validation-self-test entry points;
- repository and product validator composition;
- functional validator modules and dedicated self-test suites;
- broad or catch-all test suites;
- mutation fixtures and fixture builders;
- accepted validation authority and generated validation documentation;
- active milestone, patch, issue, migration, or compatibility references;
- initializer-exported validation paths and their runtime dependency closure.

## 3. Per-artifact questions

For each active validator, phase, self-test suite, and substantial fixture:

1. What current invariant does it own?
2. Which accepted requirement establishes that invariant?
3. Is this the correct validation domain and layer?
4. Is the same invariant implemented or tested elsewhere?
5. Is its ownership current-function-based or history-based?
6. Is its setup cost proportionate to the invariant?
7. Can it be removed without losing a distinct required boundary?
8. Does its name reveal current function without historical context?

An artifact with no current invariant owner is presumptively stale.

## 4. Finding classifications

Use functional classifications:

- **Required but misplaced** — a necessary invariant is enforced at the wrong layer or
  domain.
- **Duplicate implementation** — multiple active validators implement the same rule.
- **Duplicate self-test** — multiple suites prove the same semantic boundary without a
  distinct purpose.
- **Stale transition validation** — a check protects a completed migration, milestone, or
  compatibility transition.
- **Catch-all ownership** — a broad suite owns cases already belonging to dedicated
  functional suites.
- **Excessive fixture/setup cost** — a small invariant requires unnecessarily large or
  repeated setup.
- **Authority gap** — desired behavior lacks accepted authority and therefore requires
  specification work before implementation.

## 5. Retirement policy

A validator or self-test may be retired only when all are demonstrated:

1. no current accepted requirement uniquely depends on it, or another authoritative layer
   fully enforces that requirement;
2. its distinct semantic coverage is absent, obsolete, or duplicated;
3. removal leaves no current invariant unowned;
4. focused tests and full validation remain green;
5. historical evidence remains available where provenance requires it.

Delete obsolete structure rather than preserving empty compatibility wrappers unless a
current public contract requires the wrapper.

## 6. Compatibility rules

Temporary compatibility validation must have an explicit retirement condition, such as:

- all accepted artifacts use the replacement schema;
- the migration artifact is retired;
- the compatibility registry is empty and its governing requirement is removed.

A compatibility check without a retirement condition is a future-bloat candidate.

## 7. Desired-state completion criteria

The validation system reaches this desired state when:

- production validation, validator self-tests, and subsystem tests have distinct minimal
  public surfaces;
- every production rule maps to current accepted authority and has one primary functional
  owner;
- schema and semantic validation are not needlessly duplicated;
- validator phases have focused self-test ownership;
- broad integration suites retain only genuinely integrative cases;
- subsystem unit tests remain subsystem-owned;
- active architecture is not partitioned by patch, milestone, issue, or implementation
  increment;
- historical evidence is not active validity unless current function-based authority
  explicitly requires it;
- repeated repository parsing and setup are consolidated where clarity is preserved;
- generated artifacts remain subordinate to source authority;
- initialized-repository validation is a closed, explicit portable subset with no
  dependency on repo-spec-only validator tests, initializer implementation code, or
  historical development material;
- every validation artifact exported by the initializer has a demonstrated runtime
  purpose;
- deliberate breakage of each primary invariant is caught by its owning functional
  self-test suite;
- production validation and validation self-tests pass from a clean repository.

## 8. Audit-to-implementation workflow

The normal workflow after this plan is accepted is:

```text
accepted desired state
        ↓
fresh audit of current main
        ↓
evidence-backed delta
        ↓
bounded governed issue
        ↓
implementation
        ↓
validation and merge
        ↓
fresh audit against desired state
```

Deferred findings must be recorded in repository authority or rediscovered from current
repository state. Chat memory is not a work queue.

## 9. Risks

### Over-slimming

Removing apparently repetitive tests can erase distinct semantic coverage.

Mitigation: prove invariant ownership and remaining coverage before deletion.

### Tests becoming de facto specification

Mitigation: every production invariant must trace to accepted normative authority.

### Generic abstraction bloat

Mitigation: abstract repeated mechanics only; keep domain policy explicit.

### Optimization changing semantics

Mitigation: treat shared context or caching as implementation optimization and prove
semantic equivalence with focused tests.

### Candidate plan treated as implementation authority

Mitigation: this plan authorizes no validation code changes; implementation requires a
separate governed issue derived from a fresh audit.

## 10. Acceptance-review decisions

The acceptance cycle must resolve:

1. whether this artifact remains an `implementation-plan` or a future desired-state
   document type is needed;
2. whether validation needs a measured runtime budget;
3. whether temporary compatibility checks need machine-readable retirement conditions;
4. whether accepted plan workstreams should be assigned immediately or left to
   audit-derived issues;
5. whether initializer inventory roles sufficiently identify portable validation-core
   membership or need a dedicated machine-readable classification.

## 11. Successor action

After acceptance, audit the validation system at then-current `main` using this plan as
the architecture baseline and accepted specifications as normative authority.

That audit must include the initializer validation export and dependency boundary. It
should produce only concrete deltas; no large file, old test, or repeated fixture is
presumed wrong until duplication, staleness, excessive cost, or misownership is
demonstrated.
