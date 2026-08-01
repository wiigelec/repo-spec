# repo-spec

Repository specification workspace.

Authority chain:

`README.md` -> `specs/repo/*.json` -> `derived/specs/repo/*.md`

## Start here

- [Repository chatbot initialization](AGENTS.md)
- [Product overview](docs/overview/PRODUCT-OVERVIEW.md)
- [Repository manifest](specs/repo/manifest.json)
- [Governing issue contract](specs/repo/governing-issue.json)
- [Governing issue template](derived/specs/repo/governing-issue.md)
- [Review proposal contract](specs/repo/review-proposal.json)
- [Review proposal template](derived/specs/repo/review-proposal.md)
- [Repository structure](specs/repo/repository-structure.json)
- [Development workflow](specs/repo/development-workflow.json)
- [Validation](specs/repo/validation.json)
- [Derived repository manifest](derived/specs/repo/manifest.md)
- [Derived repository structure](derived/specs/repo/repository-structure.md)
- [Derived development workflow](derived/specs/repo/development-workflow.md)
- [Derived validation](derived/specs/repo/validation.md)
- [GitHub field policy checker](scripts/github-field-policy)
- [Repo spec schema](schemas/repo-spec.schema.json)
- [Repo manifest schema](schemas/repo-manifest.schema.json)
- [Generate docs](scripts/generate-docs)
- [GitHub field policy workflow](.github/workflows/github-field-policy.yml)

## Entry points

- `AGENTS.md` for repository-level chatbot initialization
- `docs/overview/PRODUCT-OVERVIEW.md` for high-level direction
- `specs/repo/` for repository-spec source JSON
- `specs/repo/governing-issue.json` for the canonical governing-issue contract
- `specs/repo/review-proposal.json` for the canonical review-proposal contract
- `schemas/` for JSON Schema definitions
- `derived/specs/repo/` for non-normative projections
- `scripts/generate-docs` for deterministic Markdown generation
- `scripts/validate` for the validation entry point
- `scripts/github-field-policy` for hosted GitHub field policy checks
