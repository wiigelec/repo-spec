# Repo-Spec Issue Intake and Governance Routing Implementation Plan

## Status

Accepted; planning-authoritative; non-normative with respect to repository semantics.

This document is the controlling entry point for the accepted Issue Intake and Governance Routing implementation-plan composite. Issue #400 created and reviewed the candidate plan; issue #402 records explicit acceptance. The plan authorizes separately governed implementation issues only after the accepted-plan patch is manually merged and post-merge validation passes. The plan does not itself mutate maintained implementation artifacts.

## Metadata

```json
{
  "artifact_id": "repository-implementation-plan",
  "artifact_type": "implementation-plan",
  "document_slug": "repository-implementation-plan",
  "filename_stem": "repository-implementation-plan",
  "root_path": "repo/docs/plans/",
  "title": "Repo-Spec Issue Intake and Governance Routing Implementation Plan",
  "product_id": "repo-spec",
  "authority_category": "planning",
  "lifecycle_status": "accepted",
  "governing_issue": "#400, #402",
  "controlling_documents": [
    "repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md",
    "repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md"
  ],
  "predecessor_documents": [
    "repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md"
  ],
  "evidence": [
    "repo/docs/overview/repository-functional-set/10-issue-intake-and-governance-routing.md",
    "repo/docs/decompositions/repository-decomposition/01-intake-classification.md",
    "repo/docs/decompositions/repository-decomposition/02-authority-routing.md",
    "repo/docs/decompositions/repository-decomposition/03-governed-work-promotion-and-provenance.md",
    "repo/docs/decompositions/repository-decomposition/04-platform-validation-integration.md",
    "repo/specs/repo/issue-routing-governance.json",
    "repo/specs/repo/issue-routing-classification.json",
    "repo/specs/repo/governed-work-provenance.json",
    "repo/specs/repo/issue-authority-routing.json",
    "repo/specs/repo/governed-work-promotion.json",
    "repo/specs/repo/issue-routing-platform-validation.json",
    "repo/specs/repo/issue-intake-governance-routing.json"
  ],
  "workstream_authority": [
    {
      "id": "IRP-I1",
      "controlling_product_specifications": [
        "repo.issue-routing-governance",
        "repo.issue-routing-classification"
      ]
    },
    {
      "id": "IRP-I2",
      "controlling_product_specifications": [
        "repo.issue-routing-governance",
        "repo.issue-routing-classification",
        "repo.issue-authority-routing"
      ]
    },
    {
      "id": "IRP-I3",
      "controlling_product_specifications": [
        "repo.issue-routing-governance",
        "repo.governed-work-provenance",
        "repo.issue-authority-routing",
        "repo.governed-work-promotion"
      ]
    },
    {
      "id": "IRP-I4",
      "controlling_product_specifications": [
        "repo.issue-routing-governance",
        "repo.governed-work-provenance",
        "repo.governed-work-promotion",
        "repo.issue-routing-platform-validation"
      ]
    },
    {
      "id": "IRP-I5",
      "controlling_product_specifications": [
        "repo.issue-routing-governance",
        "repo.issue-routing-classification",
        "repo.governed-work-provenance",
        "repo.issue-authority-routing",
        "repo.governed-work-promotion",
        "repo.issue-routing-platform-validation",
        "repo.issue-intake-governance-routing"
      ]
    }
  ],
  "required_content_areas": {
    "authority_and_basis": [
      "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "scope_and_exclusions": [
      "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md"
    ],
    "workstreams_and_dependencies": [
      "repo/docs/plans/repository-implementation-plan/02-workstreams-and-dependencies.md"
    ],
    "entry_and_exit_conditions": [
      "repo/docs/plans/repository-implementation-plan/02-workstreams-and-dependencies.md"
    ],
    "transition_gates": [
      "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "validation_strategy": [
      "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md"
    ],
    "risks_and_unresolved_decisions": [
      "repo/docs/plans/repository-implementation-plan/04-risks-and-unresolved-decisions.md"
    ],
    "completion_and_successor_work": [
      "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/plans/repository-implementation-plan/01-authority-scope-and-specification-map.md",
      "title": "Authority, scope, and specification map",
      "coverage": [
        "authority_and_basis",
        "scope_and_exclusions"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/plans/repository-implementation-plan/02-workstreams-and-dependencies.md",
      "title": "Workstreams and dependencies",
      "coverage": [
        "workstreams_and_dependencies",
        "entry_and_exit_conditions"
      ]
    },
    {
      "order": 3,
      "path": "repo/docs/plans/repository-implementation-plan/03-validation-gates-and-completion.md",
      "title": "Validation, gates, and completion",
      "coverage": [
        "transition_gates",
        "validation_strategy",
        "completion_and_successor_work"
      ]
    },
    {
      "order": 4,
      "path": "repo/docs/plans/repository-implementation-plan/04-risks-and-unresolved-decisions.md",
      "title": "Risks and unresolved decisions",
      "coverage": [
        "risks_and_unresolved_decisions"
      ]
    }
  ],
  "successor_action": "After the corrected repository authority chain is accepted and post-merge validation passes, create separately governed implementation issues in dependency order for IRP-I1 through IRP-I5. Each issue must cite this accepted plan, exact workstream ID(s), exact controlling accepted repository specifications, accepted default-branch base, and predecessor evidence.",
  "schema_version": "1"
}
```

