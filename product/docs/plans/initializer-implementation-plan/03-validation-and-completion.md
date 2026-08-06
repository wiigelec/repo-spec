# Initializer Implementation Plan: Validation and Completion

> Part 3 of 4 · [Initializer plan index](../INITIALIZER-IMPLEMENTATION-PLAN.md) · [Previous](./02-workstreams-and-dependencies.md) · [Next](./04-risks-and-unresolved-decisions.md)

## Status

Accepted planning content.

## Entry and exit model

Every governed implementation issue must declare:

* the workstream or bounded cross-workstream concern;
* its accepted input state;
* its expected outputs;
* applicable unresolved decisions;
* validation commands and fixtures;
* exit evidence;
* exclusions; and
* successor work not authorized by that issue.

An implementation issue is complete only when its declared output and validation evidence exist. Completion of an issue does not imply completion of its workstream unless the workstream exit gate is explicitly satisfied.

## Transition Gate 1: Request authority established

Transition from invocation and authority to framework and product foundations requires:

* explicit initialization input can be captured;
* destination authority is established;
* invalid and contradictory requests fail clearly;
* supplied source material is preserved without semantic expansion;
* deferred inputs are identified; and
* the bounded execution context is covered by tests.

## Transition Gate 2: Foundations established

Transition from framework and product foundations to platform and execution requires:

* the reusable source-material boundary is implemented;
* selected source material is tied to an exact revision;
* repository authority foundations can be installed;
* product-direction, planning, and specification foundations can be established from accepted input;
* resulting relationships and repository structure validate; and
* equivalent fixed inputs produce equivalent foundation output.

## Transition Gate 3: Execution boundary established

Transition from platform and execution to generation, validation, and handoff requires:

* workspace isolation and destination-safety behavior are implemented;
* failure and partial-output handling are explicit;
* Git-generic behavior is independent of hosting-platform profiles;
* selected profiles are installed only when explicitly requested;
* unsupported profiles or destination states fail clearly; and
* the execution result supplies the evidence needed by final validation and provenance processing.

## Transition Gate 4: Initialized repository ready for handoff

Initializer implementation reaches its product completion gate only when:

* a supported end-to-end initialization path completes;
* generated output passes repository-local validation;
* exact source-revision provenance is recorded;
* the result is self-contained for its declared supported operation;
* authority boundaries and document relationships are preserved;
* execution output identifies completed, omitted, and deferred work;
* failure-path fixtures demonstrate that invalid output is not reported as successful;
* maintained-project handoff identifies the next governed action; and
* no unauthorized successor product development is included.

## Validation strategy

Validation shall be layered.

### Unit validation

Unit tests shall cover bounded request parsing, selection rules, rendering or generation functions, path and destination guards, profile selection, provenance construction, and execution-state reporting.

### Component validation

Component tests shall cover the interfaces between:

* invocation and request context;
* request context and foundation selection;
* source selection and artifact generation;
* generation and workspace execution;
* core execution and platform profiles;
* generated output and repository validation; and
* validation results and handoff reporting.

### Fixture validation

Fixtures shall represent supported initialization paths and significant failure boundaries. Each fixture shall declare:

* request input;
* selected source revision;
* selected execution or platform profile;
* expected generated paths;
* expected omitted or deferred paths;
* expected provenance;
* expected validation result; and
* expected handoff state.

Fixtures must not normalize away meaningful nondeterminism or failure output.

### End-to-end validation

End-to-end validation shall:

1. begin from a declared initialization request;
2. use a declared source revision;
3. operate in an isolated destination;
4. perform the supported initialization path;
5. run the generated repository’s required validation;
6. inspect provenance and execution reporting;
7. verify repository authority and document relationships;
8. verify the handoff state; and
9. repeat representative fixed-input cases to detect unintended nondeterminism.

### Repository validation

Every initializer implementation proposal must run the validation required by the `repo-spec` repository itself.

Where an implementation proposal changes derived documentation through an authorized source change, the appropriate generation command shall also run and derived freshness shall be verified.

Implementation work must not modify validation scripts, schemas, generators, or specifications unless a separate governed issue explicitly authorizes that change.

### Manual review

Manual review shall confirm:

* traceability to the accepted overview and decomposition;
* preservation of authority boundaries;
* absence of invented product semantics;
* correct workstream and dependency placement;
* explicit treatment of unresolved decisions;
* safe failure and destination behavior;
* adequacy of validation evidence; and
* absence of unauthorized successor work.

## Completion conditions

The initializer implementation program is complete when:

* all four workstream exit gates pass;
* required supported initialization paths have end-to-end evidence;
* the generated repository validates locally;
* provenance and handoff obligations are met;
* maintained documentation describes supported invocation, inputs, profiles, outputs, failures, and limitations;
* unresolved decisions either remain explicitly preserved or have been closed through governed decisions;
* no known blocking defect prevents the declared supported initializer behavior; and
* the final implementation proposal is accepted under the governed review process.

Program completion does not itself establish release, distribution, or general availability. Those actions require whatever separate governed authority applies at that time.

## Non-completion conditions

The implementation program is not complete when:

* only individual components pass without a supported end-to-end path;
* generated repository validation is skipped;
* provenance identifies a branch or moving reference but not the exact source revision;
* a hosting-platform integration is required for core operation without being part of accepted direction;
* failed or partial generation can be mistaken for success;
* required product content is silently invented;
* unresolved blocking decisions are hidden;
* implementation changes accepted overview, decomposition, or specifications without separate authority; or
* handoff begins successor product implementation rather than identifying it.

