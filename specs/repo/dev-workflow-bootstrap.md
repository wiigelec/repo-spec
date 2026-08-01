# Development Workflow Bootstrap

## Status

Bootstrap discovery document for the high-level development process.

This document describes the early Markdown workflow used to shape the repository-spec foundation before any normalized JSON authority exists.

During bootstrap, files under `specs/repo/` are the authoritative bootstrap source. They cease being authoritative only through the documented JSON cutover.

Bootstrap changes use the normal governed workflow: create a governing issue, work on an isolated branch, validate the exact branch head, and merge only after acceptance.

## Purpose

Define the high-level process for working in the repository during bootstrap.

The goal is to make a fresh chatbot session able to infer the correct order of discovery, mutation, and validation without guessing at hidden process rules.

## High-level process

1. Establish a governing issue.
2. Identify the accepted default-branch base.
3. Create an isolated working branch.
4. Read the bootstrap discovery docs first.
5. Keep the work bounded to one coherent change.
6. Update the Markdown bootstrap docs directly.
7. Validate the changed files against the intended bootstrap shape.
8. Preserve a clear boundary between repository framework material and any future product material.

## Bootstrap expectations

- Markdown is the working format during bootstrap.
- The process should be simple enough to recover in a fresh chat.
- The docs should explain what the repository is for before any machine-readable contract exists.
- Product-specific material is not defined yet and should not be invented here.

## Transition note

Later, once the bootstrap stabilizes, the authoritative source will move to normalized JSON and this Markdown will become derived, non-normative documentation.
