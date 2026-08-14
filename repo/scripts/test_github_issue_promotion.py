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


def authorization_record(
    *,
    classification="bug-fix",
    governing_issue=34,
    governed_operation="operation-34",
):
    if classification == "bug-fix":
        path = "audit"
        lifecycle = {"audit": "accepted"}
    else:
        path = "feature-development"
        lifecycle = {
            "whiteboard": "accepted",
            "analysis": "accepted",
            "candidate-functional-set": "accepted",
            "explicit-functional-set-approval": "accepted",
        }
    return {
        "schema_version": "1",
        "routing_classification": classification,
        "authority_path": path,
        "governed_operation": governed_operation,
        "governing_issue": (
            f"https://github.com/wiigelec/repo-spec/issues/{governing_issue}"
        ),
        "lifecycle_evidence": lifecycle,
    }


def governed_authority_body(
    operation="operation-34",
    *,
    classification="bug-fix",
    record=None,
    unrelated_keywords="",
):
    if record is None:
        record = authorization_record(
            classification=classification,
            governed_operation=operation,
        )
    record_text = json.dumps(record, sort_keys=True)
    return (
        "## Change type\nProduct-artifact implementation\n\n"
        "## Problem statement\nBounded authority evidence.\n\n"
        f"## Intended outcome\nAuthorize {operation}.\n\n"
        "## Governing specifications\nproduct.issue-routing-governance\n\n"
        "## Accepted default-branch base\nmain at "
        "b7606ca6d058c47b10f00913e678707c22c378ee\n\n"
        "## Dependencies and predecessor evidence\n"
        "#420 b7606ca6d058c47b10f00913e678707c22c378ee\n\n"
        "```repo-governance-authorization\n"
        f"{record_text}\n"
        "```\n\n"
        f"{unrelated_keywords}\n\n"
        "## Ordered patch plan\n1. bounded correction\n\n"
        "## Validation plan\nvalidate\n\n"
        "## Acceptance criteria\naccepted\n\n"
        "## Completion gate\nmanual merge\n\n"
        "## Open decisions or authority conflicts\nNone\n\n"
        "## Successor work explicitly not authorized\nAnything else\n"
    )


