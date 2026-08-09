# repo-spec

Repository specification workspace.

Supported runtime: Python 3.10+

## Start here

- [Repository chatbot initialization](AGENTS.md)
- [Product overview](repo/docs/overview/PRODUCT-OVERVIEW.md)
- [Initializer overview](product/docs/overview/INITIALIZER-OVERVIEW.md)
- [Initializer decomposition](product/docs/decompositions/INITIALIZER-DECOMPOSITION.md)
- [Initializer reference](product/docs/initializer/README.md)
- [Repository manifest](repo/specs/repo/manifest.json)
- [Repository schemas](repo/schemas/)
- [Product schemas](product/schemas/product/)
- [Derived docs](repo/derived/specs/repo/)
- [Repository-wide validation](scripts/validate)

## Quick commands

- `scripts/validate` — run repository-wide validation, including both validation domains and their mutation/self-test suites
- `repo/scripts/validate` — run the focused repository-owned leaf validator
- `product/scripts/validate` — run the focused product-owned leaf validator
- `repo/scripts/generate-docs`

- [Initializer implementation plan](product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md)
