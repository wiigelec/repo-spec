"""Shared support role for root validation mutation self-tests."""

def expect_failure(description: str, action, fragment: str) -> None:
    try:
        action()
    except Exception as exc:
        if fragment not in str(exc):
            raise AssertionError(f"{description}: expected {fragment!r}, got {exc}") from exc
        return
    raise AssertionError(f"{description}: expected failure")
