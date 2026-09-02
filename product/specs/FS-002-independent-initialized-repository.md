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
