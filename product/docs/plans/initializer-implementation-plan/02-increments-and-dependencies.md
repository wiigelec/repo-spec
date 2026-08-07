# Implementation increments and dependencies

Status: candidate; non-authorizing

## Authority boundary

This planning chunk is non-normative with respect to product semantics. It
sequences future conformance and implementation work from the exact composite
requirement ownership established by Patch 1; it does not reinterpret an
accepted requirement, accept this candidate plan, or authorize implementation.

Composite keys use the form `<spec_id>::<requirement_id>`. Inclusive ranges are
expanded only within the named specification. Thus
`product.framework-installation::INIT-FIN-001-008` and
`product.full-initialization::INIT-FIN-001-011` are distinct sets. Every set
below is also assigned to `B0`; the listed `I1` through `I5` owner is the sole
implementation owner from Patch 1 when one is listed. The sole planning owner
of `product.initializer-level-0::INIT-L0-007` is `B0`. Cross-increment carriage
supplements rather than changes that ownership.

The accepted specifications remain the sole product authority. Source, tests,
schemas, templates, generated output, and prior behavior may be inspected in
`B0` only as evidence for `preserve`, `repair`, `replace`, or `implement`.

## Bounded implementation DAG

The implementation dependency graph is the single forward chain:

`B0 -> I1 -> I2 -> I3 -> I4 -> I5`

| Edge | Required evidence flow |
| --- | --- |
| `B0 -> I1` | Requirement-keyed evidence classifications bound all later work to accepted semantics and prevent prior behavior from becoming authority. |
| `I1 -> I2` | Validated request, canonical identities, resolved local source/material inputs, rejected unsupported modes, and absent same-filesystem destination preflight are prerequisites for staging or material realization. |
| `I2 -> I3` | The isolated `repository/` candidate, complete producer-specific inventory evidence, content digest inputs, and generated foundations must exist before provenance, handoff, or deterministic Git state can be assembled. |
| `I3 -> I4` | Complete provenance and handoff records and deterministic Git state are required validation inputs. This edge is blocked by the provenance conflict described below. |
| `I4 -> I5` | Requirement-level validation, mutually consistent finalized transaction records, and promotion/finalization outcomes are required before end-to-end orchestration can claim any terminal outcome. This edge inherits the provenance blocker. |

Accepted specification dependencies are authority entry constraints, and all
34 controlling specifications are accepted at this planning basis. A
dependency on a contract owned by a later increment does not create a reverse
implementation edge when an earlier increment only consumes the already
accepted static contract. For example, `I1` may validate material-manifest keys
against the accepted output-inventory contract before `I2` realizes output,
and `I2` may realize its producer subsets from the accepted inventory before
`I3` realizes provenance and handoff entries. Dependencies whose producers and
consumers share an increment are resolved internally in accepted lifecycle
order and create no inter-increment edge.

Assign ranks `0` through `5` to `B0`, `I1`, `I2`, `I3`, `I4`, and `I5`. Every
declared edge goes from rank `n` to rank `n + 1`; no edge is self-directed or
points to a lower rank. A directed cycle would require a non-increasing edge,
so this graph is acyclic. The canonical stage predecessor relation carried by
`I5` is also required by `product.lifecycle-stages::INIT-LCS-006` to be
acyclic; `I5` verifies that relation and does not add a competing stage order.

## B0 - Existing-implementation conformance baseline

### Purpose and outcome

Create a requirement-by-requirement evidence baseline before any maintained
product artifact changes. The outcome is one evidence-supported classification
(`preserve`, `repair`, `replace`, or `implement`) for every one of the 291
composite keys, plus an explicit blocked finding wherever accepted authority
does not permit a conforming implementation decision.

### Controlling accepted requirements

`B0` controls baseline classification for the complete Patch 1 set:

