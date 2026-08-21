# Repository Normative Base Compression Proposal

I think the repository can conservatively move from 304 requirements to roughly 195–205, a reduction of about one third, without dropping a meaningful invariant. The reduction should come almost entirely from establishing a single semantic owner for each invariant and having dependent specifications reference that owner rather than repeat it.

## The highest-value changes

The biggest compression opportunity is repo.validation. Its 47 requirements currently mix three different things: validation architecture, delegation of enforcement responsibility, and re-declaration of the semantics being enforced.

For example, the plan contract itself says an accepted implementation plan must have valid controlling specifications, with stable authority sets and no missing/candidate/invalid controlling specs. The workflow then repeats the same acceptance restrictions. Then REPO-VAL-027 through 033 repeat them again from the perspective of rejection.

That is not additional semantic protection. It is three copies of one policy.

The better form is:
- repo.implementation-plan owns what constitutes a valid plan.
- repo.development-workflow owns when a valid plan is required.
- repo.validation owns the statement that mechanically decidable plan invariants are enforced.

That one ownership rule removes most of VAL-027..033 without weakening anything.

The same pattern appears in document structure, product levels, generated projections, platform profiles, atomic transitions, routing, and authority boundaries.

## One important inconsistency before compression

There is a real semantic tension between repo.artifact-taxonomy and repo.authority-model.

The taxonomy currently classifies schema with:

```text
authority_category: "normative"
```

and an "accepted schema definition" as its authority source. Yet REPO-AUTH-004 says schemas cannot create or elevate semantics merely because validation consumes them, while REPO-AUTH-007 explicitly includes schemas among non-authoritative mechanisms/evidence that do not become controlling normative authority.

That does not necessarily create a runtime contradiction—one can interpret “normative” in the taxonomy as “normatively governed structural mechanism”—but it is ambiguous enough to explain some of the defensive repetition elsewhere.

I would resolve this explicitly:

Specifications define semantics. Schemas are authoritative enforcement representations only to the extent delegated by accepted specifications; they are not independent semantic authority.

Once that is explicit, many repetitions such as “schema/generated artifact/test cannot create semantics” become unnecessary outside the authority model.

## Four missing generic requirements

Before deleting duplicates, I would add four generic invariants. These additions allow a much larger net reduction.

### 1. Stable requirement identity across the whole repository authority domain

REPO-PL-026 protects published product-level requirement identifiers from reuse, and REPO-PL-027 reserves withdrawn IDs 018–021.

There is no equivalent generic rule for:
- REPO-AUTH-*, REPO-WF-*, REPO-VAL-*, IRG-*, etc.
- That is a significant omission in a system built around traceable IDs.
- I would add a repository-generic requirement roughly equivalent to:
- Published normative requirement identifiers shall be globally stable within their owning specification, shall not be reassigned to different semantics, and withdrawn identifiers shall remain reserved.

Also require uniqueness across the authoritative repository-spec set.

### 2. Repository-spec dependency closure and acyclicity

Product-spec dependency lifecycle and acyclicity are heavily specified. Repository-spec dependencies are not equivalently governed by an obvious normative requirement.

A generic repository requirement should say:

Every repository-spec dependency must resolve to a manifest-listed accepted repository specification; repository-spec dependency relations must be acyclic.

That makes any validator enforcing repository dependency closure clearly delegated rather than accidentally normative.

### 3. Normative status of structured contract data

Several specifications contain machine-readable normative structures:
- issue_fields
- review_fields
- artifact_classes
- profiles
- manifests
- `authority/workstream declarations`

and then repeat those structures in normative_requirements.

The base needs one rule saying, essentially:

Structured contract data explicitly designated by an accepted specification is part of that specification's normative contract; normative requirements need not re-enumerate values already established by that data.

Without this, the repetition is understandable because it is unclear whether only normative_requirements[] carries semantics.

This one addition can eliminate a surprisingly large amount of prose.

### 4. Generic faithful-projection invariant

GI and RP independently repeat that Markdown/YAML/GitHub adapters:
- are subordinate;
- must be deterministic;
- must represent required fields;
- cannot become authority.

