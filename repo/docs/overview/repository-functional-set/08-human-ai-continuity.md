# functional-set lifecycle: Human and AI Continuity

> Part 5 of 6 · [functional-set lifecycle index](../functional-set-process.md) · [Previous](./04-git-and-change-workflow.md) · [Next](./06-governance-and-evolution.md)

This part defines human and AI responsibilities and the durable context needed for an independent session to resume work.

## Human and AI collaboration

### Human responsibilities

Human maintainers retain responsibility for:

- choosing product direction;
- approving material scope and semantic decisions;
- deciding which findings become governed work;
- resolving product tradeoffs;
- performing environment-specific validation where required;
- reviewing proposed changes;
- accepting exact revisions;
- merging and releasing completed work.

### AI chatbot responsibilities

AI chatbots may:

- discover repository purpose and authority;
- read the overview, plans, specifications, and governing records;
- inspect Git and hosting-platform state;
- identify contradictions, missing decisions, and incomplete boundaries;
- propose bounded issues;
- create or refine implementation plans;
- generate reviewable repository mutations;
- evaluate validation and execution evidence;
- audit changes against governing scope and specifications;
- continue work across independent sessions.

An AI chatbot must report missing or conflicting authority rather than silently selecting a convenient interpretation.

When a lower-level task encounters missing authority, it should stop and escalate that decision to the owning layer rather than inventing the answer.

## Repository-first continuity

The repository and its durable development records are the continuity mechanism.

Essential information must not exist only in a chatbot conversation.

Durable records should preserve:

- product intent;
- authority roots;
- planning status;
- governing issues;
- scope and exclusions;
- dependencies;
- accepted bases;
- intended branches;
- implementation decisions;
- validation requirements;
- exact revision evidence;
- unresolved questions;
- successor boundaries.

A new AI session should be able to recover the smallest sufficient development context without reading the entire repository or relying on prior model memory.

## Session discovery

A new development session should be able to follow a predictable discovery path:

1. Read the repository README.
2. Read the [functional-set lifecycle index](../functional-set-process.md) and the relevant overview parts.
3. Read the current governing issue for active bounded work.
4. Discover the normative specification roots and authority hierarchy.
5. If no governing issue is open, the repository has no active implementation plan.
6. Inspect relevant prerequisites and accepted predecessor evidence.
7. Interrogate the actual local Git state.
8. Identify the next bounded action.
9. Perform only authorized mutations.
10. Review returned evidence before continuing.

Historical plans provide context only and do not authorize new work.

The repository should make each step mechanically discoverable where practical.

This continuity model supports recursive decomposition across sessions by keeping unresolved decisions, accepted bases, and bounded task boundaries in the repository.
