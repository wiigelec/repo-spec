# Reference Product Kernel

## Status

accepted

## Level

0

## Purpose

Defines the minimal Level 0 kernel foundations for the reference repository.

## Normative requirements

- `REF-KERNEL-001`: The reference product kernel shall expose `kernel_identity()` and return `reference-kernel`.

## Dependencies

- None

## Correspondence

### Implementations

- `kernel-impl`
  - Paths:
    - `src/product/kernel.py`
  - Requirements:
    - `REF-KERNEL-001`

### Tests

- `kernel-test`
  - Paths:
    - `tests/test_kernel.py`
  - Requirements:
    - `REF-KERNEL-001`

### Conformance

- `REF-KERNEL-001`
  - Status: `covered`
  - Implementation ids:
    - `kernel-impl`
  - Test ids:
    - `kernel-test`
