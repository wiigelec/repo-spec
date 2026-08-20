#!/usr/bin/env python3

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
import re


REPO_ROOT = Path(__file__).resolve().parents[3]
POLICY_SCRIPT = REPO_ROOT / "validation/github/github_field_policy.py"
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
        return "repo/validation/github/github_field_policy.py"
    if kind == "numbered-steps":
        return "1. First check\n2. Second check"
    if kind == "checklist":
        return "\n".join(f"- [ ] {item}" for item in validation["items"])
    if kind == "default-branch-base":
        return f"release/v2 at {sha}"
    if kind == "change-type":
        return validation["values"][0]
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


def create_policy_fixture(temp_root: Path) -> Path:
    repo_root = temp_root / "repo-root"
    shutil.copytree(REPO_ROOT / "repo/specs/repo", repo_root / "repo/specs/repo")
    product_spec_root = repo_root / "product/specs/product"
    product_spec_root.mkdir(parents=True)
    shutil.copy2(REPO_ROOT / "product/specs/product/manifest.json", product_spec_root / "manifest.json")
    shutil.copytree(REPO_ROOT / "product/docs/plans", repo_root / "product/docs/plans")
    return repo_root


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
            f"release/v2 at {sha[:-1]}",
            f"release/v2 at {sha}0",
            f"release/v2 at {sha[:-1]}g",
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
    cited_specs = "\n".join(
        f"- {spec_id}"
        for spec_id in (
            "product.initializer-level-0",
            "product.execution-profile",
            "product.content-equivalence",
            "product.lifecycle-stages",
            "product.execution-orchestration",
            "product.full-initialization",
        )
    )
    replacements = {
        "Maintenance": "Product-artifact implementation",
        "repo.manifest": (
            "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md\n\n"
            f"{cited_specs}"
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
            cited_specs,
            "repo.manifest",
            "missing manifest-listed accepted product specification",
        ),
        (
            "candidate product specification",
            "product.full-initialization",
            "product.platform-profile-interface",
            "missing manifest-listed accepted product specification",
        ),
        (
            "absent product specification",
            "product.full-initialization",
            "product.not-registered",
            "missing manifest-listed accepted product specification",
        ),
        (
            "unrelated accepted product specification",
            "product.full-initialization",
            "product.initialization-request",
            "cited product specifications do not equal the union of selected implementation-plan workstreams/stages",
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

    # patch2 fixture: bind existing valid spec set to canonical workstream id
    import importlib.util
    policy_spec = importlib.util.spec_from_file_location("field_policy_fixture", POLICY_SCRIPT)
    if policy_spec is None or policy_spec.loader is None:
        raise SystemExit("cannot load field policy for product-artifact fixture")
    policy_module = importlib.util.module_from_spec(policy_spec)
    policy_spec.loader.exec_module(policy_module)
    governing_match = re.search(r"^## Governing specifications\s*$\n(.*?)(?=^##\s|\Z)", body, re.M | re.S)
    if governing_match is None:
        raise SystemExit("product-artifact fixture lacks Governing specifications")
    cited_specs = {s for s in policy_module.SPEC_RE.findall(governing_match.group(1)) if s.startswith("product.") and s != "product.manifest"}
    accepted_specs = policy_module.load_accepted_product_specs(REPO_ROOT)
    authority = policy_module.load_plan_controlling_spec_sets(REPO_ROOT, "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md", accepted_specs)
    matching_ids = sorted(k for k,v in authority.items() if set(v) == cited_specs)
    if not matching_ids:
        raise SystemExit("product-artifact fixture spec set does not match canonical workstream authority")
    body = body.rstrip() + "\n\n## Implementation-plan workstreams/stages\n\n" + matching_ids[0] + "\n"

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

        fixture_root = create_policy_fixture(Path(tmpdir))
        workstream_path = fixture_root / "product/docs/plans/initializer-implementation-plan/02-increments-and-dependencies.md"
        workstream_path.write_text(
            workstream_path.read_text().replace(
                "`product.full-initialization::INIT-FIN-001-011`",
                "`product.initialization-request::INIT-REQ-001-015`",
            )
        )
        body_path.write_text(body)
        result = run_policy("issue", fixture_root, body_path)
        if result.returncode != 0:
            raise SystemExit(f"issue policy depended on incidental implementation-plan Markdown: {result.stderr.strip()}")

        plan_path = fixture_root / "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md"
        plan_path.write_text(
            plan_path.read_text().replace(
                '"product.execution-profile",\n        "product.full-initialization",',
                '"product.execution-profile",\n        "product.initialization-request",',
            )
        )
        mutated_plan_body = body.replace("product.full-initialization", "product.initialization-request")
        body_path.write_text(mutated_plan_body)
        result = run_policy("issue", fixture_root, body_path)
        if result.returncode != 0:
            raise SystemExit(f"issue policy did not follow canonical implementation-plan authority: {result.stderr.strip()}")

        plan_path.write_text(
            plan_path.read_text().replace(
                '"lifecycle_status": "accepted"',
                '"lifecycle_status": "candidate"',
            )
        )
        body_path.write_text(body)
        result = run_policy("issue", fixture_root, body_path)
        if result.returncode == 0:
            raise SystemExit("issue policy accepted a candidate implementation plan")
        if "cited implementation plan is not accepted" not in result.stderr:
            raise SystemExit(f"issue policy rejected a candidate plan for the wrong reason: {result.stderr.strip()}")


def check_multi_workstream_product_artifact_evidence() -> None:
    sha = head_sha()
    spec = load_json(REPO_ROOT / "repo/specs/repo/governing-issue.json")
    body = render_body(spec, "issue_fields", sha)

    import importlib.util
    policy_spec = importlib.util.spec_from_file_location("field_policy_multi", POLICY_SCRIPT)
    if policy_spec is None or policy_spec.loader is None:
        raise SystemExit("cannot load field policy for multi-workstream test")
    module = importlib.util.module_from_spec(policy_spec)
    policy_spec.loader.exec_module(module)

    accepted_specs = module.load_accepted_product_specs(REPO_ROOT)
    authority = module.load_plan_controlling_spec_sets(
        REPO_ROOT,
        "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md",
        accepted_specs,
    )
    ids = sorted(authority)
    if len(ids) < 2:
        raise SystemExit("multi-workstream fixture requires at least two canonical IDs")

    first, second = ids[0], ids[1]
    union_specs = sorted(set(authority[first]) | set(authority[second]))
    specs_text = "\n".join(f"- {spec_id}" for spec_id in union_specs)

    body = body.replace(
        "Maintenance",
        "Product-artifact implementation",
        1,
    )
    body = body.replace(
        "repo.manifest",
        "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md\n\n" + specs_text,
    )
    body = body.replace(
        "Substantive response for Dependencies and predecessor evidence.",
        f"Issue #299 at {sha}.",
    )
    body = body.rstrip() + (
        "\n\n## Implementation-plan workstreams/stages\n\n"
        f"{first}\n{second}\n"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "issue.md"
        body_path.write_text(body)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode != 0:
            raise SystemExit(f"multi-workstream union was rejected: {result.stderr.strip()}")

        body_path.write_text(body.replace(f"{first}\n{second}", f"{first}\nUNKNOWN_STAGE"))
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode == 0 or "unknown implementation-plan workstream/stage identifier" not in result.stderr:
            raise SystemExit(f"unknown workstream ID was not rejected correctly: {result.stderr.strip()}")

        if len(union_specs) > 1:
            subset_text = "\n".join(f"- {spec_id}" for spec_id in union_specs[:-1])
            body_path.write_text(body.replace(specs_text, subset_text))
            result = run_policy("issue", REPO_ROOT, body_path)
            if result.returncode == 0 or "do not equal the union" not in result.stderr:
                raise SystemExit(f"union subset was not rejected correctly: {result.stderr.strip()}")



def check_change_type_validation() -> None:
    sha = head_sha()
    spec = load_json(REPO_ROOT / "repo/specs/repo/governing-issue.json")
    body = render_body(spec, "issue_fields", sha)

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "issue.md"
        values = next(
            field["validation"]["values"]
            for field in spec["issue_fields"]
            if field["id"] == "change_type"
        )

        for value in values:
            body_path.write_text(body.replace("Maintenance", value, 1))
            result = run_policy("issue", REPO_ROOT, body_path)
            if value in {"Product-artifact implementation", "Atomic authority transition"}:
                if result.returncode == 0 or "missing canonical implementation-plan citation" not in result.stderr:
                    raise SystemExit(
                        f"strict change classification did not activate its evidence gate: {value}: {result.stderr.strip()}"
                    )
            elif result.returncode != 0:
                raise SystemExit(f"canonical change type was rejected: {value}: {result.stderr.strip()}")

        for description, noncanonical in (
            (
                "legacy descriptive maintenance classification",
                "Maintenance and specification consistency correction following a prior audit.",
            ),
            (
                "descriptive maintenance prose mentioning product-artifact policy",
                "Maintenance discussing Product-artifact implementation policy semantics.",
            ),
        ):
            body_path.write_text(body.replace("Maintenance", noncanonical, 1))
            result = run_policy("issue", REPO_ROOT, body_path)
            if result.returncode == 0 or "invalid change type in Change type" not in result.stderr:
                raise SystemExit(
                    f"{description} was not rejected as a noncanonical change type: {result.stderr.strip()}"
                )

        fuzzy_product = body.replace(
            "Maintenance",
            "Product-artifact implementation and some descriptive prose.",
            1,
        )
        body_path.write_text(fuzzy_product)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode == 0 or "invalid change type in Change type" not in result.stderr:
            raise SystemExit(f"fuzzy product classification was not rejected exactly: {result.stderr.strip()}")

        for invalid in ("Unknown", "maintenance", "Product artifact implementation", "Featurette"):
            body_path.write_text(body.replace("Maintenance", invalid, 1))
            result = run_policy("issue", REPO_ROOT, body_path)
            if result.returncode == 0 or "invalid change type in Change type" not in result.stderr:
                raise SystemExit(f"invalid change type was not rejected: {invalid}: {result.stderr.strip()}")



def check_atomic_transition_evidence_validation() -> None:
    sha = head_sha()
    spec = load_json(REPO_ROOT / "repo/specs/repo/governing-issue.json")
    body = render_body(spec, "issue_fields", sha)

    import importlib.util
    policy_spec = importlib.util.spec_from_file_location("field_policy_atomic", POLICY_SCRIPT)
    if policy_spec is None or policy_spec.loader is None:
        raise SystemExit("cannot load field policy for atomic-transition fixture")
    module = importlib.util.module_from_spec(policy_spec)
    policy_spec.loader.exec_module(module)

    accepted_specs = module.load_accepted_product_specs(REPO_ROOT)
    authority = module.load_plan_controlling_spec_sets(
        REPO_ROOT,
        "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md",
        accepted_specs,
    )
    stage = sorted(authority)[0]
    current_union = set(authority[stage])
    extra_candidates = sorted(accepted_specs - current_union)
    if not extra_candidates:
        raise SystemExit("atomic-transition fixture requires an accepted transition spec outside current stage union")
    transition_spec = extra_candidates[0]
    cited_specs = sorted(current_union | {transition_spec})
    specs_text = "\n".join(f"- {spec_id}" for spec_id in cited_specs)

    body = body.replace("Maintenance", "Atomic authority transition", 1)
    body = body.replace(
        "repo.manifest",
        "product/docs/plans/INITIALIZER-IMPLEMENTATION-PLAN.md\n\n" + specs_text,
        1,
    )
    body = body.replace(
        "Substantive response for Dependencies and predecessor evidence.",
        f"Issue #495 at {sha}.",
        1,
    )
    body = body.rstrip() + (
        "\n\n## Implementation-plan workstreams/stages\n\n"
        f"{stage}\n"
        "\n## Atomic transition evidence\n\n"
        "Invariant: accepted correspondence requires specification and maintained artifact key sets to remain synchronized.\n"
        "No valid intermediate revision: either ordinary ordering violates the accepted correspondence invariant.\n"
        "Plan impact: reaffirm the affected stage against the revised accepted authority before maintained implementation is treated as authorized.\n"
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        body_path = Path(tmpdir) / "issue.md"
        body_path.write_text(body)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode != 0:
            raise SystemExit(f"atomic transition evidence was rejected: {result.stderr.strip()}")

        without_extra = body.replace(f"- {transition_spec}\n", "")
        body_path.write_text(without_extra)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode == 0 or "at least one additional accepted transition specification" not in result.stderr:
            raise SystemExit(f"atomic transition without extra transition spec was not rejected correctly: {result.stderr.strip()}")

        missing_evidence = re.sub(r"\n## Atomic transition evidence\n.*\Z", "", body, flags=re.S)
        body_path.write_text(missing_evidence)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode == 0 or "missing section: Atomic transition evidence" not in result.stderr:
            raise SystemExit(f"atomic transition without evidence was not rejected correctly: {result.stderr.strip()}")

        bad_intermediate = body.replace(
            "No valid intermediate revision: either ordinary ordering violates the accepted correspondence invariant.\n",
            "",
        )
        body_path.write_text(bad_intermediate)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode == 0 or "missing atomic transition evidence item: No valid intermediate revision" not in result.stderr:
            raise SystemExit(f"atomic transition missing intermediate-revision evidence was not rejected correctly: {result.stderr.strip()}")

        bad_plan = body.replace(
            "Plan impact: reaffirm the affected stage against the revised accepted authority before maintained implementation is treated as authorized.\n",
            "Plan impact: postpone consideration until later.\n",
        )
        body_path.write_text(bad_plan)
        result = run_policy("issue", REPO_ROOT, body_path)
        if result.returncode == 0 or "missing atomic transition evidence item: Plan impact" not in result.stderr:
            raise SystemExit(f"atomic transition without revise/reaffirm plan impact was not rejected correctly: {result.stderr.strip()}")

def main() -> int:
    check_default_branch_base_validation()
    check_product_artifact_evidence_validation()
    mutate_and_expect_failure("issue", "repo/specs/repo/governing-issue.json", "issue_fields")
    mutate_and_expect_failure("pr", "repo/specs/repo/review-proposal.json", "review_fields")
    check_multi_workstream_product_artifact_evidence()
    check_atomic_transition_evidence_validation()
    check_change_type_validation()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


import unittest


class RootMutationTests(unittest.TestCase):
    def test_atomic_transition_evidence_validation(self) -> None:
        check_atomic_transition_evidence_validation()

    def test_change_type_validation(self) -> None:
        check_change_type_validation()

    def test_default_branch_base_validation(self) -> None:
        check_default_branch_base_validation()

    def test_multi_workstream_product_artifact_evidence(self) -> None:
        check_multi_workstream_product_artifact_evidence()

    def test_product_artifact_evidence_validation(self) -> None:
        check_product_artifact_evidence_validation()
