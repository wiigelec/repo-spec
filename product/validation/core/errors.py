"""Shared validation failure helpers."""

from __future__ import annotations


class ValidationFailure(Exception):
    pass


# validation-metadata: {"role": "helper"}
def fail(message: str) -> None:
    raise ValidationFailure(message)


# validation-metadata: {"role": "helper"}
def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