| Accepted specification | Composite requirement keys |
| --- | --- |
| `product.initializer-level-0` | `product.initializer-level-0::INIT-L0-001-009` |
| `product.initialization-request` | `product.initialization-request::INIT-REQ-001-016` |
| `product.source-revision-identity` | `product.source-revision-identity::INIT-SRC-001-008` |
| `product.staging-state` | `product.staging-state::INIT-STA-001-013` |
| `product.material-classification` | `product.material-classification::INIT-MAT-001-003` |
| `product.destination` | `product.destination::INIT-DST-001-003` |
| `product.staging-workspace` | `product.staging-workspace::INIT-STG-001-005` |
| `product.local-git-repository` | `product.local-git-repository::INIT-GIT-001-005` |
| `product.execution-profile` | `product.execution-profile::INIT-PRF-001-004` |
| `product.product-identity` | `product.product-identity::INIT-PID-001-007` |
| `product.provenance-record` | `product.provenance-record::INIT-PRO-001-008` |
| `product.handoff-manifest` | `product.handoff-manifest::INIT-HND-001-014` |
| `product.execution-report` | `product.execution-report::INIT-RPT-001-004`, `product.execution-report::INIT-RPT-004a`, `product.execution-report::INIT-RPT-004b`, `product.execution-report::INIT-RPT-005-012` |
| `product.content-equivalence` | `product.content-equivalence::INIT-EQV-001-015` |
| `product.git-bootstrap-profile` | `product.git-bootstrap-profile::INIT-BPF-001-005` |
| `product.material-manifest` | `product.material-manifest::INIT-MMF-001-011` |
| `product.git-object-identity` | `product.git-object-identity::INIT-OID-001-010` |
| `product.validation-profile` | `product.validation-profile::INIT-VP-001-007` |
| `product.validation-report` | `product.validation-report::INIT-VR-001-016` |
| `product.generated-repository` | `product.generated-repository::INIT-GRL-001-023` |
| `product.initializer-output-inventory-v1` | `product.initializer-output-inventory-v1::INV-V1-001-015` |
| `product.lifecycle-stages` | `product.lifecycle-stages::INIT-LCS-001-012` |
| `product.destination-preflight` | `product.destination-preflight::INIT-DPF-001-002` |
| `product.execution-orchestration` | `product.execution-orchestration::INIT-EOR-001-002` |
| `product.foundation-seeding` | `product.foundation-seeding::INIT-FSD-001-021` |
| `product.framework-installation` | `product.framework-installation::INIT-FIN-001-008` |
| `product.handoff-assembly` | `product.handoff-assembly::INIT-HAS-001` |
| `product.local-git-initialization` | `product.local-git-initialization::INIT-LGI-001-002` |
| `product.provenance-recording` | `product.provenance-recording::INIT-PRC-001` |
| `product.repository-validation` | `product.repository-validation::INIT-RVA-001-005` |
| `product.request-intake` | `product.request-intake::INIT-INT-001-002` |
| `product.source-material-resolution` | `product.source-material-resolution::INIT-SMR-001-006` |
| `product.transactional-staging` | `product.transactional-staging::INIT-TST-001-007` |
| `product.full-initialization` | `product.full-initialization::INIT-FIN-001-011` |

Within that complete baseline set, Patch 1 also assigns sole planning ownership
of `product.initializer-level-0::INIT-L0-007` to `B0`. The remaining 290 keys
have sole implementation owners in I1 through I5.

### Predecessors

None in this DAG. Patch 1 at `59fb1af` and its complete mapping are controlling
planning context, not predecessor implementation.

### Entry conditions

- The planning basis remains `d3cf252dd6022aa19bd52ee335b1ef114ccfae1b`, or a governed impact review has reaffirmed the map after later accepted changes.
- All 34 accepted `initial-bounded-workflow` specifications and all 291 mapped composite keys remain registered, structurally valid, and traceable.
- A separately governed successor issue authorizes evidence inspection without treating maintained code or tests as product authority.
- The provenance conflict is recorded as a baseline blocker and is not interpreted.

### Exit conditions and evidence

