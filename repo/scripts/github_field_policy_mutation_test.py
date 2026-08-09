#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
POLICY_SCRIPT = REPO_ROOT / "repo/scripts/github_field_policy.py"
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
        return "repo/scripts/github_field_policy.py"
    if kind == "numbered-steps":
        return "1. First check\n2. Second check"
    if kind == "checklist":
        return "\n".join(f"- [ ] {item}" for item in validation["items"])
    if kind == "default-branch-base":
        return f"release/v2 at {sha}"
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
        shutil.copytree(REPO_ROOT / "repo/specs/repo", temp_root / "repo/specs/repo")
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


def check_default_branch_base_validation() -> None:
    sha = head_sha()
    spec = load_json(REPO_ROOT / "repo/specs/repo/governing-issue.json")
    valid_body = render_body(spec, "issue_fields", sha)

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "issue.md"
        body_path.write_text(valid_body)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode != 0:
            raise SystemExit(f"issue policy rejected an alternate default branch: {result.stderr.strip()}")

        valid_base = f"release/v2 at {sha}"
        for invalid_base in (
            f"release..v2 at {sha}",
            f"release/v2 {sha}",
            f"release/v2 at {sha} extra",
            f"-release at {sha}",
            f"HEAD at {sha}",
        ):
            body_path.write_text(valid_body.replace(valid_base, invalid_base))
            result = run_policy("issue", REPO_ROOT, body_path)
            if result.returncode == 0:
                raise SystemExit(f"issue policy accepted invalid default-branch base: {invalid_base}")


def check_product_artifact_evidence_validation() -> None:
    sha = head_sha()
    spec = load_json(REPO_ROOT / "repo/specs/repo/governing-issue.json")
    body = render_body(spec, "issue_fields", sha)
    replacements = {
        "Substantive response for Change type.": "Product-artifact implementation.",
        "repo.manifest": (
            "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md\n\n"
            "- product.initializer-level-0"
        ),
        "Substantive response for Dependencies and predecessor evidence.": f"Issue #273 at {sha}.",
    }
    for old, new in replacements.items():
        body = body.replace(old, new)

    invalid_cases = (
        (
            "missing implementation plan",
            "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md",
            "Planning authority omitted",
            "missing canonical implementation-plan citation",
        ),
        (
            "missing accepted product specification",
            "product.initializer-level-0",
            "repo.manifest",
            "missing manifest-listed accepted product specification",
        ),
        (
            "candidate product specification",
            "product.initializer-level-0",
            "product.platform-profile-interface",
            "missing manifest-listed accepted product specification",
        ),
        (
            "missing predecessor issue",
            f"Issue #273 at {sha}.",
            f"Predecessor revision {sha}.",
            "missing predecessor implementation issue and revision evidence",
        ),
        (
            "missing predecessor revision",
            f"Issue #273 at {sha}.",
            "Issue #273 is the predecessor.",
            "missing predecessor implementation issue and revision evidence",
        ),
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "issue.md"
        body_path.write_text(body)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode != 0:
            raise SystemExit(f"issue policy rejected complete product-artifact evidence: {result.stderr.strip()}")

        for name, old, new, expected_error in invalid_cases:
            body_path.write_text(body.replace(old, new))
            result = run_policy("issue", REPO_ROOT, body_path)
            if result.returncode == 0:
                raise SystemExit(f"issue policy accepted {name}")
            if expected_error not in result.stderr:
                raise SystemExit(f"issue policy rejected {name} for the wrong reason: {result.stderr.strip()}")


def main() -> int:
    check_default_branch_base_validation()
    check_product_artifact_evidence_validation()
    mutate_and_expect_failure("issue", "repo/specs/repo/governing-issue.json", "issue_fields")
    mutate_and_expect_failure("pr", "repo/specs/repo/review-proposal.json", "review_fields")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
