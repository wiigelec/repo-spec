# Validation, gates, and completion

Status: accepted; planning-authoritative; non-normative with respect to product semantics

## Transition gates

Each gate passes before successor increment work may be authorized. Evidence is requirement-level, keyed to the accepted requirement-to-responsibility map.

### B0 -> I1 gate
| Requirement | Evidence |
| --- | --- |
| B0 is complete across all accepted bounded-workflow authority before I1 may be authorized | Machine-reviewable matrix contains exactly one supported classification (preserve/repair/replace/implement) for every one of the 291 composite keys across all 34 accepted specifications, with requirement-specific cited evidence; aggregate counts reconcile to 34/291 |
| No unresolved B0 finding identifies a material authority or semantic blocker to governed implementation | Matrix findings and governing B0 issue show no unresolved contradiction, missing normative semantics, invalid controlling authority, or other blocker that requires separate governance before implementation may proceed |
| Every I1-owned key has one baseline classification (preserve/repair/replace/implement) with cited source/test evidence | I1 subset reconciliation from the complete B0 matrix; counts reconcile to the accepted requirement-to-responsibility map for `product.initializer-level-0`, `product.initialization-request`, `product.source-revision-identity`, `product.destination`, `product.product-identity`, `product.material-manifest`, `product.git-object-identity`, `product.destination-preflight`, `product.request-intake`, `product.source-material-resolution` |
| No I1 key classified by file presence or undifferentiated tests alone | Each entry cites specific behavior/assertion; absence citations explicit |
| Issues #255/#257 repaired provenance/handoff keys are classified against current accepted text | Matrix cites current accepted specification revision |

### I1 -> I2 gate
| Requirement | Evidence |
| --- | --- |
| I1-owned intake/identity/source/manifest/preflight evidence at requirement level | Positive/negative test per owned spec; aggregate counts reconcile to the accepted I1 ownership rows |
| Validated request, resolved source, closed material-key mapping available | Canonical fingerprint, full SHA-1 commit identity, manifest |
| Destination preflight passed: absent and same-filesystem | Preflight evidence without mutation |
| Unsupported authority/profile/source/destination states rejected | Distinct rejection per excluded case |
| B0 classifications for I2 keys documented in governing I2 issue | Issue citation + ownership map |

### I2 -> I3 gate
| Requirement | Evidence |
| --- | --- |
| I2-owned staging/material/foundation/framework/inventory/digest evidence at requirement level | Positive/negative per I2-owned key; reconcile to the accepted I2 ownership rows |
| Staging: only `transaction/` and `repository/`, no undeclared/broad-tree/excluded paths | Path inventory; negative evidence for forbidden patterns |
| Deterministic repository-only digest available for I3 | Digest artifact; producer citations per inventory entry |
| I1-carried request/source/identity/manifest values preserved | Value comparison against I1 validated model |

### I3 -> I4 gate

| Requirement | Evidence |
| --- | --- |
| Issues #255/#257 provenance/handoff repairs reflected in B0 and I3 evidence | Current accepted specs plus this impact-review record |
| All I3-owned keys have requirement-level evidence | Composite-key reconciliation to the accepted I3 ownership rows |
| Provenance/handoff/Git consistent with repaired contracts, I2 content, I1 identities | Traceability across request/source/product/material/content/records/Git |

### I4 -> I5 gate

| Requirement | Evidence |
| --- | --- |
| I4-owned validation/promotion evidence at requirement level | Composite-key reconciliation to the accepted I4 ownership rows |
| Promotion: destination rechecked, single rename, post-rename stat commitment | Fault-injection at each boundary |
| Terminal boundaries: pre-promotion failure, promoted success, indeterminate promotion, promoted-with-finalization-error | Outcome-class evidence; consistent caller result/destination/staging/report/diagnostics |
| I3-carried provenance/handoff/Git validated as owned input | Validation-profile check results after I3 exit |

## Validation strategy

Every composite key in the accepted requirement-to-responsibility map produces observable positive/negative evidence. B0 classifies; I1-I5 produce focused evidence.

Evidence types: positive (required behavior with accepted inputs), negative (rejection of non-conforming inputs), equivalence (identical output for equivalent inputs), fault-injection (correct behavior under system faults).

Component validation per increment: request intake, source resolution, material realization, staging, provenance/handoff, Git, validation/promotion — each validates its owned keys before signaling readiness.

Cross-component validation: request values preserved through consumers, source/material identities consistent from resolution through Git record, staging-state transitions match execution-report outcomes, provenance/handoff paths match generated layout, Git objects match pre-Git digest.

End-to-end (I5): promoted success, pre-promotion failure (including report-finalization partial-write), indeterminate promotion, promoted-with-finalization-error, deterministic equivalent-input behavior, rejection of unsupported V1 (named refs, remotes, existing destination, platform, resume, migration, cross-device, undeclared output).

Evidence artifacts: B0 classification matrix, requirement-level test suite, validation report, staging state, execution report, provenance record, handoff manifest, Git repository, E2E outcome evidence.

## Completion and successor work

### Plan construction completion
- Patch 1: 34/34 accepted specs and 291/291 requirements mapped by composite key; 6/6 future-extension specs excluded
- Patch 2: acyclic B0→I1→I2→I3→I4→I5 DAG; each increment has controlling specs, requirements, predecessors, entry/exit conditions, and exclusions
- Patch 3: requirement-level transition gates; validation strategy (component/cross-component/E2E); terminal outcomes/determinism/rejection evidence; risk/decision register substantive

### Plan acceptance
Issues #255 and #257 completed the accepted provenance/handoff specification repairs and required plan impact reviews. Issue #259 / PR #260 completed synchronization of the candidate plan to that repaired authority and the required post-patch clean-room review. Issue #261 completed the separate clean-room acceptance audit and accepted this plan against the current synchronized authority.

### Successor implementation work
B0 is the next eligible governed successor and requires its own governing issue. I1-I5 require: (1) this accepted plan, (2) completed B0 requirement-level evidence, (3) each increment's predecessor exit evidence, and (4) individual governed issues citing the accepted plan, applicable accepted specifications, exact accepted base, and predecessor evidence.

### Unblocked preparatory work
B0 evidence classification is now the next authorized governed preparatory work. It remains subordinate to accepted specifications and this accepted plan, requires a separate governing issue, and does not authorize I1 until the B0→I1 gate passes.

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
| Issues #255 and #257 accepted specification repairs reflected at every affected boundary | Impact review complete |
| Future-extension specs excluded | Patches 1-3 |
| Three patches; no fourth functional correction | Verified |
| No product source/tests/schemas/specs modified | Verified |
| `./scripts/validate` passes each commit | Verified |
| Clean-room review: current accepted specs, no invented semantics | Completed under issue #259 / PR #260 and revalidated for acceptance under issue #261 |
| Governed plan acceptance | Accepted under issue #261 after current-spec, manifest, correspondence/dependency, planning-completeness, and repository validation checks |
