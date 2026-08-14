# Issue-routing analysis

## Source evidence

This analysis consumes:

- `repo/docs/overview/repository-whiteboard/02-issue-routing-intake.md`;
- the existing approved repository functional-set context for Git and change workflow;
- the existing approved repository functional-set context for governance and evolution.

The whiteboard evidence introduces a pre-governance intake/routing concern that is not covered by the migration-only analysis.

## Candidate capability grouping

The evidence clusters into one coherent capability:

**Issue Intake and Governance Routing**

This candidate capability covers the transition from an ordinary issue into the correct governed lifecycle before bounded repository mutation begins.

Its core concerns are:

- accepting ordinary unformatted issue intake;
- classifying intake as `bug-fix` or `feature-request`;
- routing `bug-fix` intake into audit;
- routing `feature-request` intake into whiteboard/functional-set development;
- promoting an issue into `governed-work` only when a bounded governed operation is ready;
- preserving original intake evidence during promotion;
- ensuring governed-work field validation begins only after promotion.

## Relationship to the existing approved functional set

The existing approved repository functional set already defines:

- Git-native bounded change workflow;
- governing issues as bounded authorization surfaces;
- hosting-platform profiles, including issue and label behavior;
- validation and hosted field-policy boundaries;
- authority separation among overview, governance, implementation, validation, review, acceptance, and merge.

The newly collected intake-routing evidence is related to these capabilities but precedes them.

The existing bounded-change workflow begins from the question of which governing issue controls work. The new candidate capability governs an earlier question: **what lifecycle should an ordinary intake issue enter before a governing issue exists or before the issue itself is promoted into one?**

This makes issue intake/routing a dependency boundary ahead of the existing governed-change workflow rather than a replacement for it.

## Dependencies

The candidate capability depends on:

1. **Audit workflow**
   - `bug-fix` routing requires an audit path capable of determining whether reported behavior violates controlling authority.
   - Audit must not invent missing product intent.

2. **Whiteboard and functional-set lifecycle**
   - `feature-request` routing requires collection as non-normative evidence, analysis, candidate functional-set formation, and explicit approval before downstream realization.

3. **Governing-issue lifecycle**
   - promotion into `governed-work` requires a canonical governed issue body and bounded scope.

4. **Hosting-platform profile**
   - issue labels, comments, issue-body updates, and issue-event behavior are GitHub-specific or profile-specific concerns rather than Git-generic behavior.

5. **Field-policy validation**
   - governed-work field validation must distinguish unformatted intake from promoted governed issues.

6. **Continuity and provenance**
   - original intake text and classification evidence must remain recoverable after canonical-body replacement.

## Candidate boundary

A candidate functional set can be bounded as follows:

### Candidate: Issue Intake and Governance Routing

Included direction:

- ordinary issue intake may exist before governance;
- intake classification is separate from governance state;
- `bug-fix` and `feature-request` act as routing classifications;
- `bug-fix` enters audit;
- `feature-request` enters whiteboard/functional-set development;
- promotion to `governed-work` establishes entry into a bounded governed operation;
- original intake evidence survives promotion;
- field-policy enforcement applies only after promotion.

Excluded from this candidate boundary:

- detailed audit semantics;
- detailed whiteboard/functional-set mechanics already governed elsewhere;
- implementation-specific GitHub API sequencing;
- exact CI YAML;
- exact label creation commands;
- detailed governing-issue schema;
- implementation planning or repository mutation.

Those belong to downstream decomposition/specification/implementation if this candidate is later approved.

## Ambiguities

The whiteboard leaves several choices unresolved.

### Classification exclusivity

It is unresolved whether `bug-fix` and `feature-request` must be mutually exclusive.

Analysis recommendation: treat them as mutually exclusive routing states by default because they direct the issue into different authority paths. If both are present, fail closed and require classification resolution before progression.

This recommendation remains candidate analysis, not accepted direction.

### Feature-request promotion timing

It is unresolved when a feature-request issue itself becomes `governed-work`.

Two models remain plausible:

1. promote the original feature-request issue when governed whiteboard/analysis work begins; or
2. keep the original feature-request as intake evidence and create or promote successor governed issues only when bounded repository mutations are authorized.

Analysis recommendation: prefer the second model because whiteboard collection and analysis are lifecycle stages that do not themselves authorize product implementation, and because it better preserves the distinction between intake intent and bounded governed mutations.

This recommendation remains candidate analysis.

### Original issue versus successor issues

It is unresolved whether downstream implementation should continue on the original feature-request issue.

Analysis recommendation: allow the original intake issue to remain the durable request/provenance surface while successor governed issues authorize bounded whiteboard, analysis, functional-set, specification, plan, and implementation mutations as needed.

This recommendation remains candidate analysis.

### Promotion mechanics

The exact order of issue comment creation, body replacement, label application, and CI triggering is implementation detail.

The analysis-level invariant is only:

1. preserve intake evidence first;
2. ensure the canonical governed body is complete before governed-work field validation becomes active;
3. avoid an observable invalid intermediate governed-work state.

### Label lifecycle

The whiteboard expects routing labels to remain visible after promotion, but exact retention/removal rules remain unresolved.

Analysis recommendation: retain the routing classification label as provenance while adding `governed-work` as lifecycle state, unless later specification identifies a reason to normalize or supersede classification.

This recommendation remains candidate analysis.

## Candidate functional-set conclusion

The collected evidence supports one coherent candidate functional set:

**Issue Intake and Governance Routing**

It is sufficiently distinct from the existing approved bounded-change workflow to merit its own candidate boundary because it governs lifecycle selection before governed work begins.

This analysis does **not** approve that functional set.

The next lifecycle decision should be whether to accept this candidate as repository direction, revise its boundary, or fold it into an existing accepted functional set.
