# Validation Package Architecture Proposal

## Status

Design proposal for audit against the current repository.

This document is non-authoritative. Its purpose is to describe a candidate validation architecture that can be compared against accepted repository authority, existing validation behavior, schemas, generated artifacts, and implementation before any normative change is proposed.

## Objective

The validation system shall be reorganized around normative requirement identifiers.

The singular architectural goal is complete bidirectional traceability between accepted normative requirements and executable validation tasks:

- every active identified normative requirement has exactly one validation package;
- every validation task is associated with exactly one active identified normative requirement through exactly one validation package.

Validation implementation shall therefore be organized as evidence and enforcement subordinate to normative authority rather than as an independently structured source of semantics.

## Established Design Truths

The proposal assumes the following truths.

1. Every normative requirement has a repository-unique stable identifier.
2. Every active identified normative requirement has exactly one associated validation package.
3. A validation package is a schema-governed JSON document.
4. Each validation package identifies exactly one active normative requirement.
5. Each validation package contains the validation-task correspondence for that normative requirement.
6. The repository defines one standardized set of validation-task categories.
7. Every validation package contains a section for every standardized validation-task category.
8. Each validation-task category contains zero or more validation-task references.
9. Each validation-task reference identifies:
    - a stable validation task identifier;
    - a repository-relative source file;
    - a functional entry point within that source file.
10. Every validation task belongs to exactly one validation package and therefore exactly one active normative requirement.
11. Every validation package has a declared derived Markdown projection.
12. Derived validation-package Markdown is subordinate generated evidence and carries no independent normative authority.

## Normative Authority Relationship

A validation package shall reference normative authority but shall not restate it.

The normative requirement remains the sole owner of its semantics.

Validation packages shall not contain independent requirement text, replacement rule text, inferred constraints, duplicated normative semantics, or other fields that could become a competing semantic authority.

Validation tasks shall test or enforce conformance to the normative requirement associated with their package. The existence, wording, implementation, or behavior of a validation task shall not independently define or amend the associated requirement.

Shared implementation helpers may support multiple requirements, but each externally identified validation task shall map to exactly one normative requirement.

## Validation Package Identity

Each validation package shall identify at minimum:

- the owning specification identifier;
- the normative requirement identifier;
- the validation disposition;
- the standardized validation-task sections;
- the derived Markdown artifact.

The normative requirement identifier is the canonical join key between accepted authority and validation evidence.

A conceptual package shape is:

```json
{
  "$schema": "<validation-package-schema>",
  "spec_id": "repo.authority-model",
  "normative_requirement_id": "REPO-AUTH-004",
  "validation_disposition": "mechanical",
  "tasks": {
    "positive": [],
    "negative": [],
    "boundary": [],
    "regression": [],
    "unit": [],
    "integration": []
  },
  "derived_artifacts": [
    {
      "type": "markdown",
      "path": "<derived-validation-package-path>"
    }
  ]
}
```

The exact schema, path rules, and field names remain subject to audit and later normative definition.

## Validation Disposition

Every validation package shall declare the relationship between the normative requirement and mechanical validation.

The proposed controlled vocabulary is:

**`mechanical`**

The normative requirement is expected to be mechanically enforceable within the repository validation system.

**`partial`**

Objective portions of the normative requirement are mechanically enforceable, but complete conformance also requires semantic judgment or review.

**`semantic-review`**

The normative requirement cannot be meaningfully established by mechanical validation and is governed primarily through human semantic review.

**`not-applicable`**

The normative requirement is active, but repository-local executable validation is not applicable to the governed behavior.

not-applicable should be rare and should not be used as a generic escape from implementing validation.

Any disposition other than mechanical shall include a non-empty rationale.

A package with zero validation tasks is therefore not inherently incomplete. Its meaning is determined by the validation disposition and rationale.

## Standard Validation Task Categories

The proposed standard validation-task categories are:

- positive
- negative
- boundary
- regression
- unit
- integration

