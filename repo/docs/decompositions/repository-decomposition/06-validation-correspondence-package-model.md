# Validation-correspondence package model

## Status

Directional decomposition content.

## Purpose

Define the repository-generic responsibility for the durable validation-correspondence source model, including package ownership, cardinality, lifecycle, and validation disposition.

## Responsibilities

- provide one canonical active correspondence package per active normative requirement in the completeness domain;
- require each active package to identify exactly one canonical normative-requirement reference;
- permit zero or more externally identified validation tasks without conflating package completeness with task population;
- record explicit validation disposition independently from task count;
- keep correspondence packages subordinate to normative authority and prohibit duplicated requirement semantics;
- define active, withdrawn, historical, and preparatory package lifecycle responsibilities without prematurely selecting their exact representation.

## Boundaries

This area defines the responsibility of the package source model, not its exact artifact type, schema, filename, filesystem namespace, disposition enum, rationale fields, or transition syntax.

The package is correspondence evidence and does not become a second normative-requirement registry.

## Dependencies

Depends on Normative-reference Identity and Active Requirement Scope.

Also depends on repository artifact taxonomy, repository structure, validation authority, generated-artifact governance, and development workflow for lifecycle transitions.

Feeds Validation-task Correspondence and Source Auditability, Validation-domain Ownership and Product Reconciliation, and Correspondence Integrity, Propagation, and Migration.

## Exclusions

- no `packages/` namespace authorization;
- no JSON/schema decision;
- no exact disposition vocabulary or rationale rules;
- no package population;
- no generated projection format;
- no implementation architecture.

## Unresolved decisions

- package artifact class and schema ownership;
- exact package namespace and deterministic path rules;
- final validation-disposition vocabulary, semantics, transitions, and rationale requirements;
- exact representation of preparatory, active, withdrawn, and historical correspondence;
- whether any package metadata is derivable rather than stored.

## Expected specification families

Directional expectation:

- **Repository validation-correspondence specification family**: package cardinality, source-of-truth, disposition, lifecycle, and semantic-subordination rules;
- **Repository artifact/structure specification families**: artifact class, allowed structural role, path envelope, and generated-projection placement if later authorized;
- **Repository development-workflow family**: lifecycle transition and accepted-state constraints where package activation interacts with authority acceptance.

Exact artifacts remain downstream normative decisions.

## Successor work

After decomposition acceptance, repository specification work must establish the package contract and its relationships to artifact taxonomy, structure, validation, and workflow before package creation or population is authorized.
