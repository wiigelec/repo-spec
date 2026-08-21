"""Reusable root validation invariant helpers."""
from .errors import fail

def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
expect.__validation_metadata__ = {"role": "helper"}