- A machine-reviewable matrix contains exactly one classification for each of the 291 composite keys and cites the relevant source path, test path, focused result, or explicit absence of evidence.
- Every `preserve` result demonstrates accepted behavior and protecting tests; every `repair` or `replace` result identifies the bounded mismatch; every `implement` result demonstrates the absence of conforming maintained behavior.
- Aggregate counts reconcile to 34 accepted specifications and 291 unique composite keys, including both distinct `INIT-FIN-001-008` sets.
- The three conflicting provenance keys remain visibly blocked; evidence may classify existing behavior against each key but may not select semantics that purport to satisfy the conflicting set.
- No product artifact is changed and no passing historical test is promoted to normative authority.

### Explicit exclusions

- No implementation, test, schema, template, generated-output, or specification mutation.
- No inferred conformance from file presence, historical behavior, or an undifferentiated all-tests-pass result.
- No provenance-field choice, alternate record, omitted-field rule, or extra-field rule.
- No implementation issue derivation or candidate-plan acceptance.

## I1 - Request and preflight

### Purpose and outcome

Produce the validated, canonical, standard-profile request model; exact local
SHA-1 source identity and validated material inputs; and absent-destination,
same-filesystem preflight evidence without destination mutation. Unsupported
authority expansion, profile behavior, source behavior, and destination states
are rejected before staging establishment.

### Controlling accepted requirements

| Accepted specification | Owned composite requirement keys |
| --- | --- |
| `product.initializer-level-0` | `product.initializer-level-0::INIT-L0-006` |
| `product.initialization-request` | `product.initialization-request::INIT-REQ-001-015` |
| `product.source-revision-identity` | `product.source-revision-identity::INIT-SRC-001-005`, `product.source-revision-identity::INIT-SRC-007-008` |
| `product.destination` | `product.destination::INIT-DST-001-002` |
| `product.product-identity` | `product.product-identity::INIT-PID-001-003`, `product.product-identity::INIT-PID-005-007` |
| `product.material-manifest` | `product.material-manifest::INIT-MMF-001-002`, `product.material-manifest::INIT-MMF-004-011` |
| `product.git-object-identity` | `product.git-object-identity::INIT-OID-001-008`, `product.git-object-identity::INIT-OID-010` |
| `product.destination-preflight` | `product.destination-preflight::INIT-DPF-001-002` |
| `product.request-intake` | `product.request-intake::INIT-INT-001-002` |
| `product.source-material-resolution` | `product.source-material-resolution::INIT-SMR-001-006` |

### Predecessors

`B0`.

### Entry conditions

- `B0` exits with classifications and cited evidence for every I1-owned key.
- The candidate plan has later been accepted after all authority blockers are resolved, and a governed I1 issue cites that accepted plan, these accepted specifications, the accepted base, and `B0` evidence.
- The accepted output inventory, product identity, material classification, and Level 0 contracts remain available as static dependency authority.

### Exit conditions and evidence

- Focused positive and negative evidence traces each I1-owned key to request parsing, canonicalization, fingerprint inputs, identity validation, local source resolution, manifest validation, and destination preflight behavior.
- Evidence shows unknown/empty/contradictory inputs and excluded profiles are rejected distinctly, only exact full SHA-1 commit identities and local commit-tree material are consumed, tree-valued material and unsupported source objects are rejected, and no remote or named-reference operation occurs.
- Evidence shows every accepted request value and authority identifier is retained or transformed only as expressly permitted, and the validated model carries exact values needed by I2 through I5.
- Evidence shows existing destinations and inaccessible or cross-device arrangements are rejected before generation and without destination mutation.
- Requirement coverage reconciles exactly to the I1 owner rows above, with all cross-increment outputs handed forward.

### Explicit exclusions

- No staging-root creation, material installation, generated repository output, provenance/handoff/Git creation, validation finalization, promotion, or orchestration.
- No remote retrieval, network access, named-reference resolution, SHA-256 Git support, implicit authority, or non-standard execution profile.
- No platform/hosting behavior, dry run, resume/recovery, migration, destination overwrite/reuse, or cross-device fallback.
- No interpretation of the provenance conflict and no claim that I1 alone authorizes downstream mutation.

