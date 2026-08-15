# Derived-repository upgrade analysis

## Source evidence

The controlling collection evidence is `product/docs/overview/INITIALIZER-WHITEBOARD.md` and its second subordinate chunk, `product/docs/overview/initializer-whiteboard/02-derived-repository-upgrade-intake.md`, with GitHub issue #418 retained as intake provenance.

The collected request is that repositories initialized from an earlier repo-spec revision should have some future product capability through which later repo-spec changes can be propagated to them. The intake explicitly names new features, bug fixes, and security enhancements, while leaving the upgrade mechanism, compatibility policy, migration policy, conflict policy, and implementation form unresolved.

## Candidate groupings

The evidence supports several capability-oriented groupings for later functional-set consideration without choosing exact behavior.

### Upgrade source and target identity

A future upgrade capability needs to reason about the relationship between the repo-spec state from which a derived repository originated and a later repo-spec state that may be applied. This includes source identity, target identity, provenance, and eligibility of changes between those states.

### Managed-content evolution

The capability must distinguish repo-spec-managed material from product-owned or repository-local material in a derived repository. Directional concerns include managed-versus-local ownership, local modifications to managed content, preservation of local customization, and human conflict resolution.

### Change-class policy

The intake distinguishes new features, bug fixes, and security enhancements. That distinction may imply different urgency, compatibility expectations, opt-in behavior, or validation needs, but this analysis does not establish whether those classes share one policy or use distinct policy paths.

### Upgrade execution lifecycle

A future upgrade capability may require a bounded lifecycle around proposal, validation, application, failure handling, completion evidence, generated artifacts, rollback or recovery, and persisted upgrade provenance.

### Local and hosted orchestration

The evidence leaves open whether upgrades are initiated only locally or may also be proposed or coordinated through hosted workflows. Hosted orchestration, if present, remains subordinate to the underlying product upgrade semantics.

## Dependencies

The candidate groupings have a directional dependency order:

1. source and target identity before eligibility;
2. managed-content boundaries before safe application;
3. change-class policy over identified changes;
4. execution lifecycle over selected eligible changes and managed-content boundaries;
5. hosted orchestration subordinate to the underlying upgrade lifecycle.

The analysis also depends on initializer provenance because derivation cannot be reasoned about reliably if the originating repo-spec identity is unavailable or untrustworthy.

## Ambiguities

The evidence does not resolve:

- what counts as repo-spec-managed content after initialization;
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
- whether hosted workflows may initiate, only propose, or merely observe upgrades.

These ambiguities remain unresolved until later lifecycle stages have authority to decide them.

## Candidate functional sets

### Candidate A — Derived-repository upgrade lifecycle

One end-to-end capability spanning source/target identity, eligibility, managed-content evolution, execution lifecycle, validation, recovery, provenance, and optional hosted coordination.

### Candidate B — Upgrade identity and compatibility foundation

A narrower foundation centered on source/target provenance, managed-content boundaries, eligibility, and compatibility determination, leaving execution orchestration and recovery to a later functional set.

### Candidate C — Managed update application

A narrower execution-centered boundary focused on safely applying an already selected and authorized repo-spec change set to a derived repository, including local-customization handling, validation, recovery, and provenance.

No candidate is approved by this analysis. Candidate A appears to best preserve the original end-to-end request, but explicit candidate formation and approval remain separate successor work.
