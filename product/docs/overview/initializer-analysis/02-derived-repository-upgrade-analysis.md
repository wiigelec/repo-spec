# Derived-repository upgrade direction and evidence

## Source evidence

The controlling collection evidence is `product/docs/overview/INITIALIZER-WHITEBOARD.md` and `product/docs/overview/initializer-whiteboard/02-derived-repository-upgrade-intake.md`, with GitHub issue #418 retained as intake provenance.

The collected request is to propagate later repo-spec features, bug fixes, and security enhancements into repositories initialized from earlier repo-spec revisions.

The governed analysis stage also examined the current repo-spec initializer architecture, its material inventories, repository validation and GitHub-profile projection behavior, generated repository `wiigelec/test-repo`, its bootstrap provenance, and the framework delta since that repository was initialized.

## Resolved product direction

The user supplied the following directional decisions during analysis:

- the public entry point is `repo-spec upgrade --repo <existing-repo>`;
- the upgrade manifest is owned by the repo-spec repository and consumed by the upgrade command; the target repository does not expose or maintain it;
- the upgrade workflow reuses the basic lifecycle model of `repo-spec init --repo <new-repo>`;
- upgrade is staged before promotion;
- the staged upgraded repository is validated before promotion;
- normal upgrade scope is the target repository's `repo/` tree;
- the upgraded repository framework is re-anchored to the new repo-spec upgrade revision before validation;
- `product/` updates are exceptional and primarily validation-related;
- repo-spec needs a workflow for identifying which source-side manifest entries apply to a particular upgrade.

## Candidate groupings

1. source and target framework identity;
2. source-side managed-material inventory and upgrade-entry selection;
3. repository-first framework mutation;
4. exceptional product-validation propagation;
5. managed projection reconciliation outside `repo/`;
6. framework re-anchoring and upgrade provenance;
7. staged validation and promotion;
8. local customization and conflict handling;
9. recovery and failure reporting.

## Dependencies

1. identify the target's current framework revision;
2. identify the exact repo-spec revision supplying the upgrade;
3. reconcile managed-material inventories;
4. select the applicable upgrade entry set;
5. stage the existing target repository;
6. apply selected managed changes;
7. reconcile managed projections;
8. re-anchor the staged framework;
9. validate the full staged repository;
10. promote only after successful validation;
11. finalize upgrade provenance and cleanup.

## Ambiguities

Still unresolved are exact manifest schema/lifecycle, revision-range rules, dependency expression, deletion/rename semantics, local modification policy, compatibility enforcement, exact anchor representation, exceptional product eligibility, projection regeneration policy, existing-repository promotion mechanics, rollback/recovery, security policy, and hosted coordination.

## Candidate functional-set direction

The architecture evidence favors one end-to-end derived-repository upgrade capability rather than independent subsystems. No functional set is approved by this analysis.
