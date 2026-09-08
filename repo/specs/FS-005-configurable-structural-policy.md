# FS-005 — Configurable Structural Policy Normative Requirements

### FS-005-NR-001 — Closed Boundary Preservation

**Classification: B**

**State: Inactive**

The maintained repository-root boundary and direct-child boundaries of `repo/` and `product/` shall remain closed and default-deny; externalizing concrete authorization into configuration shall not make an undeclared maintained entry permissible.

### FS-005-NR-002 — Canonical Structural Policy

**Classification: M**

**State: Inactive**

The repository shall contain canonical `repo/validation/structure-policy.json`, and framework structural Validation shall obtain concrete authorized-entry data from that file rather than from a second hardcoded allowlist.

### FS-005-NR-003 — Strict Policy Schema

**Classification: M**

**State: Inactive**

The canonical structural policy shall conform exactly to the FS-005 version-1 schema, reject malformed JSON, unknown keys, invalid direct-child names, duplicate entries, root file/directory name overlap, and `product.required_when_present` entries not authorized by `product.directories`, and shall fail closed when missing or invalid.

### FS-005-NR-004 — Default Policy Compatibility

**Classification: B**

**State: Inactive**

The accepted supplier default structural policy shall authorize exactly the structural roles authorized by the pre-FS-005 hardcoded policy, including the existing required baseline product roles, so externalization alone does not broaden or narrow accepted default structure.

### FS-005-NR-005 — Policy-Driven Root Enforcement

**Classification: M**

**State: Inactive**

`repository-structure` shall allow maintained repository-root direct files and directories only when explicitly authorized by the validated canonical structural policy and shall reject undeclared root entries.

### FS-005-NR-006 — Policy-Driven Ownership-Tree Enforcement

**Classification: M**

**State: Inactive**

`repository-structure` shall allow maintained direct children of `repo/` and `product/` only when explicitly authorized by the validated canonical structural policy, shall require those authorized direct children to be directories, and shall preserve nested extensibility below authorized roles unless another accepted requirement constrains it.

### FS-005-NR-007 — Required Product Roles

**Classification: M**

**State: Inactive**

When maintained `product/` exists, `repository-structure` shall require every role listed by `product.required_when_present` and shall reject a policy whose required product roles are not a subset of authorized product directories.

### FS-005-NR-008 — Configuration Is Not Normative Authority

**Classification: S**

The structural-policy file shall remain a mechanical representation of accepted structural authorization and shall not independently create Design meaning, normative requirements, ownership semantics, or permission for an unjustified architectural change.

### FS-005-NR-009 — Framework and Policy Separation

**Classification: S**

Reusable framework Validation code shall own policy-schema interpretation and enforcement mechanics, while an installed repository may intentionally carry concrete policy values different from supplier defaults without those values becoming a fork of framework implementation.

### FS-005-NR-010 — Initializer Seeds Supplier Policy

**Classification: M**

**State: Inactive**

Repository initialization shall seed the canonical structural-policy file from the exact selected supplying framework revision and shall validate the completed initialized repository using that policy before promotion.

### FS-005-NR-011 — No Independent Initializer Allowlist

**Classification: M**

**State: Inactive**

The initializer shall not maintain a second independent hardcoded copy of the concrete structural allowlist; the selected supplier policy file shall be the source used to seed initialized structural configuration.

### FS-005-NR-012 — Derived Repository Adaptation

**Classification: B**

**State: Inactive**

An initialized repository shall support an intentional repository-local policy change that authorizes additional valid direct entries while leaving all undeclared entries denied and without modifying reusable framework Validation code.

### FS-005-NR-013 — Framework Source Truthfulness

**Classification: B**

**State: Inactive**

Repository-local structural-policy values may differ from supplier defaults after intentional repository development without changing the truthful meaning of `repo/validation/framework-source.json` as the identity of the supplying reusable framework revision.

### FS-005-NR-014 — Upgrade Preserves Compatible Target Authorization

**Classification: M**

**State: Inactive**

For a schema-compatible framework upgrade, upgrade shall preserve schema-valid target-specific structural authorization, add prospective framework-required authorization, and shall not silently reset the target policy to supplier defaults or remove target-specific entries merely because they are absent from those defaults.

### FS-005-NR-015 — Upgrade Fails on Unresolved Policy Incompatibility

**Classification: M**

**State: Inactive**

When a prospective framework policy schema or requirement cannot be reconciled with target structural policy using accepted upgrade semantics, upgrade shall fail before promotion rather than guess, silently discard target authorization, or leave an invalid mixed state.

### FS-005-NR-016 — Candidate Validation

**Classification: M**

**State: Inactive**

Initialization and upgrade candidates affected by structural policy shall pass canonical repository-wide Validation against the completed candidate before promotion.

### FS-005-NR-017 — Structural Policy Regression Coverage

**Classification: M**

**State: Inactive**

Framework regression Validation shall mechanically cover default-policy compatibility, configured additional root authorization, undeclared-entry rejection, malformed/missing policy failure, strict schema rejection cases, initializer seeding, and upgrade preservation/reconciliation behavior.

### FS-005-NR-018 — No Generalized Policy Engine

**Classification: S**

FS-005 shall not introduce wildcard, glob, regex, recursive authorization, ordered override, plugin, or generalized policy-engine semantics; version 1 is a finite explicit direct-child allowlist representation.
