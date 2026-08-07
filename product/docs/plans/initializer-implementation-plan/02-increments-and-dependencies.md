# Implementation increments and dependencies

Status: candidate; non-authorizing

## Authority boundary

Non-normative with respect to product semantics. Sequences future conformance and implementation work from Patch 1's composite key ownership; does not reinterpret requirements, accept the plan, or authorize implementation. Composite keys use `<spec_id>::<requirement_id>`. `product.framework-installation::INIT-FIN-001-008` and `product.full-initialization::INIT-FIN-001-011` are distinct sets. Every set below is also assigned to B0; listed I1-I5 owner is sole implementation owner from Patch 1.

## Bounded implementation DAG

`B0 -> I1 -> I2 -> I3 -> I4 -> I5`

Edges: B0→I1 (keyed evidence bounds all work), I1→I2 (validated request/resolved source/preflight needed before staging), I2→I3 (staged content needed before provenance/handoff/Git), I3→I4 (conforming identity/handoff/Git state required before validation), I4→I5 (validated promotion/finalization behavior required before E2E orchestration). Spec dependencies are authority entry constraints. Ranks 0-5 assigned; every edge increases rank so the graph is acyclic.

## B0 - Existing-implementation conformance baseline

Purpose: requirement-by-requirement evidence baseline across all 291 composite keys before maintained artifact changes. Outcome: one supported classification per key plus explicit blocked finding.

Controlling requirements: all 34 accepted specs and all 291 composite keys from Patch 1. Sole planning owner of `product.initializer-level-0::INIT-L0-007`. Entry: planning basis remains `d3cf252`, all specs accepted and traceable, provenance conflict recorded as blocker. Exit: machine-reviewable matrix with one classification per key (preserve/repair/replace/implement), cited evidence, aggregate counts to 34/291, three conflicting provenance keys flagged blocked. Exclusions: no implementation/test/schema/spec mutation, no inferred conformance, no provenance-field choice.

## I1 - Request and preflight

Purpose: validated canonical standard-profile request, exact local SHA-1 source/material identity, absent-destination same-filesystem preflight. Unsupported modes rejected before staging.

Controlling requirements (I1-owned): `product.initializer-level-0::INIT-L0-006`, `product.initialization-request::INIT-REQ-001-015`, `product.source-revision-identity::INIT-SRC-001-005,007-008`, `product.destination::INIT-DST-001-002`, `product.product-identity::INIT-PID-001-003,005-007`, `product.material-manifest::INIT-MMF-001-002,004-011`, `product.git-object-identity::INIT-OID-001-008,010`, `product.destination-preflight::INIT-DPF-001-002`, `product.request-intake::INIT-INT-001-002`, `product.source-material-resolution::INIT-SMR-001-006`.

Predecessor: B0. Entry: B0 exit classifications, accepted plan, governed I1 issue. Exit: positive/negative evidence per I1 key, unknown/empty/contradictory/excluded inputs rejected distinctly, only exact SHA-1 local commit-tree consumed, existing/cross-device destinations rejected, all accepted values and identities preserved for downstream. Exclusions: no staging, material, records, Git, validation, promotion, orchestration, remote/platform/dry-run/resume/recovery/migration, provenance interpretation.

## I2 - Transactional and material realization

Purpose: isolated same-filesystem transaction layout, closed-inventory candidate repository content (framework, foundations), deterministic content and digest inputs for records/Git/validation.

Controlling requirements (I2-owned): `product.initializer-level-0::INIT-L0-002,003`, `product.initialization-request::INIT-REQ-016`, `product.source-revision-identity::INIT-SRC-006`, `product.material-classification::INIT-MAT-001-003`, `product.staging-workspace::INIT-STG-001-004`, `product.product-identity::INIT-PID-004`, `product.material-manifest::INIT-MMF-003`, `product.generated-repository::INIT-GRL-001-019,022-023`, `product.initializer-output-inventory-v1::INV-V1-001-015`, `product.foundation-seeding::INIT-FSD-001-021`, `product.framework-installation::INIT-FIN-001-008`.

