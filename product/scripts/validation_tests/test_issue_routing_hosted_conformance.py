from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
PRODUCT_SCRIPTS = REPO_ROOT / "product" / "scripts"
if str(PRODUCT_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(PRODUCT_SCRIPTS))

from issue_intake_governance_routing import (
    CanonicalGovernedStateObservation,
    CanonicalGovernedStateValidationResult,
    validate_canonical_governed_state,
)

HELPER_PATH = REPO_ROOT / "repo/scripts/github_issue_promotion.py"
SOURCE_WORKFLOW = REPO_ROOT / "repo/profiles/github/workflows/governed-work-promotion.yml"
INSTALLED_WORKFLOW = REPO_ROOT / ".github/workflows/governed-work-promotion.yml"

spec = importlib.util.spec_from_file_location(
    "product_hosted_conformance_promotion",
    HELPER_PATH,
)
assert spec and spec.loader
promotion = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = promotion
spec.loader.exec_module(promotion)


def authority_body(operation: str, *, classification: str) -> str:
    if classification == "bug-fix":
        route_evidence = "audit accepted correction"
    else:
        route_evidence = (
            "whiteboard analysis candidate-functional-set "
            "explicit-functional-set-approval"
        )
    return (
        "## Change type\nProduct-artifact implementation\n\n"
        "## Problem statement\nAccepted bounded repository authority.\n\n"
        f"## Intended outcome\nAuthorize {operation}.\n\n"
        "## Governing specifications\nproduct.issue-routing-governance\n\n"
        "## Accepted default-branch base\nmain at abc\n\n"
        f"## Dependencies and predecessor evidence\n{route_evidence}; {operation}\n\n"
        "## Ordered patch plan\n1. bounded correction\n\n"
        "## Validation plan\nvalidate\n\n"
        "## Acceptance criteria\naccepted\n\n"
        "## Completion gate\nmanual merge\n\n"
        "## Open decisions or authority conflicts\nNone\n\n"
        "## Successor work explicitly not authorized\nAnything else\n"
    )


