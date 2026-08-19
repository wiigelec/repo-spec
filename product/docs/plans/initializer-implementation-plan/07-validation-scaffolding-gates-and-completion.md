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

VS2 -> VS3 gate status: satisfied on accepted `main`. The first three rows were established
by issue #505 and the governed #507/#510/#511 closure chain. The final explicit-authority row
was satisfied when issue #516 selected VS3 and cited its exact controlling set. The later
#517 / PR #518 Atomic transition did not replace that selection; it synchronized required
validation-profile authority and the mechanically inseparable maintained closure handler.

### VS3 closure / completion gate

| Requirement | Evidence |
| --- | --- |
| Installed-command set is deterministic | Machine evidence classifies every common-validation dependency |
| Repository-relative commands/support are installation-authorized | Output inventory, material mapping, executable mode, and portable support close each required command |
| Zero-applicable product-test surface remains installed | Clean initialized repository resolves `product/scripts/test-product` even when lifecycle reports honest zero |
| Closure fails pre-promotion | Missing path/mode/support/misclassification is a required Phase-2 failure |
| Full initialization cannot succeed without closure | End-to-end evidence establishes closure before promotion |
| Conditional VA1 dependency is respected | If VA1 changed portable support first, VS3 uses that accepted state without bundling VA1 |

VS3 closure/completion status: satisfied on accepted `main`
`2e51069b4215d71f7eba6417e0b19b2353b6f91c` after issues #516-#517 and PR #518.
Fresh exact-main validation and the final issue-#516 completion audit confirmed deterministic
installed-command identity/classification, accepted installation authority for all required
repository-relative command/support paths, portable support closure, fail-closed Phase 2
integration, installed honest-zero `product/scripts/test-product`, and successful clean
initialization only with closure satisfied.

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


## Post-VS3 completion status under issue #519

VS1, VS2, and VS3 are completed historical validation-scaffolding work. VS1 supplied the
stable portable test surfaces, VS2 supplied governed product-test applicability/lifecycle and
common orchestration, and VS3 closed every installed common-validation command/support
reference over accepted installation authority.

Issue #516 selected VS3 under the exact accepted controlling set. Issue #517 / PR #518
performed the required Atomic validation-profile/handler synchronization and landed the
deterministic executable-reference-closure implementation. Exact merged-main validation and
the fresh #516 completion audit then confirmed every VS3 exit condition with no remaining
functional correction or authority conflict.

The validation-scaffolding sequence is therefore complete. VA1 and VA2 remain separately
governed historical work, H2 remains a separate workstream, and this status synchronization
does not select any successor implementation. A fresh successor audit is required after issue
#519 is accepted.