Predecessor: I1. Entry: validated request, resolved source/manifest, preflight evidence, B0 classifications. Exit: staging root empty and same-filesystem with only `transaction/` and `repository/`; requirement-level evidence per I2 key for closed-inventory material installation, bytes/modes/substitutions/records, deterministic enumeration, rejection of broad copies/undeclared outputs/prohibited paths/platform content; digest input carried to I3/I4. Exclusions: no provenance/handoff/Git/validation/promotion/orchestration, no recursive tree copies, no resume/recovery/migration/overwrite/cross-device.

## I3 - Repository identity, handoff, and Git

Purpose: staged repository identity records and deterministic Git state (provenance, pre-Git handoff, generated object identity, single-root-commit local repo). Issue #255 repaired the previously conflicting accepted provenance/handoff semantics.

Controlling requirements (I3-owned): `product.initializer-level-0::INIT-L0-004,008`, `product.local-git-repository::INIT-GIT-001-005`, `product.provenance-record::INIT-PRO-001-008`, `product.handoff-manifest::INIT-HND-001-014`, `product.git-bootstrap-profile::INIT-BPF-001-005`, `product.git-object-identity::INIT-OID-009`, `product.generated-repository::INIT-GRL-020-021`, `product.handoff-assembly::INIT-HAS-001`, `product.local-git-initialization::INIT-LGI-001-002`, `product.provenance-recording::INIT-PRC-001`.

Predecessor: I2. Entry: I2 exit evidence, accepted repaired provenance/handoff contracts from issue #255, B0 classifications, accepted plan, governed I3 issue. Exit (after repair): evidence for repaired provenance contract, handoff/provenance/inventory traceability, closed field sets, deterministic serialization, complete Git state on `main` with full SHA-1 objects, clean worktree. Exclusions: no guessed provenance fields, no I4/I5 work, no extra commits/tags/remotes/SHA-256, no plan acceptance from unaffected I3 preparation.

## I4 - Validation and promotion

Purpose: ordered Phase 1/Phase 2 validation, deterministic report/state finalization, promotion gating, atomic same-filesystem rename, diagnostic preservation, cleanup.

Controlling requirements (I4-owned): `product.initializer-level-0::INIT-L0-005`, `product.staging-state::INIT-STA-001-013`, `product.destination::INIT-DST-003`, `product.staging-workspace::INIT-STG-005`, `product.execution-report::INIT-RPT-001-004,004a,004b,005-012`, `product.validation-profile::INIT-VP-001-007`, `product.validation-report::INIT-VR-001-016`, `product.repository-validation::INIT-RVA-001-005`, `product.transactional-staging::INIT-TST-001-007`.

Predecessor: I3. Entry: I3 complete with conforming staged content/Git/provenance. Exit: ordered validation checks with status/failure codes, fault-injection at every report-finalization boundary (no partial pair permits promotion), promotion evidence for immediate absence recheck + single rename + post-rename stat, terminal-boundary evidence for pre-promotion failure/promoted success/indeterminate promotion/promoted-with-finalization-error. Exclusions: no provenance interpretation, no bypass of blocked predecessor, no copy/fallback/retry, no I5 completion or plan acceptance while blocked.

## I5 - End-to-end orchestration

Purpose: compose standard bounded workflow in canonical lifecycle order, enforce all predecessors and gates, prove four terminal outcomes plus determinism and rejection.

Controlling requirements (I5-owned): `product.initializer-level-0::INIT-L0-001,009`, `product.execution-profile::INIT-PRF-001-004`, `product.content-equivalence::INIT-EQV-001-015`, `product.lifecycle-stages::INIT-LCS-001-012`, `product.execution-orchestration::INIT-EOR-001-002`, `product.full-initialization::INIT-FIN-001-011`.

