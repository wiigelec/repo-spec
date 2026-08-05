# Repo-Spec Initializer

## Request intake

The initializer accepts initialization requests as local JSON documents.

### Command

```text
scripts/repo-spec-init validate-request <request.json>
```

`validate-request` performs request parsing and validation only. It does not create or modify the destination, initialize Git, contact a hosting platform, or perform any generation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Request is valid and produces a normalized execution context. |
| 1      | Request is invalid, malformed, contradictory, or unsupported. |

### Request schema (version 1)

#### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Request schema version. Must be `"1"`. |
| `destination` | string | Filesystem path for the initialized repository. Must be non-empty. |
| `authority` | object | Granted initialization authority. Must contain `granted_by` (non-empty string). |

#### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | object | Source repository identity. May contain `repository` (string) and `revision` (string). If `revision` is supplied, `repository` is required. |
| `profile` | string | Execution or platform profile identifier. Supported: `"standard"`. |
| `product` | object | Product identity hints. May contain `id` (string) and `direction_material` (list of strings). |
| `deferred` | array of strings | Field names explicitly deferred. Items must be optional field names. Required fields cannot be deferred. |
| `metadata` | object | Arbitrary metadata preserved for diagnostics or provenance handoff. |

#### Unknown fields

Unknown fields are rejected.

#### Examples

Minimal valid request:

```json
{
  "schema_version": "1",
  "destination": "/path/to/new-repo",
  "authority": {
    "granted_by": "issue-189"
  }
}
```

Full request:

```json
{
  "schema_version": "1",
  "destination": "/path/to/new-repo",
  "authority": {
    "granted_by": "issue-189"
  },
  "source": {
    "repository": "https://github.com/wiigelec/repo-spec",
    "revision": "4cde78952bb854d0c8893f80c13f0dc8ed895791"
  },
  "profile": "standard",
  "product": {
    "id": "my-product",
    "direction_material": ["/path/to/overview.md"]
  },
  "metadata": {
    "requestor": "automation"
  }
}
```

### Validation behavior

* Required fields must be present and have valid types.
* Unknown fields are rejected.
* Contradictory authority or source information is rejected.
* Unsupported profile values are rejected.
* Required fields cannot be deferred.
* Deferred fields must be recognized optional field names.
* Product direction material items must be non-empty strings.
* Schema version must be `"1"`.
* Diagnostics are deterministic.
* No destination mutation occurs during validation.

## Framework inventory and source inspection

The initializer maintains a machine-readable reusable-material inventory that classifies every repository path by role. Source inspection validates the request, resolves source selection, loads and validates the inventory, and reports classified material.

### Command

```text
scripts/repo-spec-init inspect-source <request.json>
```

`inspect-source` performs request parsing and validation, validates source identity and revision, loads and validates the framework inventory, and emits deterministic inspection output. It performs no destination mutation, copying, rendering, generation, Git mutation, or hosting-platform operation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Request, source, and inventory are valid. Inspection output is emitted to stdout. |
| 1      | Invalid request, missing or contradictory source, invalid inventory, or I/O error. |

### Inspection output

Output is a JSON object with:

* `status` — `"inspection_complete"` on success.
* `source_selection` — object with `repository` and `revision`, or `null` when no source is requested.
* `classifications` — object mapping classification names to arrays of inventory entries.

Each entry reports:

* `path` — repository-relative path.
* `authoritative` — whether this is authoritative source material.
* `installable` — whether the entry is eligible for installation.
* `profile` — applicable platform profile, if any.
* `exclusion_rationale` — explanation when the entry is excluded or uninstallable.
* `derived_from` — authoritative source paths for derived material.

### Material classifications

| Classification | Role | Installable | Example |
|----------------|------|-------------|---------|
| `framework-authoritative` | Reusable authoritative repository-framework source | Yes | `specs/repo/`, `schemas/` |
| `framework-support` | Reusable tooling or support content | Yes | `scripts/`, `AGENTS.md` |
| `derived` | Generated or projected content | Yes | `derived/` |
| `profile-source` | Reusable source selected only by explicit platform profile | No | `profiles/github/` |
| `installed-adapter` | Current repository adapter content | No | `.github/` |
| `product-instance` | Product-specific direction, planning, or specification content | No | `docs/overview/`, `docs/plans/` |
| `development-state` | Non-source workflow state | No | `.gitignore` |
| `excluded` | Content unavailable to initializer installation | No | `reference/`, `src/` |