AT says generated artifacts remain subordinate, but does not quite express the complete generic projection rule.

Add one generic projection invariant:

A declared generated adapter/projection must be deterministic, faithfully represent the authoritative source surface assigned to its renderer, remain subordinate to its source, and contain no independently authoritative semantics.

Then GI and RP only need to declare which adapters exist and any adapter-specific behavior.

## Recommended semantic ownership

After compression, I would make the ownership boundaries this sharp:

| Specification | Owns |
| --- | --- |
| authority-model | authority, precedence, non-authority, conflicts, validation/review/acceptance separation |
| manifest | authoritative repository-spec registry and repository requirement/spec identity invariants |
| repository-structure | filesystem namespaces and structural envelopes |
| artifact-taxonomy | classification vocabulary and generic artifact roles |
| platform-profiles | provider-specific source/adapter/remote-state semantics |
| development-workflow | temporal sequencing and mutation gates |
| governing-issue | canonical issue data and issue-local authorization semantics |
| review-proposal | review record shape and review-specific revision evidence |
| development-document-base | common composite-document mechanics |
| FSP/PDC/IPL | only type-specific document semantics |
| PM/PSB/PL/PC | product-spec registry, common envelope, levels, correspondence respectively |
| validation | ownership, execution architecture, delegated mechanical enforcement—not source semantics |
| IRG Level 0 | routing-family shared invariants |
| IRG capability specs | only semantics unique to that capability |
| IRG E2E | composition and observable E2E success/failure only |

That is the normalization model I would use.

## Exhaustive requirement disposition

The following ledger accounts for every current ID. Codes are:

- **KEEP** = meaningful independent invariant.
- **MERGE** = semantics should survive, but be combined with the named canonical owner.
- **DROP** = fully implied/repeated; remove as an independent normative requirement.
- **MOVE** = valid invariant, wrong semantic owner.
- **REWRITE** = keep the requirement but narrow/remove duplicated clauses.

### `repo.manifest`

Current requirement source:

| ID | Disposition |
| --- | --- |
| REPO-MAN-001 | REWRITE — explicitly say the manifest is the complete authoritative repo-spec registry, not merely that it “identifies” files. Add uniqueness/dependency closure alongside it. |

This spec is under-specified rather than bloated.

### `repo.authority-model`
| IDs | Disposition |
| --- | --- |
| REPO-AUTH-001 | KEEP — repository-authority supremacy. |
| REPO-AUTH-002 | KEEP — repository/product domain delegation. |
| REPO-AUTH-003 | KEEP — product semantic authority vs planning/coordination artifacts. |
| REPO-AUTH-004 | KEEP — validator cannot manufacture semantics. |
| REPO-AUTH-005 | KEEP — semantic review distinct from validation/acceptance. |
| REPO-AUTH-006 | KEEP — exact scope of validation evidence. |
| REPO-AUTH-007 | KEEP — canonical non-authority rule. Use this to delete many downstream repetitions. |
| REPO-AUTH-008 | KEEP — domain-aware conflict resolution and stop condition. |
| REPO-AUTH-009 | KEEP — no implicit amendment through practice/drift. |
| REPO-AUTH-010 | DROP as a normative ID, retain as explanatory guidance — governmental analogy cannot alter authority is already entailed by 001–009. |

I would add the structured-contract-data rule here.

### `repo.artifact-taxonomy`
| IDs | Disposition |
| --- | --- |
| REPO-AT-001 | KEEP |
| REPO-AT-002 | KEEP |
| REPO-AT-003 | KEEP |
| REPO-AT-003A | KEEP — useful distinction between class role and instance effectiveness. |
| REPO-AT-004 | DROP → AUTH-003/007 |
| REPO-AT-005 | REWRITE/MERGE into the new generic faithful-projection invariant. |
| REPO-AT-006 | KEEP — portability classification boundary. |
| REPO-AT-007 | KEEP — merge is an event, not an authority artifact. |
| REPO-AT-008 | KEEP — profile source/adapter/bootstrap/deployment distinction. |
| REPO-AT-009 | DROP → PP source-to-adapter rule + AUTH |
| REPO-AT-010 | DROP → STR-012 + AUTH-007 |
| REPO-AT-011 | DROP → FSP lifecycle + taxonomy data itself |

