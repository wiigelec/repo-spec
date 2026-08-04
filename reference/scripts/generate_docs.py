#!/usr/bin/env python3

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import validate_impl as impl


def write_generated_docs(repo_root: Path) -> None:
    targets = [
        (repo_root / "specs/product/level-0/kernel.json", repo_root / "derived/specs/product/level-0/kernel.md"),
        (repo_root / "specs/product/level-1/primitives.json", repo_root / "derived/specs/product/level-1/primitives.md"),
    ]
    for source_path, target_path in targets:
        spec = impl.load_json(source_path)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_text(impl.render_projection(spec))


def main(argv: list[str]) -> int:
    repo_root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    write_generated_docs(repo_root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
