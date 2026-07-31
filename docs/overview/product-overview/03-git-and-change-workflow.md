# Product Overview: Git and Change Workflow

> Part 3 of 5 · [Product overview index](../PRODUCT-OVERVIEW.md) · [Previous](./02-development-and-specifications.md) · [Next](./04-human-ai-continuity.md)

This part defines the Git-native operating model, hosting-platform boundary, and bounded development workflow.

## Git-native model

The framework assumes Git commands and Git-compatible development workflows.

The core model may rely on:

- repositories;
- commits;
- branches;
- refs;
- tags;
- object identities;
- merge bases;
- ancestry;
- diffs;
- staged and unstaged state;
- untracked and conflicted paths;
- isolated development branches;
- exact revision validation;
- merge-based integration.

Git records exact repository states and transitions. It does not by itself establish semantic correctness, review, acceptance, or product authority.

For example:

- a commit identifies an exact tree;
- a branch identifies a line of proposed work;
- a diff provides a review surface;
- a merge records integration;
- a tag names a revision;
- a CI run records selected checks against an exact revision.

Those facts remain distinct from whether the change satisfies the overview, plan, specifications, governing issue, review requirements, or acceptance criteria.

## Hosting-platform boundary

The reusable core should remain Git-compatible rather than treating one hosting provider as universal repository authority.

Hosting-platform capabilities may be defined through explicit profiles, including:

- issues;
- pull requests or merge requests;
- review comments;
- labels;
- protected branches;
- continuous-integration APIs;
- merge queues;
- release records.

GitHub may be the first fully supported platform profile.

Platform-specific behavior must remain distinguishable from Git-generic repository behavior.

## Bounded development workflow

A normal bounded change should use a Git-compatible workflow:

1. Establish a governing issue.
2. Record detailed scope and an ordered patch plan.
3. Identify the accepted default-branch base.
4. Create an isolated working branch.
5. Apply one coherent patch at a time.
6. Inspect the changed-file inventory and diff.
7. Run focused and complete validation.
8. Commit only the bounded paths.
9. Repeat the patch-and-validation loop as required.
10. Validate the exact proposed branch head.
11. Push and create a review proposal.
12. Require exact-head CI and semantic review.
13. Explicitly accept the exact revision.
14. Merge the accepted revision.
15. Validate the resulting default-branch revision.
16. Close the governing issue only after its completion gate is satisfied.

The exact tooling may evolve, but the separation among planning, mutation, validation, review, acceptance, merge, and closure must remain visible.
