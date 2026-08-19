"""Repository-relative path helpers for root validation."""
from pathlib import Path

def resolve_repo_path(repo_root: Path, relative_path: str) -> Path:
    path = (repo_root / relative_path).resolve()
    try:
        path.relative_to(repo_root.resolve())
    except ValueError as exc:
        raise ValueError(f"path escapes repository root: {relative_path}") from exc
    return path
