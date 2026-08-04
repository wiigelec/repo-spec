"""Reference product kernel behavior."""


def canonical_text(value: str) -> str:
    return " ".join(value.split()).lower()