Net: about 8 instead of 12.

### `repo.repository-structure`
| ID | Disposition |
| --- | --- |
| REPO-STR-001 | KEEP — foundational default-deny rule. |
| REPO-STR-002 | KEEP |
| REPO-STR-003 | KEEP |
| REPO-STR-004 | MERGE into STR-002 + PM activation semantics — wrong-root prohibition is repeated. |
| REPO-STR-005 | MOVE/REDUCE — physical development-document roots belong in DDB; authority claim belongs in AUTH. |
| REPO-STR-006 | REWRITE — retain only structural authorization of profile/adaptor roots; PP owns projection/authority semantics. |
| REPO-STR-007 | MOVE → platform-profiles — remote hosting-state semantics are provider-profile concerns. |
| REPO-STR-008 | KEEP |
| REPO-STR-009 | KEEP |
| REPO-STR-010 | KEEP |
| REPO-STR-011 | KEEP |
| REPO-STR-012 | KEEP |
| REPO-STR-013 | KEEP |
| REPO-STR-014 | KEEP |
| REPO-STR-015 | KEEP |
| REPO-STR-016 | KEEP |

I would also move the structural content of VAL-043/044 here, probably as one new validation-domain structural-envelope requirement.

### `repo.platform-profiles`
| ID | Disposition |
| --- | --- |
| REPO-PP-001 | KEEP |
| REPO-PP-002 | REWRITE — retain “GitHub first/current supported profile” and bootstrap distinction, remove path repetition. |
| REPO-PP-003 | DROP → STR-006 |
| REPO-PP-004 | MERGE with PP-009/010 |
| REPO-PP-005 | KEEP — make this canonical home of remote-state boundary. |
| REPO-PP-006 | MERGE with PP-015 |
| REPO-PP-007 | DROP/MERGE → AT-008 + PP-002 |
| REPO-PP-008 | KEEP |
| REPO-PP-009 | MERGE with PP-004/010 into one one-way source→adapter invariant. |
| REPO-PP-010 | DROP after merge — near-direct duplicate of 004. |
| REPO-PP-011 | KEEP — deterministic/freshness definition. |
| REPO-PP-012 | KEEP — inventory default-deny semantics. |
| REPO-PP-013 | KEEP |
| REPO-PP-014 | KEEP |
| REPO-PP-015 | MERGE with PP-006; use the complete field set, including governing issue. |
| REPO-PP-016 | KEEP |

There is an especially obvious redundancy among 004/009/010, and between 006/015.

## Workflow and issue/review governance
### `repo.development-workflow`
| ID | Disposition |
| --- | --- |
| REPO-WF-001 | KEEP |
| REPO-WF-002 | DROP — meta-restatement of WF-017..024 + WF-003; retain WF-024 as the actual gate. |
| REPO-WF-003 | KEEP |
| REPO-WF-004 | KEEP |
| REPO-WF-005 | REWRITE — retain issue/branch discovery report; remove the no-mutation clause duplicated by WF-024. |
| REPO-WF-006 | KEEP — distinct payload-safety invariant. |
| REPO-WF-007 | KEEP/REWRITE — make this the single canonical lifecycle ordering rule. |
| REPO-WF-008 | DROP → WF-007 + FSP-005 |
| REPO-WF-009 | KEEP |
| REPO-WF-010 | REWRITE — state only that applicable controlling specs must satisfy the plan contract before plan acceptance; IPL-008 owns the detailed invalidity list. |
| REPO-WF-011 | KEEP |
| REPO-WF-012 | DROP → AUTH-007 |
| REPO-WF-013 | KEEP — canonical home for plan impact after authority changes. |
| REPO-WF-014 | KEEP |
| REPO-WF-015 | KEEP — canonical exploratory-work lifecycle. |
| REPO-WF-016 | REWRITE — reference plan authority union and GI contract rather than duplicating all issue evidence semantics. |
| REPO-WF-017 | REWRITE — missing authority initialization. Explicitly require reading repo.authority-model; AGENTS already does, but the normative workflow does not. |
| REPO-WF-018 | KEEP |
| REPO-WF-019 | KEEP |
| REPO-WF-020 | KEEP |
| REPO-WF-021 | KEEP |
| REPO-WF-022 | KEEP |
| REPO-WF-023 | KEEP |
| REPO-WF-024 | KEEP — one definitive pre-mutation gate. |
| REPO-WF-025 | KEEP — canonical Atomic lifecycle semantics. |
| REPO-WF-026 | REWRITE — reference GI's Atomic evidence contract and validation's field-policy enforcement instead of duplicating both. |