## I2 - Transactional and material realization

### Purpose and outcome

Establish the isolated same-filesystem transaction layout and realize the
closed-inventory candidate repository content owned by framework installation,
direction-evidence installation, and workspace seeding. Produce deterministic
content and digest inputs for records, Git, validation, and promotion. I2 owns
staging establishment through the staging-workspace contract; I4 retains the
transactional manager's failure, report-finalization, promotion, and cleanup
requirements exactly as assigned by Patch 1.

### Controlling accepted requirements

| Accepted specification | Owned composite requirement keys |
| --- | --- |
| `product.initializer-level-0` | `product.initializer-level-0::INIT-L0-002-003` |
| `product.initialization-request` | `product.initialization-request::INIT-REQ-016` |
| `product.source-revision-identity` | `product.source-revision-identity::INIT-SRC-006` |
| `product.material-classification` | `product.material-classification::INIT-MAT-001-003` |
| `product.staging-workspace` | `product.staging-workspace::INIT-STG-001-004` |
| `product.product-identity` | `product.product-identity::INIT-PID-004` |
| `product.material-manifest` | `product.material-manifest::INIT-MMF-003` |
| `product.generated-repository` | `product.generated-repository::INIT-GRL-001-019`, `product.generated-repository::INIT-GRL-022-023` |
| `product.initializer-output-inventory-v1` | `product.initializer-output-inventory-v1::INV-V1-001-015` |
| `product.foundation-seeding` | `product.foundation-seeding::INIT-FSD-001-021` |
| `product.framework-installation` | `product.framework-installation::INIT-FIN-001-008` |

### Predecessors

`I1` (and transitively `B0`).

### Entry conditions

- I1 exits with a validated request, resolved source commit and manifest, canonical product/source identities, inventory key coverage, and passing absent/same-filesystem preflight evidence.
- `B0` classifications for every I2-owned key are incorporated into the governed I2 issue without broadening scope.
- The accepted inventory and generated-layout contracts remain unchanged or have received required plan impact review.

### Exit conditions and evidence

- Evidence shows the staging root is empty and same-filesystem, contains only `transaction/` and `repository/`, isolates transaction records from promotable content, and exposes only `repository/` to later promotion.
- Requirement-level tests show every required inventory path has exactly one producer; framework entries resolve one blob or supported symlink each; bytes, modes, substitutions, generated records, direction evidence, positional duplicates, candidate skeletons, Level placeholders, and empty product manifest satisfy their accepted contracts.
- Evidence rejects broad/tree copying, undeclared descendants, overlapping output, development-only and product-instance source content, prohibited/profile paths, unsupported symlinks, and any output not in the closed inventory.
- Deterministic enumeration and serialization evidence produces the repository-only digest input before Git initialization and carries request, source, material, product, and inventory identities into I3 and I4.
- Requirement coverage reconciles exactly to the I2 owner rows above; provenance and handoff fixed inventory entries remain declared but are not falsely claimed as I2-produced.

### Explicit exclusions

- No provenance-record or handoff-manifest assembly and no local Git initialization.
- No repository-validation execution, transaction-record finalization, destination rename, cleanup, or terminal workflow result.
- No recursive source-tree installation, undeclared output, platform/profile output, remote material, inferred product semantics, or accepted generated documents.
- No resume, generalized recovery, migration, overwrite, cross-device promotion, or provenance-conflict interpretation.

## I3 - Repository identity, handoff, and Git

### Purpose and outcome

Complete the staged repository's identity-bearing records and deterministic Git
state: provenance, handoff, generated-record layout, canonical generated object
identity, and the single-root-commit local repository. The complete I3 outcome
cannot currently be authorized or reached because provenance recording lacks
consistent accepted semantics.

### Controlling accepted requirements

