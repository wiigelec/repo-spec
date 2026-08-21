"""Shared root validation failure helpers."""
class ValidationFailure(RuntimeError):
    pass

def fail(message: str) -> None:
    raise ValidationFailure(message)
fail.__validation_metadata__ = {"role": "helper"}
