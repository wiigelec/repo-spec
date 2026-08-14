# functional-set lifecycle: Issue Intake and Governance Routing

This part defines the approved pre-governance capability that routes ordinary issue intake into the correct repository authority path before bounded governed work begins.

## Capability boundary

Issue Intake and Governance Routing governs the transition from an ordinary issue into the repository lifecycle that is appropriate for the reported or requested work.

It precedes the existing bounded governed-change workflow. It does not replace that workflow and does not itself authorize repository mutation.

## Included intent

The framework should support ordinary unformatted issue intake before governance is established.

Intake classification is distinct from governance state:

- `bug-fix` is a routing classification for reported behavior believed to violate already accepted authority;
- `feature-request` is a routing classification for new or changed direction;
- `governed-work` is a governance-state label indicating that a bounded governed operation is active.

A `bug-fix` intake should route into audit before direct repository mutation.

A `feature-request` intake should route into whiteboard collection and the functional-set lifecycle before implementation authority exists.

Promotion to `governed-work` establishes entry into a bounded governed operation and therefore requires the canonical governed issue structure appropriate to that operation.

Original intake evidence must remain recoverable when promotion replaces or restructures the issue body.

Governed-work field validation should apply only after promotion into governed state; ordinary intake should not be rejected for lacking governed-work fields.

## Relationship to existing capabilities

This capability feeds the existing Git and Change Workflow capability.

The Git and Change Workflow governs bounded work once a governing issue exists. Issue Intake and Governance Routing governs the earlier lifecycle-selection question: which authority path should an ordinary issue enter, and when is it appropriate to become governed work?

This capability also depends on:

- the audit workflow for `bug-fix` routing;
- the whiteboard, analysis, and functional-set lifecycle for `feature-request` routing;
- the governing-issue contract for promotion into bounded governed work;
- hosting-platform profiles for issue, label, comment, and event behavior;
- hosted field-policy validation;
- continuity/provenance expectations for preserving original intake.

## Exclusions

This functional set does not define:

- exact GitHub API sequencing;
- exact label creation commands or label-color choices;
- exact CI workflow YAML;
- detailed governing-issue schema;
- audit semantics beyond the routing dependency;
- whiteboard/analysis mechanics beyond the routing dependency;
- implementation planning;
- concrete automation;
- executable repository behavior.

Those belong to downstream decomposition, specifications, planning, and implementation.

## Approved directional decisions

The following direction is approved:

- issue intake may exist before governance;
- routing classification and governance state are separate concepts;
- `bug-fix` routes into audit;
- `feature-request` routes into governed whiteboard/functional-set development;
- `governed-work` marks entry into a bounded governed operation;
- intake evidence survives promotion;
- governed-work field validation begins only after promotion.

Detailed downstream mechanics remain intentionally unresolved and must be specified before implementation.

## Decomposition handoff

Downstream decomposition should define the repository-owned responsibilities, platform-profile responsibilities, lifecycle transitions, provenance requirements, and validation boundaries necessary to realize this capability without weakening existing audit, functional-set, governing-issue, or bounded-change authority.
