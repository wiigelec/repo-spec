"""Production validation runner template."""

from __future__ import annotations


def main(argv: list[str]) -> int:
    """Run production validation for the owning domain."""
    raise NotImplementedError("materialized domain must bind its production validator")