| Accepted specification | Owned composite requirement keys |
| --- | --- |
| `product.initializer-level-0` | `product.initializer-level-0::INIT-L0-004`, `product.initializer-level-0::INIT-L0-008` |
| `product.local-git-repository` | `product.local-git-repository::INIT-GIT-001-005` |
| `product.provenance-record` | `product.provenance-record::INIT-PRO-001-008` |
| `product.handoff-manifest` | `product.handoff-manifest::INIT-HND-001-014` |
| `product.git-bootstrap-profile` | `product.git-bootstrap-profile::INIT-BPF-001-005` |
| `product.git-object-identity` | `product.git-object-identity::INIT-OID-009` |
| `product.generated-repository` | `product.generated-repository::INIT-GRL-020-021` |
| `product.handoff-assembly` | `product.handoff-assembly::INIT-HAS-001` |
| `product.local-git-initialization` | `product.local-git-initialization::INIT-LGI-001-002` |
| `product.provenance-recording` | `product.provenance-recording::INIT-PRC-001` |

### Predecessors

`I2` (and transitively `I1` and `B0`).

### Entry conditions

- I2 exits with complete I2-owned staged content, inventory/material disposition evidence, direction/source traceability, and repository digest inputs.
- `B0` classifications for every I3-owned key and the I1/I2 carried identities are available to a governed successor issue.
- **Blocked provenance entry condition:** separate governed specification work has repaired the conflict among `product.provenance-recording::INIT-PRC-001`, `product.provenance-record::INIT-PRO-003`, and `product.provenance-record::INIT-PRO-006`; the repair is accepted, structurally valid, and registered; and the required material-specification plan impact review has revised or explicitly reaffirmed I3 and all affected mappings and gates.
- Until that condition passes, no provenance-dependent I3 implementation issue may be authorized. Unaffected evidence refinement must remain separately bounded and cannot claim the I3 exit outcome.

### Exit conditions and evidence

- After the blocked entry condition is resolved, requirement-level evidence demonstrates the repaired accepted provenance contract without relying on this plan for field semantics.
- Provenance, handoff, and inventory evidence is mutually traceable to the exact request, source revision, product identity, material dispositions, generated paths, initializer version, and accepted next action; closed field sets and deterministic serialization are validated.
- Handoff arrays are disjoint, sorted, regular-file-only, and complete for the accepted dispositions, and the handoff/provenance paths match the generated-layout and inventory contracts.
- Git evidence demonstrates the complete staged content is committed once on `main` using the exact `standard-v1` constants, full SHA-1 generated object identities, no parent/additional references/remotes, and a clean worktree.
- Requirement coverage reconciles exactly to the I3 owner rows above, and the complete content/Git/record evidence package is handed to I4.

### Explicit exclusions

- No guessed provenance fields, omitted required capture, extra field, optional field, alternate artifact, or record split.
- No I4 validation/promotion or I5 orchestration and no claim of complete I3 while the blocker remains.
- No additional commits, tags, remotes, non-`main` branch, variable bootstrap metadata, SHA-256 object support, platform handoff, or successor product behavior.
- No acceptance of this candidate plan or implementation authorization from unaffected I3 preparation alone.

## I4 - Validation and promotion

### Purpose and outcome

Implement ordered Phase 1 and Phase 2 validation, deterministic validation and
execution evidence, mutually consistent report/staging-state finalization,
promotion gating, one atomic same-filesystem rename, diagnostic preservation,
and post-promotion cleanup/finalization behavior. I4 can claim an outcome only
against a complete I3 repository, so authorization is currently blocked by the
provenance conflict.

### Controlling accepted requirements

| Accepted specification | Owned composite requirement keys |
| --- | --- |
| `product.initializer-level-0` | `product.initializer-level-0::INIT-L0-005` |
| `product.staging-state` | `product.staging-state::INIT-STA-001-013` |
| `product.destination` | `product.destination::INIT-DST-003` |
| `product.staging-workspace` | `product.staging-workspace::INIT-STG-005` |
| `product.execution-report` | `product.execution-report::INIT-RPT-001-004`, `product.execution-report::INIT-RPT-004a`, `product.execution-report::INIT-RPT-004b`, `product.execution-report::INIT-RPT-005-012` |
| `product.validation-profile` | `product.validation-profile::INIT-VP-001-007` |
| `product.validation-report` | `product.validation-report::INIT-VR-001-016` |
| `product.repository-validation` | `product.repository-validation::INIT-RVA-001-005` |
| `product.transactional-staging` | `product.transactional-staging::INIT-TST-001-007` |

