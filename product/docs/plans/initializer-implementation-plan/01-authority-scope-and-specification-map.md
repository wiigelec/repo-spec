# Authority, scope, and specification map

Status: candidate; non-authorizing

## Authority and basis

This candidate planning document is non-normative with respect to product
semantics. It maps accepted requirements to future implementation-planning
responsibilities; it does not restate, narrow, extend, or replace those
requirements and does not authorize implementation.

| Planning fact | Value |
| --- | --- |
| Planning basis | `d3cf252dd6022aa19bd52ee335b1ef114ccfae1b` |
| Governing planning issue | GitHub issue `#253`, Patch 1, including the accepted provenance-conflict planning amendment recorded in issue comment `#issuecomment-5222594632` |
| Controlling plan | `product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md` (candidate) |
| Directional predecessors | Accepted `product/docs/overview/INITIALIZER-OVERVIEW.md` and `product/docs/decompositions/INITIALIZER-DECOMPOSITION.md`; neither defines normative product semantics |
| Normative product authority | The accepted `initial-bounded-workflow` specifications registered by `product/specs/product/manifest.json` |
| Repository planning authority | `repo.implementation-plan`, with `repo.development-workflow`, `repo.governing-issue`, and the repository/product specification lifecycle contracts applicable through the manifest |
| Current authority result | Complete registry and requirement mapping, with the unresolved provenance conflict recorded below; affected planning and all implementation remain unauthorized |

The product manifest is the registry boundary. The requirement map below lists
all 34 accepted specifications in that boundary and all 291 of their normative
requirements. A requirement is identified only by the composite key
`<spec_id>::<requirement_id>`. This is required because the bare IDs
`INIT-FIN-001` through `INIT-FIN-008` occur in both
`product.framework-installation` and `product.full-initialization`.

## Planning responsibility model

These labels allocate future planning and evidence work; they are not product
architecture or additional product semantics.

| Code | Bounded planning responsibility |
| --- | --- |
| `B0` | Establish a requirement-by-requirement conformance baseline against existing implementation and tests before changing maintained product artifacts. `B0` applies to every composite requirement key in this document. |
| `I1` | Plan request intake, canonical identity handling, local source resolution, execution-profile rejection, and destination preflight. |
| `I2` | Plan isolated transaction establishment, closed-inventory material realization, direction evidence, and candidate workspace generation. |
| `I3` | Plan provenance, handoff, deterministic local Git identity, and repository-state assembly. |
| `I4` | Plan validation phases and reports, promotion gating, atomic promotion, diagnostic preservation, and post-promotion finalization. |
| `I5` | Plan end-to-end lifecycle orchestration, terminal outcomes, and whole-workflow conformance. |
| `X` | Carry the requirement through every affected increment and verify it again at integration and end-to-end gates; `X` supplements, rather than replaces, the listed owner. |

Patch 2 may refine increment names and dependency edges, but it must preserve
every composite assignment in this map or explicitly update this map through
governed plan work. Dependencies declared by the accepted specifications are
entry constraints for the owning responsibility, not optional sequencing
advice.

## Requirement-to-responsibility map

Ranges below are inclusive within the stated specification and prefix. For
example, `INIT-PID-001-007` represents each of the seven composite keys from
`product.product-identity::INIT-PID-001` through
`product.product-identity::INIT-PID-007`. Non-contiguous and suffixed IDs are
listed explicitly. The accepted specification remains the sole source of each
requirement's meaning.

### Level 0

