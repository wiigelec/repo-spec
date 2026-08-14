# repo-spec

`repo-spec` is a specification-governed repository bootstrap framework for long-running human and AI-assisted software development. It establishes a repository structure in which accepted repository and product specifications remain explicit authority, while generated documentation, implementation artifacts, tests, and prior behavior remain subordinate evidence.

Supported runtime: Python 3.10-3.14

## Initialize a repository

From a repo-spec checkout, the normal local initialization workflow is:

```text
product/scripts/repo-spec init --repo /path/to/new/repository-name
```

If the `repo-spec` wrapper from this checkout has been placed on `PATH`, the equivalent command is:

```text
repo-spec init --repo /path/to/new/repository-name
```

The destination path is the only normal-user bootstrap input. The repository name is derived mechanically from the destination basename.

The local wrapper determines the repo-spec framework source and exact Git revision from the clean checkout that is actually executing the initializer. You do not supply a Git SHA, source-repository field, product ID, direction material, execution profile, or separate initialization-authority token.

Repository initialization establishes the governed repository framework only. It does **not** define the product. overview collection, analysis, and functional-set approval are governed successor work performed after initialization; decomposition, product specifications, implementation planning, and implementation follow through the repository workflow.

The initializer fails closed when the destination is unsafe or the executing repo-spec checkout cannot provide accurate, unambiguous framework provenance.

### Web-chat-assisted workflow

A web chat agent does not need access to your local Git checkout to resolve Git plumbing. Tell it the local repo-spec command path you intend to use and the destination repository path. The command you run locally resolves framework provenance itself.

A useful instruction is:

> Help me initialize a new repo-spec repository. I will run the initializer locally. From a repo-spec checkout, use `product/scripts/repo-spec init --repo <destination>`. Use bare `repo-spec init --repo <destination>` only if that checkout's wrapper has already been placed on `PATH`. Do not invent product identity or product direction during initialization; those are established afterward in the initialized repository.

For lifecycle behavior and lower-level diagnostic/developer interfaces, see the [initializer reference](product/docs/initializer/README.md).

## Start here

- [Repository chatbot initialization](AGENTS.md)
- [functional-set lifecycle](repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md)
- [Initializer overview](product/docs/overview/INITIALIZER-FUNCTIONAL-SET.md)
- [Initializer decomposition](product/docs/decompositions/INITIALIZER-DECOMPOSITION.md)
- [Initializer reference](product/docs/initializer/README.md)
- [Repository manifest](repo/specs/repo/manifest.json)
- [Repository-wide validation](scripts/validate)

## Quick commands

- `product/scripts/repo-spec init --repo /path/to/new/repo` - normal local repository bootstrap
- `product/scripts/repo-spec-init --request request.json` - lower-level/developer request interface
- `scripts/validate` - repository-wide validation
- `repo/scripts/validate` - focused repository validator
- `product/scripts/validate` - focused product validator
- `repo/scripts/generate-docs`

- [Initializer implementation plan](product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md)
