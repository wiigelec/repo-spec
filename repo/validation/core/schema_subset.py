"""JSON and supported schema-validation mechanics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load UTF-8 JSON from a repository path."""
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
