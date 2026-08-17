# Validation scaffolding capability boundary and outcome

## Capability boundary

This candidate functional set covers one end-to-end initializer capability: produce a fresh initialized repository whose transported validation and test workflow is locally resolvable and usable without manual post-initialization repair.

The capability begins when the initializer selects the governed framework material for a new repository and ends when the initialized repository contains the stable validation/test surfaces required by its transported workflow, or initialization fails with sufficient evidence to explain why that usable state could not be produced.

## Included outcome

A successful initialization should leave a repository that can execute its transported common validation workflow on first push without adding missing repository-relative commands by hand.

The capability includes directional ownership of repository validation self-tests, product validation self-tests, generic product implementation tests, explicit zero-applicable product-test state, and initialized-output closure over required local commands.

The capability does not require transport of repo-spec's complete source-development test tree merely to preserve stable interfaces.

## End-to-end usability

Users should not need to know which CI commands exist only in repo-spec, reconstruct missing wrappers, or specialize the generated workflow for a fresh repository.

This functional set does not define exact command output, exit codes, discovery algorithms, file contents, or implementation architecture.