Every validation package shall contain all standard categories, including categories containing zero tasks.

### Positive

Positive validation tasks demonstrate that representative conforming states are accepted.

Positive tasks primarily detect over-enforcement and incorrect rejection of valid repository state.

### Negative

Negative validation tasks demonstrate that representative direct violations of the normative requirement are rejected.

Negative tasks primarily detect under-enforcement.

### Boundary

Boundary validation tasks exercise the limits and transitions of the normative contract.

Examples include:

- allowed versus forbidden namespace locations;
- minimum and maximum cardinality;
- empty versus populated collections;
- lifecycle transition boundaries;
- path-root boundaries;
- accepted versus rejected enumerated values.

Boundary tasks are distinct from ordinary negative tasks because they specifically test edge conditions of the accepted contract.

### Regression

Regression validation tasks preserve protection against previously observed defects or validation gaps.

Regression tasks may optionally identify historical provenance such as:

- governing issue;
- defect identifier;
- prior failing revision;
- explanatory note.

Historical provenance shall remain evidence only and shall not become normative authority.

### Unit

Unit validation tasks exercise validation implementation components in isolation.

Unit tasks establish implementation correctness but do not by themselves establish complete enforcement of the associated normative requirement.

### Integration

Integration validation tasks exercise enforcement through maintained public or aggregate validation surfaces.

Integration tasks establish that validation remains correctly composed through orchestration, wrappers, dispatch, repository-wide validation, or other maintained integration boundaries.

## Validation Task Identity

Every validation task shall have a stable repository-unique validation task identifier.

A conceptual task reference is:

```json
{
  "task_id": "REPO-AUTH-004-negative-001",
  "source": "repo/validation/authority.py",
  "entry_point": "test_undelegated_validation_is_rejected"
}
```

The validation task identifier represents the validation evidence relationship and shall remain stable across implementation movement when practical.

Source paths and functional entry points may change through implementation refactoring without requiring the task identity itself to change.

Validation task identifiers shall never be reused for unrelated validation behavior.

## Validation Function Requirement Tagging

Every externally identified validation function entry point shall carry an explicit machine-readable tag identifying the normative requirement it tests.

The tag shall contain exactly one active normative requirement identifier.

A conceptual Python form is:

```python
@validates_requirement("REPO-AUTH-004")
def test_undelegated_validation_is_rejected():
    ...
```

An equivalent attribute-based form may also be used where decorators are not appropriate:

```python
def test_undelegated_validation_is_rejected():
    ...

test_undelegated_validation_is_rejected.normative_requirement_id = "REPO-AUTH-004"
```

The repository shall define one canonical tagging mechanism for maintained validation entry points. Multiple competing tagging conventions should not be used.

The requirement tag is subordinate traceability metadata. It shall not restate, redefine, or extend the semantics of the normative requirement.

The tagged normative requirement identifier shall agree with the validation package that references the function entry point.

Mechanical validation should establish that:

- every referenced validation function entry point carries exactly one normative requirement tag;
- the tagged normative requirement exists and is active;
- the tagged normative requirement matches the `normative_requirement_id` of the validation package containing the corresponding task reference;
- no validation function entry point is tagged with multiple normative requirement identifiers;
- no maintained validation function entry point is referenced by validation packages for different normative requirements.

This creates a directly verifiable correspondence:

```text
validation package
    -> validation task reference
        -> source file
        -> functional entry point
            -> normative requirement tag
```

and requires the tag to resolve back to the same normative requirement identified by the owning validation package.

## Task-to-Requirement Cardinality

A validation task shall correspond to exactly one active normative requirement.

A single validation task shall not claim simultaneous ownership or coverage of multiple normative requirement identifiers.

When common validation logic supports multiple requirements, the implementation may use shared internal helpers, but requirement-specific validation tasks shall remain independently identifiable.

This preserves deterministic traceability:

```text
validation task
    -> validation package
        -> normative requirement ID
            -> owning specification
```

## Package-to-Requirement Cardinality

