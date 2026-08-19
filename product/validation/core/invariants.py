"""Reusable validation invariant extension point."""

from __future__ import annotations


def validate_invariants(context) -> None:
    """Validate reusable invariants shared by checks in the owning domain."""
    return None
