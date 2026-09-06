# FS-003 — Repository Upgrade Normative Requirements

### FS-003-NR-001 — Exact prospective supplying revision

Classification: B

A successful repository upgrade shall install the reusable framework supplied by the exact selected repo-spec source revision and shall record that exact revision as the target repository's current framework source.

### FS-003-NR-002 — Existing initialized target

Classification: B

Repository upgrade shall operate only on an existing initialized repository whose currently installed framework source relationship can be determined accurately enough for safe reconciliation.

### FS-003-NR-003 — Supported prior-revision reconstruction

Classification: M

FS-003 shall reject an upgrade when the target's recorded currently installed repo-spec revision cannot be resolved as a commit in the supplying repo-spec checkout sufficiently to reconstruct the prior expected installed framework state.

### FS-003-NR-004 — Framework-owned reconciliation

Classification: B

Upgrade shall reconcile framework-owned installed state from the reconstructed prior expected framework snapshot to the selected prospective framework snapshot and shall not derive mutation authority merely from path-name coincidence.

### FS-003-NR-005 — Local framework modification conflict

Classification: B

Upgrade shall fail rather than silently overwrite, delete, or semantically merge maintained framework-owned target state that has diverged from the reconstructed prior expected installed state when no unambiguous accepted policy authorizes the treatment.

### FS-003-NR-006 — Product-owned state preservation

Classification: B

Upgrade shall preserve independently developed product-owned Design, Planning, normative specifications, implementation, Validation state, and other product-owned content except for a bounded compatibility adaptation explicitly required by the prospective framework and safely realizable without inventing product meaning.

### FS-003-NR-007 — User-owned state preservation

Classification: B

Upgrade shall preserve user-owned target repository material and shall not treat user-owned state as framework reconciliation input merely because similarly named material exists in the supplying repo-spec repository.

### FS-003-NR-008 — Bounded compatibility adaptation

Classification: B

Upgrade may create or adapt repository-root or product-domain lifecycle-support state only when the prospective framework requires that compatibility and the change can be made without discarding independently developed meaning or resolving an unowned semantic decision.

### FS-003-NR-009 — Prospective-state validation

Classification: B

Before reporting success, upgrade shall mechanically evaluate the complete prospective upgraded repository state for the installed framework's applicable mechanical obligations, FS-003 mechanical upgrade obligations, and mechanically decidable compatibility conditions required by the prospective framework.

### FS-003-NR-010 — Unrelated product failure isolation

Classification: B

An existing product Validation failure that is independent of the framework transition shall not by itself cause repository upgrade to fail unless the prospective framework requires that product condition for lifecycle compatibility.

### FS-003-NR-011 — Atomic visible outcome

Classification: B

Repository upgrade shall report success only after a complete validated prospective upgrade is promoted, and failure shall leave the pre-upgrade repository state authoritative rather than presenting a partially installed prospective framework as current.

### FS-003-NR-012 — Source-record promotion ordering

Classification: M

The live target `repo/validation/framework-source.json` shall not identify the prospective supplying revision before successful promotion of the corresponding validated prospective framework state.

### FS-003-NR-013 — Independent target history

Classification: B

Upgrade shall preserve the target repository's independently rooted Git history and shall not import supplying repo-spec commit ancestry, grafts, replace refs, hidden remotes, bundles, or equivalent supplier-history machinery merely to perform the upgrade.

### FS-003-NR-014 — Unsupported or ambiguous transition failure

Classification: B

Upgrade shall fail explicitly rather than produce an undocumented hybrid framework when the requested transition is unsupported, ownership cannot be distinguished sufficiently, compatibility adaptation is semantically ambiguous, or required prospective Validation cannot pass.

### FS-003-NR-015 — Same repository identity

Classification: S

A successful framework upgrade shall leave the target as the same repository continuing its existing lifecycle rather than treating framework adoption as creation of a new repository identity.

### FS-003-NR-016 — No generalized migration infrastructure

Classification: S

FS-003 shall not introduce a generalized migration engine, provenance database, framework lineage ledger, evidence graph, universal merge system, or permanent staging architecture merely to implement the bounded repository-upgrade capability.
