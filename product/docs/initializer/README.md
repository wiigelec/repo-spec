# Repo-Spec Initializer

## Normal human workflow

The supported normal-user initialization command is:

```text
product/scripts/repo-spec-init --request request.json
```

It consumes the canonical JSON initialization request and runs the accepted full initialization lifecycle. JSON remains the input boundary: conversational text or AI-generated prose is not an initializer input mode.

### Recommended human + AI-agent workflow

An AI coding agent can inspect the current checkout, read the current request contract, and assemble JSON from facts you supply. That assistance does not grant initialization authority.

1. Open the repo-spec checkout that will supply the initializer.
2. Ask the agent to inspect the current checkout, this reference, and the current initialization-request contract.
3. Supply explicit facts for destination, product identity, product direction material, source repository and exact revision when used, execution profile, and initialization authority.
4. Ask the agent to construct `request.json` without inferring, synthesizing, or silently defaulting authority-bearing values.
5. Have the agent show the complete JSON and explain its choices.
6. Review the request yourself; correct it or supply missing facts before execution.
7. Run `product/scripts/repo-spec-init --request request.json`.
8. Read the human terminal outcome and inspect the resulting repository and canonical records.

A useful agent instruction is:

> Inspect the current repo-spec checkout and its accepted initializer request contract. Construct a canonical `request.json` using only facts I explicitly provide. Do not infer or choose authority-bearing values for me, including destination, product ID, direction material, source repository, exact source revision, execution profile, or initialization authority. Identify missing required facts instead of filling them in. Show the complete request and explain it before execution. Do not run the initializer. I will review the file and then run `product/scripts/repo-spec-init --request request.json`.

The durable initializer authority is the reviewed canonical request and its explicit authority data, not the preceding conversation and not an unreviewed AI draft.

### What the normal workflow creates

On successful full initialization, the initializer prepares and validates the repository in staging, promotes it to the requested destination, and establishes the accepted initial Git state. The initialized repository includes reusable repo-spec framework material plus product foundations derived from the explicit request, including the product overview, decomposition, implementation plan, product specification roots, and provenance/handoff records.

After success, review those generated foundations before treating later product direction or specification content as accepted successor authority.

### What the normal workflow does not do

The normal initializer does not provide interactive request prompts, infer a product ID, select a source or revision for you, accept a branch name in place of required revision identity, provide dry-run or status behavior, resume a failed initialization, overwrite or migrate an existing nonempty repository, or perform remote/cloud/platform-integrated initialization.

The lower-level commands documented below are intentional diagnostic or development interfaces. They are not the recommended first-use path. Commands retained only as explicit unavailable/fail-closed compatibility surfaces are not supported normal-user operations.


## Request intake

The initializer accepts initialization requests as local JSON documents.

### Command

```text
product/scripts/repo-spec-init validate-request <request.json>
```

`validate-request` performs request parsing and validation only. It does not create or modify the destination, initialize Git, contact a hosting platform, or perform any generation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Request is valid and produces a normalized execution context. |
| 1      | Request is invalid, malformed, contradictory, or unsupported. |

### Request schema (version 1)

The bounded full-initialization request has a closed root shape.

#### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Request schema version. Must be `"1"`. |
| `destination` | string | Filesystem path for the initialized repository. |
| `authority` | object | Initialization authority. Requires non-empty `granted_by`; optional `type` and `scope` are permitted. |
| `source` | object | Explicit local source identity. Requires `repository` and structured `revision`. |
| `product` | object | Explicit product identity. Requires `id` and nonempty `direction_material`. |

#### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `profile` | string | Execution profile. When supplied, must be `"standard"`. |

No other root fields are accepted.

`source.repository` is a local filesystem path. `source.revision` is an exact Git object identity object with `object_format: "sha1"` and a 40-character lowercase hexadecimal `object_id`. Branch names, named refs, remote URLs, and inferred source identities are not accepted.

Each `product.direction_material` item is a non-empty repository-relative path. During source-material resolution each item must name an existing regular file in the exact source revision.

#### Complete valid request

```json
{
  "schema_version": "1",
  "destination": "/tmp/new-repo",
  "authority": {
    "granted_by": "issue-332"
  },
  "source": {
    "repository": "/work/repo-spec",
    "revision": {
      "object_format": "sha1",
      "object_id": "0123456789abcdef0123456789abcdef01234567"
    }
  },
  "product": {
    "id": "my-product",
    "direction_material": [
      "README.md"
    ]
  },
  "profile": "standard"
}
```

The example demonstrates the accepted request representation. For an actual run, replace the destination, local source path, exact commit object ID, authority, product ID, and direction material with reviewed values from the source repository being initialized.

### Validation behavior

* Every required root field must be present and structurally valid.
* Unknown root and nested fields are rejected.
* `authority.granted_by`, `product.id`, and each direction-material entry must be non-empty.
* `source.repository` must identify a local filesystem path, not a URL or remote identity.
* `source.revision` must use the structured SHA-1 object identity.
* `product.direction_material` must be nonempty and preserves supplied order and duplicates.
* Unsupported profile values are rejected.
* Schema version must be `"1"`.
* Diagnostics are deterministic.
* No destination mutation occurs during request validation.

## Framework inventory and source inspection

The initializer maintains a machine-readable reusable-material inventory that classifies every repository path by role. Source inspection validates the request, resolves source selection, loads and validates the inventory, and reports classified material.

### Command

