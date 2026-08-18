# Validation-scaffolding risks and decisions

Status: accepted; planning-authoritative; non-normative with respect to product semantics.

## Validation-scaffolding risks

| Risk | Description | Impact | Controls and evidence | Trigger and owner |
| --- | --- | --- | --- | --- |
| R8: Stable-surface/source-test conflation | Installed self-tests may depend on repo-spec-only source trees or alternate repository-class interfaces. | Initialized repositories are not portable. | VS1 proves identical stable paths, portable support, and source-only extras behind the same surface. | VS1 implementation issue. |
| R9: False zero-applicable success | Missing/broken/expected tests may be mistaken for legitimate absence. | Common validation can silently succeed without governed product tests. | VS2 derives applicability from accepted authority, emits machine evidence, and fails closed on invalid/unresolved states. | VS2 implementation issue. |
| R10: Executable/support closure drift | Common validation may reference a command/support module absent from installer authority. | Fresh repositories fail first push or require manual repair. | VS3 closes every required command/support dependency over accepted output/material authority and staged state. | VS3 and any material-changing predecessor. |
| R11: Workstream scope collision | VA1/VA2 and VS1/VS2/VS3 may touch adjacent validation files and be silently bundled. | Governed scope and field-policy evidence become unreliable. | Exact workstream IDs/sets, disjoint purposes, explicit selected stages, conditional—not implicit—dependencies. | Every successor governing issue. |

## Validation-scaffolding unresolved implementation decisions

| Decision | Description | Constraints from accepted specs | Status and closure condition |
| --- | --- | --- | --- |
| U8: Stable-surface internal architecture | Wrapper/dispatcher/module layout and delegation of repo-spec extra source tests. | VTS/VTO prescribe stable paths/roles/portable behavior, not internal topology. | Closed by accepted VS1 implementation: stable wrappers delegate to portable installed self-tests first and lazy-load repo-spec source-development extras only when those source trees exist; accepted through PRs #499-#501 and issues #493-#495. |
| U9: Product-test applicability evidence representation | Concrete registry/evidence format and discovery mechanism. | PTA/PTL require deterministic accepted-authority evidence but do not prescribe registry format/framework. | Closed by issue #507 decision: accepted product specifications' existing `correspondence.tests` and `correspondence.conformance` collections are the repository-local applicability evidence carrier. For VS2 lifecycle evaluation, every normative requirement of every accepted product specification must have exactly one conformance record: `covered` selects reachable governed test mappings and `not-applicable` explicitly establishes absence for that requirement. Any undeclared accepted requirement leaves applicability invalid. This later PTA/PTL completion rule does not change ordinary product-spec acceptance or the REPO-PC-007/008 correspondence lifecycle. |
| U10: Closure algorithm and support representation | Exact closure algorithm, inventory/material keys, wrappers/support libraries, evidence format. | ICR/ERC require deterministic fail-closed closure while leaving concrete mechanics to implementation; existing one-to-one inventory/material authority remains binding. | VS3 implementation decides with clean-room closure proof. |
| U11: VA1-before-VS3 runtime convergence | Whether VA1 lands before VS3 and changes portable support. | VA1 and VS3 stay separately governed; ERC closes over the actual accepted installed support set. | Conditional: VS3 consumes the then-current accepted support set; no silent bundling. |


## Post-VS1 decision status under issue #502

U8 is closed by accepted VS1 evidence. U9 is closed by the accepted issue-#507 / PR-#508
planning decision and now awaits only its separately governed implementation follow-up under
parent VS2 issue #505. U10 remains VS3-owned, and U11 remains conditional on the separately
governed VA1/VS3 ordering. No authority set is changed by this status synchronization.

## Issue #507 U9 closure decision

U9 is closed at the planning/architecture level.

The selected applicability-evidence representation is not a new registry. It is the existing
per-product-specification correspondence envelope governed by `repo.product-correspondence`.
For VS2 lifecycle evaluation, accepted PTA/PTL authority imposes a later completeness gate over
that existing evidence:

- each accepted normative requirement has exactly one conformance record;
- `covered` references reachable governed product-test mappings;
- `not-applicable` explicitly proves absence for that requirement and retains its required
  rationale;
- missing, contradictory, malformed, unreachable, or otherwise incomplete correspondence
  remains applicability-invalid and cannot become honest zero.

This does not change REPO-PC-007/008: accepted product specifications may remain accepted before
correspondence is complete, and ordinary product-spec validation does not gain a new acceptance
requirement. Completeness is required only when resolving the separately governed
`product-test-applicability` / `product-test-lifecycle` result.

Accordingly, repo-spec's accepted state after issue #505 / PR #506 remains fail-closed
`applicability-invalid` until a subordinate Product-artifact implementation records complete
review-supported current-state correspondence and then composes `product/scripts/test-product`
into common orchestration.

No product semantics, controlling-specification set, VS3 authority, or product-specific suite
selection is changed by issue #507.