| Accepted specification | Requirement IDs | Owner | Cross-increment responsibility |
| --- | --- | --- | --- |
| `product.initializer-level-0` | `INIT-L0-001` | `I5` | `X`: determinism and canonical equivalence across all producing and validating increments |
| `product.initializer-level-0` | `INIT-L0-002` | `I2` | `X`: workspace isolation through validation and promotion |
| `product.initializer-level-0` | `INIT-L0-003` | `I2` | `X`: layer separation in generated content, Git-generic behavior, and excluded platform behavior |
| `product.initializer-level-0` | `INIT-L0-004` | `I3` | `X`: source/revision traceability through generation and validation |
| `product.initializer-level-0` | `INIT-L0-005` | `I4` | `X`: failure safety at every lifecycle boundary |
| `product.initializer-level-0` | `INIT-L0-006` | `I1` | `X`: explicit request authority constrains every downstream stage |
| `product.initializer-level-0` | `INIT-L0-007` | `B0` | `X`: accepted specifications, not documents or existing behavior, control all increments |
| `product.initializer-level-0` | `INIT-L0-008` | `I3` | `X`: initializer identity/version propagation and verification |
| `product.initializer-level-0` | `INIT-L0-009` | `I5` | `X`: lifecycle-result vocabulary across state, reports, and caller outcomes |

### Level 1

| Accepted specification | Requirement IDs | Owner | Cross-increment responsibility |
| --- | --- | --- | --- |
| `product.initialization-request` | `INIT-REQ-001-015` | `I1` | `X` for authority propagation, canonical request identity, and downstream use of accepted values |
| `product.initialization-request` | `INIT-REQ-016` | `I2` | `X` with `I1` intake and `I4` evidence validation |
| `product.source-revision-identity` | `INIT-SRC-001-005`, `INIT-SRC-007-008` | `I1` | `X` with every source-consuming increment |
| `product.source-revision-identity` | `INIT-SRC-006` | `I2` | `X` with `I1` source-type resolution and `I4` validation |
| `product.staging-state` | `INIT-STA-001-013` | `I4` | `X` across all stages that enter, complete, fail, validate, promote, or finalize |
| `product.material-classification` | `INIT-MAT-001-003` | `I2` | `X` with source selection, inventory validation, and handoff accounting |
| `product.destination` | `INIT-DST-001-002` | `I1` | `X` with the immediate pre-rename absence gate |
| `product.destination` | `INIT-DST-003` | `I4` | `X` with `I2` staged content and `I5` completion evidence |
| `product.staging-workspace` | `INIT-STG-001-004` | `I2` | `X` with digest validation and promotion |
| `product.staging-workspace` | `INIT-STG-005` | `I4` | `X` with lifecycle failure reporting |
| `product.local-git-repository` | `INIT-GIT-001-005` | `I3` | `X` with content determinism and repository validation |
| `product.execution-profile` | `INIT-PRF-001-004` | `I5` | `X` with `I1` rejection before mutation; only the accepted standard workflow is in scope |
| `product.product-identity` | `INIT-PID-001-003`, `INIT-PID-005-007` | `I1` | `X` with all product-identified generated paths and records |
| `product.product-identity` | `INIT-PID-004` | `I2` | `X` with `I1` validation and `I4` output validation |
| `product.provenance-record` | `INIT-PRO-001-008` | `I3` | `X` with request/source capture, deterministic output, and validation |
| `product.handoff-manifest` | `INIT-HND-001-014` | `I3` | `X` with inventory/material disposition and final repository validation |
| `product.execution-report` | `INIT-RPT-001-004`, `INIT-RPT-004a`, `INIT-RPT-004b`, `INIT-RPT-005-012` | `I4` | `X` across lifecycle stage status and all non-clean-success terminal outcomes |
| `product.content-equivalence` | `INIT-EQV-001-015` | `I5` | `X`: canonicalization and equivalence evidence across request, source, content, records, and Git |
| `product.git-bootstrap-profile` | `INIT-BPF-001-005` | `I3` | `X` with deterministic Git validation |
| `product.material-manifest` | `INIT-MMF-001-002`, `INIT-MMF-004-011` | `I1` | `X` with `I2` installation and `I4` inventory/key/type validation |
| `product.material-manifest` | `INIT-MMF-003` | `I2` | `X` with source-schema validation and generated-output validation |
| `product.git-object-identity` | `INIT-OID-001-008`, `INIT-OID-010` | `I1` | `X` with every record or stage carrying source/object identity |
| `product.git-object-identity` | `INIT-OID-009` | `I3` | `X` with Git-state validation |
| `product.validation-profile` | `INIT-VP-001-007` | `I4` | `X` with all producers of check inputs and the promotion gate |
| `product.validation-report` | `INIT-VR-001-016` | `I4` | `X` with request/digest linkage, staging state, failure reporting, and promotion |
| `product.generated-repository` | `INIT-GRL-001-019`, `INIT-GRL-022-023` | `I2` | `X` with material provenance, determinism, handoff, Git, and validation |
| `product.generated-repository` | `INIT-GRL-020-021` | `I3` | `X` with `I2` inventory production and `I4` validation |
| `product.initializer-output-inventory-v1` | `INV-V1-001-015` | `I2` | `X` with all six producers and `I4` closed-inventory/Git validation |
| `product.lifecycle-stages` | `INIT-LCS-001-012` | `I5` | `X`: canonical stage identity, dependency order, failure handling, promotion gate, and terminal outcomes |

