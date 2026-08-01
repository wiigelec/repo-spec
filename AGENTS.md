# Repository Chatbot Initialization

Before any repository mutation, initialize against the accepted repository workflow.

Read, in order:
- `README.md`
- `specs/repo/manifest.json`
- `specs/repo/development-workflow.json`
- the governing issue for the current bounded change
- only the relevant overview, plan, specification, and predecessor records
- the actual Git branch, accepted base, working tree, and remote state

Report the governing issue, controlling authority, accepted base, intended branch, scope, exclusions, dependencies, next authorized action, and any unresolved authority conflicts.

If authority is missing or conflicts, stop and ask.

Do not mutate the repository until initialization is complete.

Authoritative sources:
- `README.md`
- `specs/repo/*.json`
- `docs/overview/PRODUCT-OVERVIEW.md`
- `docs/plans/00-bootstrap-plan.md`

When proposing or creating governed work, chatbot sessions shall load and follow the canonical governing-issue contract in `specs/repo/governing-issue.json`. When drafting or updating pull requests or equivalent review proposals, chatbot sessions shall load and follow the canonical review-proposal contract in `specs/repo/review-proposal.json`. Use the derived Markdown projection, GitHub issue form, or GitHub pull request template only as adapters; they do not replace the canonical contracts.
