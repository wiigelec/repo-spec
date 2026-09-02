# FS-001 Plan — Minimal Repository Initialization

## Technical Objective

Implement the smallest local initializer that can create a mechanically valid, independently usable repo-spec repository from the current accepted framework source.

The implementation should remain project-native and direct. Historical repo-specv0 behavior is reference evidence, not an implementation contract.

## User Interface

Provide the normal local command:

```text
product/scripts/repo-spec init --repo <destination>
```

The destination path is the only normal-user initialization argument in this Functional Set.

The command executes from a repo-spec checkout. It derives supplying-source information from the checkout that actually contains and runs the initializer rather than requiring the user to provide a source repository, framework SHA, product identity, or initialization manifest.

Lower-level internal interfaces may exist when useful to Build or tests, but they do not replace this normal user path.

## Supplying Checkout

The initializer accepts only a supplying checkout whose repository and revision can be identified accurately enough to establish the source relationship required by Design.

For FS-001, the supplying checkout shall be clean with respect to maintained framework material used for initialization.

The supplying revision shall be an accepted repo-spec revision represented by a Git commit in the accepted `main` history available to the supplying checkout.

The normal initialization command shall reject an executing revision whose accepted status cannot be established unambiguously from repository state available to the checkout.

This acceptance check applies to the normal user initialization path. Build may provide controlled internal test seams needed to exercise candidate implementation before that implementation itself is accepted.

Build may choose the smallest reliable Git checks that establish these conditions.

## Destination Admissibility

The destination may be absent or may be an existing empty directory.

FS-001 rejects a destination containing pre-existing material rather than attempting reconciliation, overwrite, merge, or interpretation of that material.

The initializer shall not delete pre-existing destination content to make the destination admissible.

Parent directories may be created when necessary.

## Initialized Material

The initialized repository shall contain the reusable framework and repository-root operational material required for ordinary lifecycle use.

Initializer-product-owned Design, Planning, specifications, implementation, scripts, or validation from the supplying repository shall not be installed as target-product state.

User-owned operational handoff material may be seeded only where current repository behavior explicitly defines seed-on-initialization semantics.

The implementation shall derive the installed material from current accepted repository ownership rather than from repo-specv0 inventories.

## Product Readiness

The result shall establish the generic `product/` ownership domain in the form needed to begin Product Design without inserting repo-spec initializer semantics into that target repository.

No product identity, product Design document, product Planning Functional Set, or product normative requirement shall be invented for the target repository.

## Git Bootstrap

The destination shall become a Git repository capable of supporting the installed repo-spec lifecycle.

FS-001 does not require historical Git object identity to match the supplying repository.

Build owns the specific bootstrap commit sequence and low-level Git plumbing, subject to the requirement that the resulting accepted state accurately contains the installed framework material and source relationship.

## Source Relationship

The initialized repository shall retain the exact supplying repo-spec revision using the smallest repository-native representation sufficient for later interpretation and maintenance.

Planning does not introduce a provenance subsystem.

Build should prefer ordinary Git or a small maintained framework-owned record if Git alone cannot make the source relationship recoverable in the initialized repository.

If implementation reveals that the representation itself carries consequential semantic meaning not determined here, return that decision to Planning or Design rather than inventing a generalized lineage model.

## Validation Composition

Initialization shall validate the actual initialized destination before reporting success.

At minimum, the destination's canonical reusable-framework validation must pass.

Initializer-specific mechanically decidable obligations shall also be tested by product-owned validation.

FS-001 intentionally does not predetermine a generalized repository-wide validation plugin architecture. Build shall use the smallest composition mechanism needed to run the product checks and the initialized repository's canonical framework validation.

If a reusable cross-product validation-composition abstraction becomes necessary rather than merely convenient, route that need upstream instead of hiding it in initializer implementation.

## Failure Behavior

A failure before successful completion shall return non-zero status and shall not report the destination as successfully initialized.

For an initially absent destination, Build should avoid leaving a misleading partial repository after failure where practical.

For an initially empty existing directory, failure shall not destroy unrelated parent or sibling state.

Detailed cleanup mechanics remain a Build decision as long as the observable success/failure semantics are preserved.

## Implementation Freedom

Build owns:

- implementation language and module organization;
- file-copy or materialization strategy;
- temporary/staging technique;
- Git command sequence;
- source-revision discovery mechanics;
- destination cleanup mechanics;
- exact product-validation test layout; and
- internal function and lower-level command interfaces.

These choices shall not create additional product semantics or generalized framework architecture.

## Validation

Planning expects Build to provide task-specific regression coverage for at least:

- successful initialization into an absent destination;
- successful initialization into an empty directory;
- refusal of a non-empty destination;
- refusal when supplying source state cannot support truthful initialization;
- refusal when the executing supplying revision is not established as accepted;
- exclusion of initializer-product semantics from target `product/`;
- accurate source-revision retention;
- successful canonical validation inside the initialized destination;
- failure propagation when initialized-destination validation fails; and
- ordinary independent lifecycle operation without access to the supplying working tree.

Before Acceptance, also run the repository's canonical validation and `git diff --check`.
