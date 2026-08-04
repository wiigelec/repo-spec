# Reference Product Primitives

## Status

accepted

## Level

1

## Purpose

Defines the minimal Level 1 primitives for the reference repository.

## Normative requirements

- `REF-PRIM-001`: The reference product primitives shall expose `normalize_identifier()` and return the kernel canonical text with underscores converted to hyphens.

## Dependencies

- `product.kernel`

## Correspondence

### Implementations

- `primitives-impl`
  - Paths:
    - `src/product/primitives.py`
  - Requirements:
    - `REF-PRIM-001`

### Tests

- `primitives-test`
  - Paths:
    - `tests/test_primitives.py`
  - Requirements:
    - `REF-PRIM-001`

### Conformance

- `REF-PRIM-001`
  - Status: `covered`
  - Implementation ids:
    - `primitives-impl`
  - Test ids:
    - `primitives-test`
