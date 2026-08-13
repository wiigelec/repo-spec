# Governed Repository

This repository was initialized with a reusable governed repository framework. The framework establishes repository structure, governance, validation, and bootstrap handoff records without defining the product that will be developed here.

## Start here

Review the bootstrap handoff and provenance:

- `repo/initializer/handoff.json`
- `repo/initializer/provenance.json`

Review the repository governance authority:

- `repo/specs/repo/manifest.json`
- `repo/specs/repo/governing-issue.json`
- `repo/specs/repo/development-workflow.json`

## Validation

Run the complete repository validation surface with:

```sh
scripts/validate
```

The domain entry points are also available directly:

- `repo/scripts/validate`
- `product/scripts/validate`

Immediately after initialization, the product specification system may be inactive. That is a valid bootstrap state.

## Product definition

Product identity and direction are governed successor work through collection, analysis, candidate functional sets, approved functional sets, decomposition, specifications, and implementation planning. Establish those artifacts through the repository's governing issue and development workflow rather than inferring or synthesizing them during bootstrap. The initializer transports the framework contracts for that workflow, not repo-spec's own whiteboard, analysis, or functional-set working content.

The initialized framework is intended to remain stable while governed product work is introduced through the applicable repository workflow.
