# Authority, scope, and specification map

Status: accepted; planning-authoritative; non-normative with respect to product semantics

## Authority and basis

Maps accepted requirements to planning responsibilities; does not restate, narrow, extend, or replace requirements. Acceptance authorizes only governed successor work under the plan's gates; it does not itself mutate product artifacts.

| Planning fact | Value |
| --- | --- |
| Planning basis | `d3cf252dd6022aa19bd52ee335b1ef114ccfae1b` |
| Governing issue | #253 planning cycle; #255 and #257 accepted specification repairs with plan impact review; #259 plan synchronization |
| Normative authority | Accepted `initial-bounded-workflow` specs registered in `product/specs/product/manifest.json` |
| Repository planning authority | `repo.implementation-plan`, `repo.development-workflow` |

All 34 accepted specs and 291 normative requirements are mapped below by composite key `<spec_id>::<requirement_id>`. Bare IDs `INIT-FIN-001` through `INIT-FIN-008` appear in both `product.framework-installation` and `product.full-initialization`; composite keys disambiguate them.

## Planning responsibility model

| Code | Responsibility |
| --- | --- |
| `B0` | Requirement-by-requirement conformance baseline (applies to every composite key) |
| `I1` | Request intake, identity handling, source resolution, execution-profile rejection, destination preflight |
| `I2` | Transaction establishment, closed-inventory material realization, direction evidence, workspace generation |
| `I3` | Provenance, handoff, deterministic local Git identity, repository-state assembly |
| `I4` | Validation phases/reports, promotion gating, atomic promotion, diagnostic preservation, post-promotion finalization |
| `I5` | End-to-end lifecycle orchestration, terminal outcomes, whole-workflow conformance |
| `X` | Cross-increment carriage: re-verify at each consumer boundary (supplements sole owner) |

Patch 2 preserves every composite assignment; spec dependencies are entry constraints, not optional sequencing.

## Requirement-to-responsibility map

Ranges are inclusive within the named spec. Non-contiguous/suffixed IDs listed explicitly. The accepted spec is the sole source of each requirement's meaning.

| Level | Accepted specification | Composite requirement IDs | Owner | Cross-increment (X) |
| --- | --- | --- | --- | --- |
| 0 | `product.initializer-level-0` | `INIT-L0-001` | I5 | Determinism and canonical equivalence |
| 0 | `product.initializer-level-0` | `INIT-L0-002` | I2 | Workspace isolation |
| 0 | `product.initializer-level-0` | `INIT-L0-003` | I2 | Layer separation |
| 0 | `product.initializer-level-0` | `INIT-L0-004` | I3 | Source/revision traceability |
| 0 | `product.initializer-level-0` | `INIT-L0-005` | I4 | Failure safety |
| 0 | `product.initializer-level-0` | `INIT-L0-006` | I1 | Request authority constrains downstream |
| 0 | `product.initializer-level-0` | `INIT-L0-007` | B0 | Accepted specs control all increments |
| 0 | `product.initializer-level-0` | `INIT-L0-008` | I3 | Initializer identity propagation |
| 0 | `product.initializer-level-0` | `INIT-L0-009` | I5 | Lifecycle-result vocabulary |
| 1 | `product.initialization-request` | `INIT-REQ-001-015` | I1 | Authority, identity, downstream values |
| 1 | `product.initialization-request` | `INIT-REQ-016` | I2 | Evidence validation |
| 1 | `product.source-revision-identity` | `INIT-SRC-001-005, 007-008` | I1 | Source-consuming increments |
| 1 | `product.source-revision-identity` | `INIT-SRC-006` | I2 | Source-type + validation |
| 1 | `product.staging-state` | `INIT-STA-001-013` | I4 | All lifecycle stages |
| 1 | `product.material-classification` | `INIT-MAT-001-003` | I2 | Source, inventory, handoff |
| 1 | `product.destination` | `INIT-DST-001-002` | I1 | Pre-rename absence gate |
| 1 | `product.destination` | `INIT-DST-003` | I4 | Staged content + completion |
| 1 | `product.staging-workspace` | `INIT-STG-001-004` | I2 | Digest + promotion |
| 1 | `product.staging-workspace` | `INIT-STG-005` | I4 | Failure reporting |
| 1 | `product.local-git-repository` | `INIT-GIT-001-005` | I3 | Content determinism |
| 1 | `product.execution-profile` | `INIT-PRF-001-004` | I5 | I1 rejection before mutation |
| 1 | `product.product-identity` | `INIT-PID-001-003, 005-007` | I1 | Product-identified paths/records |
| 1 | `product.product-identity` | `INIT-PID-004` | I2 | I1 validation + I4 output |
| 1 | `product.provenance-record` | `INIT-PRO-001-008` | I3 | Request/source capture, output, validation |
| 1 | `product.handoff-manifest` | `INIT-HND-001-014` | I3 | Inventory/material + final validation |
| 1 | `product.execution-report` | `INIT-RPT-001-004, 004a, 004b, 005-012` | I4 | Stage status + terminal outcomes |
| 1 | `product.content-equivalence` | `INIT-EQV-001-015` | I5 | Canonicalization across all boundaries |
| 1 | `product.git-bootstrap-profile` | `INIT-BPF-001-005` | I3 | Git validation |
| 1 | `product.material-manifest` | `INIT-MMF-001-002, 004-011` | I1 | I2 install + I4 inventory validation |
| 1 | `product.material-manifest` | `INIT-MMF-003` | I2 | Source schema + generated output |
| 1 | `product.git-object-identity` | `INIT-OID-001-008, 010` | I1 | Source/object identity carriers |
| 1 | `product.git-object-identity` | `INIT-OID-009` | I3 | Git-state validation |
| 1 | `product.validation-profile` | `INIT-VP-001-007` | I4 | Check inputs + promotion gate |
| 1 | `product.validation-report` | `INIT-VR-001-016` | I4 | Request/digest linkage, state, promotion |
| 1 | `product.generated-repository` | `INIT-GRL-001-019, 022-023` | I2 | Provenance, determinism, handoff, Git |
| 1 | `product.generated-repository` | `INIT-GRL-020-021` | I3 | I2 inventory + I4 validation |
| 1 | `product.initializer-output-inventory-v1` | `INV-V1-001-015` | I2 | Six producers + I4 Git validation |
| 1 | `product.lifecycle-stages` | `INIT-LCS-001-012` | I5 | Stage identity, order, gates, outcomes |
| 2 | `product.destination-preflight` | `INIT-DPF-001-002` | I1 | Staging placement + promotion |
| 2 | `product.execution-orchestration` | `INIT-EOR-001-002` | I5 | All required stages + failure boundaries |
| 2 | `product.foundation-seeding` | `INIT-FSD-001-021` | I2 | Identity, inventory, evidence, output |
| 2 | `product.framework-installation` | `INIT-FIN-001-008` | I2 | Source resolution, closed-inventory installation, byte/mode fidelity, validation |
| 2 | `product.handoff-assembly` | `INIT-HAS-001` | I3 | Pre-Git handoff classification, provenance path, next governed action |
| 2 | `product.local-git-initialization` | `INIT-LGI-001-002` | I3 | Staged content + repository validation |
| 2 | `product.provenance-recording` | `INIT-PRC-001` | I3 | Initializer/product/source/request identity and initialization timestamp capture |
| 2 | `product.repository-validation` | `INIT-RVA-001-005` | I4 | Producers, report finalization, promotion |
| 2 | `product.request-intake` | `INIT-INT-001-002` | I1 | Rejection + downstream models |
| 2 | `product.source-material-resolution` | `INIT-SMR-001-006` | I1 | I2 install + I4 source/material checks |
| 2 | `product.transactional-staging` | `INIT-TST-001-007` | I4 | I2 staging, finalization, outcomes |
| 3 | `product.full-initialization` | `INIT-FIN-001-011` | I5 | All bounded stages, rejection, gates, outcomes |

