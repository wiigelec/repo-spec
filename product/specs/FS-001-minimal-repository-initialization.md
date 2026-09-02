# FS-001 — Minimal Repository Initialization Normative Requirements

### FS-001-NR-001 — Normal initialization command

The product shall provide a normal local initialization command at `product/scripts/repo-spec init --repo <destination>`.

Classification: M

### FS-001-NR-002 — Destination as normal user input

The destination path shall be the only normal-user initialization argument required by FS-001; the user shall not be required to provide target-product identity, target-product direction, a framework commit SHA, a source-repository identifier, or an initialization manifest.

Classification: B

### FS-001-NR-003 — Supplying source identity

Initialization shall derive the supplying repo-spec source and exact supplying Git commit from the checkout that executes the initializer, and shall fail if that relationship cannot be established accurately and unambiguously.

Classification: B

### FS-001-NR-004 — Supplying maintained state

Initialization shall not claim to install an accepted framework revision from a supplying checkout whose maintained framework material used for initialization differs from that revision.

Classification: B

### FS-001-NR-005 — Admissible destination

Initialization shall accept an absent destination or an existing empty directory.

Classification: M

### FS-001-NR-006 — Existing material refusal

Initialization shall reject a destination containing pre-existing material and shall not delete that material to make the destination admissible.

Classification: B

### FS-001-NR-007 — Reusable framework installation

A successful initialization shall install the reusable repo-spec framework and required repository-root operational material needed for ordinary lifecycle use in the destination.

Classification: B

### FS-001-NR-008 — Initializer product exclusion

A successful initialization shall not install the supplying repository's repo-spec initializer Product Design, Product Planning, product normative specifications, initializer implementation, or initializer-specific validation as the target repository's product semantics or implementation.

Classification: B

### FS-001-NR-009 — Generic product readiness

A successful initialization shall leave the target repository's `product/` ownership domain ready for subsequent Product Design without inventing target-product identity, Design meaning, Planning scope, normative requirements, implementation, Acceptance decisions, or release claims.

Classification: S

### FS-001-NR-010 — Git repository bootstrap

A successful initialization shall produce a Git repository capable of participating in the installed repo-spec lifecycle.

Classification: M

### FS-001-NR-011 — Exact source revision retention

A successful initialized repository shall retain sufficient maintained information to recover the exact supplying repo-spec Git commit from which its reusable framework state originated.

Classification: B

### FS-001-NR-012 — Supplying checkout independence

After successful initialization, ordinary lifecycle use of the initialized repository shall not require access to the supplying repo-spec working tree.

Classification: B

### FS-001-NR-013 — Initialized destination validation

Before initialization reports success, the actual initialized destination shall pass the canonical mechanical Validation required by its installed reusable framework.

Classification: M

### FS-001-NR-014 — Product regression validation

The initializer implementation shall provide mechanically executable regression coverage for the mechanically decidable FS-001 obligations, including success, destination refusal, source-state refusal, installed-material boundaries, source-revision retention, initialized-destination validation, and failure propagation.

Classification: M

### FS-001-NR-015 — Success boundary

Initialization shall report success only after all required repository construction and mechanical validation have completed successfully.

Classification: M

### FS-001-NR-016 — Failure result

When initialization cannot satisfy an active FS-001 obligation, it shall return failure rather than represent the destination as successfully initialized.

Classification: B

### FS-001-NR-017 — No generalized historical machinery requirement

FS-001 shall not require a provenance database, evidence graph, lineage system, promotion workflow, generalized template/plugin system, or framework-reconciliation architecture merely to realize minimal new-repository initialization.

Classification: S

### FS-001-NR-018 — Implementation freedom

Build may choose the implementation language, internal architecture, Git plumbing, materialization strategy, staging or cleanup technique, and validation test organization provided all active FS-001 obligations are satisfied without adding new product meaning.

Classification: S
