---
doc_id: DP-013
title: Repository Ownership and Structural Boundaries
depends_on:
  - DP-001
  - DP-010
  - DP-012
---

# Repository Ownership and Structural Boundaries

## Purpose

The repository framework is portable across products. It separates reusable repository-development framework state from the product-owned state developed through that framework while keeping the repository structure understandable and mechanically protectable.

## Ownership Domains

`repo/` is the reusable repository/framework ownership domain.

It contains the Design, Planning, normative specifications, implementation, entry points, and Validation that define or realize the portable repository-development framework itself.

`product/` is the generic product ownership domain.

It contains the Design, Planning, normative specifications, implementation, entry points, and Validation owned by whatever product a particular repository develops. The framework defines the role and structural boundary of `product/`; it does not define or pin the product's identity, semantics, technology, architecture, or feature set.

Repository/framework work and product work use the same lifecycle responsibilities. Their artifacts remain in the ownership domain whose meaning and behavior they govern.

## Other Repository State

Repository-root operational surfaces such as `README.md`, `AGENTS.md`, hosting integration, licensing, and explicitly user-owned material may exist outside the two ownership trees when their repository role requires it.

`user/` remains user-owned operational material outside framework and product normative ownership.

## Closed Structural Boundaries

Design may declare an architectural boundary closed.

At a closed boundary, an entry is permitted only when the governing structure explicitly authorizes its role. Absence of an explicit prohibition is not permission to create a new architectural namespace.

Closed boundaries should be shallow and selective. They protect architectural ownership and major repository roles; they do not require every nested implementation directory or source package to be enumerated.

A namespace may be explicitly extensible. Ordinary Build decisions may create content inside an extensible namespace when that content preserves the namespace role and governing upstream intent.

## Architectural Change Boundary

Build may choose ordinary files, modules, packages, and nested organization inside an extensible implementation namespace.

Build shall not create a new direct child at a closed architectural boundary merely for implementation convenience. If an existing boundary cannot express required behavior cleanly, work returns upstream so Design can decide whether the repository architecture changes and Planning can derive the corresponding obligations.

## Product Portability

The generic `product/` contract must remain usable for products unrelated to the repo-spec initializer.

Framework behavior may supply generic product-development surfaces and structural constraints, but product-specific meaning belongs to product Design and Planning rather than repository/framework Design.

## Validation

Closed structural boundaries are mechanically decidable where their permitted direct entries are explicit.

Validation may enforce those boundaries directly. Such enforcement protects accepted structure but does not independently create a new namespace, ownership rule, or product semantic.