class GitHubIssuePromotionTests(unittest.TestCase):
    def make_issues(
        self,
        *,
        classification="bug-fix",
        record=None,
        authority_governed=True,
        unrelated_keywords="",
    ):
        labels = [{"name": "governed-work"}] if authority_governed else []
        return {
            12: {
                "number": 12,
                "body": "ordinary intake body",
                "labels": [{"name": classification}],
            },
            34: {
                "number": 34,
                "body": "candidate governed body",
                "labels": [],
            },
            56: {
                "number": 56,
                "body": governed_authority_body(
                    classification=classification,
                    record=record,
                    unrelated_keywords=unrelated_keywords,
                ),
                "labels": labels,
            },
        }

    @mock.patch("subprocess.run")
    def test_bug_fix_requires_structured_target_bound_audit_authority(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        client = FakeClient(self.make_issues())
        authorization = promotion.require_repository_governance_authorization(
            client=client,
            authority_issue=56,
            governing_issue=34,
            governed_operation="operation-34",
            routing_labels=("bug-fix",),
            policy_command="repo/scripts/github-field-policy",
        )
        self.assertEqual(authorization.authority_path, "audit")
        self.assertEqual(authorization.governing_issue, 34)

    @mock.patch("subprocess.run")
    def test_feature_request_requires_complete_structured_feature_authority(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        complete = authorization_record(classification="feature-request")
        incomplete = authorization_record(classification="feature-request")
        incomplete["lifecycle_evidence"].pop("explicit-functional-set-approval")

        client = FakeClient(
            self.make_issues(
                classification="feature-request",
                record=incomplete,
                unrelated_keywords=(
                    "whiteboard analysis candidate-functional-set "
                    "explicit-functional-set-approval"
                ),
            )
        )
        with self.assertRaisesRegex(
            promotion.PromotionError,
            "complete structured feature-development evidence",
        ):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governing_issue=34,
                governed_operation="operation-34",
                routing_labels=("feature-request",),
                policy_command="repo/scripts/github-field-policy",
            )

        client = FakeClient(
            self.make_issues(
                classification="feature-request",
                record=complete,
            )
        )
        authorization = promotion.require_repository_governance_authorization(
            client=client,
            authority_issue=56,
            governing_issue=34,
            governed_operation="operation-34",
            routing_labels=("feature-request",),
            policy_command="repo/scripts/github-field-policy",
        )
        self.assertEqual(authorization.authority_path, "feature-development")

    @mock.patch("subprocess.run")
    def test_arbitrary_keywords_do_not_create_authority(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        body = governed_authority_body(
            unrelated_keywords=(
                "audit whiteboard analysis candidate-functional-set "
                "explicit-functional-set-approval"
            ),
        ).replace("```repo-governance-authorization", "```not-authority")
        issues = self.make_issues()
        issues[56]["body"] = body
        client = FakeClient(issues)
        with self.assertRaisesRegex(
            promotion.PromotionError,
            "exactly one structured repository-governance authorization record",
        ):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governing_issue=34,
                governed_operation="operation-34",
                routing_labels=("bug-fix",),
                policy_command="repo/scripts/github-field-policy",
            )

    @mock.patch("subprocess.run")
    def test_authority_must_match_target_classification_and_operation(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""

        cases = [
            (
                authorization_record(governing_issue=99),
                ("bug-fix",),
                "operation-34",
                "target governing issue",
            ),
            (
                authorization_record(classification="feature-request"),
                ("bug-fix",),
                "operation-34",
                "classification",
            ),
            (
                authorization_record(governed_operation="operation-99"),
                ("bug-fix",),
                "operation-34",
                "governed operation",
            ),
        ]
        for record, labels, operation, message in cases:
            with self.subTest(message=message):
                client = FakeClient(self.make_issues(record=record))
                with self.assertRaisesRegex(promotion.PromotionError, message):
                    promotion.require_repository_governance_authorization(
                        client=client,
                        authority_issue=56,
                        governing_issue=34,
                        governed_operation=operation,
                        routing_labels=labels,
                        policy_command="repo/scripts/github-field-policy",
                    )

    @mock.patch("subprocess.run")
    def test_routing_label_alone_cannot_authorize_mutation(self, run):
        run.return_value.returncode = 0
        run.return_value.stdout = ""
        run.return_value.stderr = ""
        client = FakeClient(self.make_issues(authority_governed=False))
        with self.assertRaisesRegex(
            promotion.PromotionError, "already be in governed-work state"
        ):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governing_issue=34,
                governed_operation="operation-34",
                routing_labels=("bug-fix",),
                policy_command="repo/scripts/github-field-policy",
            )
        self.assertEqual(client.operations, [])

    def test_authority_check_precedes_all_mutation(self):
        source = MODULE_PATH.read_text()
        authority_pos = source.index(
            "authorization = require_repository_governance_authorization"
        )
        comment_pos = source.index("client.add_comment(args.intake_issue")
        body_pos = source.index("client.update_issue_body(args.governing_issue")
        label_pos = source.index("client.add_labels(args.governing_issue")
        self.assertLess(authority_pos, comment_pos)
        self.assertLess(comment_pos, body_pos)
        self.assertLess(body_pos, label_pos)

    def test_hosted_helper_no_longer_searches_lifecycle_keywords_in_body(self):
        source = MODULE_PATH.read_text()
        self.assertNotIn('required_markers = ("audit",)', source)
        self.assertNotIn("missing = [marker for marker", source)
        self.assertIn("parse_repository_governance_authorization", source)


if __name__ == "__main__":
    unittest.main()
