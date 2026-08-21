# functional-set lifecycle: Normative Requirement Validation Correspondence — Part 3

This part defines lifecycle integrity, generated projections, migration direction, dependencies, and decomposition handoff for **Normative Requirement Validation Correspondence**.

## Correspondence integrity

The capability should support validation of the correspondence model itself.

Directional integrity expectations include:

- every in-scope active identified normative requirement resolves to exactly one active package;
- every active package resolves to a known active normative requirement;
- package ownership agrees with the normative owner;
- externally identified task identities are unique in their accepted scope;
- referenced task source locations and entry points resolve;
- every externally identified task belongs to exactly one package;
- task entry-point metadata agrees with package ownership;
- withdrawn requirements do not retain active package ownership;
- deterministic projections reproduce the canonical source model;
- stale or divergent projections are rejected.

These are capability-level integrity expectations. Exact error classes, validators, schema constraints, and enforcement phases remain downstream work.

## Lifecycle direction

Active correspondence follows active normative authority.

When a normative requirement is withdrawn:

- its identifier remains reserved under existing authority;
- its active correspondence package no longer counts as active coverage;
- historical package/task provenance may be retained if downstream lifecycle rules require it;
- generated active-coverage views must not present the withdrawn requirement as current.

When a requirement is replaced or superseded, downstream specification must define how historical correspondence remains traceable without treating the successor as the same semantic requirement by implication.

## Generated projections

Coverage reports and human-readable documentation should be generated from canonical correspondence sources.

Potential projections include:

- requirement-to-disposition coverage;
- requirement-to-task indexes;
- task-to-requirement indexes;
- mechanical versus review-required coverage;
- unresolved or incomplete correspondence reports.

The functional set does not mandate a particular generated file layout or presentation format.

Generated artifacts remain subordinate and deterministic.

## Ownership and namespace direction

Physical package location must follow authority ownership rather than convenience.

The collected proposal illustrated `validation/packages/<spec-id>/<requirement-id>.json`, but the current repository structure does not authorize that path and the functional set does not approve it.

Downstream decomposition must determine:

- which repository authority owns the correspondence contract;
- how repository-owned, product-owned, or whole-checkout correspondence is represented;
- whether one physical namespace can correctly represent multiple ownership domains;
- where schemas and generated projections belong;
- which structure changes are required before package files can exist.

No package namespace is authorized by this functional-set patch alone.

## Propagation and materialization integrity

Repo-owned normative validation correspondence is framework material that must accompany the repo-owned normative authority it describes.

The propagation boundary includes the repo-spec `product/` tree and the derived or initialized repository `repo/` and `product/` trees that receive repo-owned normative authority under existing framework/bootstrap contracts.

Directional integrity across those surfaces requires:

- propagated correspondence to resolve to the same canonical repo-owned normative requirement;
- package/correspondence identity to remain stable across materialization;
- active/withdrawn state to remain consistent;
- validation disposition and externally identified task ownership to remain semantically equivalent;
- generated or copied views to remain subordinate to the canonical source;
- stale, missing, or divergent propagated correspondence to be detectable.

A downstream design must not create separate mutable correspondence registries for the source tree, repo-spec product tree, initialized `repo/`, and initialized `product/` surfaces.

Exact copying, generation, initializer inventory, destination paths, and freshness-check mechanics remain owned by downstream structure, initializer, generated-artifact, and validation specifications.

## Migration direction

The repository may begin from a state with no package namespace while the intended end state requires complete package correspondence.

A later implementation must not require an invalid accepted intermediate revision.

If downstream accepted work introduces both:

- a new durable source namespace; and
- a repository-wide completeness invariant that requires a complete package population,

the transition should use the accepted atomic-transition mechanism when those changes are inseparable.

If downstream authority permits staged inactive sources, partial non-enforced population, or another valid intermediate state, atomic transition may not be necessary.

The functional set establishes the preservation-of-valid-state direction, not the exact migration plan.

## Dependencies

Downstream decomposition must account for dependencies on:

- normative requirement identity and lifecycle authority;
- repository artifact taxonomy and structure;
- validation authority and enforcement ownership;
- generated-artifact governance;
- development workflow and atomic-transition rules;
- existing validation inventory and test organization;
- provenance for withdrawn and superseded requirements.

Existing validation execution remains a dependency rather than being redefined by this capability.

## Decomposition handoff

Repository decomposition should translate this functional-set direction into bounded responsibility areas before specification work begins.

At minimum, decomposition should separate responsibilities for:

1. normative-reference identity and active requirement scope;
2. validation-correspondence package ownership, cardinality, lifecycle, and disposition;
3. validation-task identity, task dimensions, and executable entry-point correspondence;
4. correspondence propagation/materialization across the repo-spec `product/` tree and derived/initialized repository `repo/` and `product/` trees;
5. correspondence integrity, deterministic projections, and migration/conformance.

The decomposition may refine or repartition these areas if it preserves the approved capability boundary.

## Downstream decisions intentionally unresolved

Later governed work must decide, without treating this functional set as exact technical authority:

- canonical normative-reference representation;
- package artifact type and schema;
- package source namespace;
- in-scope normative requirement families;
- disposition definitions and transition rules;
- task identity granularity;
- task metadata vocabulary and cardinalities;
- entry-point tagging or registration mechanism;
- shared-helper and parameterized-test treatment;
- withdrawn/superseded correspondence retention;
- generated projection paths and formats;
- exact source-to-product and source-to-initialized-tree propagation/materialization mechanics;
- exact freshness and equivalence validation across propagated correspondence surfaces;
- exact self-validation mechanics;
- migration sequencing and whether atomic transition is required.

## Directional approval boundary

This functional-set content is directional and non-normative.

Its merge establishes the approved capability handoff into separately governed repository decomposition.

It does not itself authorize specification changes, schema creation, package creation, repository-structure changes, validation/test migration, implementation planning, or implementation.
