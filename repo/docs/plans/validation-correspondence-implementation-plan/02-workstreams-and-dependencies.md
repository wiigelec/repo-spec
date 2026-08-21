# Workstreams and dependencies

## Workstream VCP-I1 — Package schema and canonical correspondence-source realization

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.artifact-taxonomy`, `repo.repository-structure`, `repo.validation`.

**Purpose:** create the dedicated subordinate validation-correspondence package schema and minimal repository-generic parsing/structural-validation support needed by later workstreams.

**Entry conditions:**

- this plan is explicitly accepted;
- all controlling specifications remain accepted and manifest-listed;
- no semantic contradiction has been discovered.

**Planned mechanics:**

- create `repo/schemas/repo/validation-correspondence-package.schema.json`;
- choose exact JSON Schema keywords and reusable definitions while preserving the closed logical surface delegated by REPO-VC-012;
- add focused structural validation support without package population or active completeness enforcement;
- provide fixtures/self-tests proving schema acceptance/rejection behavior.

**Exit conditions:**

- schema mechanically enforces the accepted package shape and no independent semantics;
- validation can load and structurally check package documents;
- no package population completeness gate is enabled.

## Workstream VCP-I2 — Source-local role metadata and task identity adaptation

**Controlling specifications:** `repo.validation-correspondence`, `repo.repository-structure`, `repo.validation`.

**Dependency:** VCP-I1.

**Purpose:** select and implement one repository-generic source-local metadata mechanism per maintained validation implementation language and establish stable task identity/source resolution rules.

**Planned mechanics:**

- inventory framework-maintained validation callables across applicable root/repository/product validation code surfaces without treating product-specific artifact mutation as authorized;
- select one canonical metadata mechanism for each implementation language used by maintained validation code;
- classify migrated framework-maintained callables as task or helper;
- assign stable task IDs only to externally identified validation tasks;
- expose exactly one canonical normative reference from task source metadata;
- preserve shared helpers, parameterization, fixtures, and internal assertions without artificial task identities;
- introduce wrappers only where broad framework-maintained validation responsibilities cannot truthfully satisfy one-task/one-package ownership.

**Exit conditions:**

- every migrated framework-maintained validation callable in scope has exactly one role;
- every externally identified task has stable identity and resolvable source coordinates;
- task metadata can be mechanically reconciled with canonical package ownership;
- no independent source registry is introduced.

Product-specific source mutation, where present, requires separately governed product-owned implementation authority.

## Workstream VCP-I3 — Repository-owned package population framework and product-authority handoff

**Controlling specifications:** `repo.validation-correspondence`, `repo.artifact-taxonomy`, `repo.repository-structure`, `repo.product-correspondence`, `repo.product-manifest`, `repo.product-spec-base`, `repo.validation`, `repo.development-workflow`.

**Dependencies:** VCP-I1, VCP-I2.

**Purpose:** populate canonical repository-owned packages, establish deterministic discovery of product-owned package obligations, and prepare the handoff to product-owned realization without directly mutating product-owned correspondence under repository-only authority.

**Planned mechanics:**

- enumerate active accepted repository requirements and create one canonical repository-owned package at each owner-derived path;
- enumerate active accepted product requirements only to compute product-owned correspondence obligations and handoff scope;
- assign disposition/rationale and bind migrated task identities for repository-owned packages;
- implement repository-generic checks that product test mappings, when present or later created under product authority, use canonical `validation_package_refs` shape and do not independently author forbidden requirement/task/package-path registries;
- define the exact product-owned planning handoff inventory needed for product package population and product correspondence mutation;
- stage repository-owned preparatory/batched package population only where accepted lifecycle rules make the intermediate state valid.

**Exit conditions:**

- target active repository-owned requirement population has exactly one canonical package each;
- no repository-owned requirement has packages in multiple validation domains;
- product-owned obligations are deterministically enumerable and handed off without being mutated here;
- inactive/historical/preparatory material does not count toward active completeness;
- repository-wide/product-wide completeness is not enabled merely because repository-owned population is complete.

## Workstream VCP-I4 — Mechanical integrity enforcement and deterministic projections

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.repository-structure`, `repo.product-correspondence`, `repo.validation`, `repo.development-workflow`.

**Dependencies:** VCP-I1, VCP-I2, VCP-I3.

**Purpose:** enable objective repository-generic correspondence integrity enforcement and deterministic subordinate projections without asserting product completeness before product-owned realization exists.

**Planned mechanics:**

