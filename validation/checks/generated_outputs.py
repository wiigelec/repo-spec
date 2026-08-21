"""Cross-domain generated-output validation extension point."""
from __future__ import annotations
from pathlib import Path

def validate(repo_root: Path) -> None:
    return None
validate.__validation_metadata__ = {"role": "helper"}
