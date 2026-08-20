# Validation Reference

`user/validation_reference/` is non-normative convenience/reference material under the governed `user/` namespace. Accepted repository specifications remain controlling authority for validation semantics.

`user/validation_reference/` defines the neutral common baseline for validation implementation in initialized repositories.

It is a reference structure, not an executable validation domain. The same logical structure applies to top-level `validation/`, `repo/validation/`, and `product/validation/`.

`manifest.json` is the machine-readable placement authority for this reference.

## Standard structure

- `core/` — shared validation infrastructure and mechanics.
- `checks/` — production validation rule implementation.
- `runners/` — internal orchestration invoked by public script entry points.
- `tests/unit/` — ordinary unit tests discovered by Python `unittest`.
- `tests/self/` — validation-framework self-tests and support.
- `tests/fixtures/` — non-executable test input material.

The baseline defines common logical roles. Domain-specific implementations may differ, and a validation domain may add specialization files or directories when a concern does not fit a standard role.

Public executable entry points are not part of this reference tree: root validation uses top-level `scripts/`, while repository and product leaf validation use their owning `<domain>/scripts/` directories.
