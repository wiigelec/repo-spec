from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
HELPER_PATH = REPO_ROOT / "repo/scripts/github_issue_promotion.py"
SOURCE_WORKFLOW = (
    REPO_ROOT / "repo/profiles/github/workflows/governed-work-promotion.yml"
)
INSTALLED_WORKFLOW = (
    REPO_ROOT / ".github/workflows/governed-work-promotion.yml"
)

spec = importlib.util.spec_from_file_location(
    "product_hosted_conformance_promotion",
    HELPER_PATH,
)
assert spec and spec.loader
promotion = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = promotion
spec.loader.exec_module(promotion)


class FakeClient:
    instances = []

    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token
        self.operations = []
        self.issues = {
            12: {
                "number": 12,
                "body": "ordinary unformatted intake body",
                "labels": [{"name": "bug-fix"}],
            },
            34: {
                "number": 34,
                "body": "pre-promotion successor placeholder",
                "labels": [],
            },
        }
        self.__class__.instances.append(self)

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


class HostedRoutingConformanceTests(unittest.TestCase):
    def setUp(self):
        FakeClient.instances.clear()

    def invoke_apply(
        self,
        *,
        promotion_form="successor",
        intake_issue=12,
        governing_issue=34,
        governed_operation="operation-34",
    ):
        FakeClient.instances.clear()
        canonical_body = (
            "## Change type\nMaintenance\n\n"
            "## Problem statement\nA canonical governed issue body used by conformance."
        )
        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_body)
            output = io.StringIO()
            with (
                mock.patch.object(promotion, "GitHubClient", FakeClient),
                mock.patch.object(
                    promotion,
                    "validate_canonical_body",
                    return_value=canonical_body,
                ),
                mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}, clear=False),
                contextlib.redirect_stdout(output),
            ):
                rc = promotion.main(
                    [
                        "--repository",
                        "wiigelec/repo-spec",
                        "--intake-issue",
                        str(intake_issue),
                        "--governing-issue",
                        str(governing_issue),
                        "--governed-operation",
                        governed_operation,
                        "--promotion-form",
                        promotion_form,
                        "--canonical-body-file",
                        str(body_path),
                        "--apply",
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(len(FakeClient.instances), 1)
        return FakeClient.instances[0], json.loads(output.getvalue())

    def test_successor_apply_preserves_provenance_before_body_and_governed_state(self):
        client, result = self.invoke_apply()

        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )
        provenance = client.operations[0][2]
        self.assertIn("ordinary unformatted intake body", provenance)
        self.assertIn("`bug-fix`", provenance)
        self.assertIn("Captured before body replacement/restructuring: yes", provenance)

        self.assertEqual(client.operations[1][1], 34)
        self.assertEqual(client.operations[2], ("labels", 34, ("governed-work",)))

        evidence = result["canonical_state_evidence"]
        self.assertEqual(
            evidence["governing_issue"],
            "https://github.com/wiigelec/repo-spec/issues/34",
        )
        self.assertEqual(evidence["governed_operation"], "operation-34")
        self.assertEqual(
            evidence["validated_revision"],
            evidence["observed_revision"],
        )
        self.assertTrue(evidence["validation_artifact_id"])

        promotion_evidence = result["promotion_evidence"]
        self.assertEqual(promotion_evidence["routing_labels"], ["bug-fix"])
        self.assertTrue(promotion_evidence["provenance_comment_created"])
        self.assertTrue(promotion_evidence["body_installed"])
        self.assertTrue(promotion_evidence["governed_work_added"])
        self.assertFalse(promotion_evidence["mutation_authorized_by_routing"])

    def test_in_place_and_successor_forms_are_both_supported(self):
        client, result = self.invoke_apply(
            promotion_form="in-place",
            intake_issue=12,
            governing_issue=12,
            governed_operation="operation-12",
        )
        self.assertEqual(result["promotion_evidence"]["promotion_form"], "in-place")
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )

        client2, result2 = self.invoke_apply()
        self.assertEqual(result2["promotion_evidence"]["promotion_form"], "successor")
        self.assertEqual(
            [operation[0] for operation in client2.operations],
            ["comment", "body", "labels"],
        )

    def test_hosted_workflow_is_manual_managed_and_subordinate(self):
        source = SOURCE_WORKFLOW.read_text()
        installed = INSTALLED_WORKFLOW.read_text()
        self.assertEqual(source, installed)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("issues: write", source)
        self.assertNotIn("issues:\n    types:", source)
        self.assertIn("repo/scripts/github_issue_promotion.py", source)
        self.assertIn("--apply", source)

        helper = HELPER_PATH.read_text()
        self.assertIn('"mutation_authorized_by_routing": False', helper)
        self.assertIn("client.add_comment(args.intake_issue", helper)
        self.assertIn("client.update_issue_body(args.governing_issue", helper)
        self.assertIn("client.add_labels(args.governing_issue", helper)

        comment_pos = helper.index("client.add_comment(args.intake_issue")
        body_pos = helper.index("client.update_issue_body(args.governing_issue")
        label_pos = helper.index("client.add_labels(args.governing_issue")
        self.assertLess(comment_pos, body_pos)
        self.assertLess(body_pos, label_pos)

    def test_plan_mode_does_not_mutate(self):
        canonical_body = "canonical governed body"
        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_body)
            output = io.StringIO()
            with (
                mock.patch.object(promotion, "GitHubClient", FakeClient),
                mock.patch.object(
                    promotion,
                    "validate_canonical_body",
                    return_value=canonical_body,
                ),
                mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}, clear=False),
                contextlib.redirect_stdout(output),
            ):
                rc = promotion.main(
                    [
                        "--repository",
                        "wiigelec/repo-spec",
                        "--intake-issue",
                        "12",
                        "--governing-issue",
                        "34",
                        "--governed-operation",
                        "operation-34",
                        "--promotion-form",
                        "successor",
                        "--canonical-body-file",
                        str(body_path),
                    ]
                )
        self.assertEqual(rc, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "plan")
        self.assertEqual(FakeClient.instances[0].operations, [])


if __name__ == "__main__":
    unittest.main()
