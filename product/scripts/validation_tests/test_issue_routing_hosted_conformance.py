from __future__ import annotations

import contextlib
import hashlib
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
POLICY = REPO_ROOT / "repo/scripts/github-field-policy"
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

ALL_PRODUCT_SPECS = (
    "product.issue-routing-governance",
    "product.issue-routing-classification",
    "product.governed-work-provenance",
    "product.issue-authority-routing",
    "product.governed-work-promotion",
    "product.issue-routing-platform-validation",
    "product.issue-intake-governance-routing",
)


def canonical_governed_body(extra_dependency_text: str = "") -> str:
    specs = ", ".join(ALL_PRODUCT_SPECS)
    return (
        "## Change type\nProduct-artifact implementation\n\n"
        "## Problem statement\nA bounded governed operation for hosted conformance.\n\n"
        "## Intended outcome\nExercise accepted hosted routing boundaries.\n\n"
        "## Governing specifications\n"
        "repo.governing-issue, repo.development-workflow, repo.validation, "
        "repo.repository-structure, repo.artifact-taxonomy, "
        "repo.product-correspondence, repo.implementation-plan, "
        f"{specs}, and the accepted "
        "`repo/docs/plans/REPOSITORY-IMPLEMENTATION-PLAN.md` composite.\n\n"
        "## Implementation-plan workstreams/stages\n"
        "IRP-I2\nIRP-I3\nIRP-I4\nIRP-I5\n\n"
        "## Accepted default-branch base\n"
        "main at b7606ca6d058c47b10f00913e678707c22c378ee\n\n"
        "## In-scope behavior and paths\n"
        "- Exercise `product/scripts/issue_intake_governance_routing/promotion.py` "
        "through the hosted conformance boundary.\n\n"
        "## Explicit exclusions\n"
        "- No new product semantics or lifecycle authority.\n\n"
        "## Dependencies and predecessor evidence\n"
        "#420 and b7606ca6d058c47b10f00913e678707c22c378ee.\n"
        f"{extra_dependency_text}\n\n"
        "## Ordered patch plan\n"
        "1. Exercise the bounded hosted conformance path.\n\n"
        "## Validation plan\n"
        "Run the accepted repository field policy and product validators.\n\n"
        "## Acceptance criteria\n"
        "The bounded hosted path fails closed on invalid evidence and succeeds "
        "on accepted evidence.\n\n"
        "## Completion gate\n"
        "Manual review and merge remain required.\n\n"
        "## Open decisions or authority conflicts\n"
        "None identified for this bounded conformance fixture.\n\n"
        "## Successor work explicitly not authorized\n"
        "Any unrelated product, repository, or release work.\n"
    )


def authority_record(
    *,
    classification: str,
    governing_issue: int,
    operation: str,
    complete: bool = True,
) -> dict:
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
        if not complete:
            lifecycle.pop("explicit-functional-set-approval")
    return {
        "schema_version": "1",
        "routing_classification": classification,
        "authority_path": path,
        "governed_operation": operation,
        "governing_issue": (
            f"https://github.com/wiigelec/repo-spec/issues/{governing_issue}"
        ),
        "lifecycle_evidence": lifecycle,
    }


def authority_body(
    *,
    classification: str,
    governing_issue: int,
    operation: str,
    complete: bool = True,
    include_record: bool = True,
    unrelated_keywords: str = "",
) -> str:
    record_text = ""
    if include_record:
        record_text = (
            "```repo-governance-authorization\n"
            + json.dumps(
                authority_record(
                    classification=classification,
                    governing_issue=governing_issue,
                    operation=operation,
                    complete=complete,
                ),
                sort_keys=True,
            )
            + "\n```"
        )
    extra = "\n".join(
        part for part in (record_text, unrelated_keywords) if part
    )
    return canonical_governed_body(extra)


