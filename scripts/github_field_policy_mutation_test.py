#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
POLICY_SCRIPT = REPO_ROOT / "scripts/github_field_policy.py"
SYNTHETIC_FIELD = {
    "id": "synthetic_required_field",
    "label": "Synthetic required field",
    "required": True,
    "input_type": "textarea",
    "description": "Synthetic field used to prove the checker reads the canonical contract.",
    "placeholder": "Provide a substantive response.",
    "validation": {
        "kind": "meaningful",
    },
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n")


def head_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, text=True).strip()


def render_value(field: dict, sha: str) -> str:
    validation = field.get("validation", {})
    kind = validation.get("kind", "meaningful")
    if kind == "issue-link":
        return "#75"
    if kind == "commit-sha":
        return sha
    if kind == "spec-reference":
        return "repo.manifest"
    if kind == "path-list":
        return "scripts/github_field_policy.py"
    if kind == "numbered-steps":
        return "1. First check\n2. Second check"
    if kind == "checklist":
        return "\n".join(f"- [ ] {item}" for item in validation["items"])
    if kind == "default-branch-base":
        return f"{validation.get('branch', 'main')} at {sha}"
    if validation.get("allow_none"):
        return "None."
    return f"Substantive response for {field['label']}."


def render_body(spec: dict, collection_key: str, sha: str) -> str:
    lines: list[str] = []
    for field in spec[collection_key]:
        if field.get("required") is not True:
            continue
        lines.extend([
            f"## {field['label']}",
            "",
            render_value(field, sha),
            "",
        ])
    return "\n".join(lines)


def run_policy(mode: str, repo_root: Path, body_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(POLICY_SCRIPT), str(repo_root), "--mode", mode, "--body-file", str(body_path)],
        capture_output=True,
        text=True,
    )


def mutate_and_expect_failure(mode: str, spec_path: str, collection_key: str) -> None:
    sha = head_sha()
    source_spec = load_json(REPO_ROOT / spec_path)
    body = render_body(source_spec, collection_key, sha)

    with tempfile.TemporaryDirectory() as tmpdir:
        temp_root = Path(tmpdir) / "repo-root"
        shutil.copytree(REPO_ROOT / "specs/repo", temp_root / "specs/repo")
        mutated_spec_path = temp_root / spec_path
        mutated_spec = load_json(mutated_spec_path)
        mutated_spec[collection_key].append(SYNTHETIC_FIELD)
        write_json(mutated_spec_path, mutated_spec)

        body_path = Path(tmpdir) / f"{mode}.md"
        body_path.write_text(body)

        result = run_policy(mode, temp_root, body_path)
        if result.returncode == 0:
            raise SystemExit(f"{mode} policy unexpectedly passed after adding a required field")
        if f"missing section: {SYNTHETIC_FIELD['label']}" not in result.stderr:
            raise SystemExit(
                f"{mode} policy failed for the wrong reason: {result.stderr.strip() or result.stdout.strip()}"
            )


def main() -> int:
    mutate_and_expect_failure("issue", "specs/repo/governing-issue.json", "issue_fields")
    mutate_and_expect_failure("pr", "specs/repo/review-proposal.json", "review_fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
