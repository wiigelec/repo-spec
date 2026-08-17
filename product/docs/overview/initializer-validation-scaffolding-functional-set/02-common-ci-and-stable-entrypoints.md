# Common CI and stable validation/test entrypoints

## Common workflow direction

Repo-spec and fresh initialized repositories should share one common GitHub validation workflow contract. Repository-class differences should be handled behind stable local entrypoints rather than by maintaining source-only and derived-only workflow variants.

This is a capability boundary, not an approval of exact workflow syntax.

## Stable ownership surfaces

The accepted analysis identifies these candidate ownership surfaces:

- `repo/scripts/test-validation` for repository/framework validation self-tests;
- `product/scripts/test-validation` for product validation self-tests;
- `product/scripts/test-product` for broader product-owned implementation tests.

The generic `product/scripts/test-product` surface prevents common CI from encoding repo-spec's current product identity as an initializer-specific command.

Within repo-spec, initializer implementation tests may sit behind that generic product-owned surface. In a fresh initialized repository, the same surface may initially have no applicable product implementation tests.

Exact wrapper, dispatcher, executable content, invocation order, and compatibility behavior remain successor decisions.
