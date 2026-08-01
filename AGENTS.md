# Repository Chatbot Initialization

Before any repository mutation, initialize against the accepted repository workflow.

Read, in order:
- `README.md`
- `specs/repo/manifest.json`
- `specs/repo/development-workflow.json`
- the governing issue for the current bounded change
- only the relevant overview, plan, specification, and predecessor records
- the actual Git branch, open pull requests, accepted base, working tree, remote state, and hosting-platform state

Report the governing issue, controlling authority, accepted base, intended branch, scope, exclusions, dependencies, next authorized action, and any unresolved authority conflicts, along with the inspected branch, open PR, working-tree, remote, and hosting-platform state.

If authority is missing or conflicts, stop and ask.

Do not mutate the repository until initialization is complete.

Discovery entry points:
- `README.md`
- `docs/overview/PRODUCT-OVERVIEW.md`

Normative sources:
- `specs/repo/*.json`
- `derived/specs/repo/*.md` only as non-normative projections of the JSON sources

When proposing or creating governed work, chatbot sessions shall load and follow the canonical governing-issue contract in `specs/repo/governing-issue.json`. When drafting or updating pull requests or equivalent review proposals, chatbot sessions shall load and follow the canonical review-proposal contract in `specs/repo/review-proposal.json`. Use the derived Markdown projection, GitHub issue form, or GitHub pull request template only as adapters; they do not replace the canonical contracts.
