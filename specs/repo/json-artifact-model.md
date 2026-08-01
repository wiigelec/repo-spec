# JSON Artifact Model

## Status

Discovery document for the normative JSON artifact model.

The JSON files under `specs/repo/` are the authoritative repo-spec sources.

## Purpose

Define the closed JSON artifact model used by repository specs.

The model favors one file per specification so changes remain bounded and dependency edges stay visible.

## Scope

This document defines:

- one JSON file per specification;
- stable specification identity;
- title and purpose fields;
- specification status;
- normative requirements;
- dependencies and references;
- schema version;
- derived artifact relationships.

Repository manifests use the companion manifest schema and add an `authoritative_specs` list that identifies the complete repository-spec JSON set.

## Closed model

```json
{
  "spec_id": "repo.validation",
  "title": "Validation",
  "purpose": "Defines validation for repo specs.",
  "status": "accepted",
  "schema_version": "1",
  "normative_requirements": [
    {
      "id": "REPO-VAL-001",
      "text": "The repository shall provide one validation entry point."
    }
  ],
  "dependencies": [
    {
      "spec_id": "repo.repository-structure"
    }
  ],
  "references": [
    {
      "type": "specification",
      "spec_id": "repo.development-workflow"
    },
    {
      "type": "artifact",
      "path": "docs/overview/PRODUCT-OVERVIEW.md"
    }
  ],
  "derived_artifacts": [
    {
      "type": "markdown",
      "path": "derived/specs/repo/validation.md"
    }
  ]
}
```

## Fields

### `spec_id`

- Namespaced, path-independent identifier.
- Format: `^(repo|product)\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*(?:\.[a-z][a-z0-9]*(?:-[a-z0-9]+)*)*$`
- Stable for the artifact’s lifetime.
- Not derived mechanically from paths.

### `title`

- Human-readable specification name.

### `purpose`

- Short statement of what the specification governs.

### `status`

Closed set:

- `candidate`: proposed, non-authoritative.
- `accepted`: current normative authority.
- `superseded`: replaced by identified specification artifacts.
- `retired`: withdrawn without a replacement.

### `schema_version`

- String identifier for the artifact schema.
- Initial value: `"1"`.

### `normative_requirements`

- Array of structured requirement objects.
- Each object has `id` and `text`.

### `dependencies`

- Array of structured dependency objects.
- Each object has `spec_id`.
- Dependencies represent normative graph edges and must resolve to accepted specifications.

### `references`

- Array of structured reference objects.
- Each object has `type` and one target field.
- Closed types:
  - `specification`
  - `artifact`

### `derived_artifacts`

- Array of structured derived artifact objects.
- Each object has `type` and `path`.
- Closed type:
  - `markdown`

## Cutover rule

The bootstrap Markdown reference is provenance only.

It must not compete with the normative JSON specification after cutover.
