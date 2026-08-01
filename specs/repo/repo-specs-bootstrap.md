# Repo Specs Bootstrap

## Status

Bootstrap discovery document for `specs/repo`.

This document is a temporary Markdown starting point. It explains the purpose and layout of the repository-spec tree before the bootstrap material is promoted to normalized JSON.

During bootstrap, files under `specs/repo/` are the authoritative bootstrap source. They cease being authoritative only through the documented JSON cutover.

## Purpose

The `specs/repo` tree defines the portable foundation for this repository.

It exists to describe the framework-level rules, workflow structure, and authority boundaries that must remain separate from product-specific material.

## What belongs here

- repository-wide bootstrap rules;
- workflow definitions;
- validation rules for the bootstrap layer;
- authority and layout guidance for repository-spec material;
- discovery information needed by a fresh chatbot session.

## What does not belong here

- product-specific behavior;
- product domain semantics;
- implementation details for a future product;
- any material that would make the template depend on one product’s meaning.

## Intended layout

The initial `specs/repo` tree starts as a small set of Markdown discovery docs that can later be translated into normalized JSON in the same directory structure.

Expected starting files:

- `repo-specs-bootstrap.md`;
- `dev-workflow-bootstrap.md`;
- `validation.md`;
- `json-artifact-model.md`.

Placeholder JSON files:

- `manifest.json`;
- `repository-structure.json`;
- `development-workflow.json`;
- `validation.json`.

## Bootstrap role

This tree is the first place a chatbot should look when trying to understand the repository framework.

It should make the repository shape easy to infer without requiring prior conversation history.

It should also remain clearly separate from the future `specs/product` tree.
