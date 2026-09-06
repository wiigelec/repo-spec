# FS-003 Plan — Repository Upgrade

## Technical Objective

Add the smallest safe upgrade operation to the existing initializer implementation.

The implementation shall reuse the current initializer's project-native Git, filesystem, staging, and Validation mechanisms where practical. It shall not introduce a generalized migration framework.

## User-Facing Command

Extend the existing `repo-spec` CLI with:

```text
repo-spec upgrade --repo TARGET
```

The executing repo-spec checkout is the supplying source, consistent with the current initialization command.

The normal user-facing operation requires the supplying checkout HEAD to be an accepted repo-spec revision under the same accepted-source rule used by initialization. Controlled tests may use an internal seam that relaxes this only for fixture construction.

`TARGET` identifies an existing initialized repository and must not be interpreted as a new-repository destination.

## Source and Installed Revision Identification

The prospective supplying revision is the exact 40-character commit identity of the supplying checkout HEAD after normal source verification.

The target's currently installed framework revision is read from:

```text
repo/validation/framework-source.json
```

using its existing `repo_spec_source_revision` field.

Upgrade fails when that record is missing, malformed, ambiguous, or does not identify one exact prior supplying revision.

The current installed revision identifier is not required to exist in the target repository's Git object database.

## Supported Transition Boundary

FS-003 supports a transition only when the recorded currently installed repo-spec revision can be resolved as a commit in the supplying repo-spec checkout.

This is a bounded compatibility requirement for reconstructing the prior supplied framework state; it does not import that commit or its ancestry into the target repository.

If the recorded installed revision cannot be reconstructed from the supplying checkout, the transition is unsupported by FS-003 and upgrade fails explicitly.

A request whose selected supplying revision is the same as the target's recorded installed framework revision is outside this Functional Set's required upgrade behavior. FS-003 does not prescribe a successful same-revision normalization operation.

## Installed Framework Snapshot Model

For reconciliation, Planning distinguishes three states:

1. **prior expected installed state** — the reusable framework snapshot that the recorded old supplying revision would install;
2. **observed target state** — the target repository as it exists before upgrade; and
3. **prospective installed state** — the reusable framework snapshot supplied by the selected new revision.

The snapshot model shall reuse the initializer's installed-framework construction rules rather than infer ownership from matching path names.

Framework-development Planning history remains omitted from installed snapshots where the framework's accepted installation contract omits it.

The framework source record is generated installed state whose revision value differs between prior and prospective snapshots.

## Reconciliation Policy

Framework-owned installed state is reconciled from the prior expected snapshot to the prospective snapshot.

For each framework-owned path:

- unchanged between prior and prospective supplier states: preserve the target only when it still matches the prior expected installed state;
- changed in the prospective supplier state: replace the prior expected value with the prospective value only when the observed target has not independently diverged from the prior expected value;
- newly required prospective framework state: add it when its destination is absent or otherwise safely compatible;
- framework state removed by the prospective supplier: remove it only when the observed target still matches the prior expected framework-owned state.

If observed state within this reconciliation boundary differs from the prior expected installed state in a way that prevents an unambiguous treatment, upgrade fails and reports the conflicting path.

FS-003 does not perform semantic merges of locally modified framework-owned files.

## Ownership Preservation

Upgrade shall not wholesale replace the target `product/` or `user/` domains.

Independently developed product Design, Planning, specifications, implementation, Validation predicates, and other product-owned content are preserved.

User-owned material is preserved.

Repository-root operational surfaces are modified only where the prospective framework requires a mechanically determinable compatibility change and the change can be made without discarding independently intentional content.

Path coincidence with the supplying repo-spec repository is not sufficient authority for mutation.

## Generic Product Compatibility Adaptation

The prospective framework may require canonical generic product lifecycle surfaces.

Upgrade shall mechanically inspect the prospective framework contract and establish only missing generic surfaces required for compatibility.

Existing product-owned surfaces that already satisfy the prospective contract are preserved rather than replaced with initializer starter content.

When a required product compatibility surface is absent and can be created without inventing product meaning, upgrade may create the minimal generic surface.

When satisfying the prospective framework would require rewriting independently developed product meaning or resolving an ambiguous product decision, upgrade fails and reports the incompatibility.

## Repository-Root Compatibility Adaptation

The repository-wide `scripts/validate` composition surface and other root operational surfaces required by the prospective framework may be added or updated only to the extent necessary for the prospective installed framework to operate.

Existing unrelated root content remains preserved.

README and AGENTS content shall not be regenerated wholesale merely because current initialization generates starter versions. Upgrade changes documentation only when a concrete prospective framework compatibility obligation requires it and the change can be made without discarding independent repository meaning.

## Local Modification Detection

Local modification is evaluated against the prior expected installed snapshot, not against the current supplying checkout alone.

A target framework-owned path is locally modified when its maintained observed state differs from the prior expected installed state.

