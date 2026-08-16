# Repo-Spec Initializer Upgrade Decomposition

## Status

Accepted directional decomposition for the approved derived-repository upgrade functional set.

This document is the controlling entry point for the initializer-upgrade decomposition composite document. It is directional and non-normative.

## Metadata

```json
{
  "artifact_id": "initializer-upgrade-decomposition",
  "artifact_type": "product-decomposition",
  "document_slug": "initializer-upgrade-decomposition",
  "filename_stem": "initializer-upgrade-decomposition",
  "root_path": "product/docs/decompositions/",
  "title": "Repo-Spec Initializer Upgrade Decomposition",
  "product_id": "repo-spec initializer",
  "authority_category": "directional",
  "lifecycle_status": "accepted",
  "governing_issue": "#443",
  "controlling_documents": ["product/docs/overview/INITIALIZER-UPGRADE-FUNCTIONAL-SET.md"],
  "predecessor_documents": ["product/docs/overview/INITIALIZER-UPGRADE-FUNCTIONAL-SET.md"],
  "evidence": [
    "product/docs/overview/INITIALIZER-ANALYSIS.md",
    "product/docs/overview/initializer-analysis/02-derived-repository-upgrade-analysis.md",
    "product/docs/overview/initializer-analysis/03-derived-repository-upgrade-architecture-audit.md",
    "product/docs/overview/initializer-analysis/04-derived-repository-upgrade-methodologies.md",
    "product/docs/overview/initializer-analysis/05-derived-repository-upgrade-handoff.md",
    "product/docs/overview/initializer-upgrade-functional-set/01-capability-boundary-and-outcome.md",
    "product/docs/overview/initializer-upgrade-functional-set/02-framework-identity-and-managed-material.md",
    "product/docs/overview/initializer-upgrade-functional-set/03-staged-managed-upgrade.md",
    "product/docs/overview/initializer-upgrade-functional-set/04-reanchoring-validation-and-promotion.md",
    "product/docs/overview/initializer-upgrade-functional-set/05-boundaries-and-unresolved-direction.md",
    "product/docs/overview/initializer-upgrade-functional-set/06-decomposition-handoff.md"
  ],
  "required_content_areas": {
    "decomposition_basis": ["product/docs/decompositions/initializer-upgrade-decomposition/01-request-identity-and-eligibility.md"],
    "product_area_inventory": [
      "product/docs/decompositions/initializer-upgrade-decomposition/01-request-identity-and-eligibility.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/03-staged-application-and-projections.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/04-reanchoring-and-provenance.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"
    ],
    "dependency_model": [
      "product/docs/decompositions/initializer-upgrade-decomposition/01-request-identity-and-eligibility.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/03-staged-application-and-projections.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/04-reanchoring-and-provenance.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"
    ],
    "cross_cutting_concerns": [
      "product/docs/decompositions/initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/03-staged-application-and-projections.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/04-reanchoring-and-provenance.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"
    ],
    "unresolved_decisions": [
      "product/docs/decompositions/initializer-upgrade-decomposition/01-request-identity-and-eligibility.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/03-staged-application-and-projections.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/04-reanchoring-and-provenance.md",
      "product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"
    ],
    "stopping_criteria": ["product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"],
    "planning_handoff": ["product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md"]
  },
  "subordinate_chunks": [
    {"order": 1, "path": "product/docs/decompositions/initializer-upgrade-decomposition/01-request-identity-and-eligibility.md", "title": "Request, identity, and eligibility", "role": "product-area", "area_id": "request-identity-and-eligibility", "document_coverage": ["decomposition_basis", "product_area_inventory", "dependency_model", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 2, "path": "product/docs/decompositions/initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md", "title": "Managed-material delta and reconciliation", "role": "product-area", "area_id": "managed-material-delta-and-reconciliation", "document_coverage": ["product_area_inventory", "dependency_model", "cross_cutting_concerns", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 3, "path": "product/docs/decompositions/initializer-upgrade-decomposition/03-staged-application-and-projections.md", "title": "Staged application and projections", "role": "product-area", "area_id": "staged-application-and-projections", "document_coverage": ["product_area_inventory", "dependency_model", "cross_cutting_concerns", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 4, "path": "product/docs/decompositions/initializer-upgrade-decomposition/04-reanchoring-and-provenance.md", "title": "Re-anchoring and provenance", "role": "product-area", "area_id": "reanchoring-and-provenance", "document_coverage": ["product_area_inventory", "dependency_model", "cross_cutting_concerns", "unresolved_decisions"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]},
    {"order": 5, "path": "product/docs/decompositions/initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md", "title": "Validation, promotion, and outcomes", "role": "product-area", "area_id": "validation-promotion-and-outcomes", "document_coverage": ["product_area_inventory", "dependency_model", "cross_cutting_concerns", "unresolved_decisions", "stopping_criteria", "planning_handoff"], "coverage": ["purpose", "responsibilities", "boundaries", "dependencies", "exclusions", "unresolved-decisions", "successor-work"]}
  ],
  "successor_action": "Proceed to governed creation or revision and acceptance of the owner-appropriate Level 0-3 normative product specification set required to define the initializer-upgrade capability before implementation planning.",
  "schema_version": "1"
}
```

