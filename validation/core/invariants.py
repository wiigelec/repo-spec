"""Reusable root validation invariant helpers."""
from .errors import fail

def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