### Level 2

| Accepted specification | Requirement IDs | Owner | Cross-increment responsibility |
| --- | --- | --- | --- |
| `product.destination-preflight` | `INIT-DPF-001-002` | `I1` | `X` with staging placement and promotion |
| `product.execution-orchestration` | `INIT-EOR-001-002` | `I5` | `X` across all required stages and failure boundaries |
| `product.foundation-seeding` | `INIT-FSD-001-021` | `I2` | `X` with request/source identity, inventory, deterministic evidence, and output validation |
| `product.framework-installation` | `INIT-FIN-001-008` | `I2` | `X` with source resolution, inventory/material contracts, provenance, and validation |
| `product.handoff-assembly` | `INIT-HAS-001` | `I3` | `X` with material disposition, provenance, Git state, and validation |
| `product.local-git-initialization` | `INIT-LGI-001-002` | `I3` | `X` with complete staged content and repository validation |
| `product.provenance-recording` | `INIT-PRC-001` | `I3` | `X` with request/source/material/stage capture and validation |
| `product.repository-validation` | `INIT-RVA-001-005` | `I4` | `X` with every validated producer, report finalization, and promotion |
| `product.request-intake` | `INIT-INT-001-002` | `I1` | `X` with excluded-behavior rejection and downstream validated models |
| `product.source-material-resolution` | `INIT-SMR-001-006` | `I1` | `X` with `I2` installation and `I4` source/material checks |
| `product.transactional-staging` | `INIT-TST-001-007` | `I4` | `X` with `I2` staging establishment, validation finalization, and `I5` terminal outcomes |

### Level 3

| Accepted specification | Requirement IDs | Owner | Cross-increment responsibility |
| --- | --- | --- | --- |
| `product.full-initialization` | `INIT-FIN-001-011` | `I5` | `X`: integrates every bounded stage, rejection rule, determinism obligation, promotion gate, and terminal outcome |

The `product.framework-installation::INIT-FIN-001-008` row and the
`product.full-initialization::INIT-FIN-001-011` row are distinct composite-key
sets despite their shared bare prefix and numbers.

## Existing implementation and test evidence

Accepted specifications are authority. Existing source, tests, schemas,
templates, generated output, and historical behavior are evidence only and
cannot fill a missing requirement or change its meaning.

Evidence present at the planning basis includes the launcher
`product/scripts/repo-spec-init`, implementation modules and the maintained
inventory under `product/scripts/initializer/`, and the focused suites under
`product/scripts/initializer/tests/`. These source and test files establish
only that predecessor behavior and verification exist until `B0` traces them
to each composite requirement key. Passing tests are not requirement-level
conformance evidence when their expectations predate or conflict with accepted
product authority.

`B0` shall assign one future baseline classification per composite requirement
key, supported by cited implementation and test evidence:

| Classification | Future baseline meaning |
| --- | --- |
| `preserve` | Evidence demonstrates accepted behavior and tests already conform; future work protects that behavior. |
| `repair` | A relevant implementation path exists but evidence demonstrates a bounded conformance defect or missing verification. |
| `replace` | Evidence demonstrates that the existing approach cannot conform safely within a bounded repair. |
| `implement` | No maintained implementation evidence satisfies the requirement, so conforming behavior and verification must be added. |

