# Root validation

This directory is the root/whole-checkout validation domain. It owns validation
whose subject is inherently cross-domain or repository-wide, including concerns
that span `repo/`, `product/`, `.github/`, `reference/`, initializer-installed
output, or top-level checkout structure.

The common logical structure is defined by `user/validation_reference/` and is shared
with `repo/validation/` and `product/validation/`:

- `checks/` — root-owned production validation roles.
- `core/` — shared root validation infrastructure.
- `runners/` — internal production and validation-self-test orchestration.
- `tests/unit/` — ordinary root-owned Python `unittest` modules.
- `tests/self/` — root validation framework/integration self-tests.
- `tests/fixtures/` — non-executable root validation fixture material.

Domain ownership remains strict:

- `repo/validation/` validates and tests repository-owned `repo/` concerns.
- `product/validation/` validates and tests product-owned `product/` concerns.
- `validation/` owns only inherently cross-domain and whole-checkout concerns.

`github/` is a justified root specialization for hosting-platform policy behavior
that crosses repository/product and top-level `.github/` boundaries.

Public aggregate entry points remain under top-level `scripts/`; leaf public
entry points remain under their owning `repo/scripts/` and `product/scripts/`
directories.
