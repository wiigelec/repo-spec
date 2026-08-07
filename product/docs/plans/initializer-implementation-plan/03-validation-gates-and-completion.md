# Validation, gates, and completion

Status: candidate; non-authorizing

## Transition gates

Each gate below must pass before work on the successor increment may be
authorized. Evidence is requirement-level and keyed to composite
`<spec_id>::<requirement_id>` from Patch 1 ownership.

### B0 -> I1 gate

| Requirement | Evidence |
| --- | --- |
| Every I1-owned composite key has exactly one supported baseline classification (`preserve`, `repair`, `replace`, or `implement`) with cited source and test evidence. | Machine-reviewable classification matrix; aggregate counts reconcile to Patch 1 ownership for every spec and requirement ID assigned to `product.request-intake`, `product.source-revision-identity`, `product.destination`, `product.product-identity`, `product.material-manifest`, `product.git-object-identity`, `product.destination-preflight`, `product.request-intake`, and `product.source-material-resolution`. |
| No I1-owned composite key is classified by file presence or undifferentiated all-tests-pass alone. | Each matrix entry references at least one specific observable behavior or test assertion; absence citations are explicit. |
| The provenance-conflict keys `product.provenance-recording::INIT-PRC-001`, `product.provenance-record::INIT-PRO-003`, and `product.provenance-record::INIT-PRO-006` are visibly flagged as blocked rather than classified. | Matrix blocker flag confirmed. |

### I1 -> I2 gate

| Requirement | Evidence |
| --- | --- |
| I1-owned intake, identity, source, manifest, and preflight evidence exists at requirement-level for all owned composite keys. | Positive/negative test evidence per owned spec; aggregate counts reconcile exactly to Patch 1 I1 rows. |
| Validated request model and resolved source/material identities are available as deterministic inputs. | Canonical request fingerprint, full SHA-1 commit identity in already-local source, closed material-key mapping. |
| Destination preflight passed: absent and same-filesystem. | Preflight evidence without destination mutation. |
| Unsupported authority expansion, profile behavior, source behavior, or destination states are rejected. | Distinct rejection evidence per excluded case. |
| B0 classifications for I2-owned keys are documented in the governing I2 issue without broadening scope. | Issue citation and ownership map. |

### I2 -> I3 gate

| Requirement | Evidence |
| --- | --- |
| I2-owned staging establishment, material realization, foundation seeding, framework installation, inventory production, and digest evidence exists at requirement-level for all owned composite keys. | Positive/negative test per I2-owned key; aggregate counts reconcile to Patch 1 I2 rows. |
| Staging root contains only `transaction/` and `repository/`, no undeclared output, no broad/tree copies, and no excluded-content paths. | Path-inventory evidence; negative evidence for forbidden patterns. |
| Complete deterministic repository-only digest and content evidence available for I3 provenance and Git work. | Digest artifact; producer-evidence citations for every inventory entry. |
| I1-carried request, source, identity, and manifest values are preserved. | Value-comparison evidence against I1 validated model. |

### I3 -> I4 gate (blocked)

This gate inherits the entry condition from Patch 2: separate governed
specification work must repair the conflict among
`product.provenance-recording::INIT-PRC-001`,
`product.provenance-record::INIT-PRO-003`, and
`product.provenance-record::INIT-PRO-006`. The repair must be accepted,
structurally valid, and registered. A material-specification plan impact review
must then revise or reaffirm the affected plan sections.

Until those conditions are met, no I3-implementation authorization, I3 exit,
or I4 implementation authorization passes this gate. Evidence for unaffected
I3-owned keys (e.g., Git initialization, handoff-assembly contracts, Git object
identity) may be developed separately in bounded experimental or preparatory
work, but complete I3 may not be claimed.

| Requirement | Evidence |
| --- | --- |
| The blocked provenance entry condition is resolved. | Accepted repair specification revision; plan impact review record. |
| All I3-owned composite keys (excluding the three conflicting keys) have requirement-level evidence. | Composite-key reconciliation to Patch 1 I3 rows minus the three blocked keys. |
| Unblocked I3 evidence shows provenance/handoff/Git state consistent with the repaired accepted contract, I2 content, and carried I1 identities. | Traceability evidence across request, source, product, material, content, records, and Git topology. |

