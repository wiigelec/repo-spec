# Product validation scaffolding intake

> Part 3 of 3 · [Repo-Spec Initializer whiteboard](../INITIALIZER-WHITEBOARD.md) · [Previous](./02-derived-repository-upgrade-intake.md)

## Status

Collected product-direction evidence. Directional, evidentiary, and non-normative.

## Collected input

Issue #433 records this user request:

> the initializer should propagate product validation scaffolding so that development docs and specifications can be validated during early initial repo design and planning phases. the scaffolding should provide obvious and convenient access points for product development to implement product specific validation.

The request is preserved here as product intent. Collection does not select a validation-extension architecture or turn this request into normative requirements.

## Provenance

- Source request: GitHub issue #433, `propagate product validation scaffolding`.
- Product context: the approved Repo-Spec Initializer functional set already identifies validation as a major initializer capability and expects initialized repositories to validate locally and remain ready for subsequent governed development.
- Decomposition context: the accepted `generation-validation-and-handoff` area covers validation and maintained-project handoff while leaving later product work explicitly governable.
- Current implementation evidence: `product/scripts/product_validation/product_checks.py` exposes the product-owned `validate_product` entry boundary and states that future governed product development may extend or reorganize active product validation behind that boundary.
- Current installation evidence: the initializer framework inventory propagates the portable product validation entry implementation and product-validation support needed by freshly initialized repositories.

These repository artifacts are evidence about the current state. They do not decide the requested future scaffolding semantics.

## Unresolved intent

The request establishes a need for useful early product-validation scaffolding, but collection intentionally leaves at least these questions unresolved:

- What exact files or directories constitute the propagated product-validation scaffolding?
- Is the intended extension point a module, function, registry, declarative manifest, script, or another product-owned mechanism?
- Should a newly initialized repository contain a no-op/custom-validation stub, or should extension material appear only when later governed product work activates it?
- How should product-specific checks compose with the framework-provided `product/scripts/validate` entry point and existing structural product validation?
- Which validation concerns belong to generic repo-spec framework validation versus later product-specific validation?
- At what lifecycle states should development-document checks, product-specification checks, and later implementation-specific checks become active?
- What failure/exit-code and diagnostic contract should product-specific validation use?
- What compatibility guarantees should apply when repo-spec framework validation evolves after a repository has been initialized?
- What self-test or fixture surface, if any, should be propagated for product-specific validation development?
- What documentation or discoverability should make the extension points obvious and convenient to product developers?
- How should any future scaffolding avoid being mistaken for accepted product semantics or implementation authority?

These questions are successor analysis inputs. No answer is selected by this collection record.

## Collection boundary

This intake does not authorize changes to initializer runtime behavior, validation code, schemas, product specifications, implementation plans, functional sets, decompositions, or analysis conclusions. Its only purpose is to preserve the requested product direction and current evidence for later governed analysis.