Classification does not itself authorize copying or installation.

### Inventory file

The maintained inventory is at `scripts/initializer/framework-inventory.json`. It is a JSON document containing:

* `schema_version` — must be `"1"`.
* `inventory_scope` — descriptive scope identifier.
* `entries` — array of inventory entry objects.

Each entry contains:

* `path` (required) — repository-relative source path.
* `classification` (required) — one of the recognized material classifications.
* `authoritative` (boolean) — whether the entry is authoritative source.
* `installable` (boolean) — whether the entry may be installed.
* `profile` (string, optional) — platform profile identifier for profile-controlled material.
* `exclusion_rationale` (string, optional) — explanation for excluded or uninstallable entries.
* `derived_from` (array, optional) — authoritative source paths for derived entries.

### Source selection rules

* Source selection requires explicit `repository` and `revision` in the request.
* When both are absent, selection remains `null` without error.
* When only `revision` is supplied without `repository`, selection fails.
* When only `repository` is supplied without `revision`, selection fails.
* Empty repository or revision values are rejected.
* No branch, default revision, checkout, or network state is silently inferred.

## Framework staging

The initializer can materialize inventory-selected reusable framework material into an isolated staging workspace without modifying the requested destination.

### Command

```text
scripts/repo-spec-init stage-framework <request.json> [--staging-parent <dir>]
```

`stage-framework` performs request parsing and validation, validates source identity and revision, loads and validates the framework inventory, selects only installable reusable framework entries, creates a new isolated staging workspace, copies authorized material into it, and emits deterministic installation output. It performs no destination mutation, Git mutation, network access, or hosting-platform operation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Staging completed successfully with machine-readable output to stdout. |
| 1      | Invalid request, missing source, invalid inventory, staging error, or I/O error. |

### Staging behavior

* A new staging workspace is created under a temporary directory (or under `--staging-parent` if supplied).
* The workspace name begins with `repo-spec-stage-`.
* Only entries classified as `framework-authoritative`, `framework-support`, or `derived` and marked `installable: true` in the maintained framework inventory are selected.
* Repository-relative paths are preserved in the staging workspace.
* Regular files and directories are copied using deterministic traversal.
* Symbolic links are preserved only when their targets remain within the source root.
* The requested destination is not created or modified.

### Source path safety

The following conditions cause the specific entry to be rejected (not staged) while other entries continue:

* Source path does not exist in the source tree.
* Source path is absolute (`/absolute/path`).
* Source path performs parent-directory traversal (`../outside`).
* Source path resolves outside the source root.
* Source path is an unsupported filesystem entry type.
* Symbolic link target is absolute (`/etc/passwd`).
* Symbolic link target resolves outside the source root.
* Preexisting nonempty staging workspace is rejected with an error.

### Staging output

Output is a JSON object with:

* `status` — `"staging_complete"` on success.
* `source_selection` — object with `repository` and `revision`.
* `staging_workspace` — absolute path to the created staging workspace.
* `installed` — array of staged entries, each with `path`, `classification`, and `type`.
* `skipped` — array of entries skipped during staging (with `path` and `reason`).
* `rejected` — array of entries rejected during staging (with `path`, `classification`, and `reason`).

### Failure semantics

* If staging fails before any entries are copied, the incomplete workspace is cleaned up.
* If an entry copy fails, the entry is reported in `rejected` and other entries continue.
* A preexisting nonempty staging workspace causes an immediate error without modification.

## Product foundations

The initializer can establish project-specific product-direction, planning, and specification foundations in the staging workspace alongside reusable framework material.

### Prerequisites

Product-foundation establishment requires:

* A nonempty explicit `product.id` in the request.
* A nonempty `product.direction_material` array of source references.
* An explicit source selection (the same source used for framework staging).
* A completed framework staging workspace.

The supplied direction material is preserved without semantic expansion. Product semantics are not invented.

### Command