### Predecessors

`I3` (and transitively `I2`, `I1`, and `B0`).

### Entry conditions

- I3 exits with complete and conforming staged provenance, handoff, generated content, inventory evidence, repository digest, and deterministic Git state.
- Every carried I1-I3 requirement needed by a validation-profile check has requirement-level producer evidence and an expected failure mode.
- **Blocked authorization condition:** the separate accepted provenance repair and required plan impact review have completed, and the repaired I3 exit evidence makes provenance validation unambiguous. Until then, no I4 implementation issue, promotion implementation claim, or I4 completion claim is authorized.

### Exit conditions and evidence

- Evidence executes every stable validation-profile check in phase/order sequence with valid statuses, failure codes, and structured evidence, including input/source, closed inventory, byte/direction/template/record/digest, provenance/handoff, and Git checks.
- Fault-injection evidence covers each ordered report-finalization boundary: in-memory report/state construction and schema/linkage/order validation, durable validation-report write, durable staging-state write, and final dual-record consistency verification. No partial pair permits promotion.
- Requirement-level tests distinguish pre-staging failure, preserved pre-promotion failure, validation failure, report-finalization partial-record failure, promoted success, indeterminate promotion, and promoted-with-finalization-error cleanup failure without misreporting destination ownership.
- Promotion evidence shows an immediate destination-absence check, exactly one same-filesystem atomic rename of `repository/`, no copy/fallback/retry, and success only after post-rename confirmation and caller-result recording; cleanup removes only remaining transaction artifacts on clean success.
- Requirement coverage reconciles exactly to the I4 owner rows above and produces the terminal-boundary evidence consumed by I5.

### Explicit exclusions

- No validation interpretation of unresolved provenance semantics and no bypass of the blocked I3 predecessor.
- No skipped required check, recursive report self-check, promotion with one/mismatched transaction record, success before committed promotion, automatic promotion retry/rollback, or cleanup-failure retry.
- No recursive copy, cross-device fallback, destination overwrite/reuse, arbitrary resume/recovery, migration, or platform operation.
- No end-to-end orchestration completion claim, plan acceptance, or implementation authorization while the blocker remains.

## I5 - End-to-end orchestration

### Purpose and outcome

Compose the accepted standard bounded local workflow in canonical lifecycle
order, enforce every predecessor and safety gate, propagate cross-increment
identity and evidence, halt correctly at every failure boundary, and prove the
four terminal outcomes plus equivalent-input determinism and excluded-behavior
rejection. I5 integration and authorization are blocked until the provenance
repair and affected plan impact review permit I3 and I4 to exit.

### Controlling accepted requirements

| Accepted specification | Owned composite requirement keys |
| --- | --- |
| `product.initializer-level-0` | `product.initializer-level-0::INIT-L0-001`, `product.initializer-level-0::INIT-L0-009` |
| `product.execution-profile` | `product.execution-profile::INIT-PRF-001-004` |
| `product.content-equivalence` | `product.content-equivalence::INIT-EQV-001-015` |
| `product.lifecycle-stages` | `product.lifecycle-stages::INIT-LCS-001-012` |
| `product.execution-orchestration` | `product.execution-orchestration::INIT-EOR-001-002` |
| `product.full-initialization` | `product.full-initialization::INIT-FIN-001-011` |

### Predecessors

`I4` (and transitively `I3`, `I2`, `I1`, and `B0`).

### Entry conditions