Predecessor: I4. Entry: I1-I4 exits with complete evidence. Exit: E2E evidence for 13 accepted stages in order, each precondition enforced; terminal-outcome evidence for promoted success, pre-promotion failure, indeterminate promotion, promoted-with-finalization-error; equivalent inputs produce equivalent output (provenance timestamp excepted); negative E2E for unsupported profile/refs/remote/destination/platform/resume/migration/cross-device; final composite-key coverage report reconciles all 291 keys. Exclusions: no dry-run/platform/recovery/resume/remote/SHA-256/migration/overwrite, no plan acceptance or implementation issue creation while any blocker open.

## Cross-increment carriage

| Concern | Producer→consumers | Required carriage |
| --- | --- | --- |
| Accepted spec authority (`INIT-L0-007`) | B0→I1-I5 | No increment substitutes documents/code/tests/plan for accepted specs |
| Request authority and identity (`INIT-L0-006`, `INIT-REQ-001-015`, `INIT-PID-001-003,005-007`, `INIT-INT-001-002`) | I1→I2-I5 | Preserve accepted values, order, fingerprints, rejection decisions |
| Source/object/material identity (`INIT-SRC-001-005,007-008`, `INIT-OID-001-008,010`, `INIT-MMF-001-002,004-011`, `INIT-SMR-001-006`) | I1→I2-I5 | Consume only exact local SHA-1 commit tree and validated mapping |
| Destination/preflight (`INIT-DST-001-002`, `INIT-DPF-001-002`) | I1→I2,I4,I5 | Preserve absence/same-filesystem facts; recheck before rename |
| Isolation and material realization (all I2 keys) | I2→I3-I5 | Keep transaction separate, carry closed-inventory evidence |
| Traceability and identity (`INIT-L0-004,008`, non-conflicting I3 keys) | I3→I4,I5 | Validate source/request/product linkages, handoff, Git state |
| Repaired provenance/handoff contracts (`INIT-PRC-001`, `INIT-PRO-001-008`, `INIT-HND-001-014`, `INIT-HAS-001`) | I3→I4→I5 | Preserve issue #255 semantics: provenance is origin/identity only; handoff is pre-Git and uses disjoint presence/omission dispositions |
| Failure safety and transaction (all I4 keys) | I4→I5 | Phase results, record linkage, promotion gate/outcome, diagnostics |
| Determinism and lifecycle result (`INIT-L0-001,009`, all I5 keys) | I1-I4→I5 | Integrate canonical forms, stage order, vocabulary, equivalence evidence |

## Specification-repair impact

Issue #255 repaired the prior provenance/handoff authority conflicts. The repair did
not change requirement identities, ownership assignments, or the B0→I1→I2→I3→I4→I5
dependency order. This impact review reaffirms those structures against the repaired
accepted semantics. Implementation remains unauthorized because the plan is still
candidate and requires separate governed acceptance.

## Coverage and DAG checks

- B0 covers all 34 accepted specs and 291 unique composite keys
- Sole ownership unchanged from Patch 1: B0 owns `INIT-L0-007`; I1-I5 contain the remaining 290 keys; no key reassigned
- Every sole-owner set carried to consumers; provenance conflict carried through I3/I4/I5
- Edges: B0→I1→I2→I3→I4→I5; every edge increases rank → acyclic
- Six candidate future-extension specs excluded: `product.platform-profile-interface`, `product.platform-profile-execution`, `product.dry-run-validation`, `product.platform-integrated-initialization`, `product.recovery-and-cleanup`, `product.resume-from-staging`

## Plan-wide exclusions

No product source, tests, schemas, templates, generated output, or specification changes; no implementation or implementation-issue creation; no plan acceptance; no dry-run/platform/remote/named-ref/SHA-256/retry/resume/recovery/migration/overwrite/cross-device; no conformance claim from existing behavior. Future-extension specs remain candidate and deferred.
