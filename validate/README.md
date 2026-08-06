Validation guidance lives in `repo/specs/repo/validation.json` and `repo/derived/specs/repo/validation.md`.

The only enforcement entry point is `repo/scripts/validate`.

Deterministic Markdown generation lives in `repo/scripts/generate-docs`.

Validation is closed to the seven checks defined in the validation spec.

`repo/scripts/validate --mutation-tests` runs the schema mutation checks for the supported repository JSON Schema subset.
