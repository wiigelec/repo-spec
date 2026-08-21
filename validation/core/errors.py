"""Shared root validation failure helpers."""
class ValidationFailure(RuntimeError):
    pass

# validation-metadata: {"role": "helper"}
def fail(message: str) -> None:
    raise ValidationFailure(message)