```text
product/scripts/repo-spec-init inspect-source <request.json>
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
| `framework-authoritative` | Reusable authoritative repository-framework source | Yes | `repo/specs/repo/`, `schemas/` |
| `framework-support` | Reusable tooling or support content | Yes | `repo/scripts/`, `AGENTS.md` |
| `derived` | Generated or projected content | Yes | `derived/` |
| `profile-source` | Reusable source selected only by explicit platform profile | No | `repo/profiles/github/` |
| `installed-adapter` | Current repository adapter content | No | `.github/` |
| `product-instance` | Product-specific direction, planning, or specification content | No | `repo/docs/overview/`, `repo/docs/plans/` |
| `development-state` | Non-source workflow state | No | `.gitignore` |
| `excluded` | Content unavailable to initializer installation | No | `reference/`, `product/src/` |

Classification does not itself authorize copying or installation.

### Inventory file

The maintained inventory is at `product/scripts/initializer/framework-inventory.json`. It is a JSON document containing:

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

The maintained normal workflow performs framework installation inside:

```text
product/scripts/repo-spec-init --request request.json
```

The historical `stage-framework` and `stage-framework-and-foundations` command names are retained only as explicit unavailable/fail-closed compatibility surfaces. They are not supported executable initializer operations.

Maintained diagnostic/development commands exposed by the current CLI include `inspect-source`, `preflight-request`, `establish-staging`, `realize-materials`, and `complete-i2`. They are subordinate diagnostic interfaces, not the normal user workflow.

## Product foundations

The normal full-initialization workflow establishes product foundations from the explicit `product.id`, `product.direction_material`, source identity, and governing authority in the reviewed request. Product semantics are not inferred.

The historical `stage-framework-and-foundations` command is unavailable and must not be used as an operational interface.

### Generated foundations

For product slug `<slug>`, the initialized repository includes product-owned foundation documents under `product/docs/`:

* `product/docs/direction/evidence/` — verbatim positional copies of supplied direction material
* `product/docs/direction/manifest.json` — direction-evidence manifest
* `product/docs/overview/<slug>-OVERVIEW.md` — product overview controlling document
* `product/docs/overview/<slug>-overview/` — overview subordinate chunks
* `product/docs/decompositions/<slug>-DECOMPOSITION.md` — product decomposition controlling document
* `product/docs/decompositions/<slug>-decomposition/` — decomposition subordinate chunks
* `product/docs/plans/<slug>-IMPLEMENTATION-PLAN.md` — implementation-plan controlling document
* `product/docs/plans/<slug>-implementation-plan/` — plan subordinate chunks
* `product/specs/product/manifest.json` — product specification manifest
* `product/specs/product/level-0/` through `product/specs/product/level-3/` — product-specification level roots

The generated controlling documents and chunks are bootstrap foundations for governed successor work. Supplied direction material is installed as evidence without semantic expansion.

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
product/scripts/repo-spec-init preflight-destination <staging-path> <dest-path>
```

Runs destination preflight only. Returns 0 when the destination is safe for promotion, 1 when rejected. Machine-readable JSON output includes classification, decision, and rejection reason.

```text
product/scripts/repo-spec-init promote <staging-path> <dest-path>
```

Promotes a completed staging workspace to the requested destination using a bounded transaction with explicit prepare, commit, and failure states. Returns 0 on successful commit, 1 on failure.

```text
product/scripts/repo-spec-init stage-and-promote <request.json> [--staging-parent <dir>]
```

Combines framework staging, product-foundation establishment, and destination promotion in one bounded operation.

```text
product/scripts/repo-spec-init promote-staging <request.json> --staging-path <dir>
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
product/scripts/repo-spec-init git-preflight <dest-path>
```

Runs Git-specific preflight checks against the destination without performing any mutation. Returns 0 when the destination is safe for Git establishment, 1 with a JSON report when rejected. Checks include:

* Destination exists and is a directory.
* Destination is not a symbolic link.
* Destination does not already contain a `.git` file or directory.
* Destination is not inside an outer Git worktree.
* Git executable is available and meets the minimum version requirement.

```text
product/scripts/repo-spec-init git-establish <dest-path>
```

Establishes a local Git repository in the destination with a single deterministic root commit. Returns 0 on success, 1 on failure. JSON output provides the establishment result.

```text
product/scripts/repo-spec-init stage-promote-and-git <request.json> [--staging-parent <dir>]
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

The initializer code lives in `product/scripts/initializer/`. The shell wrapper is `product/scripts/repo-spec-init`.

Destination and promotion modules:

* `product/scripts/initializer/models.py` — `DestinationPreflight`, `PromotionPlan`, `PromotionResult`, and related immutable models
* `product/scripts/initializer/destination.py` — destination classification, path safety, and preflight
* `product/scripts/initializer/promotion.py` — transactional promotion with prepare, commit, cleanup, and restore
* `product/scripts/initializer/validation.py` — `validate_product_foundation_prerequisites`

Git establishment modules:

* `product/scripts/initializer/git.py` — Git preflight, environment sanitization, repository initialization, deterministic commit, post-commit verification, failure cleanup, and establishment reporting
* `product/scripts/initializer/models.py` — `GitPreflight`, `GitCommandResult`, `GitEstablishmentPlan`, `GitEstablishmentResult`, and `GitEstablishmentPhase` immutable models

To run the initializer test suite directly:

```text
python3 -c "import sys; sys.path.insert(0, 'scripts'); from initializer.tests.run_tests import run_initializer_tests; from pathlib import Path; run_initializer_tests(Path.cwd())"
```

Initializer tests are also integrated into the product-owned validation self-tests run by `scripts/validate`.

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
