# Validation-scaffolding authority impact

Status: accepted; planning-authoritative; non-normative with respect to product semantics.

## PR #490 validation-scaffolding authority extension

Issue #491 records the `REPO-IPL-011` impact review for PR #490. The original
34-spec/291-key map above remains the historical B0/I1-I5 baseline. It is not rewritten as
if completed historical evidence had covered later requirements.

PR #490 introduces exactly 59 new normative requirements requiring successor planning:
56 in six new accepted specifications plus three requirements added to existing initializer
specifications.

| Accepted specification / requirement set | Planning owner |
| --- | --- |
| `product.validation-test-surface::INIT-VTS-001-010` | VS1 |
| `product.validation-test-orchestration::INIT-VTO-001-010` | VS1 |
| `product.product-test-applicability::INIT-PTA-001-009` | VS2 |
| `product.product-test-lifecycle::INIT-PTL-001-010` | VS2 |
| `product.installed-command-requirement::INIT-ICR-001-008` | VS3 |
| `product.executable-reference-closure::INIT-ERC-001-009` | VS3 |
| `product.framework-installation::INIT-FIN-009` | VS3 |
| `product.repository-validation::INIT-RVA-006` | VS3 |
| `product.full-initialization::INIT-FIN-013` | VS3 |

No pre-PR-#490 requirement key is reassigned.

### VA1 / VA2 impact review

`VA1` is reaffirmed as production-validation ownership/extraction only. Exact controlling
set: `product.initializer-output-inventory-v1`, `product.framework-installation`,
`product.repository-validation`, `product.executable-reference-closure`.

`VA2` is reaffirmed as source-development validation-self-test ownership/consolidation only.
Exact controlling set: `product.repository-validation`, `product.validation-test-surface`,
`product.validation-test-orchestration`.

### New stage authority

- `VS1`: `product.initializer-level-0`, `product.validation-test-surface`,
  `product.validation-test-orchestration`.
- `VS2`: VS1 authority plus `product.product-test-applicability`,
  `product.product-test-lifecycle`.
- `VS3`: VS2 authority plus `product.validation-profile`,
  `product.installed-command-requirement`, `product.executable-reference-closure`,
  `product.initializer-output-inventory-v1`,
  `product.material-manifest`, `product.framework-installation`,
  `product.repository-validation`, `product.full-initialization`.

These are planning authority sets only; accepted product specifications retain semantic
authority and candidate future extensions remain excluded.

### Issue #495 atomic installation bridge

Issue #495 does not reassign any normative requirement key or alter the machine-readable
VS1, VS2, or VS3 controlling specification sets. It records a sequencing exception required
to resolve the accepted closed-output deadlock: after VS1 establishes the three stable surface
identities and portable self-test responsibility split, the minimum output-inventory/material
synchronization needed to install those existing surfaces may be accepted before VS2. Broader
product-test lifecycle semantics remain VS2-owned, and broader installed-command/reference
closure remains VS3-owned.


### Post-VS3 completion synchronization under issue #519

Issues #516 and #517 are closed completed and PR #518 is accepted on exact `main`
`2e51069b4215d71f7eba6417e0b19b2353b6f91c`. Fresh exact-main validation and the final
issue-#516 read-only completion audit confirm that all three selected VS3 corrections are
satisfied by the accepted implementation with no remaining functional correction or authority
conflict. VS3 is therefore completed historical validation-scaffolding work under the unchanged
exact controlling set above.

This status synchronization does not reassign requirement ownership or alter VS1, VS2, VS3,
H2, VA1, or VA2 authority. The complete VS1 -> VS2 -> VS3 validation-scaffolding sequence is
historical accepted work. No remaining implementation workstream is selected here; successor
selection requires a fresh audit after this Maintenance lifecycle is accepted.
