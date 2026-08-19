"""Domain-specific production validation policy extension point."""

from __future__ import annotations


def validate_policy(context) -> None:
    """Validate owning-domain policy not covered by another standard check role."""
    return None
