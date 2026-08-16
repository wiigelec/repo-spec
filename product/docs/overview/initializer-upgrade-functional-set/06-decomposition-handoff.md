# Decomposition handoff

## Handoff readiness

If explicitly approved, this functional set is intended to provide one bounded directional authority for product decomposition.

The accepted analysis identified U1-U8 as useful candidate decomposition boundaries. They remain predecessor evidence rather than an accepted decomposition at this stage.

## Analysis-derived boundaries

- U1 — upgrade request and target preflight;
- U2 — source revision and upgrade inventory resolution;
- U3 — existing-repository staging;
- U4 — managed framework application;
- U5 — managed projection reconciliation;
- U6 — framework re-anchoring and provenance;
- U7 — staged validation gate;
- U8 — promotion, failure, and finalization.

## Dependency shape

The downstream decomposition must preserve the directional lifecycle relationship:

target/source identity -> initializer-managed eligibility -> managed-material delta/reconciliation selection -> existing-repository staging -> add/modify/remove/retarget managed application -> projection reconciliation -> framework re-anchoring -> repository validation -> promotion -> finalization.

## Approval gate

This artifact is currently `candidate`.

No decomposition is authorized until the user explicitly approves this functional set and the approved lifecycle state is durably recorded.