class FakeClient:
    instances = []
    classification = "bug-fix"
    governing_issue = 34
    operation = "operation-34"
    authority_governed = True
    authority_complete = True
    include_authority_record = True
    unrelated_keywords = ""

    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.token = token
        self.operations = []
        classification = self.__class__.classification
        governing_issue = self.__class__.governing_issue
        operation = self.__class__.operation
        authority_labels = (
            [{"name": "governed-work"}]
            if self.__class__.authority_governed
            else []
        )
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
                "body": authority_body(
                    classification=classification,
                    governing_issue=governing_issue,
                    operation=operation,
                    complete=self.__class__.authority_complete,
                    include_record=self.__class__.include_authority_record,
                    unrelated_keywords=self.__class__.unrelated_keywords,
                ),
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


class FieldPolicyCanonicalValidator:
    def __init__(self, body_path: pathlib.Path, operation: str):
        self.body_path = body_path
        self.operation = operation

    def validate(self, observation):
        result = subprocess.run(
            [
                str(POLICY),
                "--mode",
                "issue",
                "--body-file",
                str(self.body_path),
            ],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        valid = result.returncode == 0
        revision = hashlib.sha256(self.body_path.read_bytes()).hexdigest()
        return CanonicalGovernedStateValidationResult(
            governing_issue=observation.governing_issue,
            governed_operation=self.operation,
            validated_revision=revision,
            validation_artifact_id=(
                f"field-policy:{self.body_path.name}:sha256:{revision}"
            ),
            validator_id="repo.github-field-policy",
            canonical_structure_valid=valid,
        )


class HostedRoutingConformanceTests(unittest.TestCase):
    def setUp(self):
        FakeClient.instances.clear()
        FakeClient.classification = "bug-fix"
        FakeClient.governing_issue = 34
        FakeClient.operation = "operation-34"
        FakeClient.authority_governed = True
        FakeClient.authority_complete = True
        FakeClient.include_authority_record = True
        FakeClient.unrelated_keywords = ""

    def invoke_apply(
        self,
        *,
        classification="bug-fix",
        promotion_form="successor",
        authority_governed=True,
        authority_complete=True,
        include_authority_record=True,
        unrelated_keywords="",
        authority_governing_issue=None,
        authority_operation=None,
    ):
        FakeClient.instances.clear()
        governing_issue = 12 if promotion_form == "in-place" else 34
        operation = "operation-12" if promotion_form == "in-place" else "operation-34"
        FakeClient.classification = classification
        FakeClient.governing_issue = (
            governing_issue
            if authority_governing_issue is None
            else authority_governing_issue
        )
        FakeClient.operation = (
            operation if authority_operation is None else authority_operation
        )
        FakeClient.authority_governed = authority_governed
        FakeClient.authority_complete = authority_complete
        FakeClient.include_authority_record = include_authority_record
        FakeClient.unrelated_keywords = unrelated_keywords

        canonical_body = canonical_governed_body()
        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_body)
            # Prove the exact canonical fixture passes the actual repository policy.
            policy_result = subprocess.run(
                [
                    str(POLICY),
                    "--mode",
                    "issue",
                    "--body-file",
                    str(body_path),
                ],
                cwd=REPO_ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)

            output = io.StringIO()
            errors = io.StringIO()
            with (
                mock.patch.object(promotion, "GitHubClient", FakeClient),
                mock.patch.dict(
                    os.environ,
                    {"GITHUB_TOKEN": "test-token"},
                    clear=False,
                ),
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
                        str(governing_issue),
                        "--authority-issue",
                        "56",
                        "--governed-operation",
                        operation,
                        "--promotion-form",
                        promotion_form,
                        "--canonical-body-file",
                        str(body_path),
                        "--apply",
                    ]
                )
            result = (
                json.loads(output.getvalue())
                if output.getvalue().strip()
                else None
            )
            canonical_copy = body_path.read_text()

        self.assertEqual(len(FakeClient.instances), 1)
        return (
            rc,
            FakeClient.instances[0],
            result,
            errors.getvalue(),
            canonical_copy,
        )

    def test_bug_fix_apply_uses_real_policy_and_structured_audit_authority(self):
        rc, client, result, _, _ = self.invoke_apply()
        self.assertEqual(rc, 0)
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )
        provenance = client.operations[0][2]
        self.assertIn("ordinary unformatted intake body", provenance)
        self.assertIn("`bug-fix`", provenance)
        self.assertEqual(
            result["plan"]["repository_authorization"]["authority_path"],
            "audit",
        )
        self.assertEqual(
            result["plan"]["repository_authorization"]["governing_issue"],
            34,
        )
        self.assertFalse(result["plan"]["mutation_authorized_by_routing"])

    def test_feature_request_requires_complete_structured_authority(self):
        rc, client, result, _, _ = self.invoke_apply(
            classification="feature-request"
        )
        self.assertEqual(rc, 0)
        self.assertEqual(
            result["plan"]["repository_authorization"]["authority_path"],
            "feature-development",
        )
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )

        rc2, client2, result2, error2, _ = self.invoke_apply(
            classification="feature-request",
            authority_complete=False,
            unrelated_keywords=(
                "whiteboard analysis candidate-functional-set "
                "explicit-functional-set-approval"
            ),
        )
        self.assertEqual(rc2, 1)
        self.assertIsNone(result2)
        self.assertIn("complete structured feature-development evidence", error2)
        self.assertEqual(client2.operations, [])

    def test_keywords_without_structured_record_cannot_authorize(self):
        rc, client, result, error, _ = self.invoke_apply(
            include_authority_record=False,
            unrelated_keywords=(
                "audit whiteboard analysis candidate-functional-set "
                "explicit-functional-set-approval"
            ),
        )
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("exactly one structured", error)
        self.assertEqual(client.operations, [])

    def test_authority_must_match_target_and_operation(self):
        rc, client, result, error, _ = self.invoke_apply(
            authority_governing_issue=99
        )
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("target governing issue", error)
        self.assertEqual(client.operations, [])

        rc2, client2, result2, error2, _ = self.invoke_apply(
            authority_operation="operation-99"
        )
        self.assertEqual(rc2, 1)
        self.assertIsNone(result2)
        self.assertIn("governed operation", error2)
        self.assertEqual(client2.operations, [])

    def test_both_promotion_forms_preserve_ordering(self):
        for promotion_form in ("successor", "in-place"):
            with self.subTest(promotion_form=promotion_form):
                rc, client, result, _, _ = self.invoke_apply(
                    promotion_form=promotion_form
                )
                self.assertEqual(rc, 0)
                self.assertEqual(
                    [operation[0] for operation in client.operations],
                    ["comment", "body", "labels"],
                )
                self.assertEqual(
                    result["plan"]["promotion_form"],
                    promotion_form,
                )

    def test_hosted_canonical_evidence_requires_real_validator_success(self):
        rc, _, result, _, canonical_body = self.invoke_apply()
        self.assertEqual(rc, 0)
        helper_evidence = result["canonical_state_evidence"]

        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_body)
            observation = CanonicalGovernedStateObservation(
                governing_issue=helper_evidence["governing_issue"],
                governed_operation=helper_evidence["governed_operation"],
                observed_revision=helper_evidence["observed_revision"],
            )
            evidence = validate_canonical_governed_state(
                observation=observation,
                validator=FieldPolicyCanonicalValidator(
                    body_path,
                    helper_evidence["governed_operation"],
                ),
            )
            self.assertTrue(evidence.is_fresh)
            self.assertEqual(evidence.validator_id, "repo.github-field-policy")

            invalid_path = pathlib.Path(tmp) / "invalid.md"
            invalid_path.write_text("not a canonical governed issue")
            with self.assertRaisesRegex(ValueError, "validation failed"):
                validate_canonical_governed_state(
                    observation=CanonicalGovernedStateObservation(
                        governing_issue=helper_evidence["governing_issue"],
                        governed_operation=helper_evidence["governed_operation"],
                        observed_revision=hashlib.sha256(
                            invalid_path.read_bytes()
                        ).hexdigest(),
                    ),
                    validator=FieldPolicyCanonicalValidator(
                        invalid_path,
                        helper_evidence["governed_operation"],
                    ),
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
        self.assertIn("parse_repository_governance_authorization", helper)
        self.assertNotIn('required_markers = ("audit",)', helper)
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