```text
scripts/repo-spec-init stage-framework-and-foundations <request.json> [--staging-parent <dir>]
```

This command combines framework staging and product-foundation establishment in one bounded operation. It performs request validation, product-foundation prerequisite validation, source and inventory validation, framework staging, and foundation generation, then emits deterministic combined output.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Staging and foundations completed successfully with machine-readable output to stdout. |
| 1      | Invalid request, missing prerequisites, source or inventory error, staging error, or foundation generation error. |

### Generated foundations

The command creates the following structure in the staging workspace:

* `docs/overview/<slug>-OVERVIEW.md` — product overview controlling document (candidate lifecycle)
* `docs/overview/<slug>-overview/` — overview subordinate chunk directory with 6 placeholder chunks
* `docs/decompositions/<slug>-DECOMPOSITION.md` — product decomposition controlling document (candidate)
* `docs/decompositions/<slug>-decomposition/` — decomposition subordinate chunk directory with 4 placeholder chunks
* `docs/plans/<slug>-IMPLEMENTATION-PLAN.md` — implementation plan controlling document (candidate)
* `docs/plans/<slug>-implementation-plan/` — plan subordinate chunk directory with 4 placeholder chunks
* `specs/product/manifest.json` — product manifest (candidate, empty specification registry)
* `specs/product/level-0/` through `specs/product/level-3/` — product-specification level roots
* Root `README.md` discoverability links under `docs/overview/`, `docs/decompositions/`, `docs/plans/`

where `<slug>` is derived from the product ID (lowercased with non-alphanumeric characters replaced by hyphens).

### Product identity and lifecycle

* Generated controlling documents use `lifecycle_status: "candidate"` because substantive successor content is not yet reviewed or accepted.
* The product overview uses `overview_role: "initial"` with bootstrap authority recorded in its metadata.
* Supplied `direction_material` paths appear in the overview metadata `evidence` field.
* The governing issue reference from the request authority is recorded in generated metadata.
* Chunks contain placeholder content indicating that governed successor work is required.

### Foundation output

The combined command output is a JSON object with:

* `status` — `"stage_and_foundations_complete"` on success.
* `installation` — the framework staging result (see staging output above).
* `foundations` — the foundation result object with:
  * `status` — `"foundations_complete"`
  * `product_id` — the explicit product identifier
  * `product_slug` — the derived slug
  * `created` — array of created foundation paths with artifact type
  * `preserved` — array of preexisting paths left unchanged
  * `omitted` — array of intentionally omitted foundation paths
  * `deferred` — array of deferred foundation paths
  * `rejected` — array of foundation paths that could not be created

### Failure semantics

* Missing or empty `product.id` fails explicitly before any staging or generation.
* Missing or empty `product.direction_material` fails explicitly.
* If framework staging fails, no foundation generation is attempted.
* If a foundation artifact already exists in staging, it is reported in `rejected` and not overwritten.
* Pre-existing staging workspace failures follow the same rules as framework staging.

## Destination preflight and promotion

The initializer inspects and classifies the requested destination before mutation and promotes staged content using a bounded transaction.

### Destination preflight

Destination state is classified before any mutation. The preflight check verifies that staging and destination paths do not alias one another, that neither path contains the other, that the staging workspace exists and is a directory, and that the destination state is supported.

**Supported destination states:**

| State | Allowed | Description |
|-------|---------|-------------|
| `absent` | Yes | Destination does not exist; parent directory must exist |
| `empty_directory` | Yes | Destination is an existing empty directory |
| `nonempty_directory` | No | Destination exists and contains files or subdirectories |
| `regular_file` | No | Destination is a regular file |
| `symlink` | No | Destination is a symbolic link |
| `unsupported` | No | Device, socket, FIFO, or other unsupported entry type |
| `inaccessible` | No | Destination cannot be read or parent does not exist |

**Path safety checks:**

* Staging and destination must not be the same resolved path.
* Staging must not be inside the requested destination.
* Destination must not be inside the staging workspace.
* Equivalent resolved paths reached through symbolic links are rejected.
* Cross-device promotion (staging and destination on different filesystems) is rejected.

### Commands

```text
scripts/repo-spec-init preflight-destination <staging-path> <dest-path>
```

