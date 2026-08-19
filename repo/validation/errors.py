from __future__ import annotations


class ValidationFailure(Exception):
    pass


def fail(message: str) -> None:
    raise ValidationFailure(message)


def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
