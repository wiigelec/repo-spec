# FS-002 — Independent Initialized Repository Normative Requirements

### FS-002-NR-001 — Independent target history

A successful initialized repository shall begin fresh Git history with one initialization root commit and shall not inherit supplying repo-spec commit ancestry.

Classification: B

### FS-002-NR-002 — Supplier object independence

A successful initialized repository shall not require the supplying repo-spec commit object to exist in the target Git object database for ordinary lifecycle use.

Classification: B

### FS-002-NR-003 — Installed framework Planning omission

A successful initialized repository shall omit the supplying framework's `repo/planning/` development history while retaining the installed framework state required for ordinary lifecycle operation.

Classification: B

### FS-002-NR-004 — Exact source record preservation

The initialized repository shall continue to record the exact supplying repo-spec revision in `repo/validation/framework-source.json` even though that revision is not imported as target history.

Classification: B

### FS-002-NR-005 — Repository-wide initialized Validation

Before initialization reports success, the initialized repository shall pass `scripts/validate`, and it shall continue to pass that Validation after the supplying checkout is unavailable.

Classification: B

### FS-002-NR-006 — Existing initializer safety preservation

FS-002 shall preserve the accepted-source, clean-source, destination-safety, generic-product, and normal CLI constraints established by FS-001.

Classification: B

### FS-002-NR-007 — No supplier-history machinery

FS-002 shall not use imported supplier ancestry, grafts, replace refs, bundles, hidden remotes, or generalized provenance machinery merely to initialize a repository.

Classification: S

### FS-002-NR-008 — Canonical Product Validation Scaffold

Classification: M

A successful initialized repository shall contain generic product starter state at `product/design/README.md`, `product/specs/README.md`, executable `product/scripts/validate`, `product/validation/requirement-evaluation.json`, and `product/validation/validate_product.py`.

### FS-002-NR-009 — Starter Guidance Without Product Semantics

Classification: S

The initialized product Design and specification README files shall provide only concise ownership and placement guidance for future product lifecycle work and shall not define target-product identity, Design meaning, normative requirements, implementation semantics, or Acceptance state.

### FS-002-NR-010 — Empty Product Requirement Evaluation Manifest

Classification: M

The initialized `product/validation/requirement-evaluation.json` shall contain the version-1 empty binding state and no product requirement binding before target-product Planning has established mechanically evaluated normative requirements.

### FS-002-NR-011 — Thin Product Validation Launcher

Classification: M

The initialized `product/scripts/validate` shall be executable and shall delegate product Validation to `product/validation/validate_product.py` while forwarding command arguments unchanged.

### FS-002-NR-012 — Inactive Product Validation Behavior

Classification: M

The initialized product validator shall expose the canonical product task interface, enumerate no product validation tasks in the initial empty state, succeed when invoked normally against the empty product manifest, and fail when asked to execute an unknown task.

### FS-002-NR-013 — Repository-Wide Scaffold Validation

Classification: B

Before initialization reports success, repository-wide `scripts/validate` shall mechanically accept the generated canonical product Validation scaffold and empty product Validation state, and that behavior shall remain valid after the supplying checkout is unavailable.
