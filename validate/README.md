Validation guidance lives in `specs/repo/validation.json` and `derived/specs/repo/validation.md`.

The only enforcement entry point is `scripts/validate`.

Deterministic Markdown generation lives in `scripts/generate-docs`.

Validation is closed to the seven checks defined in the validation spec.

`scripts/validate --mutation-tests` runs the schema mutation checks for the supported repository JSON Schema subset.
