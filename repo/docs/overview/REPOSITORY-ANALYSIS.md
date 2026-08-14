# Repo-Spec Repository Analysis

## Status

Candidate migration analysis. Directional and non-normative.

## Metadata

```json
{
  "artifact_id": "repository.analysis",
  "artifact_type": "overview-analysis",
  "document_slug": "repository-analysis",
  "filename_stem": "repository-analysis",
  "root_path": "repo/docs/overview/",
  "title": "Repo-Spec Repository Analysis",
  "product_id": "repo-spec",
  "authority_category": "directional",
  "lifecycle_status": "candidate",
  "governing_issue": "#374",
  "required_content_areas": {
    "source_evidence": [
      "repo/docs/overview/repository-analysis/01-migration-analysis.md",
      "repo/docs/overview/repository-analysis/02-issue-routing-analysis.md"
    ],
    "candidate_groupings": [
      "repo/docs/overview/repository-analysis/01-migration-analysis.md",
      "repo/docs/overview/repository-analysis/02-issue-routing-analysis.md"
    ],
    "dependencies": [
      "repo/docs/overview/repository-analysis/01-migration-analysis.md",
      "repo/docs/overview/repository-analysis/02-issue-routing-analysis.md"
    ],
    "ambiguities": [
      "repo/docs/overview/repository-analysis/01-migration-analysis.md",
      "repo/docs/overview/repository-analysis/02-issue-routing-analysis.md"
    ],
    "candidate_functional_sets": [
      "repo/docs/overview/repository-analysis/01-migration-analysis.md",
      "repo/docs/overview/repository-analysis/02-issue-routing-analysis.md"
    ]
  },
  "controlling_documents": [
    "repo/docs/overview/REPOSITORY-WHITEBOARD.md"
  ],
  "predecessor_documents": [
    "repo/docs/overview/REPOSITORY-WHITEBOARD.md"
  ],
  "evidence": [
    "repo/docs/overview/repository-whiteboard/01-migration-input.md",
    "repo/docs/overview/repository-whiteboard/02-issue-routing-intake.md"
  ],
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/overview/repository-analysis/01-migration-analysis.md",
      "title": "Migration analysis",
      "coverage": [
        "source_evidence",
        "candidate_groupings",
        "dependencies",
        "ambiguities",
        "candidate_functional_sets"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/overview/repository-analysis/02-issue-routing-analysis.md",
      "title": "Issue-routing analysis",
      "coverage": [
        "source_evidence",
        "candidate_groupings",
        "dependencies",
        "ambiguities",
        "candidate_functional_sets"
      ]
    }
  ],
  "successor_action": "Decide whether to approve, revise, or reject the Issue Intake and Governance Routing candidate functional-set boundary before downstream decomposition or implementation.",
  "schema_version": "1"
}
```

## Overview

This analysis performs only the structural interpretation necessary to migrate maintained direction into the functional-set lifecycle.

## Chunk index

- [Migration analysis](repository-analysis/01-migration-analysis.md)
- [Issue-routing analysis](repository-analysis/02-issue-routing-analysis.md)

## Relationships

The analysis is controlled by and succeeds [Repo-Spec Repository whiteboard](./REPOSITORY-WHITEBOARD.md).

## Next authorized action

Review the **Issue Intake and Governance Routing** candidate boundary from [Issue-routing analysis](repository-analysis/02-issue-routing-analysis.md) before creating or approving successor functional-set material.

## Discoverability

- [Overview root index](./README.md)
