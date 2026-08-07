Validation guidance lives in `repo/specs/repo/validation.json` and `repo/derived/specs/repo/validation.md`.

The repository leaf entry point is `repo/scripts/validate`.

The product leaf entry point is `product/scripts/validate`.

The aggregate enforcement entry point is `scripts/validate`; it runs both leaf validators plus repository- and product-owned validation self-tests.

Deterministic Markdown generation lives in `repo/scripts/generate-docs`.

Validation ownership and checks are defined by the validation spec.
