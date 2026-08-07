# Validation, gates, and completion

Status: candidate; non-authorizing

## Transition gates

Each gate passes before successor increment work may be authorized. Evidence is requirement-level, keyed to Patch 1 composite ownership.

### B0 -> I1 gate
| Requirement | Evidence |
| --- | --- |
| Every I1-owned key has one baseline classification (preserve/repair/replace/implement) with cited source/test evidence | Machine-readable matrix; counts reconcile to ownership for `product.request-intake`, `product.source-revision-identity`, `product.destination`, `product.product-identity`, `product.material-manifest`, `product.git-object-identity`, `product.destination-preflight`, `product.request-intake`, `product.source-material-resolution` |
| No I1 key classified by file presence or undifferentiated tests alone | Each entry cites specific behavior/assertion; absence citations explicit |
| Three provenance-conflict keys flagged blocked, not classified | Matrix blocker flag confirmed |

### I1 -> I2 gate
| Requirement | Evidence |
| --- | --- |
| I1-owned intake/identity/source/manifest/preflight evidence at requirement level | Positive/negative test per owned spec; aggregate counts reconcile to Patch 1 I1 rows |
| Validated request, resolved source, closed material-key mapping available | Canonical fingerprint, full SHA-1 commit identity, manifest |
| Destination preflight passed: absent and same-filesystem | Preflight evidence without mutation |
| Unsupported authority/profile/source/destination states rejected | Distinct rejection per excluded case |
| B0 classifications for I2 keys documented in governing I2 issue | Issue citation + ownership map |

### I2 -> I3 gate
| Requirement | Evidence |
| --- | --- |
| I2-owned staging/material/foundation/framework/inventory/digest evidence at requirement level | Positive/negative per I2-owned key; reconcile to Patch 1 I2 rows |
| Staging: only `transaction/` and `repository/`, no undeclared/broad-tree/excluded paths | Path inventory; negative evidence for forbidden patterns |
| Deterministic repository-only digest available for I3 | Digest artifact; producer citations per inventory entry |
| I1-carried request/source/identity/manifest values preserved | Value comparison against I1 validated model |

### I3 -> I4 gate (blocked)
Inherits blocked entry condition from Patch 2: separate governed spec repair of `product.provenance-recording::INIT-PRC-001` / `product.provenance-record::INIT-PRO-003,006` plus required plan impact review. Until met, no I3 exit or I4 authorization.

| Requirement | Evidence |
| --- | --- |
| Blocked provenance entry condition resolved | Accepted repair, plan impact review record |
| All I3-owned keys (excluding three conflicting) have requirement-level evidence | Composite-key reconciliation to Patch 1 I3 rows minus three blocked |
| Unblocked I3: provenance/handoff/Git consistent with repaired contract, I2 content, I1 identities | Traceability across request/source/product/material/content/records/Git |

### I4 -> I5 gate (blocked)
Inherits I3->I4 blockage.

| Requirement | Evidence |
| --- | --- |
| I4-owned validation/promotion evidence at requirement level | Composite-key reconciliation to Patch 1 I4 rows |
| Promotion: destination rechecked, single rename, post-rename stat commitment | Fault-injection at each boundary |
| Terminal boundaries: pre-promotion failure, promoted success, indeterminate promotion, promoted-with-finalization-error | Outcome-class evidence; consistent caller result/destination/staging/report/diagnostics |
| I3-carried provenance/handoff/Git validated as owned input | Validation-profile check results; blocked until I3 exit |

## Validation strategy

Every Patch 1 composite key produces observable positive/negative evidence. B0 classifies; I1-I5 produce focused evidence.

Evidence types: positive (required behavior with accepted inputs), negative (rejection of non-conforming inputs), equivalence (identical output for equivalent inputs), fault-injection (correct behavior under system faults).

Component validation per increment: request intake, source resolution, material realization, staging, provenance/handoff, Git, validation/promotion — each validates its owned keys before signaling readiness.

Cross-component validation: request values preserved through consumers, source/material identities consistent from resolution through Git record, staging-state transitions match execution-report outcomes, provenance/handoff paths match generated layout, Git objects match pre-Git digest.

End-to-end (I5): promoted success, pre-promotion failure (including report-finalization partial-write), indeterminate promotion, promoted-with-finalization-error, deterministic equivalent-input behavior, rejection of unsupported V1 (named refs, remotes, existing destination, platform, resume, migration, cross-device, undeclared output).

Evidence artifacts: B0 classification matrix, requirement-level test suite, validation report, staging state, execution report, provenance record (blocked), handoff manifest, Git repository, E2E outcome evidence.

## Completion and successor work

### Candidate plan completion
- Patch 1: 34/34 accepted specs and 291/291 requirements mapped by composite key; provenance conflict recorded; 6/6 future-extension specs excluded
- Patch 2: acyclic B0→I1→I2→I3→I4→I5 DAG; each increment has controlling specs, requirements, predecessors, entry/exit conditions, exclusions; provenance blocker propagated
- Patch 3: requirement-level transition gates; validation strategy (component/cross-component/E2E); terminal outcomes/determinism/rejection evidence; risk/decision register substantive

### Plan acceptance (blocked)
Not while provenance conflict unresolved or any controlling spec missing/candidate/contradictory/structurally invalid. Separately governed decision; not authorized by issue #253.

### Successor implementation work (blocked)
Requires: (1) provenance spec repair, (2) plan impact review, (3) plan acceptance, (4) individual issues citing accepted plan/specs/base/B0 evidence.

### Unblocked preparatory work
B0 evidence classification, I1 evidence for non-conflicting keys (controlled experimental context), provenance spec repair — each requires separate governed issue.

### Completion gate summary
| Condition | Status |
| --- | --- |
| 34/34 accepted specs mapped by composite key | Patch 1 |
| 291/291 requirements assigned to planning responsibility | Patch 1 |
| Acyclic B0→I1→I2→I3→I4→I5 DAG with controlling spec/requirement citations | Patch 2 |
| Each increment has entry/exit conditions and exclusions | Patch 2 |
| Requirement-level transition gates defined | Patch 3 |
| Validation strategy (component/cross-component/E2E) defined | Patch 3 |
| Terminal outcomes, determinism, rejection evidence defined | Patch 3 |
| Risk/decision register substantive | Patch 3 |
| Provenance conflict blocker at every affected boundary | Patches 1-3 |
| Future-extension specs excluded | Patches 1-3 |
| Three patches; no fourth functional correction | Verified |
| No product source/tests/schemas/specs modified | Verified |
| `./scripts/validate` passes each commit | Verified |
| Clean-room review: blocked gaps, no invented semantics | Pending |
