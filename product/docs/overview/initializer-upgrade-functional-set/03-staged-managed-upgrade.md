# Staged managed upgrade

## Existing-repository staging

Upgrade reuses the initializer product's basic staged lifecycle rather than mutating the live target incrementally.

The prospective complete upgraded repository is prepared in staging before promotion.

Unlike fresh initialization, staging begins from the existing target repository state. The initializer-managed portion is then re-initialized/reconciled in place within the staged copy, while material outside the initializer-managed universe remains present and outside upgrade mutation authority.

## Managed application

Upgrade application is limited to initializer-managed material that the initializer is capable of installing into a derived repository.

For eligible material, reconciliation may create newly installable entries, replace changed entries, remove retired entries, or retarget managed outputs. Where initializer-managed sources project behavior outside `repo/`, those installed surfaces remain inside the same managed reconciliation boundary.

This rule applies uniformly across paths. For example, initializer-installed `product/` validation support and product level-spec schemas may be eligible, while ordinary product-owned specifications and implementation artifacts that the initializer does not install are not upgrade targets.

## Local customization

The capability must recognize that an existing repository may contain local changes to paths that repo-spec also considers managed.

The functional set includes detecting and surfacing that condition as part of safe upgrade handling.

It does not decide whether exact conflicts are merged, rejected, preserved, interactively resolved, or handled through another normative policy.
