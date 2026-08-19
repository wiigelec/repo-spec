"""JSON loading role for root validation."""
import json
from pathlib import Path
from typing import Any

def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)
