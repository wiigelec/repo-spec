# Validation Reference

`validation_reference/` defines the neutral common baseline for validation implementation in initialized repositories.

It is a reference structure, not an executable validation domain. The same logical structure is intended to be materialized beneath both `repo/validation/` and `product/validation/`.

`manifest.json` is the machine-readable placement authority for this reference.

## Standard structure

- `core/` — shared validation infrastructure and mechanics.
- `checks/` — production validation rule implementation.
- `runners/` — internal orchestration invoked by public script entry points.
- `tests/unit/` — ordinary unit tests discovered by Python `unittest`.
- `tests/self/` — validation-framework self-tests and support.
- `tests/fixtures/` — non-executable test input material.

The baseline defines common logical roles. Domain-specific implementations may differ, and a validation domain may add specialization files or directories when a concern does not fit a standard role.

Public executable entry points remain under the owning `scripts/` directory and are not part of this reference tree.
