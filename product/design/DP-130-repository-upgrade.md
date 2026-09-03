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

Upgrade directly reconciles framework-owned state supplied by the selected repo-spec revision.

A prospective framework may also require generic lifecycle-support state in another ownership domain or in a repository-root operational surface. Where that state is required for the prospective framework to operate correctly, upgrade may establish or adapt it to the extent necessary to satisfy the prospective framework while preserving independently developed meaning and content in that domain.

Such bounded upgrade authority does not transfer ownership of the affected state to the initializer or framework. Product-owned state remains product-owned, repository-root operational state retains its established role, and user-owned state remains user-owned.

A required generic lifecycle surface that is absent from an older initialized repository may therefore be created by upgrade. Existing state that already satisfies the prospective framework requirement shall not be replaced merely to reproduce initializer-generated starter content.

Where an existing surface contains independently developed product meaning or other repository-owned content, upgrade shall preserve that meaning and content unless current Design explicitly authorizes a transformation. If the prospective framework requirement cannot be satisfied without an unresolved semantic change to independently developed state, upgrade shall surface the incompatibility rather than invent the required product decision.

The mere existence of a similarly named path in the supplying repository does not create upgrade authority. Upgrade authority follows current Design meaning and the requirements of the prospective installed framework rather than historical initializer authorship or path coincidence.

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

The prospective result includes the reconciled framework-owned state, any bounded compatibility adaptations required by the prospective framework, and the preserved repository-owned material with which that framework must operate.

Evaluation shall establish that the prospective framework is internally mechanically valid and that the repository satisfies mechanically decidable compatibility obligations introduced by adopting that framework.

Design does not require every unrelated product-owned mechanical obligation to pass merely because framework upgrade is occurring. Existing product Validation failures that are independent of the framework transition shall not by themselves redefine an otherwise correct framework upgrade as unsuccessful.

This distinction does not permit upgrade to ignore a product-owned condition when the prospective framework requires that condition for lifecycle compatibility. Planning shall derive the mechanical evaluation boundary necessary to distinguish framework-transition obligations from unrelated product-development state.

Design does not require a particular staging implementation.

Planning and Build may use a staged copy, temporary worktree, transaction-like construction, reversible working-tree operation, or another reliable technique so long as the required observable behavior is preserved.

## Validation

Before reporting successful upgrade, the initializer shall cause the prospective upgraded repository state to undergo the mechanical evaluation required to establish:

- the prospective installed framework's own mechanically decidable obligations;
- the initializer's applicable mechanically decidable upgrade obligations; and
- mechanically decidable repository compatibility conditions that the prospective framework requires of other ownership domains or repository-root operational state.

Validation shall evaluate the state that the repository would actually possess after successful upgrade.

The canonical repository-wide Validation entry point may be used when its full product Validation result is an appropriate gate for the selected upgrade. Design does not require Planning to use repository-wide Validation as the sole upgrade gate when doing so would make unrelated product-development failures block an otherwise valid framework transition.

Passing upgrade mechanical evaluation establishes only the applicable mechanically checked conditions.

It does not establish that every semantic consequence of a framework change is acceptable to the repository's product, and it does not convert unrelated product Validation status into framework-upgrade meaning.

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
- identification of framework-owned state and framework-required compatibility adaptations within the upgrade boundary;
- derivation of the source-to-target managed delta;
- treatment of locally modified managed material;
- construction and evaluation of the prospective upgraded repository;
- update of the current framework source relationship;
- compatibility checks where necessary;
- failure behavior; and
- the user-facing upgrade command interface.

Those decisions shall preserve the ownership, independence, validation, and simplicity boundaries established by this Design.