- I1 through I4 each exit with complete requirement-level evidence and all cross-increment handoffs below reconcile by composite key.
- The canonical stage vocabulary and predecessor relation remain accepted and acyclic, with only the standard bounded local workflow selected.
- **Blocked authorization condition:** separate accepted provenance repair, plan impact review, unblocked I3 completion, and unblocked I4 completion all exist. Until then, no I5 implementation issue, whole-workflow conformance claim, plan acceptance, or completion claim is authorized.

### Exit conditions and evidence

- End-to-end evidence executes all 13 required bounded-workflow stages in accepted order, enforces each precondition and promotion gate, stops at each injected failure, and never reports success before committed promotion and success finalization.
- Terminal-outcome evidence covers promoted success, pre-promotion failure (including report-finalization failure before either write and after only one durable write), indeterminate promotion, and promoted-with-finalization-error cleanup failure, with mutually consistent caller result, destination state, staging state, execution report, and diagnostic preservation.
- Equivalent canonical requests and equivalent exact local source revisions produce equivalent inventory-defined repository content, records, handoff, and Git topology/metadata, with only the accepted provenance timestamp variability; non-equivalent inputs remain distinguishable.
- Negative end-to-end evidence rejects unsupported profile behavior, named references, remote retrieval, existing destination, platform/hosting operations, arbitrary resume, migration, cross-device promotion, and undeclared output before unauthorized destination mutation.
- A final composite-key coverage report reconciles B0's all-key baseline role, B0's one sole planning-owner key, and the 290 I1-I5 sole implementation-owner keys to all 291 keys; it carries every cross-increment obligation and reports zero omitted or multiply sole-owned keys.

### Explicit exclusions

- No dry-run, platform-integrated, recovery/cleanup workflow extension, resume-from-staging, remote source, named reference, SHA-256 Git, migration, existing-destination behavior, or cross-device promotion.
- No alternate lifecycle, optional omission of a required bounded stage, arbitrary retry/resume, inferred authority, or semantics supplied by orchestration.
- No plan acceptance, implementation issue creation, implementation authorization, release, or whole-workflow completion claim while any authority blocker or predecessor gate remains open.

## Cross-increment carriage

The following handoffs make Patch 1's `X` assignments operational. Each row is
carried in addition to, not instead of, the sole owner above. The consumer must
retain the producer's composite-key evidence and re-verify the stated
postcondition at its own boundary. In this table, "all `In`-owned keys" is an
exact alias for the complete composite-key union in that increment's
controlling-requirements table; it does not abbreviate or expand ownership.
"All non-conflicting I3-owned keys" is that exact I3 union minus only
`product.provenance-recording::INIT-PRC-001`,
`product.provenance-record::INIT-PRO-003`, and
`product.provenance-record::INIT-PRO-006`.

