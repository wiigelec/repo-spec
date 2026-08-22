"""Reusable root validation invariant helpers."""
from .errors import fail

# validation-metadata: {"role": "helper"}
def expect(condition: bool, message: str) -> None:
    if not condition:
        fail(message)
