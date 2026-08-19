"""Shared validation failure helpers."""

from __future__ import annotations


class ValidationFailure(RuntimeError):
    """Raised when validation fails cleanly."""


def fail(message: str) -> None:
    raise ValidationFailure(message)


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
