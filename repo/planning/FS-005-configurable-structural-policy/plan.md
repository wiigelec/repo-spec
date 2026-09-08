# FS-005 Plan — Configurable Structural Policy

## Technical Objective

Replace the concrete structural allowlists embedded in `repo/validation/validate_framework.py` with one strict repository-local configuration while retaining exactly the same default-deny enforcement model.

The framework owns:

- the policy schema;
- loading and strict validation of policy data;
- closed-boundary enforcement semantics;
- framework-required structural invariants; and
- initializer/upgrade mechanics needed to keep the policy operable.

The target repository owns the concrete authorized-entry values in its installed policy, subject to current accepted Design and Planning.

Changing an installed repository's structural policy is therefore not an arbitrary runtime bypass. It is a maintained repository change that must be justified by that repository's controlling Design/Planning where the change is consequential.

## Canonical Policy Location

The canonical structural-policy file shall be:

`repo/validation/structure-policy.json`

This location is a framework-defined configuration surface consumed by `repository-structure`. It is not a second normative specification and does not replace Design or Planning.

`repository-structure` shall not contain a fallback copy of the concrete allowlists. Missing or invalid policy fails closed.

## Policy Schema

The file shall use this version-1 JSON shape:

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

- the top-level object contains exactly `version`, `root`, `repo`, and `product`;
- `version` is exactly integer `1`;
- `root` contains exactly `files` and `directories`;
- `repo` contains exactly `directories`;
- `product` contains exactly `directories` and `required_when_present`;
- every collection is a JSON array of unique non-empty strings;
- entries are direct-child names only: no `/`, `\`, `.`, `..`, empty name, absolute path, or path traversal;
- a root name shall not appear in both `root.files` and `root.directories`;
- `product.required_when_present` shall be a subset of `product.directories`;
- unknown keys fail closed;
- malformed JSON fails closed.

No wildcard, glob, regex, recursive rule, negative rule, or ordered override semantics are introduced.

## Default Policy

The accepted default policy shall be semantically identical to the current hardcoded behavior:

```json
{
  "version": 1,
  "root": {
    "files": [
      ".gitignore",
      "AGENTS.md",
      "LICENSE",
      "README.md"
    ],
    "directories": [
      ".github",
      "product",
      "repo",
      "scripts",
      "user"
    ]
  },
  "repo": {
    "directories": [
      "design",
      "planning",
      "scripts",
      "specs",
      "src",
      "validation"
    ]
  },
  "product": {
    "directories": [
      "design",
      "planning",
      "scripts",
      "specs",
      "src",
      "validation"
    ],
    "required_when_present": [
      "design",
      "scripts",
      "specs",
      "validation"
    ]
  }
}
```

Array ordering is canonical lexicographic order in framework-generated policy files. Validation shall not rely on input ordering for meaning.

## Structural Enforcement

`validate_structural_paths()` shall consume validated policy data rather than embed concrete path sets.

For every tracked or untracked non-ignored maintained candidate path:

- repository-root direct files are allowed only when named by `root.files`;
- repository-root direct directories are allowed only when named by `root.directories`;
- direct children of `repo/` are allowed only when named by `repo.directories` and shall be directories;
- direct children of `product/` are allowed only when named by `product.directories` and shall be directories;
- when maintained `product/` exists, every `product.required_when_present` role shall be present;
- nested organization below authorized direct-child roles remains extensible unless another accepted requirement constrains it.

The policy authorizes structural roles only. It does not assign framework, product, runtime, user, or application semantic meaning to an entry merely by listing its name.

## Framework Source Relationship

The reusable Validation implementation remains supplied by the selected framework revision.

The structural-policy file is an installed repository configuration surface. Its concrete authorized-entry values may intentionally differ from the supplier repository's default policy after initialization without making the installed validator code an undocumented fork.

`repo/validation/framework-source.json` continues to identify the supplying framework revision. It does not claim that every repository-local configuration value must remain byte-identical to supplier defaults.

## Initialization

The repo-spec initializer shall:

1. install the reusable framework;
2. seed `repo/validation/structure-policy.json` using the accepted default policy from the supplying framework revision;
3. construct the remaining generic initialized-repository state;
4. run canonical repository Validation against the completed initialized repository; and
5. promote only a valid candidate.

The initializer shall not hardcode a second independent copy of the default policy in implementation logic. The supplier framework shall contain the canonical default policy file, and initialization copies/seeds that file as installed configuration.

## Derived Repository Adaptation

After initialization, a target repository may intentionally change its installed structural policy through that repository's own lifecycle.

Such adaptation may authorize additional root files or directories required by that repository's accepted architecture while preserving default-deny behavior for all undeclared entries.

A consumer such as ADR App Builder may therefore:

1. invoke the exact accepted repo-spec initializer;
2. receive a valid initialized repository;
3. modify the initialized repository's structural policy to add only its accepted repository-specific roles;
4. add the corresponding repository-owned material; and
5. run canonical `scripts/validate` on the completed result.

This adaptation changes repository configuration, not reusable framework Validation code.

## Upgrade

Upgrade shall distinguish:

- supplier framework implementation and schema requirements;
- supplier default policy; and
- target repository's current concrete structural authorization.

For version-1-to-version-1 upgrade where the schema remains compatible:

- preserve target-authorized entries that remain schema-valid;
- ensure all entries required by the prospective framework default/invariants are present;
- add newly framework-required entries;
- do not silently remove target-specific authorized entries merely because they are absent from supplier defaults.

If a prospective framework changes the policy schema incompatibly, upgrade shall use the accepted upgrade semantics for that framework revision. If no accepted reconciliation rule exists, fail and surface the incompatibility rather than resetting or guessing.

Upgrade shall validate the completed candidate with the prospective framework before promotion.

## Validation Construction

Extend existing framework Validation rather than creating a parallel task family.

The existing `repository-structure` task remains the normative mechanical surface for structural closure. Its implementation gains strict policy loading and policy-driven path validation.

Framework regression coverage shall exercise policy parsing directly and through initialized/upgrade repository flows.

## Planning-to-Build Activation

All FS-005 requirements classified `M` or `B` are initially inactive during Planning.

Build shall activate each mechanically evaluated requirement only in the same candidate that:

- implements the real predicate/mechanism;
- removes that requirement's `State: Inactive`; and
- adds the exact existing `repository-structure`, `framework-regression`, or product initializer/upgrade Validation task binding that genuinely evaluates it.

No placeholder binding or vacuous task is permitted.

## Validation

Before commit, Build shall run:

- focused structural-policy parser/enforcement regressions;
- initializer regressions;
- upgrade regressions;
- canonical `scripts/validate`; and
- `git diff --check`.

Semantic Review shall verify that moving concrete authorization into policy has not weakened the closed-boundary meaning or turned configuration into independent normative authority.
