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
| U9: Product-test applicability evidence representation | Concrete registry/evidence format and discovery mechanism. | PTA/PTL require deterministic accepted-authority evidence but do not prescribe registry format/framework. | Closed and implemented by the VS2 chain: issue #507 selected accepted product specifications' existing `correspondence.tests` and `correspondence.conformance` collections as the repository-local applicability evidence carrier; issue #510 / PR #513 supplied complete reviewed current-state conformance and common orchestration; the final issue-#505 audit confirmed deterministic honest-zero behavior. This later PTA/PTL completion rule does not change ordinary product-spec acceptance or the REPO-PC-007/008 correspondence lifecycle. |
| U10: Closure algorithm and support representation | Exact closure algorithm, inventory/material keys, wrappers/support libraries, evidence format. | ICR/ERC require deterministic fail-closed closure while leaving concrete mechanics to implementation; existing one-to-one inventory/material authority remains binding. | VS3 implementation decides with clean-room closure proof. |
| U11: VA1-before-VS3 runtime convergence | Whether VA1 lands before VS3 and changes portable support. | VA1 and VS3 stay separately governed; ERC closes over the actual accepted installed support set. | Current ordering resolved: VA1 landed before VS3 entry, so VS3 consumes the current accepted support set without bundling VA1. The same conditional rule remains binding if ordering changes in a future lifecycle. |


## Post-VS2 decision status under issue #514

U8 is closed by accepted VS1 evidence. U9 is closed and implemented by the accepted VS2 chain:
issue #507 / PRs #508-#509 selected the correspondence representation; issue #510 / PR #513
supplied complete current-state applicability evidence and common orchestration; and the final
fresh issue-#505 audit confirmed the VS2 lifecycle exit conditions.

U10 remains intentionally VS3-owned. Its exact closure algorithm, support representation,
inventory/material keys, and evidence format are implementation decisions constrained by
accepted ICR/ERC and the existing closed one-to-one installation authority; this Maintenance
lifecycle does not choose them.

U11's current ordering is resolved because separately governed VA1 implementation landed before
VS3 entry. VS3 therefore consumes the current accepted portable runtime/inventory state and does
not bundle VA1. The conditional convergence rule remains part of the plan for any future
ordering change.

No product semantics or machine-readable workstream authority set is changed by this status
synchronization.
