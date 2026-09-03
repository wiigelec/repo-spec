---
doc_id: DP-130
title: Repository Upgrade
depends_on:
  - DP-100
  - DP-110
  - DP-120
---

# Repository Upgrade

## Purpose

Repository upgrade is the transformation performed by the repo-spec initializer product when an already initialized repository intentionally adopts the reusable framework supplied by a later accepted repo-spec revision.

Upgrade exists so an initialized repository can receive maintained framework improvements without being recreated from scratch and without surrendering ownership of the product and user material developed after initialization.

Repository upgrade is distinct from repository initialization.

Initialization establishes a new repository. Upgrade begins from an existing initialized repository whose independent development history and repository-owned material already matter.

## User Intent

A user chooses an existing repo-spec-initialized repository and a repo-spec source revision whose reusable framework they intend that repository to adopt.

The upgrade capability transforms the existing repository from its currently installed framework state to the selected supplying framework state while preserving material outside the framework-managed upgrade boundary.

The initializer shall not interpret the request to upgrade the framework as permission to redesign, regenerate, discard, or reinterpret the repository's independently developed product.

## Existing Repository

An upgrade target is an existing initialized repository rather than a new destination.

The target may contain product Design, Planning, normative specifications, implementation, Validation, accepted history, user-owned material, and other state created after original initialization.

That material remains repository-owned state.

Upgrade shall preserve repository state that is outside the material the initializer is authorized to reconcile.

The mere existence of a similarly named path in a later repo-spec revision does not give upgrade authority over independently owned target-repository material.

## Supplying Framework

Upgrade uses an identifiable repo-spec source revision as the supplier of the prospective framework state.

The selected source shall identify the framework revision actually being supplied.

Upgrade shall not silently substitute another framework revision while representing the result as having adopted the selected one.

The source representation may differ from the representation used during original initialization when Planning can support that difference without changing this meaning.

## Installed Framework Relationship

A repository eligible for upgrade shall retain enough truthful information about its currently installed framework state for the initializer to determine the framework relationship required to perform the upgrade safely.

After successful upgrade, the repository shall truthfully identify the newly installed supplying framework revision as its current framework source.

This source relationship exists to support correct interpretation, maintenance, Validation, and later upgrade.

It does not require a generalized provenance database, framework lineage ledger, imported supplier Git ancestry, evidence graph, hidden remote, graft, replace reference, or other historical authority architecture.

Historical information may remain in ordinary repository history where naturally preserved, but Design does not require a second framework-history system.

## Upgrade Boundary

Upgrade authority is bounded by material that the initializer owns installing and maintaining as reusable framework or generic lifecycle-support state.

Upgrade may reconcile framework-owned material and other initializer-established generic repository surfaces where current Design and Planning identify those surfaces as initializer-managed.

Upgrade shall not use framework maintenance as authority to rewrite arbitrary product-owned or user-owned material.

The managed boundary is semantic rather than merely path-based.

For example, material under `repo/` may ordinarily be framework-owned, while material under `product/` is ordinarily product-owned. If initialization establishes particular generic product-support artifacts that remain initializer-managed, Planning may identify those exact artifacts as upgradeable without making the rest of `product/` upgrade-owned.

Repository-root operational material may likewise be reconciled only where its ownership and initializer-management relationship authorize that action.

## Reconciliation

Upgrade reconciles the currently installed managed framework state with the managed framework state supplied by the selected repo-spec revision.

Reconciliation may require adding newly required managed material, updating changed managed material, removing material that is no longer part of the installed framework, or changing a managed representation where the framework has intentionally evolved.

The result shall correspond coherently to the selected supplying framework revision rather than becoming an undocumented mixture of unrelated framework states.

Upgrade is not required to preserve obsolete framework material merely because it existed in the earlier installed revision.

Conversely, upgrade shall not remove target material merely because it is absent from the later supplying repository when that material is outside the managed upgrade boundary.

## Local Modification

An initialized repository may contain local modification of material that upgrade otherwise considers managed.

Upgrade shall not silently overwrite such a condition when doing so could destroy independently intentional repository work or make the resulting framework relationship untruthful.

The capability shall identify conflicts or ambiguity that prevent safe reconciliation.

When the initializer cannot determine a correct treatment from accepted Design and Planning, it shall fail and surface the condition rather than guess.

Exact conflict policy, including whether particular cases may be automatically replaced, preserved, merged, rejected, or explicitly resolved by the user, belongs to Planning where that policy can be derived without additional semantic meaning.

## Product Preservation

Upgrade does not restart the target repository's product lifecycle.

Existing product Design remains product Design.

Existing Planning and normative requirements retain their meaning subject to ordinary lifecycle changes made by that repository.

Existing implementation and accepted product history remain repository-owned state.

Upgrade may change generic lifecycle mechanics on which later product development depends, but it shall not manufacture product changes merely to make framework upgrade convenient.

If a later framework revision introduces an incompatibility that requires substantive product meaning to change, framework upgrade alone shall not invent that change.

The incompatibility shall instead be surfaced for appropriate repository lifecycle work.

## Independent History

