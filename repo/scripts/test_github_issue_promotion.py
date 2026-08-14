#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import pathlib
import subprocess
import sys
import tempfile
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
            label["name"] if isinstance(label, dict) else label
            for label in self.issues[number].get("labels", [])
        }
        existing.update(labels)
        self.issues[number]["labels"] = [
            {"name": value} for value in sorted(existing)
        ]
        return self.issues[number]["labels"]


class GitHubIssuePromotionTests(unittest.TestCase):
    def make_issues(self):
        return {
            12: {
                "number": 12,
                "body": "ordinary intake body",
                "labels": [{"name": "bug-fix"}],
            },
            34: {
                "number": 34,
                "body": "candidate governed body",
                "labels": [],
            },
        }

    def test_plan_requires_exactly_one_routing_classification(self):
        issues = self.make_issues()
        issues[12]["labels"] = [{"name": "bug-fix"}, {"name": "feature-request"}]
        client = FakeClient(issues)
        with self.assertRaisesRegex(
            promotion.PromotionError,
            "exactly one pre-promotion routing classification",
        ):
            promotion.inspect_and_plan(
                client=client,
                repository="wiigelec/repo-spec",
                intake_issue=12,
                governing_issue=12,
                governed_operation="operation-12",
                promotion_form="in-place",
                canonical_body="canonical",
            )

    def test_successor_requires_distinct_existing_governing_issue(self):
        client = FakeClient(self.make_issues())
        with self.assertRaisesRegex(
            promotion.PromotionError,
            "distinct existing governing issue",
        ):
            promotion.inspect_and_plan(
                client=client,
                repository="wiigelec/repo-spec",
                intake_issue=12,
                governing_issue=12,
                governed_operation="operation-12",
                promotion_form="successor",
                canonical_body="canonical",
            )

    def test_provenance_comment_contains_original_body_and_routing_label(self):
        client = FakeClient(self.make_issues())
        _, _, labels, comment, _ = promotion.inspect_and_plan(
            client=client,
            repository="wiigelec/repo-spec",
            intake_issue=12,
            governing_issue=34,
            governed_operation="operation-12",
            promotion_form="successor",
            canonical_body="canonical",
        )
        self.assertEqual(labels, ("bug-fix",))
        self.assertIn("ordinary intake body", comment)
        self.assertIn("`bug-fix`", comment)
        self.assertIn("/issues/12", comment)
        self.assertIn("/issues/34", comment)

    def test_target_already_governed_fails_closed(self):
        issues = self.make_issues()
        issues[34]["labels"] = [{"name": "governed-work"}]
        client = FakeClient(issues)
        with self.assertRaisesRegex(
            promotion.PromotionError,
            "already in governed-work state",
        ):
            promotion.inspect_and_plan(
                client=client,
                repository="wiigelec/repo-spec",
                intake_issue=12,
                governing_issue=34,
                governed_operation="operation-12",
                promotion_form="successor",
                canonical_body="canonical",
            )

    def test_apply_order_is_comment_body_verify_then_label(self):
        client = FakeClient(self.make_issues())
        canonical = "## Change type\nMaintenance\n\n## Problem statement\nA meaningful governed body."
        _, _, labels, comment, body_sha = promotion.inspect_and_plan(
            client=client,
            repository="wiigelec/repo-spec",
            intake_issue=12,
            governing_issue=34,
            governed_operation="operation-12",
            promotion_form="successor",
            canonical_body=canonical,
        )

        client.add_comment(12, comment)
        client.update_issue_body(34, canonical)
        observed = client.get_issue(34)
        self.assertEqual(observed["body"], canonical)
        self.assertNotIn(
            "governed-work",
            promotion.normalize_labels(observed),
        )
        client.add_labels(34, ["governed-work"])

        self.assertEqual(
            [op[0] for op in client.operations],
            ["comment", "body", "labels"],
        )
        self.assertEqual(labels, ("bug-fix",))
        self.assertEqual(len(body_sha), 64)

    def test_workflow_is_manual_and_adds_governed_state_last_through_helper(self):
        source = (
            REPO_ROOT
            / "repo/profiles/github/workflows/governed-work-promotion.yml"
        ).read_text()
        installed = (
            REPO_ROOT
            / ".github/workflows/governed-work-promotion.yml"
        ).read_text()
        self.assertEqual(source, installed)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("issues: write", source)
        self.assertNotIn("issues:\n    types:", source)
        self.assertIn("--apply", source)
        self.assertIn("repo/scripts/github_issue_promotion.py", source)

    def test_helper_defaults_to_plan_only_without_apply(self):
        source = MODULE_PATH.read_text()
        self.assertIn('parser.add_argument("--apply", action="store_true")', source)
        self.assertIn("if not args.apply:", source)
        self.assertIn('"status": "plan"', source)


if __name__ == "__main__":
    unittest.main()
