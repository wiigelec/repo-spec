# Validation-scaffolding stages and dependencies

Status: accepted; planning-authoritative; non-normative with respect to product semantics.

## VS1 - Stable validation/test interfaces and portable self-tests

Status: completed historical work after issues #493-#495 and PRs #499-#501.

Purpose: implement stable validation/test surface identity, portable repository/framework and
product validation self-tests, and common orchestration without changing production-validation
semantics.

Controlling accepted product specifications: `product.initializer-level-0`,
`product.validation-test-surface`, `product.validation-test-orchestration`.

Owned PR-#490 requirements: `product.validation-test-surface::INIT-VTS-001-010` and
`product.validation-test-orchestration::INIT-VTO-001-010`.

Entry: accepted issue-#491 plan; a later Product-artifact implementation issue selects `VS1`
and cites the exact controlling set. Scope includes the stable `repo/scripts/test-validation`,
`product/scripts/test-validation`, and `product/scripts/test-product` interface identities,
portable installed validator self-tests, and common-orchestration consumption of stable
surfaces. Internal wrapper/dispatcher/module/test-framework choices remain implementation
decisions constrained by accepted specs.

Exit: stable required surfaces exist with accepted executable/failure meaning; portable
validator self-tests exercise their respective responsibilities without the complete repo-spec
source-development tree; common orchestration consumes stable interfaces; missing/non-executable/
unstartable required surfaces fail closed. Product-test applicability/lifecycle semantics remain
a VS2 concern.

Exclusions: no product-test applicability/zero-state semantics, no VS3 concrete installed
closure, no VA1 production-ownership refactor, no VA2 source-development test consolidation,
no product-specific suite, no semantic weakening.

Atomic bridge under issue #495: once the VS1 stable surfaces and portable responsibility split
exist, the minimum accepted output-inventory/material synchronization required to make those
same surfaces installable may land atomically before VS2. This is installation correspondence
for already-owned VS1 identities, not VS2 lifecycle implementation and not completion of the
broader VS3 installed-command/executable-reference closure.

## VS2 - Generic product-test applicability and lifecycle

Purpose: implement generic `product/scripts/test-product` applicability/lifecycle behavior,
including deterministic honest zero-applicable evidence and distinct failure classes.

Controlling accepted product specifications: `product.initializer-level-0`,
`product.validation-test-surface`, `product.validation-test-orchestration`,
`product.product-test-applicability`, `product.product-test-lifecycle`.

Owned PR-#490 requirements: `product.product-test-applicability::INIT-PTA-001-009` and
`product.product-test-lifecycle::INIT-PTL-001-010`.

Predecessor: VS1, now completed historical work. VS2 implementation was authorized by issue
#505 with the exact VS2 controlling set and accepted through PR #506. The issue-#507 / PR-#508
U9 decision now governs the remaining correspondence/orchestration closure follow-up.

Scope: deterministic accepted-authority-based applicability evidence; zero-applicable,
applicable-and-resolved, invalid applicability; execution of every governed applicable
obligation; distinct expected-but-unresolved, missing dependency/interface, broken discovery,
failed-test, and infrastructure classifications; stable-interface activation without common-CI
redesign.

Exit: honest zero success is machine-evidenced and cannot mask missing/broken/
expected-but-undiscovered tests; applicable obligations execute deterministically; common
orchestration observes the governed generic result; focused and aggregate validation pass.

Exclusions: no product-specific suite/framework selection, no VS3 install closure, no VA1/VA2
implementation, no unrelated workflow redesign.

## VS3 - Installed validation executable-reference closure

Purpose: implement installed-command/executable-reference closure and concrete initializer
installation, staged-validation, and full-initialization correspondence.

Controlling accepted product specifications: `product.initializer-level-0`,
`product.validation-test-surface`, `product.validation-test-orchestration`,
`product.product-test-applicability`, `product.product-test-lifecycle`,
`product.installed-command-requirement`, `product.executable-reference-closure`,
`product.initializer-output-inventory-v1`, `product.material-manifest`,
`product.framework-installation`, `product.repository-validation`,
`product.full-initialization`.

