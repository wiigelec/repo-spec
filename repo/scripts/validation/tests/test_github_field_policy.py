from __future__ import annotations

from pathlib import Path

from github_field_policy import PolicyError, check_issue, load_fields, parse_change_type


def _expect_policy_error(label: str, action, expected: str | None = None) -> None:
    try:
        action()
    except PolicyError as exc:
        if expected is not None and expected not in str(exc):
            raise AssertionError(f"{label}: unexpected policy error: {exc}") from exc
        return
    raise AssertionError(f"{label}: expected PolicyError")


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
            value = "repo/scripts/github_field_policy.py"
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


def run_github_field_policy_tests(repo_root: Path) -> None:
    fields = load_fields(repo_root, "repo/specs/repo/governing-issue.json", "issue_fields")
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
