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

Status: completed historical work after issue #505 and its governed #507/#510/#511 closure chain.

Purpose: implement generic `product/scripts/test-product` applicability/lifecycle behavior,
including deterministic honest zero-applicable evidence and distinct failure classes.

Controlling accepted product specifications: `product.initializer-level-0`,
`product.validation-test-surface`, `product.validation-test-orchestration`,
`product.product-test-applicability`, `product.product-test-lifecycle`.

Owned PR-#490 requirements: `product.product-test-applicability::INIT-PTA-001-009` and
`product.product-test-lifecycle::INIT-PTL-001-010`.

Predecessor: VS1, completed historical work. VS2 was authorized by issue #505 with the exact
VS2 controlling set and accepted through PR #506. Issue #507 / PRs #508-#509 resolved U9,
issue #511 / PR #512 repaired the bounded requirement-ID schema conflict, and issue #510 /
PR #513 completed current-state correspondence and common orchestration. Exact-main validation
and the final fresh #505 audit then satisfied the VS2 exit gate.

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

Status: completed historical work after issues #516-#517 and PR #518.

Purpose: implement installed-command/executable-reference closure and concrete initializer
installation, staged-validation, and full-initialization correspondence.

Controlling accepted product specifications: `product.initializer-level-0`,
`product.validation-test-surface`, `product.validation-test-orchestration`,
`product.product-test-applicability`, `product.product-test-lifecycle`,
`product.validation-profile`, `product.installed-command-requirement`,
`product.executable-reference-closure`, `product.initializer-output-inventory-v1`,
`product.material-manifest`, `product.framework-installation`,
`product.repository-validation`, `product.full-initialization`.

Owned PR-#490 requirements: `product.installed-command-requirement::INIT-ICR-001-008`,
`product.executable-reference-closure::INIT-ERC-001-009`,
`product.framework-installation::INIT-FIN-009`,
`product.repository-validation::INIT-RVA-006`,
`product.full-initialization::INIT-FIN-013`.

Predecessor: VS2, completed before VS3 entry. The conditional VA1 dependency resolved in the
accepted order: separately governed VA1 implementation landed first, and VS3 consumed that
accepted portable runtime/inventory state without bundling VA1. Issue #516 selected VS3 with
the exact controlling set; issue #517 / PR #518 supplied the required Atomic authority
transition and final maintained closure integration.

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

Normal validation-scaffolding order `VS1 -> VS2 -> VS3` is completed historical work.
VS1 completed through issues #493-#495 and PRs #499-#501. VS2 completed through issue #505
and the governed #507/#510/#511 closure chain. VS3 completed through issues #516-#517 and
PR #518, followed by exact-main validation and fresh completion audit. The complete
validation-scaffolding DAG has therefore satisfied its accepted entry and exit gates.

Issue #495 is the sole accepted bounded bridge to that order: the minimum closed
output-inventory/material correspondence for the already-defined VS1 stable surfaces may be
synchronized after VS1 and before VS2 because neither a spec-only nor material-only intermediate
revision is valid. The bridge does not mark VS2 complete, does not mark VS3 complete, and does
not authorize broader executable-reference closure.

`VA1` and `VA2` remain separate issue-#350 workstreams. VA1 landed before VS3 entry, and VS3
consumed that accepted portable runtime/inventory state without bundling VA1. The general
conditional dependency remains historical planning guidance for any future lifecycle that
materially changes the same support boundary. Completion of VS3 does not select H2 or any
other remaining workstream; successor selection requires a fresh governed audit.

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

Repo-spec's state immediately after PR #506 was intentionally
`applicability-invalid`; issue #507 did not itself declare honest zero or select a
product-specific test suite.

That historical follow-up is now complete. Issue #510 / PR #513 supplied one
`not-applicable` conformance record for every accepted normative requirement under the
reviewed current-state decision, preserved false-zero protections, and composed
`product/scripts/test-product` into common `scripts/test-validation`. Exact-main validation
and the final fresh issue-#505 parent audit confirmed deterministic `successful-zero-applicable`
behavior, complete 49-spec/392-requirement conformance evidence, and common-orchestration
participation. VS2 is therefore complete. This completion does not implement VS3.
