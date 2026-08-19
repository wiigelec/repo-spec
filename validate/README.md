# Root validation

This directory owns validation and tests whose subject intentionally crosses
top-level repository domains.

Examples include integration across `repo/`, `product/`, `.github/`,
`reference/`, initializer-installed output, and top-level aggregate validation.

Domain-specific validators remain independently owned:

- `repo/validation/` validates and tests `repo/`.
- product-owned validation validates and tests `product/`.
- `validate/` owns cross-domain and aggregate integration validation.

The public aggregate entry points remain under `scripts/`.
