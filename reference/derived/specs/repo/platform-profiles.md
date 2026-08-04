# Reference Platform Profiles

## Status

accepted

## Purpose

Declares the minimal profile source used by the reference skeleton.

## Profiles

- `github`: GitHub
  - Source root: `profiles/github/`
  - Installed adapter root: `.github/`
  - Authority boundary: `profile-source-authoritative`
  - Adapter generation policy: `source-to-adapter`
  - Artifact inventory:
    - `profiles/github/README.md` -> `profile-source` / `profile-source-authoritative` / `github`
    - `.github/README.md` -> `installed-adapter` / `profile-source-derived` / `github`
  - Remote state kinds:
    - none
  - Hosting mutation record fields:
    - None

## Dependencies

- `repo.manifest`
- `repo.repository-structure`

## References

- specification: `repo.manifest`
- specification: `repo.repository-structure`
- artifact: `profiles/github/README.md`
- artifact: `.github/README.md`

## Derived artifacts

- `markdown`: `derived/specs/repo/platform-profiles.md`

## Normative requirements

- None
