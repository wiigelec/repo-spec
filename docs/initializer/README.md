# Repo-Spec Initializer

## Request intake

The initializer accepts initialization requests as local JSON documents.

### Command

```text
scripts/repo-spec-init validate-request <request.json>
```

`validate-request` performs request parsing and validation only. It does not create or modify the destination, initialize Git, contact a hosting platform, or perform any generation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Request is valid and produces a normalized execution context. |
| 1      | Request is invalid, malformed, contradictory, or unsupported. |

### Request schema (version 1)

#### Required fields

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | Request schema version. Must be `"1"`. |
| `destination` | string | Filesystem path for the initialized repository. Must be non-empty. |
| `authority` | object | Granted initialization authority. Must contain `granted_by` (non-empty string). |

#### Optional fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | object | Source repository identity. May contain `repository` (string) and `revision` (string). If `revision` is supplied, `repository` is required. |
| `profile` | string | Execution or platform profile identifier. Supported: `"standard"`. |
| `product` | object | Product identity hints. May contain `id` (string) and `direction_material` (list of strings). |
| `deferred` | array of strings | Field names explicitly deferred. Items must be optional field names. Required fields cannot be deferred. |
| `metadata` | object | Arbitrary metadata preserved for diagnostics or provenance handoff. |

#### Unknown fields

Unknown fields are rejected.

#### Examples

Minimal valid request:

```json
{
  "schema_version": "1",
  "destination": "/path/to/new-repo",
  "authority": {
    "granted_by": "issue-189"
  }
}
```

Full request:

```json
{
  "schema_version": "1",
  "destination": "/path/to/new-repo",
  "authority": {
    "granted_by": "issue-189"
  },
  "source": {
    "repository": "https://github.com/wiigelec/repo-spec",
    "revision": "4cde78952bb854d0c8893f80c13f0dc8ed895791"
  },
  "profile": "standard",
  "product": {
    "id": "my-product",
    "direction_material": ["/path/to/overview.md"]
  },
  "metadata": {
    "requestor": "automation"
  }
}
```

### Validation behavior

* Required fields must be present and have valid types.
* Unknown fields are rejected.
* Contradictory authority or source information is rejected.
* Unsupported profile values are rejected.
* Required fields cannot be deferred.
* Deferred fields must be recognized optional field names.
* Product direction material items must be non-empty strings.
* Schema version must be `"1"`.
* Diagnostics are deterministic.
* No destination mutation occurs during validation.

### Maintainer notes

The initializer code lives in `scripts/initializer/`. The shell wrapper is `scripts/repo-spec-init`.

To run the initializer test suite directly:

```text
python3 -c "import sys; sys.path.insert(0, 'scripts'); from initializer.tests.run_tests import run_initializer_tests; from pathlib import Path; run_initializer_tests(Path.cwd())"
```

Initializer tests are also integrated into `scripts/validate --mutation-tests`.
