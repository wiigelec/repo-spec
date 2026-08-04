# Product Overview

## Status

Product-direction overview, divided into small, task-oriented documents for selective chatbot consumption.

The complete product overview consists of this index and the six linked parts below. Together they record the intended outcome, decomposition model, and development model for this repository. They are directional and non-normative.

The overview does not replace accepted normative specifications, authorize repository mutations, or define detailed implementation requirements. Normative behavior remains governed by accepted specifications until those specifications are explicitly revised, superseded, or retired through bounded governed work.

## Overview parts

| Part | Read when you need |
| --- | --- |
| [1. Product direction](./product-overview/01-product-direction.md) | Vision, desired outcome, intended users, success conditions, or non-goals |
| [2. Decomposition model](./product-overview/02-decomposition-model.md) | Canonical decomposition, bounded tasks, stopping criteria, reasoning boundaries, or terminology |
| [3. Development and specifications](./product-overview/03-development-and-specifications.md) | Development layers, specification authority, or the Level 0–3 model |
| [4. Git and change workflow](./product-overview/04-git-and-change-workflow.md) | Git concepts, hosting-platform boundaries, or the bounded change process |
| [5. Human and AI continuity](./product-overview/05-human-ai-continuity.md) | Human/AI responsibilities, session recovery, or repository-first continuity |
| [6. Governance and evolution](./product-overview/06-governance-and-evolution.md) | Validation, authority, generated artifacts, portability, or migration boundaries |

## Minimal reading paths

- To understand what the product is and how its central method works: read Parts 1 and 2.
- To design or revise product specifications: read Parts 1, 3, and 6.
- To implement a bounded repository change: read Parts 4 and 6, plus the governing specification and issue.
- To understand the canonical decomposition model: read Part 2.
- To resume work in a new AI session: read Part 5, then load only the parts relevant to the bounded task.
- To review whether a change has the correct authority: read Parts 3 and 6.

Each part is self-contained enough to load independently and links back to this index. When a question crosses part boundaries, load only the listed combination rather than the entire overview.
