# FS-003 Plan — Repository Ownership and Structural Boundaries

## Technical Objective

Implement the smallest portable repository structure needed to distinguish reusable framework state from generic product-owned state and prevent accidental architectural namespace drift.

## Closed Maintained Root Boundary

Authorized maintained repository-root directories are `.github/`, `repo/`, `product/`, and `user/`.

Authorized maintained repository-root files are `.gitignore`, `AGENTS.md`, `LICENSE`, and `README.md`.

Authorized roles may be absent until needed. Additional maintained root roles are rejected.

For this Functional Set's mechanical enforcement, candidate maintained paths are the tracked and untracked non-ignored paths visible to Git. Ignored transient local state is outside that mechanical candidate set; content intended to become accepted repository state must not rely on ignore rules to bypass the Design-declared closed boundary.

## `repo/` Boundary

Maintained direct children of `repo/` may be only `design/`, `planning/`, `scripts/`, `specs/`, `src/`, and `validation/`, and must be directories.

## `product/` Boundary

When present, maintained direct children of `product/` may be only `design/`, `planning/`, `scripts/`, `specs/`, `src/`, and `validation/`, and must be directories.

The product role set is generic and shall not encode initializer-specific structure.

## Extensibility

Closure applies only to the declared root and ownership-tree direct-child boundaries. Nested organization inside authorized roles remains extensible according to that role and ordinary Design, Planning, and Build decisions.

## Mechanical Enforcement

Add one required project-native Validation task named `repository-structure`. It shall inspect tracked and untracked non-ignored candidate paths and reject unauthorized root, `repo/`, and `product/` direct-child roles while allowing nested content inside authorized roles.

## Operational Guidance

README and AGENTS shall describe the generic ownership split and closed-boundary rule without becoming normative authority.

## Validation

Run `repo/scripts/validate --task repository-structure`, canonical `repo/scripts/validate`, and `git diff --check`.
