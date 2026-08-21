# functional-set lifecycle: Normative Requirement Validation Correspondence — Part 1

This part defines the capability boundary, authority boundary, and normative-requirement identity direction for **Normative Requirement Validation Correspondence**.

## Capability boundary

Normative Requirement Validation Correspondence governs the durable relationship between accepted normative requirements and maintained validation evidence.

The capability is about correspondence, not validation execution itself. It establishes the directional expectation that validation evidence can be traced to the normative requirement it supports without allowing validation artifacts to become a source of product or repository semantics.

The correspondence model shall remain subordinate to accepted normative authority.

## Included intent

The framework should support a canonical correspondence model in which:

- each in-scope active identified normative requirement has one durable active validation-correspondence package;
- each active package identifies one unambiguous normative requirement;
- maintained externally identified validation tasks belong through exactly one package to exactly one normative-requirement reference;
- package metadata records how the requirement is validated without restating the requirement's normative semantics;
- machine-readable correspondence can drive deterministic coverage and documentation views;
- integrity validation can detect missing, duplicated, stale, or conflicting correspondence.

The capability applies to repository-owned normative requirements and may support other owner domains only where downstream authority explicitly defines the ownership and namespace rules.

## Relationship to normative authority

Normative specifications remain the sole semantic authority for the requirements they own.

A validation-correspondence package:

- may identify a normative requirement;
- may classify validation disposition;
- may identify maintained validation tasks and entry points;
- may provide rationale required by downstream correspondence rules;
- may participate in deterministic generated coverage views.

A package must not:

- rewrite a normative requirement;
- weaken or strengthen the requirement;
- create new normative behavior;
- resolve an ambiguity that belongs to the normative specification;
- become an independent competing requirement registry.

Validation failures may show that implementation or correspondence is inconsistent with accepted authority, but the validator does not manufacture replacement semantics.

## Canonical normative-requirement reference

The capability requires every package and externally identified validation task to resolve through an unambiguous canonical normative-requirement reference.

The functional set does not require bare requirement identifiers to be repository-global.

Accepted authority already provides stability and withdrawal reservation for requirement identifiers, but the analysis did not establish repository-global uniqueness of a bare `normative_requirement_id`.

Therefore the directional boundary permits a composite reference that includes normative specification identity plus requirement identity.

Downstream specification work may establish a stronger identity invariant if independently justified, but this functional set does not depend on doing so.

## Requirement lifecycle boundary

Correspondence follows the lifecycle of the normative requirement it references.

The directional model distinguishes:

- active identified requirements that participate in the active correspondence set;
- withdrawn requirements whose identifiers remain reserved but do not retain active package ownership;
- retained historical correspondence that may remain available as provenance without being counted as active validation coverage.

Exact retention format and archival mechanics remain downstream decisions.

## Completeness scope

The intended end state is complete correspondence for the set of normative requirements declared in scope by downstream authority.

The functional set does not silently define which specification families or lifecycle states constitute that in-scope set.

Downstream decomposition and specification must make the completeness domain explicit so validators do not infer scope from directory presence or implementation convenience.

## Exclusions

This capability does not decide:

- bare repository-global requirement-ID uniqueness;
- exact package artifact identifiers;
- exact package schemas;
- exact package filesystem paths;
- exact validation annotation or decorator syntax;
- exact task execution mechanisms;
- exact CI orchestration;
- exact generated report format;
- decomposition, specification partition, implementation planning, or implementation architecture.

Those decisions belong to later governed lifecycle stages.