### I4 -> I5 gate (blocked)

This gate inherits the I3 -> I4 blockage. I5 implementation and completion
evidence cannot replace the missing predecessor.

| Requirement | Evidence |
| --- | --- |
| I4-owned validation phases, report finalization, promotion, and post-promotion evidence exists at requirement-level. | Composite-key reconciliation to Patch 1 I4 rows. |
| Promotion gate: destination absence rechecked, exactly one same-filesystem atomic rename, post-rename stat confirms commitment. | Fault-injection evidence at each rename/finalization boundary. |
| Terminal-boundary evidence covers pre-promotion failure, promoted success, indeterminate promotion, and promoted-with-finalization-error failure without misreporting destination ownership. | Outcome-class-specific evidence; mutually consistent caller result, destination state, staging state, report, and diagnostics. |
| I3-carried provenance/handoff/Git evidence is validated as a composite key owned input. | Validation-profile check results; blocked until I3 exit. |

## Validation strategy

### Requirement-level validation

Every composite key in Patch 1 must produce observable positive or negative
evidence. The B0 baseline classifies each key. Implementation increments I1-I5
then produce focused evidence. Cross-increment requirements are re-verified at
each consumer boundary.

Evidence types:

| Type | Description | Examples |
| --- | --- | --- |
| Positive | Demonstrates required behavior for accepted inputs. | Valid request accepted; correct provenance field written. |
| Negative | Demonstrates rejection of non-conforming inputs. | Named reference rejected; existing destination rejected. |
| Equivalence | Demonstrates identical output for equivalent inputs. | Same request + same source = same generated repository. |
| Fault-injection | Demonstrates correct behavior under filesystem or system faults. | Report-finalization write fails; rename becomes indeterminate. |

### Component validation

Each implementation increment validates its owned composite keys before
signaling readiness to the successor increment. Component validators focus on
one accepted specification or a cohesive group:

- Request intake: `product.initialization-request`, `product.request-intake`
- Source resolution: `product.source-revision-identity`, `product.source-material-resolution`, `product.git-object-identity`
- Material realization: `product.foundation-seeding`, `product.framework-installation`, `product.generated-repository`, `product.initializer-output-inventory-v1`
- Staging: `product.staging-workspace`, `product.transactional-staging`
- Provenance and handoff: `product.provenance-record`, `product.provenance-recording`, `product.handoff-manifest`, `product.handoff-assembly`
- Git initialization: `product.local-git-repository`, `product.local-git-initialization`, `product.git-bootstrap-profile`
- Validation and promotion: `product.validation-profile`, `product.validation-report`, `product.repository-validation`, `product.execution-report`, `product.staging-state`, `product.destination`

### Cross-component validation

Cross-component validation verifies that producers and consumers agree on shared
values and that no increment broadens its scope:

- Request values are preserved through all consuming increments.
- Source and material identities are consistent from resolution through Git record.
- Staging-state transitions match execution-report lifecycle outcomes.
- Provenance and handoff paths are consistent with generated-repository layout.
- Git objects match the repository-only digest produced before Git initialization.

### End-to-end validation

After I5 orchestrates the complete bounded workflow, E2E evidence covers:

- Promoted success: complete lifecycle with success finalization.
- Pre-promotion failure: failure before rename (including report-finalization partial-write failure).
- Indeterminate promotion: rename started but commitment unclear.
- Promoted-with-finalization-error: rename succeeded but cleanup failed.
- Deterministic equivalent-input behavior: equivalent canonical requests and source revisions produce equivalent repository content, records, handoff, and Git topology.
- Rejection of unsupported V1 behavior: named references, remote retrieval, existing destination, platform/hosting operations, arbitrary resume, migration, cross-device promotion, and undeclared output.

### Evidence artifacts

