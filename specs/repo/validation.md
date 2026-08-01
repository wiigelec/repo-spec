# Validation Bootstrap

## Status

Bootstrap validation plan for `specs/repo`.

This document defines what validation is meant to prove during the Markdown bootstrap phase.

## Purpose

Validation during bootstrap exists to answer one question:

Can a fresh chatbot session correctly discover the repository-spec foundation, the workflow shape, and the intended boundary between framework material and future product material?

## Validation goals

- confirm the three bootstrap docs exist;
- confirm they describe the repo-spec tree at a high level;
- confirm they describe the development process at a high level;
- confirm they define validation as a bootstrap concern;
- confirm they do not introduce product-specific semantics.

## Validation boundaries

This phase does not yet require:

- JSON schemas;
- generated docs;
- machine-enforced conformance rules;
- product-spec definitions;
- source-code validation.

## Bootstrap success signal

Bootstrap validation succeeds when the docs are sufficient for a fresh chatbot to infer:

- what `specs/repo` is for;
- how bootstrap work should proceed;
- where the boundaries are;
- why the tree exists before normalized JSON takes over.