Owned PR-#490 requirements: `product.installed-command-requirement::INIT-ICR-001-008`,
`product.executable-reference-closure::INIT-ERC-001-009`,
`product.framework-installation::INIT-FIN-009`,
`product.repository-validation::INIT-RVA-006`,
`product.full-initialization::INIT-FIN-013`.

Predecessor: VS2. Conditional entry dependency: if separately governed VA1 implementation
changes portable validation support first, VS3 consumes that resulting accepted runtime and
inventory state; VA1 is not bundled.

Scope: determine governed installed-command requirements; classify repository-relative versus
explicit external/platform dependencies; add concrete output-inventory/material-manifest/
framework-inventory mappings and portable support needed for stable surfaces; implement
deterministic closure evidence; fail staged Phase 2 pre-promotion when closure is absent; require
full-initialization success only after closure.

Exit: all governed repository-relative common-validation commands/support resolve through
accepted installation authority; external/platform dependencies are explicit;
`product/scripts/test-product` remains installed/resolvable in honest zero state; source-only
test trees are not copied merely for repo-spec coverage; missing path/mode/support/classification
fails closed before promotion; clean initialized-repository closure evidence passes.

Exclusions: no complete source-development tree transport, product-specific suites, automatic
upgrade propagation, VA1/VA2 bundling, or semantic change to accepted specs.

## Validation-scaffolding implementation DAG

Normal successor order remains `VS1 -> VS2 -> VS3`. VS1 is complete; VS2 implementation has
landed through issue #505 / PR #506, and its U9 decision has landed through issue #507 / PR
#508. VS2 is not yet closed because the separately governed correspondence/orchestration
follow-up remains outstanding; VS3 therefore remains blocked.

Issue #495 is the sole accepted bounded bridge to that order: the minimum closed
output-inventory/material correspondence for the already-defined VS1 stable surfaces may be
synchronized after VS1 and before VS2 because neither a spec-only nor material-only intermediate
revision is valid. The bridge does not mark VS2 complete, does not mark VS3 complete, and does
not authorize broader executable-reference closure.

`VA1` and `VA2` remain separate issue-#350 workstreams. VS3 has only the conditional VA1
dependency described above. A later Product-artifact issue may select multiple adjacent VS
stages only when every selected ID and the union of exact controlling specification sets are
explicit in the issue. Selecting one stage never implicitly authorizes another workstream.

## Issue #507 U9 applicability-evidence decision

U9 is resolved without changing normative product semantics or the machine-readable VS2
controlling set.

The canonical VS2 applicability-evidence carrier is the existing correspondence envelope owned
by each accepted product specification under `repo.product-correspondence`:

- `correspondence.tests` declares stable governed test mappings and their repository-relative paths;
- `correspondence.conformance` declares one requirement-level applicability record as either
  `covered` or `not-applicable`;
- `covered` records select the governed product-test mappings that must resolve and execute;
- `not-applicable` records explicitly establish that no product implementation-test obligation
  applies to that normative requirement and require the existing non-empty rationale;
- for VS2 lifecycle evaluation, every normative requirement of every accepted product
  specification must have exactly one conformance record before applicability can be considered
  complete.

This is a later completion rule supplied by accepted PTA/PTL authority. It does not revise the
ordinary correspondence lifecycle: accepted product specifications may still exist before
correspondence is complete, and ordinary repository validation must not require undeclared
conformance merely for acceptance. Instead, incomplete accepted correspondence means
`product/scripts/test-product` remains `applicability-invalid` until a separately governed
implementation supplies complete current-state evidence.

Repo-spec's accepted state after PR #506 therefore remains intentionally
`applicability-invalid`; issue #507 does not declare honest zero and does not select any
product-specific test suite.

A separately governed Product-artifact implementation follow-up is required to:
1. audit every accepted product specification's normative requirements;
2. add only review-supported `covered` or `not-applicable` correspondence needed to make the
   current applicability state complete;
3. preserve the accepted false-zero protections; and
4. only once the stable product-test surface can produce a valid governed result, add
   `product/scripts/test-product` to common `scripts/test-validation` orchestration.

Parent issue #505 remains open until that follow-up is merged, exact-main validation passes, and
a fresh VS2 completion audit confirms the VS2 exit conditions. VS3 remains unauthorized.