- implement leaf enforcement for repository-owned correspondence;
- implement framework-generic validation logic applicable to product correspondence while leaving product-owned source mutation to product authority;
- implement only genuine cross-domain/whole-checkout invariants in root validation;
- enforce schema conformance, canonical binding, task uniqueness/source resolution, task-to-package uniqueness, source/package agreement, lifecycle state, and projection freshness for scopes whose canonical sources are validly present;
- defer aggregate active completeness enforcement across product-owned requirements until corresponding product-owned package population exists under accepted product authority;
- generate aggregate requirement-to-disposition/task views only where they add operational value;
- keep generated output reconstructible and non-authoritative.

**Exit conditions:**

- objective repository-generic REPO-VAL-043 invariants fail closed for validly activated scopes;
- no product completeness claim is made from repository-owned population alone;
- generated views reproduce canonical package sources deterministically;
- no validator invents semantic sufficiency or coverage requirements.

## Workstream VCP-I5 — Repository-generic propagation/materialization and freshness/equivalence realization

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.repository-structure`, `repo.validation`, `repo.development-workflow`.

**Dependencies:** VCP-I1, VCP-I4.

**Purpose:** preserve canonical correspondence identity and subordinate status across actual repository/framework-owned maintained materialized validation surfaces.

**Planned mechanics:**

- inventory repository/framework-owned maintained propagation/materialization surfaces;
- decide whether each framework-owned surface copies canonical package sources, derives a projection, or references canonical source without duplication;
- preserve canonical package identity/reference, lifecycle state, disposition, and task ownership;
- implement deterministic freshness/equivalence proofs appropriate to the selected framework-owned mechanism;
- reject stale, missing, duplicated, or semantically divergent propagated correspondence;
- produce a separate product-owned handoff inventory for any product-specific materialization surface discovered.

**Exit conditions:**

- every required repository/framework-owned materialized surface has one explicit source relationship;
- no separately mutable framework correspondence registry exists;
- freshness/equivalence checks are repository-local and deterministic;
- product-specific materialization is not mutated under this workstream.

## Workstream VCP-I6 — Repository-generic migration completion and cross-domain conformance integration

**Controlling specifications:** `repo.authority-model`, `repo.validation-correspondence`, `repo.artifact-taxonomy`, `repo.repository-structure`, `repo.product-correspondence`, `repo.product-manifest`, `repo.product-spec-base`, `repo.validation`, `repo.development-workflow`.

**Dependencies:** VCP-I1 through VCP-I5 plus accepted evidence from separately governed product-owned realization where product requirements participate in active completeness.

**Purpose:** complete repository-generic migration, retire obsolete repository-owned duplicate mappings, and integrate repository and product evidence into end-to-end conformance without mutating product-owned artifacts under repository-only authority.

**Planned mechanics:**

- remove or normalize obsolete repository-owned manually maintained requirement-to-validation mappings after canonical package/source checks are active;
- complete remaining repository-owned package/task migration batches;
- consume, but do not create, product-owned package/correspondence evidence from separately governed product-owned work;
- enable repository-wide active completeness only at a revision where both repository-owned and required product-owned canonical package populations validly exist;
- use an Atomic authority transition only if the exact final enablement proves there is no valid intermediate accepted revision;
- run full validation/self-test/conformance checks across canonical and materialized surfaces.

**Exit conditions:**

- every active repository-owned requirement has exactly one canonical package;
- required product-owned completion evidence is accepted and present before aggregate completeness is claimed;
- every externally identified task in the completed scope resolves through exactly one package to exactly one canonical requirement;
- package/source/product/projection/materialization invariants pass;
- obsolete competing repository-owned correspondence registries are absent;
- the feature-request implementation completion gate can be evaluated from both repository-owned and product-owned accepted evidence.

## Dependency graph

Repository-generic chain:

`VCP-I1 -> VCP-I2 -> VCP-I3 -> VCP-I4 -> VCP-I5 -> VCP-I6`

VCP-I6 additionally depends on separately governed product-owned realization evidence wherever active product requirements are part of aggregate completeness.

## Implementation-issue boundary

Each repository-generic successor implementation issue must cite one or more dependency-compatible workstream IDs. Combining workstreams is allowed only when the issue remains reviewable and all controlling repository-specification sets are cited as their deterministic union.

No implementation issue may claim authority from a candidate version of this plan.

Product-owned implementation issues may not cite this repository-owned plan as a substitute for product-owned planning authority or exact controlling accepted product specifications.
