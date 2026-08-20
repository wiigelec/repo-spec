# Validation System Desired-State Architecture

## Status

Accepted architecture authority under governing issue #348.

This document defines the desired steady-state architecture for the repo-spec validation
system. It is intentionally not an implementation plan, cleanup issue, or migration log.
Its purpose is to provide a stable repository-resident baseline against which future
validation audits compare the maintained system.

Accepted normative specifications remain authoritative for required validation behavior.
Current implementation and historical issues are evidence of present or past realization,
not authority for the desired architecture.

## Metadata

```json
{
  "artifact_id": "validation-system-desired-state",
  "artifact_type": "architecture-plan",
  "document_slug": "validation-system-desired-state",
  "filename_stem": "validation-system-desired-state-architecture",
  "root_path": "repo/docs/architecture/",
  "title": "Validation System Desired-State Architecture",
  "product_id": "repo-spec validation system",
  "authority_category": "directional",
  "lifecycle_status": "accepted",
  "governing_issue": "#348",
  "controlling_documents": [],
  "predecessor_documents": [],
  "evidence": [
    "repo/specs/repo/validation.json",
    "repo/validation/checks/domain.py",
    "repo/validation/checks/specifications.py",
    "repo/validation/checks/policy.py",
    "repo/validation/checks/development_documents.py",
    "repo/validation/checks/generated_outputs.py"
  ],
  "required_content_areas": {
    "authority_and_basis": [
      "repo/docs/architecture/validation-system-desired-state/01-purpose-authority-and-boundaries.md"
    ],
    "scope_and_boundaries": [
      "repo/docs/architecture/validation-system-desired-state/01-purpose-authority-and-boundaries.md"
    ],
    "target_architecture": [
      "repo/docs/architecture/validation-system-desired-state/02-target-architecture-and-ownership.md"
    ],
    "portability_and_ownership": [
      "repo/docs/architecture/validation-system-desired-state/02-target-architecture-and-ownership.md"
    ],
    "validation_strategy": [
      "repo/docs/architecture/validation-system-desired-state/03-test-strategy-and-efficiency.md"
    ],
    "risks_and_unresolved_decisions": [
      "repo/docs/architecture/validation-system-desired-state/04-audit-model-retirement-and-completion.md"
    ],
    "audit_and_successor_work": [
      "repo/docs/architecture/validation-system-desired-state/04-audit-model-retirement-and-completion.md"
    ]
  },
  "subordinate_chunks": [
    {
      "order": 1,
      "path": "repo/docs/architecture/validation-system-desired-state/01-purpose-authority-and-boundaries.md",
      "title": "Purpose, authority, and boundaries",
      "coverage": [
        "authority_and_basis",
        "scope_and_boundaries"
      ]
    },
    {
      "order": 2,
      "path": "repo/docs/architecture/validation-system-desired-state/02-target-architecture-and-ownership.md",
      "title": "Target architecture and ownership",
      "coverage": [
        "target_architecture",
        "portability_and_ownership"
      ]
    },
    {
      "order": 3,
      "path": "repo/docs/architecture/validation-system-desired-state/03-test-strategy-and-efficiency.md",
      "title": "Test strategy and efficiency",
      "coverage": [
        "validation_strategy"
      ]
    },
    {
      "order": 4,
      "path": "repo/docs/architecture/validation-system-desired-state/04-audit-model-retirement-and-completion.md",
      "title": "Audit model, retirement, and completion",
      "coverage": [
        "risks_and_unresolved_decisions",
        "audit_and_successor_work"
      ]
    }
  ],
  "successor_action": "After this architecture is accepted through issue #348, perform a fresh validation-system audit against then-current main and current accepted normative specifications. Any implementation changes require separate bounded governed issue authority.",
  "schema_version": "1"
}
```

## Architecture basis

The accepted `repo.validation` specification defines what repository and product validation
must enforce. This architecture is subordinate to those normative requirements and defines
how the maintained validation system should be partitioned, owned, tested, exported, and
audited over time.

The architecture also incorporates the accepted initializer output-inventory and
framework-installation contracts as evidence for a deliberate portability boundary:
initialized repositories should receive a closed, explicit validation runtime subset
rather than repo-spec development-only validation infrastructure.

## Desired state

The steady-state validation system is small, deterministic, repository-local, and
function-owned. Every maintained production rule exists because current accepted authority
assigns a machine-checkable invariant to that validation domain. Every self-test exists to
prove a current validator contract or distinct failure boundary.

Historical milestones, patches, migrations, issues, and one-time conformance campaigns do
not define permanent validation architecture.

Future audits should be able to answer for every validator, test module, fixture, and
public entry point:

- Which current invariant does this own?
- Why is this the correct layer to own it?
- Is the same invariant being proved elsewhere?
- Would removing this artifact reduce current required coverage?
- Is this artifact present because of current architecture or only because of history?
- If exported by the initializer, is it part of the closed portable runtime dependency
  set actually required by initialized repositories?

If those questions cannot be answered from accepted authority and this architecture, the
artifact is a candidate for consolidation, relocation, or retirement.

## Chunk index

- [Purpose, authority, and boundaries](./validation-system-desired-state/01-purpose-authority-and-boundaries.md)
- [Target architecture and ownership](./validation-system-desired-state/02-target-architecture-and-ownership.md)
- [Test strategy and efficiency](./validation-system-desired-state/03-test-strategy-and-efficiency.md)
- [Audit model, retirement, and completion](./validation-system-desired-state/04-audit-model-retirement-and-completion.md)

## Relationships

This architecture is directionally controlled by
`repo/docs/overview/REPOSITORY-FUNCTIONAL-SET.md`.

Normative validation behavior remains governed by accepted specifications, especially
`repo.validation`. The initializer output inventory and framework-installation
specifications are evidence for the portable runtime boundary; they are not substituted
for development-document relationships.

## Next authorized action

Perform a fresh validation-system audit against this accepted architecture and
then-current `main`, using current accepted normative specifications as behavioral
authority.

The audit shall include the initialized-repository validation export and runtime
dependency boundary. Any implementation change found by that audit requires a separate
bounded governed issue.

## Discoverability

Use this architecture when auditing validation ownership, test duplication, stale
transition coverage, routine-validation efficiency, or the initialized-repository
portable validation boundary.

For normative requirements, consult accepted specifications. For implementation changes,
use a separately bounded governing issue derived from a fresh audit against this
architecture.
