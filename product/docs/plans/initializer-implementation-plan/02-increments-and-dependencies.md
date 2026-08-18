# Implementation increments and dependencies

Status: accepted; planning-authoritative; non-normative with respect to product semantics

## Authority boundary

Non-normative with respect to product semantics. Sequences governed conformance and implementation work from the accepted requirement-to-responsibility map and does not reinterpret requirements. Issue #261 accepted this plan. The B0→I1→I2→I3→I4→I5 gates remain the historical execution structure; all six bounded increments have since completed under separate governing issues and maintained evidence. Issue #311 added H1 as a bounded successor consumer/presentation workstream without reassigning historical requirement ownership; issue #313 completed that implementation and issue #318 completed bounded post-H1 conformance correction. Composite keys use `<spec_id>::<requirement_id>`. `product.framework-installation::INIT-FIN-001-008` and `product.full-initialization::INIT-FIN-001-011` are distinct sets. Every set below is also assigned to B0; the listed I1-I5 owner is the sole implementation owner recorded by the accepted requirement-to-responsibility map.

## Bounded implementation DAG

`B0 -> I1 -> I2 -> I3 -> I4 -> I5 -> H1`

Edges: B0→I1 (keyed evidence bounds all work), I1→I2 (validated request/resolved source/preflight needed before staging), I2→I3 (staged content needed before provenance/handoff/Git), I3→I4 (conforming identity/handoff/Git state required before validation), I4→I5 (validated promotion/finalization behavior required before E2E orchestration), I5→H1 (completed whole-workflow evidence is the predecessor for a human-facing entry point that must not alter semantics). Spec dependencies are authority entry constraints. Ranks 0-6 assigned; every edge increases rank so the graph is acyclic.

## B0 - Existing-implementation conformance baseline

Purpose: requirement-by-requirement evidence baseline across all 291 composite keys before maintained artifact changes. Outcome: one supported classification per key plus explicit blocked finding.

Controlling requirements: all 34 accepted specs and all 291 composite keys from the accepted requirement-to-responsibility map. Sole planning owner of `product.initializer-level-0::INIT-L0-007`. Entry: current accepted initial-bounded-workflow specifications are accepted and traceable under the governing plan revision. Exit: machine-reviewable matrix with one classification per key (preserve/repair/replace/implement), cited evidence, and aggregate counts reconciled to 34/291. Exclusions: no implementation/test/schema/spec mutation, no inferred conformance, and no reinterpretation of accepted product semantics.

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

Predecessor: I2. Entry: I2 exit evidence, current accepted provenance/handoff contracts, B0 classifications, accepted plan, governed I3 issue. Exit: evidence for conforming provenance origin/identity fields, pre-Git handoff classification and traceability, closed field sets, deterministic serialization, complete Git state on `main` with full SHA-1 objects, and clean worktree. Exclusions: no invented provenance/handoff fields, no I4/I5 work, no extra commits/tags/remotes/SHA-256, and no implementation work before plan acceptance.

## I4 - Validation and promotion

Purpose: ordered Phase 1/Phase 2 validation, deterministic report/state finalization, promotion gating, atomic same-filesystem rename, diagnostic preservation, cleanup.

Controlling requirements (I4-owned): `product.initializer-level-0::INIT-L0-005`, `product.staging-state::INIT-STA-001-013`, `product.destination::INIT-DST-003`, `product.staging-workspace::INIT-STG-005`, `product.execution-report::INIT-RPT-001-004,004a,004b,005-012`, `product.validation-profile::INIT-VP-001-007`, `product.validation-report::INIT-VR-001-016`, `product.repository-validation::INIT-RVA-001-005`, `product.transactional-staging::INIT-TST-001-007`.

Predecessor: I3. Entry: I3 complete with conforming staged content/Git/provenance/handoff evidence under the accepted plan. Exit: ordered validation checks with status/failure codes, fault-injection at every report-finalization boundary (no partial pair permits promotion), promotion evidence for immediate absence recheck + single rename + post-rename stat, terminal-boundary evidence for pre-promotion failure/promoted success/indeterminate promotion/promoted-with-finalization-error. Exclusions: no reinterpretation of accepted provenance/handoff semantics, no copy/fallback/retry, and no I5 completion before I4 exit.

## I5 - End-to-end orchestration

Purpose: compose standard bounded workflow in canonical lifecycle order, enforce all predecessors and gates, prove four terminal outcomes plus determinism and rejection.

Controlling requirements (I5-owned): `product.initializer-level-0::INIT-L0-001,009`, `product.execution-profile::INIT-PRF-001-004`, `product.content-equivalence::INIT-EQV-001-015`, `product.lifecycle-stages::INIT-LCS-001-012`, `product.execution-orchestration::INIT-EOR-001-002`, `product.full-initialization::INIT-FIN-001-011`.

