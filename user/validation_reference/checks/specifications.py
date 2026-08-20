"""Specification-system validation extension point."""

from __future__ import annotations


def validate_specifications(context) -> None:
    """Validate specifications, manifests, references, and lineage owned by the domain."""
    return None
