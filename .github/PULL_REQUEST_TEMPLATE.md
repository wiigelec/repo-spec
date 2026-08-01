## Development

Use the PR's GitHub `Development` section to link the governing issue.
Do not use automatic close syntax unless the governing issue explicitly permits closure on merge.
When closure on merge is authorized, end the PR body with `Closes #<issue-number>`.

## Governing issue

Record the issue URL or `#<number>` here for durable traceability.

## Change purpose

Describe the bounded purpose of this pull request.

## Accepted base revision

Exact commit SHA for the accepted base.

## Proposed head revision

Exact commit SHA for the proposed review head.

## Controlling specifications

List the governing specifications and records.

## Summary of implemented changes

Summarize what changed and why.

## Changed-path inventory

List every changed path.

## Scope and exclusions

Confirm scope, and list explicit exclusions.

## Patch or commit summary

Provide the ordered patch or commit sequence.

## Specification and authority effects

State any specification, projection, or authority impact.

## Generated-artifact effects

State which generated artifacts changed and whether they are current.

## Validation commands and results

List the exact commands run and the results observed.

## Exact revision validated

Exact commit SHA that the validation evidence covers.

## Known limitations or questions

List unresolved questions, deviations, or limitations.

## Focused review requests

Ask reviewers for the specific checks you want.

## Acceptance checklist

- [ ] Governing issue is linked in the PR's Development section and is in scope.
- [ ] Accepted base and proposed head are exact SHAs.
- [ ] Validation evidence names the exact head revision.
- [ ] Review requests are focused on the bounded change.
- [ ] No excluded work has been introduced.
- [ ] PR body ends with the correct `Closes #<issue-number>` text when merge closes the issue.

## Post-merge validation and closure

Describe the required post-merge validation and the issue-closure gate.

## Successor work not included

List deferred follow-up work that this PR does not authorize.