Runs destination preflight only. Returns 0 when the destination is safe for promotion, 1 when rejected. Machine-readable JSON output includes classification, decision, and rejection reason.

```text
scripts/repo-spec-init promote <staging-path> <dest-path>
```

Promotes a completed staging workspace to the requested destination using a bounded transaction with explicit prepare, commit, and failure states. Returns 0 on successful commit, 1 on failure.

```text
scripts/repo-spec-init stage-and-promote <request.json> [--staging-parent <dir>]
```

Combines framework staging, product-foundation establishment, and destination promotion in one bounded operation.

```text
scripts/repo-spec-init promote-staging <request.json> --staging-path <dir>
```

Promotes an explicitly identified completed staging result to the destination specified in the request.

### Exit status (promotion)

| Status | Meaning |
|--------|---------|
| 0      | Promotion committed successfully. Staging workspace is consumed. |
| 1      | Preflight rejected, prepare failed, or commit failed. Staging workspace is preserved. |

### Transaction phases

| Phase | Meaning |
|-------|---------|
| `preflight` | Destination classified and checked before mutation |
| `prepared` | Destination prepared (parent created or empty directory moved aside) |
| `committed` | Staging renamed to destination; promotion complete |
| `failed` | Transaction failed; destination restored or left in explicit failed state |
| `rolled_back` | Destination explicitly restored to prior state |

### Atomicity

Same-filesystem promotion uses `os.rename()` for an atomic final commit at the destination boundary. Cross-device promotion is rejected before destructive mutation — no recursive non-atomic fallback is used.

### Failure semantics

* Failure before prepare leaves the destination unchanged.
* Failure during prepare leaves staging preserved.
* Failure during commit restores the prior destination state (empty directory case) or leaves an explicit failed state.
* Failed or partial output never reports a successful status.
* Staging workspace is preserved for retry or diagnosis when commit has not succeeded.
* Staging workspace is consumed only after successful commit.

### Retry behavior

After a failed promotion (preflight rejection), the caller may correct the destination state and retry. After a prepare or commit failure, the staging workspace remains intact for diagnosis. There is no automatic retry.

## Git establishment

The initializer can establish a local Git repository in a successfully promoted destination, creating exactly one deterministic root commit with the promoted repository content.

### Prerequisites

* A successfully promoted destination (promotion status `"success"`).
* The promoted destination must exist as a regular directory.
* The Git executable must be available (minimum version 2.5.0).
* The destination must not already be a Git repository or inside an outer Git worktree.

### Commands

```text
scripts/repo-spec-init git-preflight <dest-path>
```

Runs Git-specific preflight checks against the destination without performing any mutation. Returns 0 when the destination is safe for Git establishment, 1 with a JSON report when rejected. Checks include:

* Destination exists and is a directory.
* Destination is not a symbolic link.
* Destination does not already contain a `.git` file or directory.
* Destination is not inside an outer Git worktree.
* Git executable is available and meets the minimum version requirement.

```text
scripts/repo-spec-init git-establish <dest-path>
```

Establishes a local Git repository in the destination with a single deterministic root commit. Returns 0 on success, 1 on failure. JSON output provides the establishment result.

```text
scripts/repo-spec-init stage-promote-and-git <request.json> [--staging-parent <dir>]
```

Combines framework staging, product-foundation establishment, destination promotion, and Git establishment in one bounded end-to-end operation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0 | Git establishment succeeded. Repository has one root commit on the initial branch with a clean worktree. |
| 1 | Preflight rejected, initialization failed, staging failed, commit failed, or verification failed. |

### Deterministic commit behavior

The initializer creates a deterministic first commit using:

| Property | Default value |
|----------|---------------|
| Initial branch | `main` |
| Author name | `Repo-Spec Initializer` |
| Author email | `initializer@repo-spec.local` |
| Committer name | Same as author (unless explicitly overridden) |
| Committer email | Same as author (unless explicitly overridden) |
| Author timestamp | `1234567890 +0000` (bootstrap epoch) |
| Committer timestamp | `1234567890 +0000` (bootstrap epoch) |
| Commit message | `Initial repository foundation` |

