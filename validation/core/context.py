"""Root validation context role."""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
@dataclass(frozen=True)
class ValidationContext:
    repo_root: Path
