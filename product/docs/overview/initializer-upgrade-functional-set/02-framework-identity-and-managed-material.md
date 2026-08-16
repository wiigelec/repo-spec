# Framework identity and managed material

## Source and target framework identity

Upgrade depends on a trustworthy relationship between the framework revision currently accepted by the target repository, the later repo-spec revision supplying the upgrade, and the managed material associated with each revision.

The original initialization provenance remains historical evidence and should not be discarded merely because later upgrades occur.

## Source-side managed-material authority

The upgrade manifest is owned by the repo-spec source repository and consumed by `repo-spec upgrade`.

The target repository does not expose or maintain the source-side upgrade manifest.

The legal upgrade universe is constrained to material the initializer can install. The upgrade manifest therefore selects or qualifies transitions within initializer-managed material; it does not create an independent authority to mutate arbitrary repo-spec or target-repository paths.

The accepted analysis favors reusing the initializer's stable material-key and output-inventory concepts so upgrade selection is based on managed material identity rather than raw Git-path differences.

## Directional entry selection

The capability includes determining the applicable managed-material delta between the target's accepted framework revision and the supplying repo-spec revision.

That directional responsibility includes classifying initializer-managed material as unchanged, added, modified, removed, or retargeted across the two framework states, plus resolving the dependencies necessary for a coherent upgrade set.

Exact manifest schema, revision applicability fields, dependency representation, compatibility fields, and selection algorithms remain later specification concerns.