A key missing detail is that WF-017 does not normatively require the authority model to be loaded, although AGENTS.md does. That should be corrected before treating AGENTS as a pure projection.

### `repo.governing-issue`
| ID | Disposition |
| --- | --- |
| REPO-GI-001 | KEEP |
| REPO-GI-002 | MERGE — once issue_fields is explicitly normative structured data, do not re-enumerate all fields in prose. |
| REPO-GI-003 | DROP/MERGE — required is already represented in the canonical field definitions. |
| REPO-GI-004 | KEEP — meaningful validation invariant. |
| REPO-GI-005 | DROP → WF-003 |
| REPO-GI-006 | KEEP |
| REPO-GI-007 | KEEP |
| REPO-GI-008 | KEEP |
| REPO-GI-009 | MERGE into generic projection invariant |
| REPO-GI-010 | MERGE into generic projection invariant |
| REPO-GI-011 | MERGE into generic projection invariant |
| REPO-GI-012 | KEEP — canonical change-type activation semantics. |
| REPO-GI-013 | KEEP |
| REPO-GI-014 | DROP → WF-025 — Atomic eligibility belongs to lifecycle authority. |
| REPO-GI-015 | REWRITE — retain only the issue evidence fields required for an Atomic transition; remove lifecycle semantics already owned by WF-025/026. |

The field definitions themselves already carry much of the contract. Making their normative status explicit is the key compression enabler here.

### `repo.review-proposal`
| ID | Disposition |
| --- | --- |
| REPO-RP-001 | KEEP |
| REPO-RP-002 | MERGE — rely on normative review_fields; keep only the linked-evidence allowance. |
| REPO-RP-003 | KEEP |
| REPO-RP-004 | MERGE with 005/008/017 |
| REPO-RP-005 | MERGE with 004/008/017 |
| REPO-RP-006 | DROP → AUTH-005/006 |
| REPO-RP-007 | DROP → AUTH-005 |
| REPO-RP-008 | MERGE with 004/005/017 |
| REPO-RP-009 | KEEP |
| REPO-RP-010 | KEEP |
| REPO-RP-011 | KEEP |
| REPO-RP-012 | MERGE into generic projection invariant |
| REPO-RP-013 | KEEP — agent-specific use of installed PR adapter. |
| REPO-RP-014 | MERGE into generic projection invariant |
| REPO-RP-015 | MERGE into generic projection invariant |
| REPO-RP-016 | KEEP or combine with RP-013 — genuinely PR-presentation-specific. |
| REPO-RP-017 | MERGE with 004/005/008 — one exact-revision freshness requirement. |
| REPO-RP-018 | DROP → AUTH-005 |
| REPO-RP-019 | DROP → AUTH-005 |
| REPO-RP-020 | DROP → AUTH-007 |
| REPO-RP-021 | DROP → AUTH-008 |

RP-018..021 are good requirements—but they are almost exactly what the authority model now exists to say. Keeping both sets makes it harder to know which wording controls if they later diverge.

