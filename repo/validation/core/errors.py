"""Shared validation failure helpers."""

from __future__ import annotations


class ValidationFailure(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationFailure(message)
fail.__validation_metadata__ = {"role": "helper"}


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
expect.__validation_metadata__ = {"role": "helper"}
