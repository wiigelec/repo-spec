## Development

Use the PR's GitHub `Development` section to link the governing issue.
Do not use automatic close syntax unless the governing issue explicitly permits closure on merge.
When closure on merge is authorized, end the PR body with `Closes #<issue-number>`.

## Governing issue

Record the governing issue URL or issue number.

`governing_issue` (required, `input`)

Issue URL or #<number>

## Change purpose

Describe the bounded purpose of this pull request.

`change_purpose` (required, `textarea`)

Summarize the bounded purpose of the change.

## Accepted base revision

Exact commit SHA for the accepted base.

`accepted_base_revision` (required, `input`)

<exact base SHA>

## Proposed head revision

Exact commit SHA for the proposed review head.

`proposed_head_revision` (required, `input`)

<exact head SHA>

## Controlling specifications

List the governing specifications and records.

`controlling_specifications` (required, `textarea`)

repo.manifest, repo.development-workflow, and any other governing specs.

## Summary of implemented changes

Summarize what changed and why.

`summary_of_implemented_changes` (required, `textarea`)

Summarize the implemented changes.

## Changed-path inventory

List every changed path.

`changed_path_inventory` (required, `textarea`)

List the changed repository paths.

## Scope and exclusions

Confirm scope, and list explicit exclusions.

`scope_and_exclusions` (required, `textarea`)

Confirm in-scope work and any explicit exclusions.

## Patch or commit summary

Provide the ordered patch or commit sequence.

`patch_or_commit_summary` (required, `textarea`)

1. ... 2. ... 3. ...

## Specification and authority effects

State any specification, projection, or authority impact.

`specification_and_authority_effects` (required, `textarea`)

Describe any specification or authority impact.

## Generated-artifact effects

State which generated artifacts changed and whether they are current.

`generated_artifact_effects` (required, `textarea`)

List generated artifacts and freshness status.

## Validation commands and results

List the exact commands run and the results observed.

`validation_commands_and_results` (required, `textarea`)

scripts/validate, scripts/validate --mutation-tests, and outcomes.

## Exact revision validated

Exact commit SHA that the validation evidence covers.

`exact_revision_validated` (required, `input`)

<exact validated SHA>

## Known limitations or questions

List unresolved questions, deviations, or limitations.

`known_limitations_or_questions` (required, `textarea`)

List any known limitations or open questions.

## Focused review requests

Ask reviewers for the specific checks you want.

`focused_review_requests` (required, `textarea`)

Call out the review focus areas.

## Acceptance checklist

List the checklist items that must be satisfied.

- [ ] Governing issue is linked
- [ ] Accepted base and head are exact SHAs
- [ ] Validation evidence names the exact head revision
- [ ] Review requests are focused
- [ ] No excluded work has been introduced
- [ ] PR body ends with the correct closure text when applicable

## Post-merge validation and closure

Describe the required post-merge validation and the issue-closure gate.

`post_merge_validation_and_closure` (required, `textarea`)

Describe any post-merge validation and the issue-closure gate.

## Successor work not included

List deferred follow-up work that this PR does not authorize.

`successor_work_not_included` (required, `textarea`)

List any deferred successor work.
