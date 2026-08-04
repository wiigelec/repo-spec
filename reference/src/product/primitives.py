"""Reference product primitives behavior."""

from .kernel import canonical_text


def normalize_identifier(value: str) -> str:
    return canonical_text(value).replace("_", "-")
