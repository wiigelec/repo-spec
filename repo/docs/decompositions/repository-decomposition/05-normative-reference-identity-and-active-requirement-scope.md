# Normative-reference identity and active requirement scope

## Status

Directional decomposition content.

## Purpose

Define the repository-generic responsibility for identifying the normative requirements that participate in validation correspondence without turning correspondence metadata into normative authority.

## Responsibilities

- establish an unambiguous canonical normative-requirement reference boundary that can distinguish specification identity from requirement identity;
- define the active completeness domain as all active identified normative requirements in accepted repository and accepted product specifications governed by the framework;
- preserve the distinction between active requirements, withdrawn reserved identifiers, and retained historical provenance;
- keep candidate requirements outside active normative completeness while permitting later preparatory correspondence rules;
- prevent completeness scope from being inferred from filesystem presence, implementation status, or ownership convenience.

## Boundaries

This area identifies repository-generic identity, lifecycle, and completeness responsibilities. It does not select an exact reference serialization, require bare repository-global requirement-ID uniqueness, or define package/schema mechanics.

Normative specifications remain the semantic owners of the requirements they define.

## Dependencies

Depends on accepted repository authority for specification identity, normative requirement lifecycle, manifest membership, product specification lifecycle, and withdrawal reservation.

Feeds Validation-correspondence Package Model and all later correspondence areas.

## Exclusions

- no exact canonical reference object or string format;
- no new requirement-ID uniqueness rule;
- no package path or schema;
- no candidate-acceptance mechanism;
- no validation implementation or task tagging.

## Unresolved decisions

- exact canonical normative-reference representation;
- whether accepted authority should establish any stronger uniqueness invariant than specification identity plus requirement identity;
- exact preparatory correspondence eligibility for candidate specifications;
- historical retention representation for withdrawn or superseded requirements.

## Expected specification families

Directional expectation:

- **Repository authority/identity specification family**: canonical normative-reference identity and lifecycle interaction with accepted specification authority;
- **Repository validation-correspondence specification family**: active completeness-domain rules and correspondence applicability;
- **Cross-specification relationships**: manifest, authority-model, product-specification-base, requirement withdrawal/supersession, and validation authority must remain consistent.

Repository-generic identity and completeness requirements shall remain under repository specification authority rather than being duplicated in product-specification levels.

## Successor work

After this decomposition is accepted, owner-appropriate repository specification work must define the canonical identity and active completeness rules before correspondence artifacts or validators rely on them.