Upgrade shall preserve the target repository as an independently rooted repository.

Adopting a later repo-spec framework revision does not make supplier commits ancestors of the target repository and does not require importing supplier Git history.

Exact source revision identity may be retained as maintained repository information without importing the corresponding supplier Git objects.

A framework source identifier remains meaningful as the identity of the supplying repo-spec state even when that Git object is not present in the target repository's object database.

## Candidate Result

Upgrade shall evaluate a complete prospective upgraded repository state before reporting success.

The prospective result includes both the reconciled managed framework material and the preserved repository-owned material with which that framework must operate.

Validation shall therefore evaluate the candidate repository as a whole to the extent required by applicable mechanically decidable obligations rather than validating only copied framework files in isolation.

Design does not require a particular staging implementation.

Planning and Build may use a staged copy, temporary worktree, transaction-like construction, reversible working-tree operation, or another reliable technique so long as the required observable behavior is preserved.

## Validation

Before reporting successful upgrade, the initializer shall cause the prospective upgraded repository state to undergo the mechanical Validation required by the prospective installed framework and the initializer's applicable mechanically decidable upgrade obligations.

Validation shall use the framework state that the candidate repository would actually possess after successful upgrade.

Passing mechanical Validation establishes only the applicable mechanically checked conditions.

It does not establish that every semantic consequence of a framework change is acceptable to the repository's product.

## Atomic Meaning

Repository upgrade has two user-visible semantic outcomes:

- a successfully upgraded repository; or
- upgrade failure.

The initializer shall not knowingly report success while leaving the repository in a partially reconciled or ambiguously installed framework state.

Failure shall not intentionally destroy valid pre-upgrade repository-owned material merely to simplify recovery.

Exact staging, rollback, filesystem replacement, Git transaction, recovery, and promotion techniques belong to Planning and Build unless further Design meaning proves necessary.

## Successful Result

A successful upgrade produces the same existing repository with:

- its independently developed repository and product state preserved except where explicitly authorized upgrade-managed material changes;
- its managed framework state coherently corresponding to the selected supplying repo-spec revision;
- its current framework source relationship updated truthfully;
- the mechanical Validation capability required by that installed framework operating correctly; and
- the repository ready to continue its existing lifecycle.

Upgrade does not create a new repository identity merely because its reusable framework changed.

## Failure

Upgrade shall fail rather than knowingly produce or report a result when:

- the existing installed framework relationship cannot be determined sufficiently for safe reconciliation;
- the selected supplying framework state cannot be identified accurately;
- managed and repository-owned material cannot be distinguished sufficiently to avoid unauthorized mutation;
- local modification creates an unresolved conflict under accepted policy;
- the prospective repository cannot satisfy required mechanical Validation; or
- the initializer otherwise cannot establish the required upgraded state accurately and unambiguously.

Failure shall surface the relevant condition rather than conceal it through invented assumptions.

## Compatibility

Not every historical framework revision is necessarily required to upgrade directly to every later revision.

Compatibility constraints may exist when justified by actual framework evolution.

Design does not require an elaborate compatibility matrix merely because upgrades exist.

Planning shall introduce only the compatibility representation necessary to determine whether a requested upgrade can be performed correctly.

Unsupported or ambiguous transitions shall fail explicitly rather than produce an undocumented hybrid result.

## Simplicity

Repository upgrade should perform the minimum reconciliation necessary to move an existing initialized repository from its current installed framework state to the selected supplying framework state safely.

Historical repo-spec implementations are useful evidence for upgrade problems and techniques, but their architectures are not requirements.

In particular, upgrade does not inherently require:

- a durable framework lineage ledger;
- imported repo-spec Git ancestry;
- a provenance database;
- transportable historical authority bundles;
- a generalized migration engine;
- an evidence graph;
- universal three-way merge machinery; or
- permanent staging infrastructure.

Such mechanisms should be introduced only if later Design establishes semantic need or bounded Planning demonstrates that a simpler implementation cannot satisfy current Design.

## Relationship to Initialization

Initialization and upgrade share the repo-spec initializer product but perform different transformations.

Initialization:

    accepted repo-spec source
              ↓
        new destination
              ↓
       initialized repository

Upgrade:

    existing initialized repository
              +
      accepted repo-spec source
              ↓
            upgrade
              ↓
      upgraded same repository

DP-110 continues to define fresh repository initialization.

DP-120 continues to define the initialized repository and its independent lifecycle handoff.

This document defines the later framework-adoption transformation of that existing repository.

## Further Planning

Once this Design is accepted, Planning may select a bounded Repository Upgrade Functional Set.

Planning should resolve only the technical decisions necessary for that Functional Set, including:

- identification of the currently installed framework revision;
- identification of initializer-managed upgrade material;
- derivation of the source-to-target managed delta;
- treatment of locally modified managed material;
- construction and evaluation of the prospective upgraded repository;
- update of the current framework source relationship;
- compatibility checks where necessary;
- failure behavior; and
- the user-facing upgrade command interface.

Those decisions shall preserve the ownership, independence, validation, and simplicity boundaries established by this Design.