Every active normative requirement shall have exactly one validation package.

No active normative requirement may have:

- zero validation packages;
- multiple validation packages.

No validation package may identify:

- an unknown normative requirement;
- more than one normative requirement;
- a withdrawn normative requirement as its active owner.

## Withdrawn Requirements

Withdrawn normative requirement identifiers remain reserved historical identifiers but shall not retain active validation packages.

When normative semantics move, merge, or are otherwise normalized into surviving requirements:

- active validation ownership shall move to the surviving normative requirement or requirements;
- applicable validation tasks shall be reassigned to the surviving package that now owns the tested semantics;
- obsolete validation tasks may be removed;
- regression provenance may retain historical references to the withdrawn requirement where useful;
- no validation package shall cause a withdrawn requirement to continue acting as an independent semantic owner.

## Package Location

Validation package locations should be deterministic.

A proposed layout is:

```text
validation/
  packages/
    repo.authority-model/
      REPO-AUTH-001.json
      REPO-AUTH-002.json
      REPO-AUTH-003.json
    repo.manifest/
      REPO-MAN-001.json
      REPO-MAN-002.json
```

The final path convention shall be schema- and structure-governed.

Arbitrary package registration should be avoided when a deterministic path can be mechanically derived from specification identity and normative requirement identity.

## Derived Markdown

Every validation package shall declare exactly one canonical derived Markdown projection.

The generated Markdown should provide a human-readable view of package correspondence without creating new semantics.

It may include:

- owning specification identifier;
- normative requirement identifier;
- validation disposition;
- validation rationale where applicable;
- task counts by category;
- validation task identifiers;
- source files;
- functional entry points;
- optional regression provenance.

The derived Markdown shall not independently define:

- requirement semantics;
- validation obligations not present in accepted authority;
- package relationships not present in the source JSON;
- implementation behavior not represented by the validation tasks.

## Derived Coverage Views

Repository-wide validation coverage should be generated from validation packages rather than manually declared.

Potential generated views include:

| Requirement | Disposition | + | - | Boundary | Regression | Unit | Integration |
| --- | --- | --- | --- | --- | --- | --- | --- |
| REPO-AUTH-004 | mechanical | 1 | 3 | 1 | 2 | 4 | 1 |
| REPO-AUTH-005 | semantic-review | 0 | 0 | 0 | 0 | 0 | 0 |

Coverage percentages or boolean declarations such as `validated: true` should not be authoritative package fields.

Coverage is derived evidence from the maintained correspondence graph.

## Validation of the Validation System

The validation system shall mechanically verify its own correspondence model.

At minimum it should establish the following invariants.

### Requirement completeness

For every active identified normative requirement:

- exactly one validation package exists;
- the validation package identifies the correct owning specification;
- the validation package conforms to the validation-package schema.

### Package integrity

For every validation package:

- the referenced specification exists;
- the referenced normative requirement exists;
- the normative requirement is active;
- the referenced requirement belongs to the declared specification;
- the package path conforms to the canonical location rule;
- every standard task category is present;
- the validation disposition is valid;
- required disposition rationale is present;
- exactly one canonical derived Markdown artifact is declared.

### Task integrity

For every validation task reference:

- the task identifier is repository-unique;
- the source file exists;
- the functional entry point exists;
- the task appears in exactly one validation package;
- the task therefore resolves to exactly one active normative requirement;
- the category containing the task is one of the standardized validation-task categories.

### Withdrawn requirement integrity

For every withdrawn normative requirement:

- no active validation package exists for that withdrawn identifier;
- surviving validation ownership resolves through active normative requirements where applicable.

### Derived artifact integrity

For every validation package:

- the declared Markdown projection exists or is reproducibly generatable;
- the projection is a deterministic faithful representation of the package;
- stale or divergent generated validation documentation is rejected.

## Mechanical Validation Versus Semantic Review

The existence of a validation package for every normative requirement does not imply that every normative requirement is mechanically provable.

