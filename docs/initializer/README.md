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

## Framework inventory and source inspection

The initializer maintains a machine-readable reusable-material inventory that classifies every repository path by role. Source inspection validates the request, resolves source selection, loads and validates the inventory, and reports classified material.

### Command

```text
scripts/repo-spec-init inspect-source <request.json>
```

`inspect-source` performs request parsing and validation, validates source identity and revision, loads and validates the framework inventory, and emits deterministic inspection output. It performs no destination mutation, copying, rendering, generation, Git mutation, or hosting-platform operation.

### Exit status

| Status | Meaning |
|--------|---------|
| 0      | Request, source, and inventory are valid. Inspection output is emitted to stdout. |
| 1      | Invalid request, missing or contradictory source, invalid inventory, or I/O error. |

### Inspection output

Output is a JSON object with:

* `status` — `"inspection_complete"` on success.
* `source_selection` — object with `repository` and `revision`, or `null` when no source is requested.
* `classifications` — object mapping classification names to arrays of inventory entries.

Each entry reports:

* `path` — repository-relative path.
* `authoritative` — whether this is authoritative source material.
* `installable` — whether the entry is eligible for installation.
* `profile` — applicable platform profile, if any.
* `exclusion_rationale` — explanation when the entry is excluded or uninstallable.
* `derived_from` — authoritative source paths for derived material.

### Material classifications

| Classification | Role | Installable | Example |
|----------------|------|-------------|---------|
| `framework-authoritative` | Reusable authoritative repository-framework source | Yes | `specs/repo/`, `schemas/` |
| `framework-support` | Reusable tooling or support content | Yes | `scripts/`, `AGENTS.md` |
| `derived` | Generated or projected content | Yes | `derived/` |
| `profile-source` | Reusable source selected only by explicit platform profile | No | `profiles/github/` |
| `installed-adapter` | Current repository adapter content | No | `.github/` |
| `product-instance` | Product-specific direction, planning, or specification content | No | `docs/overview/`, `docs/plans/` |
| `development-state` | Non-source workflow state | No | `.gitignore` |
| `excluded` | Content unavailable to initializer installation | No | `reference/`, `src/` |

Classification does not itself authorize copying or installation.

### Inventory file

The maintained inventory is at `scripts/initializer/framework-inventory.json`. It is a JSON document containing:

* `schema_version` — must be `"1"`.
* `inventory_scope` — descriptive scope identifier.
* `entries` — array of inventory entry objects.

Each entry contains:

* `path` (required) — repository-relative source path.
* `classification` (required) — one of the recognized material classifications.
* `authoritative` (boolean) — whether the entry is authoritative source.
* `installable` (boolean) — whether the entry may be installed.
* `profile` (string, optional) — platform profile identifier for profile-controlled material.
* `exclusion_rationale` (string, optional) — explanation for excluded or uninstallable entries.
* `derived_from` (array, optional) — authoritative source paths for derived entries.

### Source selection rules

* Source selection requires explicit `repository` and `revision` in the request.
* When both are absent, selection remains `null` without error.
* When only `revision` is supplied without `repository`, selection fails.
* When only `repository` is supplied without `revision`, selection fails.
* Empty repository or revision values are rejected.
* No branch, default revision, checkout, or network state is silently inferred.

### Maintainer notes

The initializer code lives in `scripts/initializer/`. The shell wrapper is `scripts/repo-spec-init`.

To run the initializer test suite directly:

```text
python3 -c "import sys; sys.path.insert(0, 'scripts'); from initializer.tests.run_tests import run_initializer_tests; from pathlib import Path; run_initializer_tests(Path.cwd())"
```

Initializer tests are also integrated into `scripts/validate --mutation-tests`.
