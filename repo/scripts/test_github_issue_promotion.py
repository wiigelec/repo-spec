#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "repo/scripts/github_issue_promotion.py"

spec = importlib.util.spec_from_file_location("github_issue_promotion", MODULE_PATH)
assert spec and spec.loader
promotion = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = promotion
spec.loader.exec_module(promotion)


class FakeClient:
    def __init__(self, issues):
        self.repository = "wiigelec/repo-spec"
        self.issues = issues
        self.operations = []

    def get_issue(self, number):
        return json.loads(json.dumps(self.issues[number]))

    def add_comment(self, number, body):
        self.operations.append(("comment", number, body))
        return {"id": 1, "body": body}

    def update_issue_body(self, number, body):
        self.operations.append(("body", number, body))
        self.issues[number]["body"] = body
        return self.get_issue(number)

    def add_labels(self, number, labels):
        self.operations.append(("labels", number, tuple(labels)))
        existing = {
            item["name"] if isinstance(item, dict) else item
            for item in self.issues[number].get("labels", [])
        }
        existing.update(labels)
        self.issues[number]["labels"] = [
            {"name": value} for value in sorted(existing)
        ]
        return self.issues[number]["labels"]


def governed_authority_body(operation, *, feature=False):
    evidence = "audit accepted correction"
    if feature:
        evidence = (
            "whiteboard analysis candidate-functional-set "
            "explicit-functional-set-approval"
        )
    return (
        "## Change type\nProduct-artifact implementation\n\n"
        "## Problem statement\nBounded authority evidence.\n\n"
        f"## Intended outcome\nAuthorize {operation}.\n\n"
        "## Governing specifications\nproduct.issue-routing-governance\n\n"
        "## Accepted default-branch base\nmain at abc\n\n"
        f"## Dependencies and predecessor evidence\n{evidence}; operation={operation}\n\n"
        "## Ordered patch plan\n1. bounded correction\n\n"
        "## Validation plan\nvalidate\n\n"
        "## Acceptance criteria\naccepted\n\n"
        "## Completion gate\nmanual merge\n\n"
        "## Open decisions or authority conflicts\nNone\n\n"
        "## Successor work explicitly not authorized\nAnything else\n"
    )


class GitHubIssuePromotionTests(unittest.TestCase):
    def make_issues(self, *, classification="bug-fix", feature_authority=False):
        return {
            12: {"number": 12, "body": "ordinary intake body", "labels": [{"name": classification}]},
            34: {"number": 34, "body": "candidate governed body", "labels": []},
            56: {
                "number": 56,
                "body": governed_authority_body("operation-34", feature=feature_authority),
                "labels": [{"name": "governed-work"}],
            },
        }

    @mock.patch("subprocess.run")
    def test_bug_fix_requires_governed_audit_authority_evidence(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        client = FakeClient(self.make_issues())
        authorization = promotion.require_repository_governance_authorization(
            client=client,
            authority_issue=56,
            governed_operation="operation-34",
            routing_labels=("bug-fix",),
            policy_command="repo/scripts/github-field-policy",
        )
        self.assertEqual(authorization.authority_path, "audit")

    @mock.patch("subprocess.run")
    def test_feature_request_requires_all_feature_development_stage_evidence(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        client = FakeClient(self.make_issues(classification="feature-request", feature_authority=False))
        with self.assertRaisesRegex(promotion.PromotionError, "accepted authority path"):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governed_operation="operation-34",
                routing_labels=("feature-request",),
                policy_command="repo/scripts/github-field-policy",
            )
        client = FakeClient(self.make_issues(classification="feature-request", feature_authority=True))
        authorization = promotion.require_repository_governance_authorization(
            client=client,
            authority_issue=56,
            governed_operation="operation-34",
            routing_labels=("feature-request",),
            policy_command="repo/scripts/github-field-policy",
        )
        self.assertEqual(authorization.authority_path, "feature-development")

    @mock.patch("subprocess.run")
    def test_routing_label_alone_cannot_authorize_mutation(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        issues = self.make_issues()
        issues[56]["labels"] = []
        client = FakeClient(issues)
        with self.assertRaisesRegex(promotion.PromotionError, "already be in governed-work state"):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governed_operation="operation-34",
                routing_labels=("bug-fix",),
                policy_command="repo/scripts/github-field-policy",
            )
        self.assertEqual(client.operations, [])

    @mock.patch("subprocess.run")
    def test_authority_evidence_must_match_operation(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        client = FakeClient(self.make_issues())
        with self.assertRaisesRegex(promotion.PromotionError, "not traceable"):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governed_operation="operation-99",
                routing_labels=("bug-fix",),
                policy_command="repo/scripts/github-field-policy",
            )

    def test_authority_check_precedes_all_mutation(self):
        source = MODULE_PATH.read_text()
        authority_pos = source.index("authorization = require_repository_governance_authorization")
        comment_pos = source.index("client.add_comment(args.intake_issue")
        body_pos = source.index("client.update_issue_body(args.governing_issue")
        label_pos = source.index("client.add_labels(args.governing_issue")
        self.assertLess(authority_pos, comment_pos)
        self.assertLess(comment_pos, body_pos)
        self.assertLess(body_pos, label_pos)

    def test_workflow_requires_authority_issue_input(self):
        source = (REPO_ROOT / "repo/profiles/github/workflows/governed-work-promotion.yml").read_text()
        installed = (REPO_ROOT / ".github/workflows/governed-work-promotion.yml").read_text()
        self.assertEqual(source, installed)
        self.assertIn("authority_issue:", source)
        self.assertIn("--authority-issue", source)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("issues: write", source)


if __name__ == "__main__":
    unittest.main()
