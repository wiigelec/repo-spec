# Derived-repository upgrade analysis

## Source evidence

The controlling collection evidence is `product/docs/overview/INITIALIZER-WHITEBOARD.md` and its second subordinate chunk, `product/docs/overview/initializer-whiteboard/02-derived-repository-upgrade-intake.md`, with GitHub issue #418 retained as intake provenance.

The collected request is that repositories initialized from an earlier repo-spec revision should have some future product capability through which later repo-spec changes can be propagated to them. The intake explicitly names new features, bug fixes, and security enhancements, while leaving the upgrade mechanism, compatibility policy, migration policy, conflict policy, and implementation form unresolved.

During governed analysis, the user supplied three additional directional decisions:

- the user invokes upgrade through `repo-spec upgrade --repo <existing-repo>`;
- the target derived repository exposes a manifest identifying repo-spec-managed/upgradable files;
- the upgrade command should fit within the same basic lifecycle as `repo-spec init --repo <new-repo>`, specifically staging the prospective repository state, validating it, promoting only after successful validation, and then finalizing success.

The existing initializer implementation provides the established lifecycle vocabulary: `staging-establishment`, `repository-validation`, `promotion`, and `success-finalization`. Upgrade should adapt that model rather than introduce an unrelated lifecycle.

## Candidate groupings

The evidence supports several capability-oriented groupings for later functional-set consideration without choosing exact behavior.

### Upgrade source and target identity

A future upgrade capability needs to reason about the relationship between the repo-spec state from which a derived repository originated and a later repo-spec state that may be applied. This includes source identity, target identity, provenance, and eligibility of changes between those states.

### Managed-content evolution and upgrade manifest

The target derived repository should expose a manifest identifying files managed by repo-spec and therefore eligible for upgrade handling.

That manifest provides the directional basis for distinguishing repo-spec-managed material from product-owned or repository-local material. The exact manifest name, location, schema, producer, lifecycle, revision metadata, and ownership semantics remain unresolved.

Directional concerns include managed-versus-local ownership, local modifications to managed content, preservation of local customization, human conflict resolution, and how the manifest itself is created and maintained as the repository evolves.

### Change-class policy

The intake distinguishes new features, bug fixes, and security enhancements. That distinction may imply different urgency, compatibility expectations, opt-in behavior, or validation needs, but this analysis does not establish whether those classes share one policy or use distinct policy paths.

### Initializer-aligned upgrade execution lifecycle

The upgrade command should reuse the same basic lifecycle model already used by `repo-spec init --repo <new-repo>` rather than define a parallel lifecycle.

For upgrade, the established initializer stages imply this directional sequence:

1. establish a staged prospective repository state (`staging-establishment`);
2. perform upgrade-specific preparation and file application inside that staged state;
3. validate the staged repository (`repository-validation`);
4. permit promotion only after successful repository validation (`promotion`);
5. finalize the successful operation after promotion (`success-finalization`).

The exact upgrade-specific stages between staging establishment and repository validation remain unresolved, as do staging representation, promotion mechanics, rollback/recovery, and handling of indeterminate promotion.

### Upgrade command and hosted coordination

The user-facing initiation surface is resolved as `repo-spec upgrade --repo <existing-repo>`, where `<existing-repo>` identifies the existing derived repository to upgrade.

The command should enter the initializer-aligned staged lifecycle described above. This does not decide how it discovers source or target repo-spec state, how it consumes the managed-file manifest, or whether hosted workflows may propose or coordinate command invocation. Any hosted coordination remains subordinate to the command-driven product lifecycle.

## Dependencies

The candidate groupings have a directional dependency order:

1. source and target identity before eligibility;
2. the target repository's managed-file manifest and resulting managed-content boundaries before safe application;
3. change-class policy over identified changes;
4. initializer-aligned `staging-establishment` before upgrade application and `repository-validation` before `promotion`;
5. `success-finalization` only after committed promotion;
6. any hosted coordination subordinate to the `repo-spec upgrade --repo <existing-repo>` command lifecycle.

The analysis also depends on initializer provenance because derivation cannot be reasoned about reliably if the originating repo-spec identity is unavailable or untrustworthy.

## Ambiguities

The evidence does not resolve:

- the exact managed-file manifest name, path, schema, producer, lifecycle, and trust model;
- what counts as repo-spec-managed content after initialization and how the manifest represents that ownership;
- whether all repo-spec revisions are valid sources or targets;
- whether upgrades may skip revisions;
- what compatibility guarantees exist;
- how local modifications are preserved, merged, rejected, or escalated;
- whether feature, bug-fix, and security updates use one policy or distinct policy paths;
- whether security updates may alter ordinary opt-in or compatibility expectations;
- whether application must be atomic;
- how generated artifacts participate;
- what rollback guarantees exist;
- how partial upgrades are represented;
- what exact provenance must be persisted;
- whether hosted workflows may propose, coordinate, or observe invocation of the command-driven upgrade flow.

These ambiguities remain unresolved until later lifecycle stages have authority to decide them.

## Candidate functional sets

### Candidate A — Derived-repository upgrade lifecycle

One end-to-end capability exposed through `repo-spec upgrade --repo <existing-repo>`, using a managed-file manifest and the initializer-aligned staged validation/promotion lifecycle, while spanning source/target identity, eligibility, managed-content evolution, recovery, provenance, and optional hosted coordination.

### Candidate B — Upgrade identity and compatibility foundation

A narrower foundation centered on source/target provenance, managed-content boundaries, eligibility, and compatibility determination, leaving execution orchestration and recovery to a later functional set.

### Candidate C — Managed update application

A narrower execution-centered boundary focused on safely applying an already selected and authorized repo-spec change set to a derived repository, including local-customization handling, validation, recovery, and provenance.

No candidate is approved by this analysis. Candidate A appears to best preserve the original end-to-end request, but explicit candidate formation and approval remain separate successor work.
