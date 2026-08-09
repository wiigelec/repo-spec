# repo-spec

Repository specification workspace.

Supported runtime: Python 3.10+

## Initialize a repository

The normal local initializer workflow uses a reviewed JSON request:

```text
product/scripts/repo-spec-init --request request.json
```

The request is the authority-bearing input to initialization. A practical first-use workflow is to have an AI coding agent help construct that file from the current repo-spec checkout, then review the JSON yourself before running the initializer.

1. Clone or open the repo-spec checkout you intend to use.
2. Ask the agent to inspect this checkout and the current initializer request contracts. Do not ask it to guess from an older example.
3. Give the agent the explicit facts required for your initialization, including the destination, product identity and direction material, source/revision when used, execution profile, and the authority granting initialization.
4. Have the agent construct a canonical `request.json` without inventing, defaulting, or inferring authority-bearing values.
5. Require the agent to show the complete request and explain the material choices before execution.
6. Review the JSON. The conversation is assistance; the reviewed request file is the initializer input.
7. Run `product/scripts/repo-spec-init --request request.json`.
8. Review the terminal outcome and initialized repository, especially the generated product overview, decomposition, implementation plan, product specification foundations, provenance/handoff records, and initial Git state.

The initializer does not accept conversational prose as authority and does not provide an interactive field-by-field request builder. It will not infer a product ID, choose a source revision, or replace review of the canonical JSON request.

### Reusable AI-agent instruction

> Inspect this repo-spec checkout and its current initializer request schema and documentation. Help me construct a canonical `request.json` for a new local repository. Use only facts I explicitly provide for authority-bearing fields. Do not infer a product ID, source repository, source revision, direction material, execution profile, destination, or initialization authority. If a required fact is missing, tell me what is missing. Show me the complete JSON and explain the important fields before I run anything. Do not execute the initializer for me. After I approve the file, the command I will run is `product/scripts/repo-spec-init --request request.json`.

For request fields, validation rules, lifecycle behavior, and intentional developer/diagnostic commands, see the [initializer reference](product/docs/initializer/README.md).

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

- `product/scripts/repo-spec-init --request request.json` - run normal local initialization from a reviewed canonical request
- `scripts/validate` - run repository-wide validation, including both validation domains and their mutation/self-test suites
- `repo/scripts/validate` - run the focused repository-owned leaf validator
- `product/scripts/validate` - run the focused product-owned leaf validator
- `repo/scripts/generate-docs`

- [Initializer implementation plan](product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md)
