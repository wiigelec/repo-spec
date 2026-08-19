"""Validation context and domain-loading extension point."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ValidationContext:
    """Common validation context shape extended by the owning domain."""

    repo_root: Path
    repository: Any | None = None
    product: Any | None = None
