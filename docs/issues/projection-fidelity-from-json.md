# Governing Issue: Projection fidelity from JSON

## Change type

Validation hardening and generator fidelity.

## Problem statement

scripts/docgen.py hard-codes substantive contract text for the governing issue, review proposal, and validation projections. Freshness only compares generated files against those same renderer outputs, so accepted JSON changes can go unnoticed when a renderer ignores the authoritative fields.

## Intended outcome

Generate requirements, references, fields, and boundaries directly from structured JSON; make freshness sensitive to authoritative field changes; and keep the projections deterministic.

## Governing specifications

- `repo.manifest`
- `repo.repository-structure`
- `repo.development-workflow`
- `repo.governing-issue`
- `repo.review-proposal`
- `repo.validation`

## Accepted default-branch base

`main` at `82bcbfee8a3f5dc08c22515d6e4fc8ea7112c2fb`.

## Intended branch

`issue-39-projection-fidelity-from-json`.

## In-scope behavior and paths

- `scripts/docgen.py`
- `scripts/validate_impl.py`
- `derived/specs/repo/governing-issue.md`
- `derived/specs/repo/review-proposal.md`
- `derived/specs/repo/validation.md`
- mutation coverage for projected authoritative fields

## Explicit exclusions

- Product-spec changes.
- Unrelated repository restructuring.
- New validation categories unrelated to projection fidelity.
- Schema redesign.

## Dependencies and predecessor evidence

- Accepted JSON spec model.
- Existing deterministic doc generation entry point.
- Existing generated-document freshness check.

## Ordered patch plan

1. Replace hard-coded contract text with data-driven rendering from the authoritative JSON fields.
2. Make the validation projection reflect all requirements and boundaries from JSON.
3. Add mutation coverage proving projected authoritative field changes alter the output, or that a field is explicitly non-projected.
4. Regenerate derived docs and rerun validation.

## Validation plan

- Run `scripts/validate`.
- Run mutation coverage for the generator/validation renderer.

## Acceptance criteria

- Editing a projected authoritative field changes the rendered output.
- Any explicitly non-projected authoritative field is named as such in the generated projection.
- The validation projection no longer contradicts `specs/repo/validation.json`.
- `scripts/validate` passes.

## Completion gate

This issue may close only after the generator changes, mutation coverage, regenerated derived docs, and validation all pass.

## Open decisions or authority conflicts

None.

## Successor work explicitly not authorized

This issue does not authorize product-spec redesign, unrelated validator hardening, or broader repository refactors.
