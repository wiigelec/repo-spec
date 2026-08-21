from __future__ import annotations

import json
import tempfile
from pathlib import Path

from validation.github.github_field_policy import (
    PolicyError,
    check_issue,
    load_body_from_event,
    load_fields,
    parse_change_type,
)


# validation-metadata: {"role": "helper"}
def _expect_policy_error(label: str, action, expected: str | None = None) -> None:
    try:
        action()
    except PolicyError as exc:
        if expected is not None and expected not in str(exc):
            raise AssertionError(f"{label}: unexpected policy error: {exc}") from exc
        return
    raise AssertionError(f"{label}: expected PolicyError")


# validation-metadata: {"role": "helper"}
def _issue_body(fields: list[dict], change_type: str) -> str:
    sections: list[str] = []
    for field in fields:
        if field.get("required") is not True:
            continue
        validation = field.get("validation", {"kind": "meaningful"})
        kind = validation.get("kind", "meaningful")
        if field["id"] == "change_type":
            value = change_type
        elif kind == "issue-link":
            value = "#305"
        elif kind == "commit-sha":
            value = "644c7ed11335548805cb068fffdacd0c15729669"
        elif kind == "spec-reference":
            value = "repo.validation"
        elif kind == "path-list":
            value = "repo/validation/github/github_field_policy.py"
        elif kind == "numbered-steps":
            value = "1. Validate the exact Change type boundary."
        elif kind == "checklist":
            value = "\n".join(f"- [x] {item}" for item in validation["items"])
        elif kind == "default-branch-base":
            value = "main at 644c7ed11335548805cb068fffdacd0c15729669"
        else:
            value = "Meaningful governed policy test content."
        sections.append(f"## {field['label']}\n\n{value}")
    return "\n\n".join(sections) + "\n"



# validation-metadata: {"role": "helper"}
def _check_unlabeled_issue_workflow_policy(repo_root: Path, fields: list[dict]) -> None:
    workflow = (repo_root / ".github/workflows/github-field-policy.yml").read_text()

    accepted_event_set = "types: [opened, edited, reopened, labeled]"
    if accepted_event_set not in workflow:
        raise AssertionError("issue workflow event set changed")
    if "types: [opened, edited, reopened]\n" in workflow:
        raise AssertionError("issue workflow event set regressed")

    issue_condition = (
        "  issue-policy:\n"
        "    if: github.event_name == 'issues'\n"
    )
    if issue_condition not in workflow:
        raise AssertionError("issue-policy job is not unconditional with respect to labels")

    issue_block = workflow.split("  issue-policy:\n", 1)[1].split(
        "\n  pr-policy:\n", 1
    )[0]
    if "governed-work" in issue_block or "labels" in issue_block:
        raise AssertionError("issue-policy job still depends on labels")

    pr_condition = (
        "  pr-policy:\n"
        "    if: github.event_name == 'pull_request_target'\n"
    )
    if pr_condition not in workflow:
        raise AssertionError("pull-request policy condition changed unexpectedly")

    valid_body = _issue_body(fields, "Maintenance")
    malformed_body = valid_body.replace(
        "## Problem statement\n\nMeaningful governed policy test content.",
        "",
        1,
    )
    if malformed_body == valid_body:
        raise AssertionError("could not construct malformed issue fixture")

    with tempfile.TemporaryDirectory() as tmpdir:
        event_path = Path(tmpdir) / "event.json"

        event_path.write_text(json.dumps({
            "action": "opened",
            "issue": {"body": valid_body, "labels": []},
        }))
        check_issue(load_body_from_event(event_path, "issue"), fields, repo_root)

        event_path.write_text(json.dumps({
            "action": "edited",
            "issue": {"body": malformed_body, "labels": []},
        }))
        _expect_policy_error(
            "unlabeled malformed issue event",
            lambda: check_issue(
                load_body_from_event(event_path, "issue"),
                fields,
                repo_root,
            ),
            "missing section: Problem statement",
        )

# validation-metadata: {"role": "helper"}
def run_github_field_policy_tests(repo_root: Path) -> None:
    fields = load_fields(repo_root, "repo/specs/repo/governing-issue.json", "issue_fields")
    _check_unlabeled_issue_workflow_policy(repo_root, fields)
    field = next(item for item in fields if item["id"] == "change_type")
    values = field["validation"]["values"]

    for value in values:
        if parse_change_type("Change type", value, values) != value:
            raise AssertionError(f"exact canonical Change type changed: {value!r}")

    variants: set[str] = {"Not-a-change-type"}
    for value in values:
        variants.update({
            " " + value, value + " ", "\t" + value, value + "\t",
            "\n" + value, value + "\n", "prefix " + value,
            value + ": descriptive prose", value + " - descriptive prose",
        })
        if " " in value:
            variants.add(value.replace(" ", "  ", 1))
            variants.add(value.replace(" ", "\t", 1))
            variants.add(value.replace(" ", "\n", 1))

    for variant in sorted(variants):
        _expect_policy_error(
            f"non-canonical Change type {variant!r}",
            lambda variant=variant: parse_change_type("Change type", variant, values),
            "invalid change type",
        )

    check_issue(_issue_body(fields, "Maintenance"), fields, repo_root)

    _expect_policy_error(
        "non-canonical Product-artifact implementation dispatch",
        lambda: check_issue(_issue_body(fields, "Product-artifact  implementation"), fields, repo_root),
        "invalid change type",
    )

    try:
        check_issue(_issue_body(fields, "Product-artifact implementation"), fields, repo_root)
    except PolicyError as exc:
        if "invalid change type" in str(exc):
            raise AssertionError("exact Product-artifact implementation rejected as classification") from exc
        if "implementation-plan" not in str(exc) and "Governing specifications" not in str(exc):
            raise AssertionError(f"exact Product-artifact implementation did not reach evidence gate: {exc}") from exc
    else:
        raise AssertionError("exact Product-artifact implementation did not activate stricter evidence gate")


import unittest


class GitHubFieldPolicyTests(unittest.TestCase):
    # validation-metadata: {"role": "helper"}
    def test_github_field_policy(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        run_github_field_policy_tests(repo_root)
