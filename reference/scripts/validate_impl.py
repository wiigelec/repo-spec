#!/usr/bin/env python3

from __future__ import annotations

import json
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "README.md",
    "AGENTS.md",
    "docs/overview/REFERENCE-OVERVIEW.md",
    "docs/plans/01-reference-repository-plan.md",
    "specs/repo/manifest.json",
    "specs/repo/governing-issue.json",
    "specs/repo/review-proposal.json",
    "specs/repo/repository-structure.json",
    "specs/repo/artifact-taxonomy.json",
    "specs/repo/platform-profiles.json",
    "specs/repo/development-workflow.json",
    "specs/repo/validation.json",
    "schemas/repo-manifest.schema.json",
    "schemas/repo-spec.schema.json",
    "schemas/repo-artifact-taxonomy.schema.json",
    "schemas/repo-platform-profiles.schema.json",
    "schemas/repo-validation.schema.json",
    "profiles/github/README.md",
    "profiles/github/manifest.json",
    "scripts/validate",
]


def load_json(path: Path) -> None:
    with path.open("r", encoding="utf-8") as handle:
        json.load(handle)


def main(argv: list[str]) -> int:
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()

    missing = [str(path) for path in REQUIRED_PATHS if not (root / path).exists()]
    if missing:
        print("missing required reference paths:", file=sys.stderr)
        for path in missing:
            print(f"- {path}", file=sys.stderr)
        return 1

    for relpath in [
        "specs/repo/manifest.json",
        "specs/repo/governing-issue.json",
        "specs/repo/review-proposal.json",
        "specs/repo/repository-structure.json",
        "specs/repo/artifact-taxonomy.json",
        "specs/repo/platform-profiles.json",
        "specs/repo/development-workflow.json",
        "specs/repo/validation.json",
        "profiles/github/manifest.json",
    ]:
        load_json(root / relpath)

    if (root / "specs/product/manifest.json").exists():
        print("product activation must remain minimal or empty for this issue", file=sys.stderr)
        return 1

    print("ok: reference skeleton validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