class FakeClient:
    instances = []
    classification = "bug-fix"
    authority_governed = True
    feature_complete = True

    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token
        self.operations = []
        classification = self.__class__.classification
        auth_classification = classification
        auth_body = authority_body("operation-34", classification=auth_classification)
        if classification == "feature-request" and not self.__class__.feature_complete:
            auth_body = auth_body.replace("explicit-functional-set-approval", "")
        authority_labels = [{"name": "governed-work"}] if self.__class__.authority_governed else []
        self.issues = {
            12: {
                "number": 12,
                "body": "ordinary unformatted intake body",
                "labels": [{"name": classification}],
            },
            34: {
                "number": 34,
                "body": "pre-promotion successor placeholder",
                "labels": [],
            },
            56: {
                "number": 56,
                "body": auth_body,
                "labels": authority_labels,
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


class HostedCanonicalValidator:
    def __init__(self, helper_evidence):
        self.helper_evidence = helper_evidence

    def validate(self, observation):
        return CanonicalGovernedStateValidationResult(
            governing_issue=self.helper_evidence["governing_issue"],
            governed_operation=self.helper_evidence["governed_operation"],
            validated_revision=self.helper_evidence["validated_revision"],
            validation_artifact_id=self.helper_evidence["validation_artifact_id"],
            validator_id="hosted-conformance.github-field-policy",
            canonical_structure_valid=True,
        )


class HostedRoutingConformanceTests(unittest.TestCase):
    def setUp(self):
        FakeClient.instances.clear()
        FakeClient.classification = "bug-fix"
        FakeClient.authority_governed = True
        FakeClient.feature_complete = True

    def invoke_apply(
        self,
        *,
        classification="bug-fix",
        authority_governed=True,
        feature_complete=True,
    ):
        FakeClient.instances.clear()
        FakeClient.classification = classification
        FakeClient.authority_governed = authority_governed
        FakeClient.feature_complete = feature_complete
        canonical_body = (
            "## Change type\nMaintenance\n\n"
            "## Problem statement\nA canonical governed issue body used by conformance."
        )
        policy_ok = subprocess.CompletedProcess([], 0, "", "")
        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_body)
            output = io.StringIO()
            errors = io.StringIO()
            with (
                mock.patch.object(promotion, "GitHubClient", FakeClient),
                mock.patch.object(
                    promotion,
                    "validate_canonical_body",
                    return_value=canonical_body,
                ),
                mock.patch.object(
                    promotion.subprocess,
                    "run",
                    return_value=policy_ok,
                ),
                mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}, clear=False),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(errors),
            ):
                rc = promotion.main(
                    [
                        "--repository",
                        "wiigelec/repo-spec",
                        "--intake-issue",
                        "12",
                        "--governing-issue",
                        "34",
                        "--authority-issue",
                        "56",
                        "--governed-operation",
                        "operation-34",
                        "--promotion-form",
                        "successor",
                        "--canonical-body-file",
                        str(body_path),
                        "--apply",
                    ]
                )
        self.assertEqual(len(FakeClient.instances), 1)
        result = json.loads(output.getvalue()) if output.getvalue().strip() else None
        return rc, FakeClient.instances[0], result, errors.getvalue()

    def test_bug_fix_apply_requires_authority_and_preserves_provenance_order(self):
        rc, client, result, _ = self.invoke_apply()
        self.assertEqual(rc, 0)
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )
        provenance = client.operations[0][2]
        self.assertIn("ordinary unformatted intake body", provenance)
        self.assertIn("`bug-fix`", provenance)
        self.assertIn("Captured before body replacement/restructuring: yes", provenance)
        self.assertEqual(result["plan"]["repository_authorization"]["authority_path"], "audit")
        self.assertFalse(result["plan"]["mutation_authorized_by_routing"])

    def test_feature_request_requires_complete_feature_authority_before_mutation(self):
        rc, client, result, _ = self.invoke_apply(classification="feature-request")
        self.assertEqual(rc, 0)
        self.assertEqual(
            result["plan"]["repository_authorization"]["authority_path"],
            "feature-development",
        )
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )

        rc2, client2, result2, error2 = self.invoke_apply(
            classification="feature-request",
            feature_complete=False,
        )
        self.assertEqual(rc2, 1)
        self.assertIsNone(result2)
        self.assertIn("accepted authority path", error2)
        self.assertEqual(client2.operations, [])

    def test_routing_label_or_manual_dispatch_cannot_substitute_for_authority(self):
        rc, client, result, error = self.invoke_apply(authority_governed=False)
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("already be in governed-work state", error)
        self.assertEqual(client.operations, [])

    def test_hosted_canonical_result_is_consumable_only_through_product_validator(self):
        rc, _, result, _ = self.invoke_apply()
        self.assertEqual(rc, 0)
        helper_evidence = result["canonical_state_evidence"]
        observation = CanonicalGovernedStateObservation(
            governing_issue=helper_evidence["governing_issue"],
            governed_operation=helper_evidence["governed_operation"],
            observed_revision=helper_evidence["observed_revision"],
        )
        evidence = validate_canonical_governed_state(
            observation=observation,
            validator=HostedCanonicalValidator(helper_evidence),
        )
        self.assertTrue(evidence.is_fresh)
        self.assertEqual(
            evidence.validation_artifact_id,
            helper_evidence["validation_artifact_id"],
        )

    def test_hosted_workflow_is_manual_managed_and_authority_gated(self):
        source = SOURCE_WORKFLOW.read_text()
        installed = INSTALLED_WORKFLOW.read_text()
        self.assertEqual(source, installed)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("authority_issue:", source)
        self.assertIn("--authority-issue", source)
        self.assertIn("issues: write", source)
        self.assertNotIn("issues:\n    types:", source)

        helper = HELPER_PATH.read_text()
        authority_pos = helper.index(
            "authorization = require_repository_governance_authorization"
        )
        comment_pos = helper.index("client.add_comment(args.intake_issue")
        body_pos = helper.index("client.update_issue_body(args.governing_issue")
        label_pos = helper.index("client.add_labels(args.governing_issue")
        self.assertLess(authority_pos, comment_pos)
        self.assertLess(comment_pos, body_pos)
        self.assertLess(body_pos, label_pos)


if __name__ == "__main__":
    unittest.main()