Predecessor: I4. Entry: I1-I4 exits with complete evidence under the accepted plan. Exit: E2E evidence for 13 accepted stages in order, each precondition enforced; terminal-outcome evidence for promoted success, pre-promotion failure, indeterminate promotion, promoted-with-finalization-error; equivalent inputs produce equivalent output (provenance timestamp excepted); negative E2E for unsupported profile/refs/remote/destination/platform/resume/migration/cross-device; final composite-key coverage report reconciles all 291 keys. Exclusions: no dry-run/platform/recovery/resume/remote/SHA-256/migration/overwrite.

## H1 - Human-facing initialization workflow

Purpose: make the accepted bounded local initializer usable through one obvious public
entry point while preserving the canonical JSON request and all accepted workflow
semantics. The normal user model is human + AI agent: the agent helps author and review
`request.json`; the initializer consumes that reviewed JSON unchanged through canonical
request intake.

Controlling accepted product specifications: `product.initializer-level-0`,
`product.initialization-request`, `product.source-revision-identity`,
`product.execution-profile`, `product.product-identity`, `product.execution-report`,
`product.lifecycle-stages`, `product.execution-orchestration`,
`product.request-intake`, `product.full-initialization`.

Predecessor: completed I5 evidence and accepted H1 planning amendment. Entry: H1 is
selected by a separate Product-artifact implementation governing issue; all listed
controlling product specifications remain accepted and manifest-registered; no material
specification change has invalidated the H1 mapping.

Implementation scope: reconcile the public initializer command surface with supported
behavior; provide one public `repo-spec-init --request <file>` entry point over the accepted
full-initialization workflow; provide human-readable progress and terminal
success/failure presentation that does not replace or reinterpret canonical machine
records; rewrite root README/getting-started material around AI-assisted construction
and human review of the canonical JSON request; add directly relevant regression
coverage.

Exit: public help advertises only supported normal-user operations; `repo-spec-init --request <file>` invokes the accepted full workflow without lifecycle reordering or request
synthesis; terminal presentation agrees with accepted terminal outcomes; documentation
shows the human + AI-agent request-authoring/review boundary accurately; relevant tests
and repository/product/aggregate validation pass.

Exclusions: no interactive prompting; no CLI synthesis or defaulting of authority-bearing
request fields; no automatic source/revision or product-ID inference; no `status`; no
dry-run; no remote/platform integration; no recovery/resume; no new capability; no
product-specification semantic change; no reassignment of the 291 B0/I1-I5 requirement
owners.

## VA1 - Production validation ownership correction

Purpose: authorize one bounded successor implementation stage that separates genuinely
cross-domain validation mechanics and shared context from repository-domain policy
implementation while preserving all accepted validation behavior and the established
repository/product validation entry points.

Controlling accepted product specifications: `product.initializer-output-inventory-v1`,
`product.framework-installation`, `product.repository-validation`,
`product.executable-reference-closure`.

Predecessor: issue #350 Patch 1 portable-runtime authority correction. Entry: a separate
Product-artifact implementation governing issue selects stable workstream `VA1`, cites
the exact three-spec controlling set above, starts from the then-current accepted default
branch, and confirms the accepted validation-system desired-state architecture remains
directional and subordinate to normative specifications.

Implementation scope: extract only mechanics/context/helpers that are genuinely shared by
repository and product validation into function-named shared modules; keep repository
policy repository-owned and product policy product-owned; update portable runtime
inventory only if the resulting maintained shared module set changes; preserve public
validation entry points, phase ordering, diagnostics, exit behavior, and accepted product
validation semantics.

Exit: repository and product production validators no longer require product validation
to import repository-domain policy implementation merely to obtain shared mechanics;
dependency-direction checks demonstrate the intended ownership boundary; portable
runtime inventory remains closed over every maintained runtime dependency; focused,
aggregate, and applicable self-test validation passes with no accepted semantic change.

