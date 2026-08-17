# Decomposition handoff

## Candidate decomposition concerns

If explicitly approved, decomposition should assign responsibilities for:

- common CI orchestration versus stable installed interfaces;
- repository validation self-test ownership;
- product validation self-test ownership;
- generic product implementation-test ownership;
- zero-applicable product-test lifecycle handling;
- initializer output closure and installation responsibility;
- source-development-only test boundaries;
- compatibility with later product and upgrade lifecycle work.

These are capability responsibilities, not a selected technical architecture.

## Downstream authority

Decomposition should preserve the distinction between production validation (`repo/scripts/validate` and `product/scripts/validate`) and the test surfaces exercised by common CI.

Later product specifications should make exact command contracts, zero-applicable semantics, installation requirements, failure diagnostics, and closure rules normative before implementation begins.

## Approval gate

The next lifecycle action after this candidate is available on `main` is explicit user approval or rejection/modification of the candidate functional set.

No decomposition mutation is authorized until that explicit decision.
