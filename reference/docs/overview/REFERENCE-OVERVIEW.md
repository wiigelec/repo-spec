# Reference Repository Overview

This overview records the intended shape of the reference repository.

## Intended users

- implementers extending the framework
- reviewers checking isolated-copy portability
- automated agents recovering the repo state

## Desired outcome

The reference copy should prove that a minimal initialized repository can be described, discovered, generated, validated, and mutation-tested with an active product manifest, product-level source behavior, product tests, and complete correspondence records for the accepted product requirements.

## Success conditions

- a new session can identify the governing issue, plan, and active repository/product files
- the reference repository validates from its own root without parent-checkout dependence
- repository-derived and product-derived projections stay fresh
- the product example demonstrates Level 0 foundations and Level 1 dependent normalization

## Constraints

- keep the reference copy small and self-contained
- retain isolated-copy validation
- keep repository-generic authority separate from product-specific behavior
- preserve deterministic generation and reproducible validation

## Explicit non-goals

- no generalized initializer
- no future product runtime semantics beyond the reference proof
- no remote hosting mutation
- no product expansion beyond the minimal proof set

## Product boundaries

- repository specifications govern repository-generic behavior
- product specifications govern the minimal example product behavior
- derived projections are subordinate to their source specifications
- bootstrap scripts remain support infrastructure until replaced