`product.framework-installation::INIT-FIN-001-008` and `product.full-initialization::INIT-FIN-001-011` are distinct composite-key sets despite shared bare prefix.

## Existing implementation and test evidence

Accepted specifications are authority. Source, tests, schemas, templates, generated output, and prior behavior are evidence only and cannot fill a missing requirement or change its meaning. Evidence includes `product/scripts/repo-spec-init`, modules under `product/scripts/initializer/`, and suites under `product/scripts/initializer/tests/`.

`B0` shall assign one future baseline classification per composite key:

| Classification | Meaning |
| --- | --- |
| `preserve` | Accepted behavior and protecting tests already conform |
| `repair` | Relevant path exists but bounded conformance defect or missing verification |
| `replace` | Existing approach cannot conform safely within bounded repair |
| `implement` | No maintained evidence satisfies the requirement |

No composite key is classified here. Lack of correspondence records and a requirement-keyed audit prevent blanket conformance conclusions.

## Specification-impact review

Issues #255 and #257 repaired the accepted provenance producer/record conflict,
pre-Git handoff completion-state conflict, handoff disposition conflict, and
classification-array ordering gap. Requirement identities,
accepted-spec count (34), and total normative-requirement count (291) are unchanged.
The existing B0/I1-I5 ownership map therefore remains valid without reassignment.
Affected I3/I4/I5 descriptions and gates are reaffirmed against the repaired semantics.
Issue #261 accepted the synchronized plan after current-authority revalidation; future
material specification changes still invalidate affected mapping until governed impact review.

## Scope

Single standard bounded local initialization workflow: JSON request intake; exact SHA-1 commit in already-local source; absent destination preflight; same-filesystem isolated staging; closed-inventory framework/foundation realization; provenance/handoff assembly; deterministic local Git; ordered validation and report finalization; atomic promotion; terminal outcomes. Includes requirement-level baseline, increment/gate/validation planning for every composite key.

## Exclusions

Six candidate future-extension specs excluded (no implementation authority):

| Level | Spec | Capability |
| --- | --- | --- |
| 1 | `product.platform-profile-interface` | Platform-profile interface |
| 2 | `product.platform-profile-execution` | Platform-profile execution |
| 3 | `product.dry-run-validation` | Dry-run workflow |
| 3 | `product.platform-integrated-initialization` | Hosting/platform-integrated workflow |
| 3 | `product.recovery-and-cleanup` | Generalized recovery/cleanup |
| 3 | `product.resume-from-staging` | Resume from preserved staging |

Also excluded from the planned V1 product scope: remote retrieval, named-reference resolution, SHA-256 Git, retry/resume, migration, overwrite, cross-device promotion, release, and any conformance claim without B0 evidence. This accepted plan does not itself perform product source/test/schema/spec mutation or create successor governing issues; each B0/I1-I5 increment proceeds only through its own governed work and predecessor gates.

## Coverage verification

| Level | Accepted specs | Requirements mapped |
| --- | ---: | ---: |
| 0 | 1 | 9 |
| 1 | 21 | 214 |
| 2 | 11 | 57 |
| 3 | 1 | 11 |
| **Total** | **34** | **291** |

- Accepted manifest entries represented: 34/34
- Normative requirements represented by composite key: 291/291
- Unique composite keys: 291; omitted: 0; duplicates: 0
- Unique bare IDs: 283 (8 intentional INIT-FIN collisions under two specs)
- Candidate future-extension entries: 6/6 excluded; implementation-authorized: 0

Any later accepted specification change invalidates affected mapping until governed impact review.