## Development-document family
### `repo.development-document-base`
| ID | Disposition |
| --- | --- |
| REPO-DDB-001 | KEEP |
| REPO-DDB-002 | KEEP — make this canonical home of development-document root/type mapping. |
| REPO-DDB-003 | KEEP |
| REPO-DDB-004 | KEEP |
| REPO-DDB-005 | KEEP |
| REPO-DDB-006 | DROP — invalidity already follows from 003/007/011/012 plus delegated validation. |
| REPO-DDB-007 | KEEP |
| REPO-DDB-008 | MERGE with DDB-010 — coherent/small chunks + semantic partition judgment. |
| REPO-DDB-009 | DROP → generic validation delegation |
| REPO-DDB-010 | MERGE with DDB-008 |
| REPO-DDB-011 | KEEP |
| REPO-DDB-012 | KEEP |
### `repo.functional-set-process`
| ID | Disposition |
| --- | --- |
| REPO-FSP-001 | REWRITE — name recognized artifact types; reference DDB for roots instead of repeating literal paths. |
| REPO-FSP-002 | KEEP |
| REPO-FSP-003 | KEEP |
| REPO-FSP-004 | KEEP |
| REPO-FSP-005 | REWRITE — approval establishes the directional handoff to decomposition; avoid wording that can sound as though approval itself authorizes planning/implementation. Later gates remain controlling. |
| REPO-FSP-006 | KEEP |
| REPO-FSP-007 | KEEP |

This spec is already fairly efficient.

### `repo.product-decomposition`
| ID | Disposition |
| --- | --- |
| REPO-PDC-001 | DROP → DDB-002/003 |
| REPO-PDC-002 | KEEP |
| REPO-PDC-003 | KEEP |
| REPO-PDC-004 | DROP → DDB-005 |
| REPO-PDC-005 | DROP → DDB-008 |
| REPO-PDC-006 | DROP → already contained in PDC-002 |
| REPO-PDC-007 | KEEP — important decomposition→normative-spec handoff semantics. |

This can go from 7 to 3 with essentially no loss.

### `repo.implementation-plan`
| ID | Disposition |
| --- | --- |
| REPO-IPL-001 | DROP → DDB-002/003 |
| REPO-IPL-002 | KEEP |
| REPO-IPL-003 | KEEP |
| REPO-IPL-004 | DROP → DDB-005 |
| REPO-IPL-005 | KEEP |
| REPO-IPL-006 | KEEP |
| REPO-IPL-007 | KEEP |
| REPO-IPL-008 | KEEP — canonical owner of plan validity against controlling specs. |
| REPO-IPL-009 | KEEP |
| REPO-IPL-010 | DROP → IPL-003 + AUTH-003 |
| REPO-IPL-011 | DROP → WF-013 — plan-impact transition behavior belongs to workflow. |
## Product-specification framework
### `repo.product-manifest`
| ID | Disposition |
| --- | --- |
| REPO-PM-001 | KEEP |
| REPO-PM-002 | REWRITE — retain registry authority; remove derived-projection details owned by PSB. |
| REPO-PM-003 | KEEP |
| REPO-PM-004 | KEEP |
| REPO-PM-005 | KEEP |
| REPO-PM-006 | KEEP |
| REPO-PM-007 | DROP → PSB-004 |
| REPO-PM-008 | KEEP |
| REPO-PM-009 | KEEP |
| REPO-PM-010 | DROP → PL-010 |
| REPO-PM-011 | DROP → PSB-006 / PL-010 |
| REPO-PM-012 | DROP as normative — it merely points at repo.product-levels. |
| REPO-PM-013 | DROP → PSB-011 |
| REPO-PM-014 | KEEP |
| REPO-PM-015 | DROP → AUTH-002 |
### `repo.product-spec-base`
| ID | Disposition |
| --- | --- |
| REPO-PSB-001 | KEEP |
| REPO-PSB-002 | REWRITE/MERGE with PSB-012 |
| REPO-PSB-003 | KEEP |
| REPO-PSB-004 | KEEP — canonical lifecycle vocabulary. |
| REPO-PSB-005 | KEEP |
| REPO-PSB-006 | KEEP — canonical common-envelope Level field semantics. |
| REPO-PSB-007 | KEEP |
| REPO-PSB-008 | DROP → PL-008 |
| REPO-PSB-009 | KEEP |
| REPO-PSB-010 | KEEP |
| REPO-PSB-011 | KEEP — canonical projection declaration rule. |
| REPO-PSB-012 | MERGE with PSB-002; remove workflow-authority prose already covered by AUTH. |
| REPO-PSB-013 | DROP → PL-011 |
| REPO-PSB-014 | KEEP |
| REPO-PSB-015 | KEEP |
| REPO-PSB-016 | KEEP |
| REPO-PSB-017 | KEEP |