Untracked or additional maintained content inside a framework-owned closed boundary is also treated according to the governing structural contract; unauthorized or ambiguous additions fail upgrade rather than being silently deleted.

Ignored transient local state remains outside maintained-state reconciliation unless a governing requirement says otherwise.

## Prospective Construction

Upgrade shall construct a complete prospective repository in a temporary sibling staging directory.

The stage is based on the target repository's current maintained working-tree state and Git metadata needed for validation, then receives the planned framework reconciliation and bounded compatibility adaptations.

The target working tree is not mutated during prospective construction or Validation.

The staging representation may use a temporary copy plus an independent Git working tree representation or another direct project-native mechanism, but it shall preserve the target's independent repository history semantics.

## Framework Source Record

The staged prospective result writes:

```text
repo/validation/framework-source.json
```

with the exact new supplying revision only after the prospective framework state has been constructed.

The live target source record is not updated before successful promotion.

A failed upgrade therefore cannot truthfully present the prospective revision as currently installed.

## Upgrade Validation Boundary

Upgrade Validation has three required components:

1. validate the prospective installed framework's mechanically decidable obligations;
2. validate the initializer's FS-003 mechanically decidable upgrade obligations; and
3. validate mechanically decidable compatibility conditions the prospective framework requires from repository-root or product-owned lifecycle surfaces.

The implementation shall not require unrelated pre-existing product-development failures to pass merely because upgrade is occurring.

Where repository-wide `scripts/validate` would execute unrelated product predicates, upgrade shall instead run the narrower combination of framework Validation and explicit compatibility checks needed for the transition.

Product-owned predicates are executed only when the prospective framework compatibility contract specifically requires their result for the upgrade.

## Promotion and Failure Atomicity

No live target mutation occurs before prospective construction and required Validation succeed.

After successful Validation, promotion applies the already-validated prospective maintained state to the target with rollback protection sufficient to restore the pre-upgrade authoritative state if promotion itself fails.

Build may use a sibling backup/rename strategy or an equivalently simple project-native mechanism.

Promotion shall preserve target repository identity and history.

Upgrade shall not create supplier commits as target ancestors and shall not force-push or rewrite target history.

If promotion cannot complete safely, upgrade fails and restores the pre-upgrade authoritative repository state.

## Commit Behavior in the Target

FS-003 does not require upgrade to create an Acceptance commit or make an Acceptance decision for the target repository.

Upgrade changes the target working repository state and leaves ordinary target lifecycle review and Acceptance semantics intact.

If implementation requires an internal commit solely to make prospective Validation technically possible, that commit shall not be silently promoted as a new target Acceptance decision.

## Error Reporting

Upgrade errors shall identify the consequential failure class and, where applicable, the conflicting path or revision.

At minimum, distinguish:

- target is not an eligible initialized repository;
- installed source record invalid or missing;
- installed supplier revision unavailable for supported reconstruction;
- prospective supplier revision invalid or unaccepted;
- local framework modification conflict;
- product/root compatibility conflict;
- prospective Validation failure; and
- promotion/rollback failure.

Failure messages need not create a durable migration report.

## Regression Strategy

Build shall add focused regression coverage for at least:

- successful upgrade from an older supported initialized framework to the selected later framework;
- exact source-record transition from old revision to new revision;
- no supplier ancestry imported into target history;
- preservation of independently developed product Design, specifications, implementation, Validation state, and user material;
- addition of newly required framework-owned state;
- update of changed unmodified framework-owned state;
- removal of obsolete unmodified framework-owned state;
- conflict on locally modified framework-owned state;
- conflict on ambiguous required product compatibility change;
- preservation of existing compatible product lifecycle surfaces;
- creation of a missing generic compatibility surface when semantically safe;
- unsupported transition when the old supplying revision cannot be reconstructed;
- malformed or missing framework source record;
- prospective Validation failure leaving the live target unchanged;
- promotion failure restoring the pre-upgrade authoritative state;
- unrelated product Validation failure not blocking a transition when outside the upgrade compatibility boundary;
- CLI success and failure behavior; and
- `git diff --check`.

## Implementation Freedom

Build may factor shared source verification, installed-snapshot construction, Git helpers, staging helpers, and Validation helpers out of the current initialization implementation when doing so reduces duplication without creating generalized infrastructure.

Ordinary function names, module decomposition, temporary-directory layout, copy strategy, and command plumbing remain Build decisions.

## Build Review Focus

Build Review should challenge especially:

- any mutation authority derived merely from path coincidence;
- any wholesale replacement of independently developed `product/`, `user/`, README, or AGENTS state;
- any dependence on supplier ancestry in the target repository;
- any generalized migration/provenance framework;
- any silent merge of locally modified framework state;
- any upgrade gate that accidentally turns unrelated product-development failures into framework-transition failures; and
- any failure path that can leave the target claiming a prospective framework revision that was not fully installed.