## Planning basis

The accepted Issue Intake and Governance Routing repository specifications are normative repository authority. This plan sequences and coordinates implementation without redefining those semantics.

Accepted planning authority migration basis: `issue-431-correct-repository-lifecycle-authority` at `d9cf6acc1167ff60534e3fef23a359b0b116aa1c`.

The controlling directional predecessors are the approved repository functional set and accepted repository decomposition. Exact behavior remains controlled by the accepted repository specifications listed in the metadata evidence and workstream authority sets.

## Workstreams

| Workstream | Purpose | Dependency |
| --- | --- | --- |
| IRP-I1 | Intake classification realization | none |
| IRP-I2 | Authority routing realization | IRP-I1 |
| IRP-I3 | Provenance-preserving governed-work promotion | IRP-I1, IRP-I2 |
| IRP-I4 | Hosted validation and platform integration | IRP-I3 |
| IRP-I5 | End-to-end integration and conformance | IRP-I1 through IRP-I4 |

Each workstream's exact controlling accepted repository specifications are declared in `workstream_authority`.

## Execution order

Primary order:

`IRP-I1 -> IRP-I2 -> IRP-I3 -> IRP-I4 -> IRP-I5`

Parallel work is allowed only where an implementation issue can prove that its entry conditions and controlling accepted specifications are satisfied without depending on unfinished predecessor behavior.

## Accepted planning boundary

This accepted plan may select implementation mechanics needed to realize accepted repository behavior, but it may not manufacture new repository semantics. A newly discovered semantic gap must return to specification governance.

Portable implementation, test, and conformance artifacts used as maintained correspondence evidence for the seven controlling `repo.*` specifications are repository-owned and shall reside within the accepted repository-owned implementation/test/conformance surface rather than repository/framework tooling paths. Repository/framework helpers and hosting-profile source or installed adapters may remain under their accepted repository/profile-owned locations, but those repository/profile artifacts do not substitute for repository-owned correspondence evidence when IRP-I5 claims covered implementation/test/conformance for a repository specification.

This ownership boundary constrains implementation mechanics only; it does not redefine routing, provenance, promotion, authority, or hosted-validation repository semantics.

## Chunk index

- [Authority, scope, and specification map](./repository-implementation-plan/01-authority-scope-and-specification-map.md)
- [Workstreams and dependencies](./repository-implementation-plan/02-workstreams-and-dependencies.md)
- [Validation, gates, and completion](./repository-implementation-plan/03-validation-gates-and-completion.md)
- [Risks and unresolved decisions](./repository-implementation-plan/04-risks-and-unresolved-decisions.md)

## Relationships

- Governing issue: #400.
- Controlling planning contracts: `repo.implementation-plan`, `repo.development-document-base`, `repo.development-workflow`, and `repo.validation`.
- Controlling functional-set capability: Issue Intake and Governance Routing.
- Controlling decomposition: `repo/docs/decompositions/REPOSITORY-DECOMPOSITION.md`.
- Normative product authority: the seven accepted Issue Intake and Governance Routing repository specifications.

## Next authorized action

After the corrected repository authority chain is manually merged and post-merge validation passes, separately governed implementation issues may cite IRP-I1 through IRP-I5 as planning authority in dependency order.

## Discoverability

- [Repository plan root](./README.md)
- [Repository decomposition](../decompositions/REPOSITORY-DECOMPOSITION.md)
- [Repository functional set](../overview/REPOSITORY-FUNCTIONAL-SET.md)