I would make PSB-014..017 the single owner of the JSON-Schema composition mechanics and remove their duplicates from product-levels.

### `repo.product-correspondence`
| ID | Disposition |
| --- | --- |
| REPO-PC-001 | KEEP |
| REPO-PC-002 | KEEP |
| REPO-PC-003 | KEEP |
| REPO-PC-004 | KEEP |
| REPO-PC-005 | KEEP |
| REPO-PC-006 | MERGE with PC-008 |
| REPO-PC-007 | KEEP |
| REPO-PC-008 | MERGE with PC-006 — one complete mapping/conformance consistency invariant. |
| REPO-PC-009 | KEEP |

Already quite efficient.

### `repo.product-levels`
| ID | Disposition |
| --- | --- |
| REPO-PL-001 | KEEP |
| REPO-PL-002 | REWRITE, fold PL-014's exclusion into it; remove repeated dependency clause. |
| REPO-PL-003 | REWRITE, fold PL-015 into it. |
| REPO-PL-004 | REWRITE, fold PL-016 into it. |
| REPO-PL-005 | REWRITE, fold PL-017 into it. |
| REPO-PL-006 | KEEP — single generic directional dependency rule. |
| REPO-PL-007 | KEEP |
| REPO-PL-008 | KEEP |
| REPO-PL-009 | KEEP |
| REPO-PL-010 | REWRITE — own Level-root correspondence; let PSB-006 own field-value agreement. |
| REPO-PL-011 | KEEP |
| REPO-PL-012 | KEEP |
| REPO-PL-013 | DROP → PSB-011 |
| REPO-PL-014 | MERGE into PL-002 |
| REPO-PL-015 | MERGE into PL-003 |
| REPO-PL-016 | MERGE into PL-004 |
| REPO-PL-017 | MERGE into PL-005 |
| REPO-PL-022 | DROP → PSB-014/015 |
| REPO-PL-023 | DROP → PSB-015 |
| REPO-PL-024 | DROP → PSB-016/017 |
| REPO-PL-025 | DROP → PL-011 |
| REPO-PL-026 | KEEP, but generalize at repository level as well |
| REPO-PL-027 | REWRITE — the reservation itself should live in machine-readable withdrawn-ID metadata; the generic no-reuse requirement provides the normative rule. |

There are two conspicuous duplicate sets here:

PL-002..005 + PL-014..017, and
PL-022..024 + PSB-014..017.

## Validation

This is where most compression should occur.

