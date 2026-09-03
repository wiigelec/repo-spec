# FS-002 Plan — Independent Initialized Repository

## Technical Objective

Replace supplier-history fetch/checkout materialization with direct copying of the maintained installed-framework/root surfaces from the verified clean supplying checkout, followed by fresh target `git init`, one bootstrap commit, and repository-wide Validation.

## Installed Material

Copy the reusable framework and repository-root operational surfaces required by the installed framework. Do not copy initializer Product state. Remove `repo/planning/` from the installed framework snapshot. Preserve `repo/validation/framework-source.json` with the exact supplying revision.

## Git Bootstrap

The target shall contain a fresh `main` history with exactly one initialization commit and no supplier commit objects or ancestry required for ordinary operation.

## Validation

The initialized result shall validate through `scripts/validate`. Product regressions shall prove independent root history, absence of `repo/planning/`, exact source record retention, supplier-object absence, and continued validation after the source checkout is removed.

## Compatibility

Preserve the accepted-source check, clean-source requirement, destination safety, generic target Product seed, controlled pre-merge test seam, and existing CLI surface.

## Complexity Boundary

Use ordinary filesystem copy and Git initialization only. Do not introduce archive plumbing, object filtering, shallow-history tricks, grafts, replace refs, bundles, or generalized provenance machinery.

## Issue #12 Product Scaffold

In addition to the existing independent-history materialization, initialization shall create this generic product-owned starter state:

```text
product/
├── design/
│   └── README.md
├── specs/
│   └── README.md
├── scripts/
│   └── validate
└── validation/
    ├── requirement-evaluation.json
    └── validate_product.py
```

`product/design/README.md` and `product/specs/README.md` are concise ownership guidance, not target-product Design or normative specifications. They explain what future agents should place in those directories. Use these useful starter files instead of `.gitkeep` placeholders.

`product/scripts/validate` shall use the canonical thin launcher form selected by framework FS-004 and delegate to `product/validation/validate_product.py`.

The initial product Requirement Evaluation Manifest shall be exactly the version-1 empty binding state:

```json
{
  "version": 1,
  "bindings": []
}
```

The initial product validator shall implement the canonical task interface, report no available tasks, succeed when run with no arguments against the empty manifest, and fail when asked to execute an unknown task.

The generated README guidance, manifest, launcher, and validator are generic lifecycle substrate. They shall not identify, describe, constrain, or implement the future target product.

Initializer regression coverage shall verify the exact starter paths, README-over-placeholder behavior, executable product entry point, empty manifest, empty task listing, successful product Validation, successful repository-wide Validation, and continued operation after the supplying checkout is unavailable.