| Artifact | Purpose | Producer |
| --- | --- | --- |
| B0 classification matrix | Requirement-by-requirement baseline | Separate governed issue |
| Requirement-level test suite | Positive/negative evidence per composite key | Each implementation increment |
| Validation report | Ordered phase results, failure codes, timestamps, digest | I4 |
| Staging state | Lifecycle-stage status, report linkage, digest | I4 |
| Execution report | Stage-by-stage status per terminal outcome | I4 |
| Provenance record | Initializer identity, source, request, timestamp | I3 (blocked) |
| Handoff manifest | Material disposition, identities, content equivalence | I3 |
| Git repository | Single-root-commit local repo with complete content | I3 |
| E2E outcome evidence | One per terminal outcome class + determinism + rejection | I5 |

## Completion and successor work

### Candidate plan completion

This plan composite document is complete when:

- Patch 1: all 34 accepted `initial-bounded-workflow` specifications and all
  291 normative requirements are mapped by composite key and assigned to bounded
  planning responsibility; the provenance conflict is recorded; all 6 candidate
  `future-extension` specifications are excluded.
- Patch 2: the bounded acyclic DAG `B0 -> I1 -> I2 -> I3 -> I4 -> I5` is
  defined; every increment specifies controlling accepted specs, requirement
  IDs, predecessors, entry conditions, exit conditions, and exclusions; the
  provenance blocker propagates through I3, I4, and I5.
- Patch 3: requirement-level transition gates are defined for every increment
  boundary; validation strategy covers component, cross-component, and
  end-to-end evidence; completion evidence covers all accepted terminal outcome
  classes, determinism, and rejection; the risk/decision register is substantive
  and does not silently resolve planning choices.

### Plan acceptance (blocked)

The candidate plan may not be accepted while the accepted provenance conflict
remains unresolved or while any accepted specification that the plan relies upon
is missing, merely placeholder scaffolding, candidate where acceptance is
required, structurally invalid, mutually contradictory, or absent from the
product manifest.

Plan acceptance is a separately governed decision and is not authorized by the
three patches of issue #253.

### Successor implementation work (blocked)

Successor governed implementation issues may not be derived from this candidate
plan until:

1. The accepted provenance conflict is repaired through separate governed
   specification work.
2. The required material-specification plan impact review has revised or
   reaffirmed every affected map, increment, edge, gate, and validation claim.
3. The candidate plan is accepted through a governed decision that confirms
   all `repo.implementation-plan` requirements are satisfied.
4. Individual implementation issues cite the accepted plan, applicable accepted
   specifications, the exact accepted base, and B0 predecessor evidence.

### Unblocked preparatory work

The following successor work may proceed without plan acceptance or
provenance repair if separately bounded and authorized:

- B0 evidence classification (requires a governed issue that cites this
  candidate plan and respects the provenance blocker).
- Development of I1 evidence for non-conflicting keys in a controlled
  experimental context, provided it does not claim implementation authorization.
- Specification repair of the provenance conflict (requires a separate governed
  issue).

### Completion gate summary

| Condition | Status |
| --- | --- |
| 34/34 accepted specs mapped by composite key | Patch 1 complete |
| 291/291 normative requirements assigned to planning responsibility | Patch 1 complete |
| B0 -> I1 -> I2 -> I3 -> I4 -> I5 DAG defined, acyclic, with controlling spec/requirement citations | Patch 2 complete |
| Each increment has entry conditions, exit conditions, and exclusions | Patch 2 complete |
| Requirement-level transition gates defined for all boundaries | Patch 3 complete |
| Validation strategy covers component, cross-component, and E2E evidence | Patch 3 complete |
| Terminal outcomes, determinism, and rejection evidence defined | Patch 3 complete |
| Risk/decision register is substantive | Patch 3 complete |
| Provenance conflict recorded as blocker at every affected boundary | Patches 1-3 complete |
| Candidate `future-extension` specs excluded | Patches 1-3 complete |
| Three-patch count not exceeded; no fourth functional correction | Verified |
| No product source, tests, schemas, or normative specs modified | Verified |
| `repo/scripts/validate` passes on each commit | Verified |
| A clean-room post-patch review finds blocked gaps but no invented semantics | Pending |
