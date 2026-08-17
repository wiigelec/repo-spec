# Initialized-output executable closure

## Closure outcome

A transported workflow creates an installed-repository obligation: every required repository-relative command it invokes must resolve in initialized output, unless the dependency is explicitly external or platform-provided.

Initialization should therefore close over the stable local validation/test interfaces required by the workflow it installs.

## Framework and source-test boundary

The capability requires enough installed material to satisfy stable repository and product interfaces. It does not require copying repo-spec's complete source-development test implementation into every derived repository.

Portable framework self-tests, minimal wrappers, dispatchers, stubs, or other representations remain implementation alternatives rather than selected behavior here.

## Evidence boundary

The failed first-push validation in `wiigelec/test-repo` demonstrates the current implementation gap: transported CI referenced repository-local test commands absent from generated output.

That repository and its workflow remain implementation evidence, not normative authority.

Exact inventory entries, generation rules, closure validation algorithms, and upgrade propagation remain deferred.
