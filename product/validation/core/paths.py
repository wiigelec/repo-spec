"""Repository-relative validation path helpers."""

# Product-owned repository-relative path mechanics.

from __future__ import annotations

from pathlib import Path

from validation.core.errors import fail


# validation-metadata: {"role": "helper"}
def resolve_repo_path(repo_root: Path, value: str) -> Path:
    if (
        not value
        or value.startswith("/")
        or value.startswith("./")
        or "/./" in value
        or value.endswith("/.")
        or "\\" in value
        or "//" in value
    ):
        fail(f"invalid repository-relative path: {value}")

    relative = Path(value)
    if any(part in {".", ".."} for part in relative.parts):
        fail(f"invalid repository-relative path: {value}")

    resolved = (repo_root / relative).resolve()
    try:
        resolved.relative_to(repo_root.resolve())
    except ValueError:
        fail(f"invalid repository-relative path: {value}")
    return resolved