## Decomposition basis

This decomposition translates the approved derived-repository upgrade functional set into bounded product areas. It is directional and non-normative. It does not define exact product semantics, accept any normative product specification, select an implementation architecture, or authorize implementation.

The analysis-stage U1-U8 boundaries remain predecessor evidence. This accepted decomposition deliberately regroups that evidence into five coherent product areas and does not treat U1-U8 as independently accepted decomposition units.

## Bounded areas

The upgrade capability is decomposed into request/identity/eligibility, managed-material delta/reconciliation, staged application/projections, re-anchoring/provenance, and validation/promotion/outcomes.

The dependency direction is:

request and framework identity -> resolve the currently accepted baseline repo-spec initialization manifest and supplying reconciliation-target initialization manifest -> compare those initializer-managed inventories and select the legal reconciliation set -> staged managed application and projection reconciliation -> framework re-anchoring and durable accepted reconciliation lineage -> complete staged validation -> promotion or non-promotion outcome -> finalization.

## Cross-cutting concerns

Cross-cutting concerns include preservation of product-owned work outside initializer-managed authority, local changes to initializer-managed material, compatibility across framework revisions, deterministic evidence, failure isolation, security-sensitive upgrade eligibility, consistency between managed source material and managed projections, and durable lineage from original initialization through every successfully accepted reconciliation. For a new reconciliation, the currently accepted repo-spec revision is the active baseline and its initialization manifest is compared with the supplying reconciliation-target revision's initialization manifest. Historical accepted lineage entries remain provenance evidence; failed or non-promoted attempts do not become accepted lineage entries. Exact schemas and mechanics remain unresolved until governed normative specification work.

## Downstream specification families

Expected owner-appropriate product specification work is directional at this stage:

- **Level 0:** only minimal upgrade-wide identity, authority, lifecycle, or common interpretation semantics required by multiple otherwise independent areas.
- **Level 1:** independently meaningful primitives such as upgrade request identity, framework revision identity, managed-material identity/classification, accepted target anchor/provenance identity, and validation/outcome primitives where those concepts remain independently meaningful.
- **Level 2:** coherent reusable responsibilities such as managed upgrade-set resolution, staged managed reconciliation, projection reconciliation, re-anchoring/provenance update, and staged validation/promotion gating where they compose primitives without defining the complete upgrade outcome.
- **Level 3:** the complete derived-repository upgrade lifecycle and observable terminal outcome from request through validated promotion or non-promotion failure.

Later specification work determines exact specification boundaries, identifiers, dependency edges, reuse of existing accepted specifications, and whether every listed Level is needed. This decomposition does not require an intermediate Level merely because the Level model permits one.

## Chunk index

- [01 - Request, identity, and eligibility](./initializer-upgrade-decomposition/01-request-identity-and-eligibility.md)
- [02 - Managed-material delta and reconciliation](./initializer-upgrade-decomposition/02-managed-material-delta-and-reconciliation.md)
- [03 - Staged application and projections](./initializer-upgrade-decomposition/03-staged-application-and-projections.md)
- [04 - Re-anchoring and provenance](./initializer-upgrade-decomposition/04-reanchoring-and-provenance.md)
- [05 - Validation, promotion, and outcomes](./initializer-upgrade-decomposition/05-validation-promotion-and-outcomes.md)

## Relationships

The approved [Repo-Spec Initializer Upgrade functional set](../overview/INITIALIZER-UPGRADE-FUNCTIONAL-SET.md) is the controlling and predecessor directional authority.

The existing [Repo-Spec Initializer decomposition](./INITIALIZER-DECOMPOSITION.md) remains the accepted decomposition for the original initializer capability and is not modified or superseded by this document.

## Next authorized action

Create or revise, review, and accept the owner-appropriate normative product specification set required for this decomposition. Implementation planning remains unauthorized until the necessary controlling product specifications are accepted.

## Discoverability

- [Product decomposition root index](./README.md)
- [Approved upgrade functional set](../overview/INITIALIZER-UPGRADE-FUNCTIONAL-SET.md)
