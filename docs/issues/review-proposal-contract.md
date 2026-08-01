# Governing Issue: Review Proposal Contract

## Change type

Standardization of the review-proposal format for pull requests and equivalent review proposals.

## Problem statement

Independent chatbot sessions need one durable, platform-neutral review-proposal structure that survives outside conversation history and makes exact revision evidence traceable.

## Intended outcome

Provide a canonical review-proposal contract, a deterministic Markdown projection, and a GitHub pull request template adapter that all represent the same required fields.

## Governing specifications

- `repo.manifest`
- `repo.repository-structure`
- `repo.development-workflow`
- `repo.governing-issue`
- `repo.validation`
- `repo.review-proposal`

## Accepted default-branch base

`main` at `fa0c43aa630e7aacc318b8dc2f0ed825a50500cc`.

## Intended branch

`issue-review-proposal-contract`.

## In-scope behavior and paths

- `specs/repo/review-proposal.json`
- `derived/specs/repo/review-proposal.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `AGENTS.md`
- `README.md`
- `scripts/docgen.py`
- `scripts/validate_impl.py`
- `specs/repo/manifest.json`
- validation tables and projections that enumerate repository-spec artifacts

## Explicit exclusions

- Previously identified validator fixes.
- Product-spec changes.
- Unrelated repository restructuring.

## Dependencies and predecessor evidence

- Merged chatbot-initialization standard.
- Merged governing-issue standard.
- Existing deterministic doc generation and validation entry points.

## Ordered patch plan

1. Define the canonical review-proposal contract.
2. Add the deterministic Markdown projection.
3. Add the GitHub pull request template adapter.
4. Update discoverability, chatbot guidance, and validation tables.
5. Regenerate derived artifacts.

## Validation plan

- Run `scripts/validate`.
- Inspect the complete diff.
- Verify the PR template represents every required canonical field.

## Acceptance criteria

- A chatbot can discover one canonical review-proposal format without conversation history.
- The GitHub PR template represents every required field.
- The same contract can be used on a non-GitHub hosting platform.
- A reviewer can trace the proposal to its governing issue and controlling specifications.
- The proposal distinguishes validation, review, acceptance, merge, and closure.
- Exact-base, exact-head, and exact-validation revisions are visible.
- Generated artifacts are current.
- `scripts/validate` passes.

## Completion gate

This issue may close once the exact proposed revision has been reviewed and accepted, and the accepted revision has been merged. The pull request may use automatic issue-closing syntax when the merge is intended to authorize closure.

## Open decisions or authority conflicts

None.

## Successor work explicitly not authorized

This issue does not authorize product-spec redesign, validator fixes previously identified elsewhere, or unrelated workflow changes.
