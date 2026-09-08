# FS-004 Plan — Structural Policy Integration

## Technical Objective

Integrate the framework FS-005 structural-policy configuration into existing initializer and upgrade workflows without duplicating framework policy or changing ownership boundaries.

## Initialization

The supplier framework contains canonical `repo/validation/structure-policy.json`.

Initialization shall:

1. verify the selected supplying checkout as already required;
2. copy/install the supplier framework, including the exact policy file;
3. not synthesize or hardcode a second copy of the default allowlist;
4. construct generic product and root operational state;
5. run canonical repository-wide Validation against the completed candidate; and
6. promote only on success.

Because `repo/` is copied from the exact selected supplying revision, the supplier policy file is the source of initialized policy state.

## Initialized Repository Adaptation

After initialization, the target repository owns its installed concrete policy values subject to its own lifecycle. Product behavior shall not treat any difference from supplier default policy as an automatic framework-code modification conflict.

Framework source identity continues to identify reusable framework provenance rather than asserting that target policy values remain byte-identical to supplier defaults.

## Upgrade Reconciliation

`repo/validation/structure-policy.json` is a special framework-defined installed configuration surface.

Upgrade shall not reconcile it with the ordinary byte-for-byte framework-owned file algorithm.

For schema-compatible version 1 policy:

1. load and strictly validate prior supplier policy;
2. load and strictly validate target installed policy;
3. load and strictly validate prospective supplier policy;
4. require the target policy to contain at least the structural authorization required by the prior supplier policy;
5. preserve schema-valid target-specific additional authorization;
6. union in authorization newly required by the prospective supplier policy;
7. use the prospective policy's schema/version;
8. preserve default-deny semantics; and
9. validate the completed upgrade candidate before promotion.

For `product.required_when_present`, reconciliation preserves target additions and includes all prospective required roles, while ensuring the result remains a subset of reconciled product directories.

If policy versions differ or any policy cannot be validated/reconciled under accepted rules, fail before promotion.

Upgrade shall not silently reset target policy to prospective defaults.

## Conflict Boundary

Ordinary local modification conflict detection remains unchanged for reusable framework implementation. The structural policy is excluded from that byte-identity conflict path because its concrete values are intentionally repository-adaptable configuration.

This exception applies only to the canonical structural-policy path.

## Mechanical Coverage

Extend existing product initializer/upgrade tests to cover:

- initialization copies exact supplier policy;
- no independent initializer allowlist;
- initialized candidate Validation consumes policy;
- target-specific additional root authorization survives upgrade;
- prospective newly required authorization is added;
- undeclared structure remains denied after upgrade;
- malformed target policy fails upgrade;
- incompatible policy version fails upgrade;
- upgrade candidate Validation still gates promotion.

## Planning-to-Build Activation

All product FS-004 `M`/`B` requirements are initially inactive. Build activates them only with real product Validation task coverage and matching product Requirement Evaluation Manifest bindings.

## Validation

Before commit:

- focused initializer tests;
- focused upgrade tests;
- canonical `scripts/validate`;
- `git diff --check`.

Semantic Review verifies that the initializer consumes framework policy rather than owning a competing policy definition.