All identity and timestamp values are fixed and repository-local. Global Git configuration is not read or modified. Equivalent fixed inputs produce the same commit tree and, because timestamps are also fixed, the same root commit identity.

### Git establishment phases

| Phase | Meaning |
|-------|---------|
| `preflight` | Checks performed before any Git mutation |
| `initialized` | `git init` completed with explicit initial branch |
| `indexed` | `git add -A` staged the promoted content |
| `committed` | `git commit` created the root commit |
| `verified` | Post-commit checks passed (branch, commit count, parent count, clean worktree, no remotes) |
| `failed` | An unrecoverable error occurred |
| `cleaned` | Incomplete `.git` metadata removed after failure |

### Failure semantics

* Failures before `git init` leave the destination unchanged.
* Failures during `git add` or before a valid commit cause removal of the incomplete `.git` directory only. Promoted repository content is never altered.
* Failures during post-commit verification preserve the valid root commit.
* Failed or partial Git establishment never reports success.
* No remote, hook, signing configuration, submodule, LFS state, or platform configuration is introduced.

### Establishment output

Successful output is a JSON object with:

* `status` — `"success"`
* `phase` — `"verified"`
* `destination_path` — absolute path to the initialized repository
* `git_version` — the detected Git version string
* `initial_branch` — the created initial branch name
* `root_commit` — the full SHA of the root commit
* `commit_tree` — the tree object SHA of the root commit
* `author_identity` — the commit author identity
* `committer_identity` — the commit committer identity
* `timestamps` — the author and committer timestamps
* `commit_message` — the commit message
* `staged_path_count` — number of paths staged
* `worktree_clean` — `true`
* `remote_count` — `0`
* `completed_phases` — list of completed phases

Failed output includes `status: "failed"`, the `phase` where failure occurred, and a `failure_reason` string.

### Exclusions

Git establishment in this bounded increment does not:

* Create or configure a Git remote.
* Access a network.
* Create a hosting-platform repository.
* Apply platform profiles or install platform adapters.
* Create additional branches or tags.
* Create signed commits or discover signing keys.
* Modify global or system Git configuration.
* Read the operator's implicit global author identity.
* Install Git hooks, submodules, or LFS.
* Perform sparse checkout or create worktrees.
* Alter generated repository content to make Git commands succeed.
* Repair an existing partially initialized `.git` directory.
* Validate the generated repository semantically.
* Record final provenance or create a handoff document.
* Claim that the root commit constitutes semantic acceptance.

### Maintainer notes

The initializer code lives in `scripts/initializer/`. The shell wrapper is `scripts/repo-spec-init`.

Destination and promotion modules:

* `scripts/initializer/models.py` — `DestinationPreflight`, `PromotionPlan`, `PromotionResult`, and related immutable models
* `scripts/initializer/destination.py` — destination classification, path safety, and preflight
* `scripts/initializer/promotion.py` — transactional promotion with prepare, commit, cleanup, and restore
* `scripts/initializer/validation.py` — `validate_product_foundation_prerequisites`

Git establishment modules:

* `scripts/initializer/git.py` — Git preflight, environment sanitization, repository initialization, deterministic commit, post-commit verification, failure cleanup, and establishment reporting
* `scripts/initializer/models.py` — `GitPreflight`, `GitCommandResult`, `GitEstablishmentPlan`, `GitEstablishmentResult`, and `GitEstablishmentPhase` immutable models

To run the initializer test suite directly:

```text
python3 -c "import sys; sys.path.insert(0, 'scripts'); from initializer.tests.run_tests import run_initializer_tests; from pathlib import Path; run_initializer_tests(Path.cwd())"
```

Initializer tests are also integrated into `scripts/validate --mutation-tests`.

### Deferred content

The following product content is intentionally deferred (requires governed successor work):

* Substantive product overview content beyond supplied direction material.
* Product-area decomposition decisions.
* Implementation workstream planning and execution ordering.
* Product specifications at any Level.
* Product-specification correspondence declarations.
* Derived product projections.
* Platform-profile selection or application.
* Hosting-platform adapter installation.
* Final generated-repository validation.
* Provenance recording.
* Initializer completion or handoff.
