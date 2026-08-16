# Derived-repository upgrade architecture audit

## Audit target

The analysis examined the current repo-spec initializer and validation architecture together with generated repository `wiigelec/test-repo`.

`test-repo` records initialization from repo-spec revision `b221de3b8f8ec44bea5eab9c0720a3c08ff7ed04`, while repo-spec subsequently accumulated substantial repository-framework changes.

## Existing reusable architecture

### Exact source-revision resolution

Initializer source resolution already requires an exact clean Git commit and reads framework material inventory from that commit.

### Stable material keys and destination inventory

`framework-inventory.json` identifies source material by stable `material_key`, source path, role, operation, type, and mode.

`initializer-output-inventory-v1.json` maps those same keys to generated-repository destination paths.

Together they already form the basis of a source-side upgrade inventory:

`material_key -> source path -> destination path -> role -> operation -> mode`

### Staging and validation lifecycle

Initialization already establishes an isolated same-filesystem staging workspace, validates the candidate repository, gates promotion on validation success, and finalizes afterward.

### Generated repository provenance

Generated repositories retain the exact repo-spec framework revision used for initialization.

## Existing shortcomings

### Root-commit immutability blocks legitimate upgrade

Initialized-repository validation currently treats the root commit's `repo/` tree as the permanent baseline. Any legitimate later `repo/` change fails validation until the anchoring model changes.

### Bootstrap preflight requires an absent destination

Upgrade targets an existing nonempty repository, so it needs an upgrade-specific preflight.

### Promotion is creation-oriented

Current promotion is designed for an absent destination. Upgrade needs safe promotion of an existing repository.

### Provenance has no current-framework concept

Original initialization provenance exists, but there is no later accepted framework anchor or upgrade history.

### Repo-owned behavior projects outside `repo/`

Repository-owned GitHub profile sources under `repo/profiles/github/` install adapters under `.github/`. Updating only `repo/` can leave those projections stale.

### Product validation is already framework material

The initializer deliberately propagates product validation scripts and support modules, matching the expected exceptional `product/` upgrade boundary.

### No upgrade-specific inventory semantics

Bootstrap inventory lacks revision applicability, dependency closure, removal/retirement, rename/retarget semantics, compatibility requirements, upgrade classification, and local-modification policy.

### No target-local modification model

Bootstrap writes into an empty candidate. Upgrade must reason about user changes to managed files.

## Architectural consequence

The core problem is preserving a trustworthy relationship among the supplying repo-spec revision, managed framework material, the target's accepted framework anchor, subsequent product-owned work, and the staged prospective upgraded state.
