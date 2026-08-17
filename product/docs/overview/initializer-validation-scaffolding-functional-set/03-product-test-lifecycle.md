# Product-test lifecycle and zero-applicable state

## Product-test lifecycle

A fresh repository can be structurally valid before governed product implementation behavior and its corresponding tests exist. The common product-test surface therefore needs a lifecycle state that can represent no applicable governed product tests yet.

That state is different from a missing required test command, missing dependency, broken test discovery mechanism, or expected test suite that silently failed to run.

## Honest zero-applicable outcome

A zero-applicable product-test result may succeed only because the current governed product state has no applicable implementation tests.

Later product development should be able to establish applicable product tests without replacing the common CI ownership model.

## Deferred exact semantics

Successor decomposition and specifications must decide:

- how applicable tests are discovered or registered;
- how zero-applicable state is reported;
- exact exit behavior and diagnostics;
- when zero-applicable state ceases to be valid;
- how expected-but-missing tests are distinguished from legitimately absent tests.

This functional set does not choose those mechanics.