| IDs | Disposition |
| --- | --- |
| REPO-VAL-001 | KEEP/merge with 045 — validation entry points and domain ownership. |
| REPO-VAL-002 | KEEP |
| REPO-VAL-003 | MERGE into generic core structural/specification validation obligation. |
| REPO-VAL-004 | MERGE |
| REPO-VAL-005 | MERGE |
| REPO-VAL-006 | MERGE |
| REPO-VAL-007 | MERGE; source semantics belong to PL/PSB. |
| REPO-VAL-008 | MERGE into generated-projection enforcement. |
| REPO-VAL-009 | KEEP |
| REPO-VAL-010 | KEEP — extremely valuable anti-overreach boundary. |
| REPO-VAL-011 | MOVE/DROP — this declares source lineage semantics rather than validation behavior; product lineage is already PSB-010. |
| REPO-VAL-012 | MERGE into lineage validation. |
| REPO-VAL-013 | MERGE into specification-root/registry validation. |
| REPO-VAL-014 | DROP → subset of VAL-013 + STR-002 |
| REPO-VAL-015 | MERGE into platform-profile validation. |
| REPO-VAL-016 | MERGE with 018; source fields are PP-006/015. |
| REPO-VAL-017 | MERGE; source contract is PSB-011. |
| REPO-VAL-018 | MERGE into one platform-profile enforcement requirement. |
| REPO-VAL-019 | MERGE into one development-document validation requirement |
| REPO-VAL-020 | MERGE |
| REPO-VAL-021 | MERGE |
| REPO-VAL-022 | MERGE |
| REPO-VAL-023 | MERGE |
| REPO-VAL-024 | MERGE into lifecycle/lineage validation. |
| REPO-VAL-025 | MERGE into development-document validation; source semantics should live in DDB. |
| REPO-VAL-026 | MERGE into development-document validation. |
| REPO-VAL-027 | MERGE into one plan-authority validation requirement |
| REPO-VAL-028 | MERGE |
| REPO-VAL-029 | MERGE |
| REPO-VAL-030 | MERGE |
| REPO-VAL-031 | MERGE |
| REPO-VAL-032 | MERGE |
| REPO-VAL-033 | MERGE |
| REPO-VAL-034 | MERGE into development-document/decomposition validation; source is PDC-007. |
| REPO-VAL-035 | DROP/MOVE → WF-015 |
| REPO-VAL-036 | KEEP — distinct remote issue-body field-policy boundary for ordinary product implementation. |
| REPO-VAL-037 | DROP → AUTH-004/007 + generic projection rule |
| REPO-VAL-038 | DROP → PL-009 |
| REPO-VAL-039 | MERGE into one generic structural-envelope enforcement requirement referencing STR. |
| REPO-VAL-040 | MERGE into development-document lifecycle validation; source is FSP. |
| REPO-VAL-041 | KEEP — unique transportable local validation-authority invariant. |
| REPO-VAL-042 | KEEP/REWRITE — distinct Atomic issue-body field-policy boundary; reference GI/WF rather than restating every semantic condition. |
| REPO-VAL-043 | MOVE structural definition → repository-structure; validation merely enforces it. |
| REPO-VAL-044 | MOVE structural definition → repository-structure, combine with 043. |
| REPO-VAL-045 | MERGE with VAL-001 |
| REPO-VAL-046 | DROP detailed restatement; enforce STR/DDB via the consolidated development-document validator requirement. |
| REPO-VAL-047 | DROP detailed restatement; enforce STR-013/014 through consolidated structural-envelope requirement. |

I would reduce 47 validation requirements to roughly 14–17.

That is the single biggest improvement available.

The final validation spec should describe what validation owns and how delegated rules are enforced, not recopy the repository architecture.

## Issue-routing family

This family is logically well decomposed but normatively repetitive. The Level-0 foundation already says classification ≠ governance, routing metadata ≠ mutation authority, raw intake needn't satisfy governed fields, provenance must be traceable, and governed validation must not activate early.

Child specs should therefore stop restating those invariants.

### `repo.issue-routing-governance`
| ID | Disposition |
| --- | --- |
| IRG-L0-001 | KEEP |
| IRG-L0-002 | KEEP |
| IRG-L0-003 | KEEP |
| IRG-L0-004 | KEEP |
| IRG-L0-005 | KEEP |
| IRG-L0-006 | KEEP/REWRITE — useful explicit boundary, but could be shortened. |

This should be the canonical owner of shared routing invariants.

