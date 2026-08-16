# Staged managed upgrade

## Existing-repository staging

Upgrade reuses the initializer product's basic staged lifecycle rather than mutating the live target incrementally.

The prospective complete upgraded repository is prepared in staging before promotion.

Unlike initialization, staging begins from the existing target repository state so subsequent product-owned work remains present in the prospective result.

## Managed application

Normal upgrade application is limited to repo-spec-managed repository framework material, principally the target `repo/` tree.

Where repository-owned sources project behavior outside `repo/`, the capability includes reconciling those managed projections so installed surfaces do not remain stale relative to their authoritative framework sources.

Exceptional `product/` propagation is limited directionally to repo-spec-managed validation support unless later approved product direction expands that boundary.

## Local customization

The capability must recognize that an existing repository may contain local changes to paths that repo-spec also considers managed.

The functional set includes detecting and surfacing that condition as part of safe upgrade handling.

It does not decide whether exact conflicts are merged, rejected, preserved, interactively resolved, or handled through another normative policy.