The validation package is the complete validation correspondence record for the requirement, including the explicit declaration that validation is partial, semantic-review based, or not applicable when appropriate.

Mechanical validation shall not manufacture executable tests merely to make a package appear populated.

Human semantic review remains necessary where accepted authority requires interpretation beyond objective mechanical enforcement.

## Completeness Versus Population

Package completeness and task population are distinct concepts.

A complete package:

- exists;
- conforms to schema;
- identifies one active normative requirement;
- contains every standard task category;
- declares a valid disposition;
- contains valid task references where tasks exist;
- declares its derived Markdown.

A complete package may contain zero tasks in one or more categories.

Mechanical validation shall not infer that every standard category must contain a task.

Whether the task set provides sufficient enforcement remains a semantic review concern unless accepted normative authority establishes stronger mechanical coverage requirements.

## Schema Principles

The validation-package schema should:

- use a closed object model;
- reject unknown fields where practical;
- prohibit embedded normative requirement text;
- require all standardized task categories;
- constrain validation disposition to the accepted vocabulary;
- require rationale for non-mechanical dispositions;
- constrain task references to the canonical task-reference shape;
- require unique task identifiers within a package;
- require exactly one derived Markdown declaration;
- avoid fields that duplicate information deterministically derivable from authority or repository structure.

The schema defines package structure only. It shall not independently establish normative validation semantics beyond authority explicitly delegated to it.

## Implementation Principles

Validation implementation may be freely refactored beneath stable package correspondence.

Shared helper functions are permitted.

Validation task entry points should remain externally resolvable and independently invocable where practical.

Aggregate validation runners should discover or consume validation correspondence through the canonical package model rather than maintaining a second manually curated requirement-to-validator registry.

Repository validation should avoid duplicate mappings encoded independently in:

- source code;
- shell dispatch tables;
- test lists;
- generated documentation;
- ad hoc manifests.

Where such projections are required for execution, they should be deterministically generated or mechanically verified against validation packages.

## Desired End State

The repository should expose one mechanically verifiable graph:

```text
accepted specification
    -> active normative requirement
        -> exactly one validation package
            -> standardized task categories
                -> zero or more validation tasks
                    -> source file
                    -> functional entry point
```

and the reverse graph:

```text
```

```text
validation task
    -> exactly one validation package
        -> exactly one active normative requirement
            -> exactly one owning specification
```

Every maintained validation task is therefore accountable to accepted authority.

Every active normative requirement has an explicit validation disposition and correspondence record.

No validator, test, schema, task registry, generated document, implementation detail, or historical behavior independently owns normative semantics.

## Proposed Primary Design Invariant

The overhaul should be evaluated against the following invariant:

> Every active identified normative requirement shall possess exactly one schema-governed validation package, and every validation task shall belong through exactly one validation package to exactly one active normative requirement.

All schema, structure, task taxonomy, orchestration, generation, migration, and self-validation decisions should preserve this invariant.

## Audit Questions

The current repository should be audited against this proposal by determining:

1. Which active normative requirements currently have no identifiable validation implementation.
2. Which current validation tasks cannot be mapped to exactly one active normative requirement.
3. Which validation tasks currently enforce multiple normative requirements simultaneously.
4. Which requirement-to-validation relationships are duplicated across source code, tests, schemas, runners, registries, or documentation.
5. Which existing tests are positive, negative, boundary, regression, unit, or integration tasks.
6. Which existing tests do not fit the proposed task taxonomy and whether the taxonomy should be extended.
7. Which active normative requirements require partial, semantic-review, or not-applicable disposition.
8. Which current validation semantics are encoded only in implementation and have no accepted normative owner.
9. Which withdrawn normative requirements still retain active validation behavior that should migrate to surviving normative owners.
10. Which existing generated validation artifacts can be replaced by deterministic projections from validation packages.
11. Which existing validation entry points and orchestration structures should remain as execution surfaces and which currently act as independent correspondence registries.
12. Which accepted repository specifications must change to establish this architecture normatively without duplicating semantic ownership.
