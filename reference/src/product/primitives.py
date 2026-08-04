"""Reference product primitives behavior."""

from .kernel import kernel_identity


def primitive_identity() -> str:
    return f"{kernel_identity()}-primitives"
