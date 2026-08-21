# Workstreams and dependencies

## Workstream VCP-I1 — Package schema and canonical correspondence-source realization

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.artifact-taxonomy`, `repo.repository-structure`, `repo.validation`.

**Purpose:** create the dedicated subordinate validation-correspondence package schema and the minimal repository-owned parsing/structural-validation support needed by later workstreams.

**Entry conditions:**

- this plan is accepted;
- all controlling specifications remain accepted and manifest-listed;
- no semantic contradiction has been discovered.

**Planned mechanics:**

- create `repo/schemas/repo/validation-correspondence-package.schema.json`;
- choose exact JSON Schema keywords and reusable definitions while preserving the closed logical surface delegated by REPO-VC-012;
- add focused structural validation support without introducing package population or active completeness enforcement prematurely;
- provide fixtures/self-tests proving schema acceptance/rejection behavior.

**Exit conditions:**

- schema mechanically enforces the accepted package shape and no independent semantics;
- validation can load and structurally check package documents;
- no package population completeness gate is enabled yet unless a valid accepted transition is separately proven.

## Workstream VCP-I2 — Source-local role metadata and task identity adaptation

**Controlling specifications:** `repo.validation-correspondence`, `repo.repository-structure`, `repo.validation`.

**Dependency:** VCP-I1.

**Purpose:** select and implement one source-local metadata mechanism per maintained validation implementation language and establish stable task identity/source resolution.

**Planned mechanics:**

- inventory maintained validation callables in root/repository/product validation domains;
- select one canonical metadata mechanism for each implementation language used;
- classify maintained callables as task or helper;
- assign stable task IDs only to externally identified validation tasks;
- expose exactly one canonical normative reference from task source metadata;
- preserve shared helpers, parameterization, fixtures, and internal assertions without artificial task identities;
- introduce wrappers only where existing broad validation responsibilities cannot truthfully satisfy one-task/one-package ownership.

**Exit conditions:**

- every migrated maintained validation callable in the selected scope has exactly one role;
- every externally identified task has stable identity and resolvable source coordinates;
- task metadata agrees with planned canonical package ownership;
- no independent source registry is introduced.

## Workstream VCP-I3 — Canonical package population and product reconciliation

**Controlling specifications:** `repo.validation-correspondence`, `repo.artifact-taxonomy`, `repo.repository-structure`, `repo.product-correspondence`, `repo.product-manifest`, `repo.product-spec-base`, `repo.validation`.

**Dependencies:** VCP-I1, VCP-I2.

**Purpose:** populate canonical package sources and reconcile product test mappings with canonical validation-package references.

**Planned mechanics:**

- enumerate active accepted repository requirements and active accepted product requirements from their authoritative manifests/specifications;
- create one canonical package at its owner-derived path for each active requirement;
- assign disposition/rationale from accepted semantics and actual validation applicability;
- bind migrated task identities to package records;
- update product test mappings to use canonical `validation_package_refs` without independently authoring requirement/task/package-path data;
- stage preparatory or batched package population only where accepted lifecycle rules make the intermediate state valid.

**Exit conditions:**

- target active requirement population has exactly one canonical package each;
- no canonical requirement has packages in multiple validation domains;
- product mappings resolve through canonical package references;
- inactive/historical/preparatory material does not count toward active completeness.

## Workstream VCP-I4 — Mechanical integrity enforcement and deterministic projections

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.repository-structure`, `repo.product-correspondence`, `repo.validation`.

**Dependencies:** VCP-I1, VCP-I2, VCP-I3.

**Purpose:** enable objective correspondence integrity enforcement and useful deterministic subordinate projections.

**Planned mechanics:**

- implement leaf enforcement for repository-owned and product-owned correspondence;
- implement only genuine cross-domain/whole-checkout invariants in root validation;
- enforce active package uniqueness/completeness, canonical binding, task uniqueness/source resolution, task-to-package uniqueness, source/package agreement, lifecycle state, schema conformance, and projection freshness;
- generate aggregate requirement-to-disposition/task views only where they add operational value;
- keep all generated output reconstructible and non-authoritative.

**Exit conditions:**

- objective REPO-VAL-043 invariants fail closed;
- generated views reproduce canonical package sources deterministically;
- no validator invents semantic sufficiency or coverage requirements beyond accepted authority.

## Workstream VCP-I5 — Propagation/materialization and freshness/equivalence realization

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.repository-structure`, `repo.validation`, `repo.development-workflow`.

**Dependencies:** VCP-I1, VCP-I4.

**Purpose:** preserve canonical correspondence identity and subordinate status across any maintained materialized validation surfaces that require the repository-generic framework.

**Planned mechanics:**

- inventory only actual maintained propagation/materialization surfaces;
- decide whether each surface copies canonical package sources, derives a projection, or references canonical source without duplication;
- preserve canonical package identity/reference, lifecycle state, disposition, and task ownership;
- implement deterministic freshness/equivalence proofs appropriate to the selected mechanism;
- reject stale, missing, duplicated, or semantically divergent propagated correspondence.

**Exit conditions:**

- every required maintained materialized surface has one explicit source relationship;
- no separately mutable correspondence registry exists;
- freshness/equivalence checks are repository-local and deterministic.

## Workstream VCP-I6 — Migration completion and end-to-end conformance

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.artifact-taxonomy`, `repo.repository-structure`, `repo.product-correspondence`, `repo.product-manifest`, `repo.product-spec-base`, `repo.validation`, `repo.development-workflow`.

**Dependencies:** VCP-I1 through VCP-I5.

**Purpose:** complete staged migration, retire obsolete duplicate mappings, and prove end-to-end conformance.

**Planned mechanics:**

- remove or normalize obsolete manually maintained requirement-to-validation mappings after canonical package/source checks are active;
- complete any remaining package/task migration batches;
- enable repository-wide active completeness only at a revision that remains valid under accepted lifecycle rules;
- use an Atomic authority transition only if the exact final enablement proves there is no valid intermediate accepted revision;
- run full validation/self-test/conformance checks across source and materialized surfaces.

**Exit conditions:**

- every active identified requirement has exactly one canonical package;
- every externally identified task resolves through exactly one package to exactly one canonical requirement;
- package/source/product/projection/materialization invariants pass;
- obsolete competing correspondence registries are absent;
- the feature-request implementation completion gate can be evaluated from accepted plan and implementation evidence.

## Dependency graph

`VCP-I1 -> VCP-I2 -> VCP-I3 -> VCP-I4 -> VCP-I5 -> VCP-I6`

VCP-I5 also requires VCP-I1 directly because propagation mechanics must understand canonical source/schema identity.

## Implementation-issue boundary

Each successor implementation issue must cite one or more contiguous/dependency-compatible workstream IDs. Combining workstreams is allowed only when the issue remains reviewable and all controlling specification sets are cited as their deterministic union.

No implementation issue may claim authority from an unaccepted candidate version of this plan.