| Carried concern and requirement set | Producer -> consumers | Required carriage |
| --- | --- | --- |
| Accepted-spec authority: `product.initializer-level-0::INIT-L0-007` | `B0 -> I1, I2, I3, I4, I5` | No increment substitutes documents, code, tests, or plan text for accepted product semantics. |
| Request authority and canonical identity: `product.initializer-level-0::INIT-L0-006`; `product.initialization-request::INIT-REQ-001-015`; `product.product-identity::INIT-PID-001-003`, `::INIT-PID-005-007`; `product.request-intake::INIT-INT-001-002` | `I1 -> I2, I3, I4, I5` | Preserve accepted values, authority, order, duplicates, resolved paths, request fingerprint inputs, and rejection decisions. |
| Source/object/material identity: `product.source-revision-identity::INIT-SRC-001-005`, `::INIT-SRC-007-008`; `product.git-object-identity::INIT-OID-001-008`, `::INIT-OID-010`; `product.material-manifest::INIT-MMF-001-002`, `::INIT-MMF-004-011`; `product.source-material-resolution::INIT-SMR-001-006` | `I1 -> I2, I3, I4, I5` | Consume only the exact local SHA-1 commit tree and validated closed material mapping; retain canonical identities in records and evidence. |
| Destination/preflight: `product.destination::INIT-DST-001-002`; `product.destination-preflight::INIT-DPF-001-002` | `I1 -> I2, I4, I5` | Preserve absent-only and same-filesystem facts; recheck absence immediately before I4 rename. |
| Isolation and material realization: `product.initializer-level-0::INIT-L0-002-003`; all I2-owned keys listed above | `I2 -> I3, I4, I5` | Keep transaction content separate, preserve closed inventory/producer/mode/type evidence, and carry deterministic repository content and digest inputs. |
| Traceability and initializer identity: `product.initializer-level-0::INIT-L0-004`, `::INIT-L0-008`; all non-conflicting I3-owned keys listed above | `I3 -> I4, I5` | Validate exact source/request/product/initializer linkages, handoff disposition, and complete deterministic Git state. |
| Provenance conflict: `product.provenance-recording::INIT-PRC-001`; `product.provenance-record::INIT-PRO-003`; `product.provenance-record::INIT-PRO-006` | `I3 -blocked-> I4 -blocked-> I5` | Carry the unresolved blocker without selecting fields or artifacts; reopen only after accepted repair and required plan impact review. |
| Failure safety and transaction evidence: `product.initializer-level-0::INIT-L0-005`; all I4-owned keys listed above | `I4 -> I5` | Preserve phase results, record linkage, promotion gate/outcome, diagnostics, and destination ownership at every terminal boundary. |
| Determinism and lifecycle result: `product.initializer-level-0::INIT-L0-001`, `::INIT-L0-009`; all I5-owned keys listed above | `I1, I2, I3, I4 -> I5` | Integrate canonical forms, stage order, terminal vocabulary, equivalent-input evidence, and rejection evidence without changing producer ownership. |

## Blocked authority path

The accepted conflict is not an implementation choice:

- `product.provenance-recording::INIT-PRC-001` requires capture of material-manifest schema version and entry count and completed bounded-workflow stages and requires writing the provenance record.
- `product.provenance-record::INIT-PRO-003` defines a required field set with no fields for those values.
- `product.provenance-record::INIT-PRO-006` rejects unknown and optional fields.

This plan does not choose omission, extra fields, an alternate record, or any
other semantic resolution. The provenance-dependent portion of I3 is blocked;
therefore complete I3 exit, I4 authorization and exit, and I5 authorization and
exit are blocked. Separate governed specification repair must become accepted,
then the material-change impact review required by `repo.development-workflow`
and `repo.implementation-plan` must revise or explicitly reaffirm every
affected map, increment, edge, gate, and validation claim before affected
implementation may proceed.

## Coverage and DAG checks

- `B0` covers all 34 accepted `initial-bounded-workflow` specifications and all 291 unique composite requirement keys.
- Sole ownership is unchanged from Patch 1: `B0` solely owns `product.initializer-level-0::INIT-L0-007`, and `I1`, `I2`, `I3`, `I4`, and `I5` contain exactly their mapped 290 keys; no key is reassigned here.
- Every sole-owner set is carried to each affected consumer and to I5 integration; the provenance conflict is explicitly carried through I3, I4, and I5.
- The only inter-increment edges are `B0 -> I1 -> I2 -> I3 -> I4 -> I5`; every edge increases rank, so the graph is acyclic.
- Six candidate `future-extension` specifications receive no owner, edge, entry condition, or implementation authority: `product.platform-profile-interface`, `product.platform-profile-execution`, `product.dry-run-validation`, `product.platform-integrated-initialization`, `product.recovery-and-cleanup`, and `product.resume-from-staging`.

## Plan-wide exclusions and status

This candidate plan remains non-authorizing. It excludes product source, tests,
schemas, templates, generated output, and normative specification changes;
implementation and implementation-issue creation; plan acceptance; dry run;
platform or hosting integration; remote retrieval; named-reference resolution;
SHA-256 Git support; arbitrary retry, resume, or generalized recovery;
migration or existing-destination overwrite/reuse; cross-device promotion or
fallback copying; release work; and any claim that existing behavior is
authority. Future-extension specifications remain candidate and deferred.
