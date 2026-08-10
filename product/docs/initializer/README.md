# Repo-Spec Initializer

## Normal human workflow

The supported normal-user command is:

```text
repo-spec init --repo /path/to/new/repository-name
```

From an uninstalled repo-spec checkout:

```text
product/scripts/repo-spec init --repo /path/to/new/repository-name
```

`--repo` names the destination repository path. The repository name is derived mechanically from the final destination path segment. No user-authored JSON is required for the normal workflow.

## Local framework provenance

The executing wrapper identifies its own repo-spec Git repository and exact clean `HEAD` commit. Framework material is read from that exact commit tree and the repository path/revision are recorded in bootstrap provenance.

Initialization fails closed when the executing framework checkout is dirty, ambiguous, not a local Git repository, uses an unsupported Git object format, or cannot provide an exact local commit.

## What bootstrap creates

Successful bootstrap creates and validates a local Git repository containing the reusable repository framework declared by the closed framework/output inventories, plus:

- `repo/initializer/provenance.json`
- `repo/initializer/handoff.json`
- the deterministic initial Git state

The normal wrapper `product/scripts/repo-spec` is installed as reusable runtime framework material.

## What bootstrap does not create

Repository bootstrap does not establish:

- product ID or product identity
- product direction material or direction evidence
- product overview
- product decomposition
- product specifications or product manifest authority
- product implementation plan
- hosting-platform state

Those are governed successor activities after the repository exists.

## Internal canonical request

The lower-level runtime uses a strict normalized request representation internally:

```json
{
  "schema_version": "2",
  "destination": "/absolute/path/to/new/repository-name"
}
```

The normal wrapper constructs this from `--repo`; users normally do not author it.

The canonical request fingerprint is SHA-256 over the deterministic canonical JSON bytes. Framework repository/revision provenance is carried separately and does not alter that fingerprint. Unknown fields are rejected.

## Lower-level developer interface

The subordinate launcher remains available for diagnostic/developer work:

```text
product/scripts/repo-spec-init --request request.json
```

A schema-version-2 request contains only `schema_version` and `destination`.

Lower-level diagnostic commands are implementation/development surfaces, not the recommended normal-user workflow.

## Transaction safety

Bootstrap works in an isolated staging transaction on the destination filesystem. Promotion occurs only after validation passes. The final repository directory is promoted atomically to the confirmed-absent destination.

The initializer does not overwrite or migrate an existing repository, perform remote retrieval, create a hosted repository, or silently resume a failed staging transaction.

## Provenance and handoff

`repo/initializer/provenance.json` records initializer identity/version, exact local framework repository/revision, initialization timestamp, and canonical bootstrap request fingerprint.

`repo/initializer/handoff.json` classifies installed framework material and generated bootstrap records. Product foundations are empty at bootstrap. The next governed action is product overview/direction work.

## Validation

Before a governed initializer change is proposed for merge, run:

```text
scripts/validate
```
