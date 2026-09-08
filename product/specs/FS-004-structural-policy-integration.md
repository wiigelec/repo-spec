# FS-004 — Structural Policy Integration Normative Requirements

### FS-004-NR-001 — Supplier Policy Seeding

**Classification: M**

**State: Inactive**

Repository initialization shall install canonical `repo/validation/structure-policy.json` from the exact selected supplying framework revision and shall not substitute a separately hardcoded structural allowlist.

### FS-004-NR-002 — Initialized Candidate Validation

**Classification: M**

**State: Inactive**

Repository initialization shall run canonical repository-wide Validation against the completed initialized candidate using its installed structural policy and shall promote only a passing candidate.

### FS-004-NR-003 — Installed Policy Adaptability

**Classification: S**

After successful initialization, concrete schema-valid structural-policy authorization is target-repository configuration subject to that repository's lifecycle and shall not be treated as immutable supplier product state.

### FS-004-NR-004 — Framework Source Truthfulness

**Classification: S**

Intentional target structural-policy differences from supplier defaults shall not change the meaning of the recorded framework source revision as the identity of the supplying reusable framework.

### FS-004-NR-005 — Policy-Aware Upgrade Reconciliation

**Classification: M**

**State: Inactive**

For schema-compatible structural policy, repository upgrade shall preserve target-specific valid authorization, add prospective framework-required authorization, and shall not silently reset target policy to supplier defaults.

### FS-004-NR-006 — Required Product Role Reconciliation

**Classification: M**

**State: Inactive**

Policy-aware upgrade shall preserve valid target `product.required_when_present` additions, add prospective required roles, and ensure the reconciled required-role set remains a subset of reconciled authorized product directories.

### FS-004-NR-007 — Unresolved Policy Incompatibility

**Classification: M**

**State: Inactive**

Upgrade shall fail before promotion when prior, target, or prospective structural policy is malformed, unsupported, or cannot be reconciled using accepted schema-compatible rules.

### FS-004-NR-008 — Policy Excluded From Byte-Identity Conflict

**Classification: M**

**State: Inactive**

Upgrade's ordinary reusable-framework local-modification conflict check shall treat only canonical structural policy as repository-adaptable configuration rather than requiring byte identity with the prior supplier policy.

### FS-004-NR-009 — Upgrade Candidate Validation

**Classification: M**

**State: Inactive**

A policy-aware upgrade shall run prospective canonical repository Validation against the completed candidate and shall promote only when it passes.

### FS-004-NR-010 — Structural Policy Product Regression Coverage

**Classification: M**

**State: Inactive**

Product Validation shall mechanically cover exact supplier-policy initialization, candidate Validation, target-specific authorization preservation, prospective authorization addition, malformed/incompatible policy failure, and successful post-reconciliation Validation.

### FS-004-NR-011 — Legacy Policy Introduction Migration

**Classification: M**

**State: Inactive**

When upgrading a repository whose reconstructed prior framework revision and target repository both predate and therefore lack the canonical structural-policy file, upgrade shall seed the prospective valid FS-005-compatible default policy into the candidate; disagreement about legacy policy presence shall fail rather than be guessed.
