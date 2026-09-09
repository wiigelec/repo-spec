# FS-005 Plan — Configurable Structural Policy

## Technical Objective

Replace concrete structural allowlists embedded in `repo/validation/validate_framework.py` with one strict repository-local configuration while retaining the same default-deny enforcement model.

The framework owns:

- the policy schema;
- loading and strict validation of policy data;
- closed-boundary enforcement semantics; and
- framework-required structural invariants.

The installed repository owns the concrete authorized-entry values in its policy, subject to accepted Design and Planning.

Changing an installed repository's structural policy is a maintained repository change. It is not a Validation bypass.

## Canonical Policy Location

The canonical structural-policy file is:

`repo/validation/structure-policy.json`

It is a framework-defined configuration surface consumed by `repository-structure`. It is not a second normative specification.

`repository-structure` shall not retain a fallback copy of the concrete allowlists. Missing or invalid policy fails closed.

## Policy Schema

Version 1:

```json
{
  "version": 1,
  "root": {
    "files": [],
    "directories": []
  },
  "repo": {
    "directories": []
  },
  "product": {
    "directories": [],
    "required_when_present": []
  }
}
```

Schema rules:

- top level contains exactly `version`, `root`, `repo`, and `product`;
- `version` is integer `1`;
- `root` contains exactly `files` and `directories`;
- `repo` contains exactly `directories`;
- `product` contains exactly `directories` and `required_when_present`;
- every collection is an array of unique non-empty strings;
- entries are direct-child names only: no `/`, `\`, `.`, `..`, empty name, absolute path, or traversal;
- a root name may not appear in both root files and directories;
- `product.required_when_present` is a subset of `product.directories`;
- unknown keys and malformed JSON fail closed.

No wildcard, glob, regex, recursive rule, negative rule, or ordered override semantics are introduced.

## Default Policy

The canonical default file in the supplier framework shall be:

```json
{
  "version": 1,
  "root": {
    "files": [".gitignore", "AGENTS.md", "LICENSE", "README.md"],
    "directories": [".github", "product", "repo", "scripts", "user"]
  },
  "repo": {
    "directories": ["design", "planning", "scripts", "specs", "src", "validation"]
  },
  "product": {
    "directories": ["design", "planning", "scripts", "specs", "src", "validation"],
    "required_when_present": ["design", "scripts", "specs", "validation"]
  }
}
```

Framework-generated arrays use canonical lexicographic order. Validation does not assign semantic meaning to array ordering.

## Structural Enforcement

`validate_structural_paths()` consumes validated policy data rather than concrete hardcoded sets.

- root files must be authorized by `root.files`;
- root directories must be authorized by `root.directories`;
- direct children of `repo/` must be authorized by `repo.directories` and be directories;
- direct children of `product/` must be authorized by `product.directories` and be directories;
- when maintained `product/` exists, all `product.required_when_present` roles must be present;
- nested content below authorized roles remains extensible unless another requirement constrains it.

Policy authorization names structural roles only. It does not assign semantic ownership or meaning.

## Installed Repository Adaptation

The policy is installed repository configuration, not immutable supplier code.

An installed repository may intentionally modify concrete authorized-entry values through its own lifecycle. Such a repository may authorize additional valid root or ownership-tree entries while all undeclared entries remain denied.

A changed policy does not modify the reusable Validation implementation and does not by itself create the Design/Planning justification for the added role.

## Framework Source Relationship

Repository-local policy values may differ from supplier defaults without making the reusable framework implementation a fork. Framework source identity continues to identify the supplying reusable framework revision rather than asserting byte identity for repository-owned configuration values.

## Product Boundary

How the repo-spec initializer seeds the supplier policy and how repository upgrade reconciles target-specific values are product behaviors. They are specified by product FS-004, not by this framework Functional Set.

## Validation Construction

Extend the existing `repository-structure` and `framework-regression` tasks. Do not create a parallel structural Validation task family.

## Planning-to-Build Activation

All FS-005 `M`/`B` requirements are initially inactive. Build activates each only in the same candidate that implements its real predicate and adds its real framework Requirement Evaluation Manifest binding.

## Validation

Before commit:

- focused policy parser/enforcement regressions;
- canonical `scripts/validate`;
- `git diff --check`.

Semantic Review verifies default-deny preservation and absence of policy-as-authority drift.
