# Validation Bootstrap

## Status

Bootstrap validation plan for `specs/repo`.

During bootstrap, files under `specs/repo/` are the authoritative bootstrap source. They cease being authoritative only through the documented JSON cutover.

One entry point: `scripts/validate`.

This document is a closed bootstrap specification. No new check may be added without an accepted specification change.

Bootstrap-only checks must be deleted or replaced at JSON cutover.

## Purpose

Validation during bootstrap exists to confirm that a fresh chatbot session can discover the repository-spec foundation, the workflow shape, and the boundary between framework material and future product material.

## Closed list

Exactly four checks exist during bootstrap.

| Check | Reason | Pass condition | Failure message |
| --- | --- | --- | --- |
| Required files | Confirms the bootstrap source set exists. | `README.md`, `docs/overview/PRODUCT-OVERVIEW.md`, `docs/plans/00-bootstrap-plan.md`, `specs/repo/repo-specs-bootstrap.md`, `specs/repo/dev-workflow-bootstrap.md`, `specs/repo/validation.md`, `specs/repo/json-artifact-model.md`, and `scripts/validate` all exist. | `missing required bootstrap file: <path>` |
| Directory separation | Confirms bootstrap source, planning docs, and overview docs stay in separate trees. | `docs/` contains only `overview/` and `plans/`; `specs/repo/` contains only the three bootstrap docs. | `bootstrap directory separation violated` |
| Relative links | Confirms entry docs route by repository-relative paths. | `README.md` contains the six bootstrap navigation links to `docs/overview/PRODUCT-OVERVIEW.md`, `docs/plans/00-bootstrap-plan.md`, `specs/repo/repo-specs-bootstrap.md`, `specs/repo/dev-workflow-bootstrap.md`, `specs/repo/validation.md`, and `specs/repo/json-artifact-model.md`; `docs/overview/PRODUCT-OVERVIEW.md` contains the five part links to its local `product-overview` files. | `relative link check failed: <file>` |
| Correct failure exit status | Confirms the validator fails when a required file is missing. | The internal file-check helper returns a non-zero status for a guaranteed-missing sentinel path. | `failure exit status check failed` |

## Validation boundaries

The validator does not check:

- formatting;
- prose quality;
- Git workflow;
- hosting-platform behavior;
- future schema design;
- product-spec definitions;
- source-code behavior.

## Bootstrap success signal

Bootstrap validation succeeds when all four checks pass and the repository can still be understood as bootstrap-only Markdown source plus instructional docs.