These are future baseline outcomes, not conclusions of this map. No composite
requirement is classified as `preserve`, `repair`, `replace`, or `implement`
here. Absence of correspondence in accepted specification records and the lack
of a requirement-keyed audit prevent an evidence-based blanket conformance
conclusion.

## Authority gap

One material conflict between accepted requirements remains unresolved:

| Conflicting composite keys | Conflict | Planning effect |
| --- | --- | --- |
| `product.provenance-recording::INIT-PRC-001`; `product.provenance-record::INIT-PRO-003`; `product.provenance-record::INIT-PRO-006` | `INIT-PRC-001` requires the provenance-recording component to capture the material-manifest schema version and entry count and completed bounded-workflow stages and to write the provenance record. The provenance-record contract's closed field set contains no fields for those values, and it rejects unknown fields. | Do not choose an omitted-field, extra-field, or alternate-record implementation in this plan. `I3`, dependent `I4` validation, and `I5` end-to-end planning require a separately governed normative specification resolution before the affected plan sections can become implementation-authorizing. |

This map does not resolve the conflict by interpretation. The complete accepted
set remains represented so the gap is traceable, but plan acceptance and
successor implementation issue derivation are blocked where they depend on the
conflicting provenance requirements.

## Scope

Planning scope is the single standard, bounded, local initialization workflow:
explicit JSON request intake; exact SHA-1 commit identity in an already-local
source repository; absent local destination preflight; same-filesystem isolated
staging; closed-inventory framework and foundation realization; provenance and
handoff assembly; deterministic local Git initialization; ordered validation
and report finalization; atomic promotion; success finalization; and the
accepted terminal failure outcomes. Scope also includes requirement-level
baseline classification, increment allocation, dependency/gate planning, and
validation evidence planning for every composite key above.

This planning scope does not change any accepted requirement. Where a planning
label is broader than one specification, successor increments must cite the
exact composite keys they implement and validate.

## Exclusions and deferred authority

The following manifest entries are candidate `future-extension`
specifications. They are explicitly outside this plan, supply no implementation
authority, and receive no requirement allocation:

| Level | Candidate specification | Excluded capability |
| --- | --- | --- |
| 1 | `product.platform-profile-interface` | Platform-profile interface |
| 2 | `product.platform-profile-execution` | Platform-profile execution |
| 3 | `product.dry-run-validation` | Dry-run workflow |
| 3 | `product.platform-integrated-initialization` | Hosting/platform-integrated workflow |
| 3 | `product.recovery-and-cleanup` | Generalized recovery and cleanup workflow |
| 3 | `product.resume-from-staging` | Resume from preserved staging state |

Also excluded are remote retrieval, named-reference resolution, SHA-256 Git
object support, arbitrary retry or resume, migration, overwrite or reuse of an
existing destination, cross-device promotion or fallback copying, product
source/test/schema/specification mutation in this planning patch, acceptance of
this candidate plan, creation of implementation issues, implementation itself,
release work, and any claim that existing code or tests already conform without
`B0` evidence.

## Coverage verification

| Level | Accepted specifications | Normative requirements mapped |
| --- | ---: | ---: |
| 0 | 1 | 9 |
| 1 | 21 | 214 |
| 2 | 11 | 57 |
| 3 | 1 | 11 |
| **Total** | **34** | **291** |

Coverage checks for this candidate map:

- Accepted manifest entries in capability group `initial-bounded-workflow`:
  `34` of `34` represented.
- Normative requirements in those entries: `291` of `291` represented by
  composite key and assigned to `B0` plus at least one bounded owner.
- Unique composite keys: `291`; omitted composite keys: `0`; duplicate
  composite keys: `0`.
- Unique bare requirement IDs: `283`; the difference is the eight intentional
  `INIT-FIN-001-008` collisions represented under both owning spec IDs.
- Candidate manifest entries in capability group `future-extension`: `6` of
  `6` explicitly excluded; implementation-authorized future-extension entries:
  `0`.

Any later accepted specification change invalidates the affected mapping until
the plan is revised or explicitly reaffirmed under governed impact review.
