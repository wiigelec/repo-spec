# Governing Issue Example

## Change type

Standardization of the governing issue format.

## Problem statement

Independent chatbot sessions need one durable governing-issue structure that survives outside conversation history.

## Intended outcome

Provide a repository-generic canonical governing issue contract, a Markdown projection, and a GitHub Issue Form adapter.

## Governing specifications

- `repo.manifest`
- `repo.repository-structure`
- `repo.development-workflow`
- `repo.governing-issue`

## Accepted default-branch base

`main` at `1bdaa98`.

## Intended branch

`issue-governing-issue-standard`.

## In-scope behavior and paths

- `specs/repo/governing-issue.json`
- `derived/specs/repo/governing-issue.md`
- `.github/ISSUE_TEMPLATE/governing-issue.yml`
- `AGENTS.md`
- `README.md`
- `scripts/docgen.py`
- `scripts/validate_impl.py`

## Explicit exclusions

- Previously identified validator fixes.
- Unrelated repository restructuring.
- Product-spec changes.

## Dependencies and predecessor evidence

- Merged chatbot initialization work in `issue-19-chatbot-initialization`.
- Accepted repository-spec manifests and workflow records.

## Ordered patch plan

1. Add the canonical governing-issue contract.
2. Add the Markdown projection.
3. Add the GitHub Issue Form adapter.
4. Update discoverability and validation tables.
5. Regenerate derived artifacts.

## Validation plan

- Run `scripts/validate`.
- Inspect the complete diff.

## Acceptance criteria

- One canonical issue format is discoverable without conversation history.
- The GitHub form covers every required canonical field.
- The Markdown form can express the same structure without GitHub.

## Completion gate

This issue may close only after the canonical contract, adapters, example issue, generated artifacts, and validation all pass.

## Open decisions or authority conflicts

None.

## Successor work explicitly not authorized

This issue does not authorize product-spec redesign, validator hardening unrelated to this contract, or broad repository refactors.