Exclusions: no new validation rule, no weakened requirement, no lifecycle or report
semantic change, no broad validator rewrite, no self-test ownership consolidation
(which is reserved for issue #350 Patch 3 authority), no H2 work, and no reassignment of
historical B0/I1-I5/H1 requirement ownership.

## VA2 - Validation self-test ownership correction

Purpose: authorize bounded self-test ownership consolidation without changing production validation semantics. Controlling accepted product specifications: `product.repository-validation`, `product.validation-test-surface`, and `product.validation-test-orchestration`.

Predecessor/entry: issue #350 Patch 2 plus the issue-#491 impact review; a separate Product-artifact implementation issue must select `VA2`, cite exactly `product.repository-validation`, `product.validation-test-surface`, and `product.validation-test-orchestration`, use the then-current accepted base, and keep VA1 and VS1 implementation separate.

Scope/exit: consolidate duplicate or catch-all product validation self-tests into function-owned focused coverage, retain genuinely integrative cases, remove literal duplicates, preserve dependency-direction and every distinct accepted invariant, and require product/aggregate validation plus the complete product validation self-test runner to pass.

Exclusions: no production-validator changes, new/weakened semantics, loss of distinct invariant coverage, VA1 extraction, initializer/H2 work, general cleanup, or historical B0/I1-I5/H1 ownership reassignment.

## Cross-increment carriage

| Concern | Producer→consumers | Required carriage |
| --- | --- | --- |
| Accepted spec authority (`INIT-L0-007`) | B0→I1-I5 | No increment substitutes documents/code/tests/plan for accepted specs |
| Request authority and identity (`INIT-L0-006`, `INIT-REQ-001-015`, `INIT-PID-001-003,005-007`, `INIT-INT-001-002`) | I1→I2-I5 | Preserve accepted values, order, fingerprints, rejection decisions |
| Source/object/material identity (`INIT-SRC-001-005,007-008`, `INIT-OID-001-008,010`, `INIT-MMF-001-002,004-011`, `INIT-SMR-001-006`) | I1→I2-I5 | Consume only exact local SHA-1 commit tree and validated mapping |
| Destination/preflight (`INIT-DST-001-002`, `INIT-DPF-001-002`) | I1→I2,I4,I5 | Preserve absence/same-filesystem facts; recheck before rename |
| Isolation and material realization (all I2 keys) | I2→I3-I5 | Keep transaction separate, carry closed-inventory evidence |
| Traceability and identity (`INIT-L0-004,008`, I3-owned identity keys) | I3→I4,I5 | Validate source/request/product linkages, handoff, and Git state |
| Repaired provenance/handoff contracts (`INIT-PRC-001`, `INIT-PRO-001-008`, `INIT-HND-001-014`, `INIT-HAS-001`) | I3→I4→I5 | Preserve issues #255/#257 semantics: provenance is origin/identity only; handoff is pre-Git, uses disjoint presence/omission classifications, and orders all six classification arrays deterministically |
| Failure safety and transaction (all I4 keys) | I4→I5 | Phase results, record linkage, promotion gate/outcome, diagnostics |
| Determinism and lifecycle result (`INIT-L0-001,009`, all I5 keys) | I1-I4→I5 | Integrate canonical forms, stage order, vocabulary, equivalence evidence |
| Human-facing init presentation | I1-I5→H1 | Re-present the accepted JSON request, standard local workflow, and terminal outcomes without new defaults, lifecycle semantics, or machine-record authority |

## Specification-repair impact

Issues #255 and #257 repaired the prior provenance/handoff authority conflicts and
classification-ordering gap. Those repairs did not change requirement identities,
ownership assignments, or the B0→I1→I2→I3→I4→I5 dependency order. This impact review reaffirms those structures against the repaired
accepted semantics. Issue #261 accepted the plan after current-authority revalidation.
B0 through I5 are completed historical increments. Maintained I5 exit evidence records
zero blockers. Issue #311 authorized the H1 planning amendment as the sole bounded
successor scope; issue #313 completed H1 under that authority, and issue #318 completed bounded post-H1 correction. H1 consumes existing accepted authority and does not alter the completed
B0/I1-I5 requirement ownership or evidence.

## Coverage and DAG checks

- B0 covers all 34 accepted specs and 291 unique composite keys
- Sole ownership recorded by the accepted requirement-to-responsibility map: B0 owns `INIT-L0-007`; I1-I5 contain the remaining 290 keys; no key reassigned
- Every sole-owner set carried to consumers; repaired provenance/handoff semantics carried through I3/I4/I5 without blocker state
- Edges: B0→I1→I2→I3→I4→I5→H1; every edge increases rank → acyclic
- Six candidate future-extension specs excluded: `product.platform-profile-interface`, `product.platform-profile-execution`, `product.dry-run-validation`, `product.platform-integrated-initialization`, `product.recovery-and-cleanup`, `product.resume-from-staging`

## Plan-wide exclusions

The plan itself performs no product source, tests, schemas, templates, generated output, or specification mutation and creates no implementation governing issue. No dry-run/platform/remote/named-ref/SHA-256/retry/resume/recovery/migration/overwrite/cross-device capability is authorized, and no conformance claim may be inferred from existing behavior. Future-extension specs remain candidate and deferred. B0/I1-I5 and H1 are completed historical work. H1 was the bounded successor authorized by the #311 planning amendment and was implemented under issue #313. Issue #350 adds VA1 as a separate bounded successor authority for production-validation ownership correction and VA2 as a separate bounded successor authority for validation self-test ownership correction. Neither VA1 nor VA2 reopens or reassigns historical requirement ownership, and no other successor scope is implied.
