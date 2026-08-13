# Repository Chatbot Initialization

Before any repository mutation, initialize against the accepted repository workflow.

Read, in order:
- `README.md`
- `repo/specs/repo/manifest.json`
- `repo/specs/repo/development-workflow.json`
- discover an existing governing issue for the current bounded change, or create one only when the accepted development workflow explicitly authorizes that no-existing-issue bootstrap
- the resulting governing issue
- only the relevant overview, decomposition, plan, specification, and predecessor records
- the actual Git branch, open pull requests, accepted base, working tree, remote state, and hosting-platform state

Verify that the branch recorded in the accepted default-branch base is the repository's actual current default branch. Report the governing issue, controlling authority, accepted base, intended branch, scope, exclusions, dependencies, next authorized action, and any unresolved authority conflicts, along with the inspected branch, open PR, working-tree, remote, and hosting-platform state.

If controlling authority is missing or conflicts, stop and ask, except that absence of a governing issue shall follow the explicit discovery-or-create procedure in `REPO-WF-003`.

Before any mutation that creates or modifies maintained product artifacts, verify that applicable accepted product specifications exist for the planned implementation scope. Stop before source mutation when applicable product specifications are missing or their acceptance status conflicts with the planned work.

Do not mutate the repository until initialization is complete.

The normative development lifecycle for product development is: collection, analysis, candidate functional set, approved functional set, accepted decomposition, accepted product specifications, accepted implementation plan, governed implementation issues, and product artifacts. No additional development-document gate exists between functional-set approval and decomposition. An implementation plan may not become accepted without its required controlling product specifications being accepted and structurally valid. A plan cannot supply missing normative product semantics.

Code, tests, schemas, templates, generated output, or prior implementation behavior do not become product authority merely because they exist.

When proposing or creating governed work, chatbot sessions shall load and follow the canonical governing-issue contract in `repo/specs/repo/governing-issue.json`. When drafting or updating pull requests or equivalent review proposals, chatbot sessions shall load and follow the canonical review-proposal contract in `repo/specs/repo/review-proposal.json`. When working with overview-process artifacts, product decompositions, or implementation plans, chatbot sessions shall identify the required artifact class first, load the governing document specification, use the canonical root and controlling-document naming model, update the controlling entry point and subordinate chunks together, and avoid inventing headings, paths, metadata, or lifecycle vocabulary. Whiteboard evidence and analysis remain non-normative; candidate functional sets do not authorize decomposition; only approved functional sets provide the new decomposition handoff. Use the derived Markdown projection, GitHub issue form, or GitHub pull request template only as adapters; they do not replace the canonical contracts.
