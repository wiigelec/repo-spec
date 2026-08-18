# Validation-scaffolding gates and completion

Status: accepted; planning-authoritative; non-normative with respect to product semantics.

## Validation-scaffolding transition and authorization gates

### VS1 authorization / exit gate

| Requirement | Evidence |
| --- | --- |
| Later Product-artifact issue selects `VS1` | Exact VS1 controlling set is cited and no unselected successor scope is implied |
| Stable surface identity is preserved | Focused evidence covers all three stable test surfaces and their distinction from production validation |
| Installed validator self-tests are portable | Clean portable evidence does not require the complete repo-spec source-development test tree |
| Required surfaces fail closed | Missing/non-executable/unstartable cases remain failures, not skip/zero |
| Common orchestration consumes stable interfaces | No repository-class-specific alternate interface is required |

VS1 completion status: satisfied on accepted `main` after issues #493-#495 and PRs #499-#501.
The stable interfaces, portable/source-development responsibility split, fail-closed behavior,
common orchestration, and minimum installation correspondence have been accepted and freshly audited.

### VS1 -> VS2 gate

| Requirement | Evidence |
| --- | --- |
| VS1 interface/orchestration foundation is present | Stable paths and common-orchestration evidence pass |
| VS2 authority is explicit | Governing issue selects VS2 explicitly and cites the exact VS2 controlling set |
| No lifecycle semantics are invented by VS1 | Applicability/zero/discovery behavior comes only from accepted PTA/PTL authority |

### VS2 -> VS3 gate

| Requirement | Evidence |
| --- | --- |
| Product-test lifecycle evidence passes | Zero/applicable/invalid and required failure classes are distinguishable |
| Honest zero cannot mask absence/breakage | Missing dependency, broken discovery, expected-but-undiscovered obligations do not normalize to success |
| Common orchestration observes governed product-test result | Stable `product/scripts/test-product` composes without repository-class redesign |
| VS3 authority is explicit | Governing issue selects VS3 and exact controlling set |

VS2 predecessor status: satisfied on accepted `main` after issue #505 and the governed
#507/#510/#511 closure chain. The first three gate rows have accepted evidence. The final row
remains an entry requirement for the separately governed VS3 Product-artifact implementation
issue; this Maintenance lifecycle does not select VS3.

### VS3 closure / completion gate

| Requirement | Evidence |
| --- | --- |
| Installed-command set is deterministic | Machine evidence classifies every common-validation dependency |
| Repository-relative commands/support are installation-authorized | Output inventory, material mapping, executable mode, and portable support close each required command |
| Zero-applicable product-test surface remains installed | Clean initialized repository resolves `product/scripts/test-product` even when lifecycle reports honest zero |
| Closure fails pre-promotion | Missing path/mode/support/misclassification is a required Phase-2 failure |
| Full initialization cannot succeed without closure | End-to-end evidence establishes closure before promotion |
| Conditional VA1 dependency is respected | If VA1 changed portable support first, VS3 uses that accepted state without bundling VA1 |

## Validation-scaffolding validation strategy

VS1 evidence covers stable interfaces, ownership separation, portable validator self-tests,
common orchestration, and fail-closed required-surface behavior. VS2 covers deterministic
applicability evidence, honest zero, complete applicable-test execution, ordering/classification,
and distinct failure classes. VS3 covers clean initialized-repository command/support closure,
explicit external/platform classification, accepted inventory/material correspondence,
pre-promotion failure, and successful full initialization only after closure.

Every selected implementation issue must run its focused evidence plus applicable validation
self-tests and `product/scripts/validate`, `repo/scripts/validate`, `scripts/validate`, and
`git diff --check`. Passing validation never substitutes for semantic review and validators
must not be weakened.

## Issue #491 planning completion and successor boundary

Issue #491 is complete only when the controlling plan and all four chunks consistently record
the PR-#490 impact review, revised VA1/VA2 authority, VS1/VS2/VS3 machine-readable authority,
DAG/gates/validation strategy, risks/decisions, and no maintained implementation.

After manual merge and post-merge planning audit, closing #491 authorizes only later creation
of separately governed Product-artifact implementation issues selecting explicit stage IDs.


## Post-VS2 successor status under issue #514

VS1 and VS2 are completed historical validation-scaffolding work. The VS1 -> VS2 gate was
satisfied before issue #505. VS2 implementation landed through PR #506; issue #507 / PRs
#508-#509 resolved U9; issue #511 / PR #512 repaired the bounded requirement-ID schema conflict;
and issue #510 / PR #513 completed the 49-spec/392-requirement current-state correspondence
evidence plus common `product/scripts/test-product` orchestration.

The user validated exact merged `main`, and a fresh final issue-#505 audit confirmed:
- zero/applicable/invalid and all required failure classes remain distinguishable;
- honest zero cannot mask missing, broken, or expected-but-undiscovered obligations;
- current accepted state is deterministic `successful-zero-applicable`;
- common orchestration observes the stable product-test lifecycle result.

The predecessor evidence for VS3 is therefore satisfied. VS3 is the next normal
validation-scaffolding implementation stage. Entry still requires a separately governed
Product-artifact implementation issue selecting `VS3` and citing the exact VS3 controlling
specification set.

VA1 has already landed under separate governance. For current VS3 entry, the conditional VA1
row is satisfied by consuming the then-current accepted portable runtime/inventory state; VA1
is not bundled into VS3. No VS3 closure condition is satisfied merely by this status
synchronization.