### `repo.issue-routing-classification`
| ID | Disposition |
| --- | --- |
| IRG-CLS-001 | KEEP |
| IRG-CLS-002 | KEEP |
| IRG-CLS-003 | DROP → L0-001 |
| IRG-CLS-004 | KEEP |
| IRG-CLS-005 | KEEP |
### `repo.governed-work-provenance`
| ID | Disposition |
| --- | --- |
| IRG-PROV-001 | DROP → L0-001 |
| IRG-PROV-002 | KEEP |
| IRG-PROV-003 | KEEP |
| IRG-PROV-004 | DROP → L0-004 |
| IRG-PROV-005 | KEEP |
### `repo.issue-authority-routing`
| ID | Disposition |
| --- | --- |
| IRG-ROUTE-001 | KEEP |
| IRG-ROUTE-002 | KEEP |
| IRG-ROUTE-003 | KEEP |
| IRG-ROUTE-004 | DROP → already entailed by ROUTE-002 |
| IRG-ROUTE-005 | KEEP |
| IRG-ROUTE-006 | DROP as normative — dependency boundaries already prevent this spec from redefining those contracts. |
### `repo.governed-work-promotion`
| ID | Disposition |
| --- | --- |
| IRG-PROM-001 | KEEP |
| IRG-PROM-002 | REWRITE — simply require satisfaction of provenance contract before destructive restructuring; don't restate provenance semantics. |
| IRG-PROM-003 | DROP → L0-002 + WF |
| IRG-PROM-004 | DROP → L0-004 |
| IRG-PROM-005 | KEEP — in-place vs successor issue choice is a real promotion-specific invariant. |
### `repo.issue-routing-platform-validation`
| ID | Disposition |
| --- | --- |
| IRG-PVAL-001 | DROP → AUTH + L0 |
| IRG-PVAL-002 | DROP → L0-003/005 |
| IRG-PVAL-003 | KEEP |
| IRG-PVAL-004 | DROP → L0-002 |
| IRG-PVAL-005 | KEEP — unique observable-ordering/platform-profile boundary. |
### `repo.issue-intake-governance-routing`
| ID | Disposition |
| --- | --- |
| IRG-E2E-001 | DROP → L0-003 |
| IRG-E2E-002 | KEEP — actual orchestration/composition ordering. |
| IRG-E2E-003 | DROP → ROUTE-001/002 + WF lifecycle |
| IRG-E2E-004 | DROP → ROUTE-005 + AUTH-008 |
| IRG-E2E-005 | KEEP — E2E observable success condition. |
| IRG-E2E-006 | KEEP — E2E observable failure condition. |
| IRG-E2E-007 | DROP/convert to explanatory boundary — PROM-005 already establishes both realization forms and dependencies establish non-redefinition. |

The routing family can probably go from 39 requirements to about 23–25 while becoming easier to reason about.

## What the compressed model would look like

I would not simply delete 100 IDs and leave holes. The refactoring should intentionally normalize the base.

A plausible endpoint is approximately:

| Area | Current | Target |
| --- | --- | --- |
| Authority + manifest | 11 | 12–14 including missing generic invariants |
| Taxonomy + structure + platform | 44 | ~31 |
| Workflow + GI + RP | 62 | ~40 |
| Validation | 47 | ~15 |
| Development documents | 37 | ~26 |
| Product spec framework | 64 | ~43 |
| Issue routing | 39 | ~24 |
| Total | 304 | ~195–205 |

So I would target about 200 normative requirements.

The important part is that semantic coverage actually becomes stronger, because each concept acquires one authoritative home.

## The central refactoring rule

The repository currently often uses repetition as protection against ambiguity. That made sense while the authority model was being built.

Now that repo.authority-model is mature, repetition starts creating the opposite risk:

two supposedly equivalent normative statements can diverge later.

The normalization rule should be:

**One semantic invariant, one normative owner.**

Other specifications may depend on it, compose it, establish when it applies, or assign mechanical enforcement—but should not paraphrase it into another independent requirement.

Examples:
- AUTH owns “tests don't create semantics”; WF/RP/VAL stop repeating it.
- STR owns “this path exists/is closed”; VAL only says it enforces STR.
- DDB owns composite-document layout; PDC/IPL stop repeating base layout.
- IPL owns valid implementation-plan authority data; WF owns the timing gate; VAL enforces IPL.
- PSB owns common product-spec fields/schema composition; PL only owns Level semantics.
- PP owns source→adapter behavior; AT only classifies the artifacts.
- IRG-L0 owns routing/governance separation; every child stops restating it.

That is the compression strategy I would recommend.

The most useful next step would be to turn this evaluation into a proposed normalized requirement set, preserving existing IDs where possible, explicitly marking withdrawn IDs, and writing the replacement wording for the ~200 surviving/merged requirements. That would make the result directly actionable as a governed authority revision rather than just an audit.
