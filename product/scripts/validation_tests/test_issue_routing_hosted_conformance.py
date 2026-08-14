from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import pathlib
import stat
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
        "## Implementation-plan workstreams/stages\nIRP-I2\nIRP-I3\nIRP-I4\nIRP-I5\n\n"
        "## Accepted default-branch base\n"
        "main at de7d75ffc8d08a40be4ca46cfbd9336c9fa0b4ec\n\n"
        "## In-scope behavior and paths\n"
        "- Exercise trusted promotion evidence producers through hosted conformance.\n\n"
        "## Explicit exclusions\n"
        "- No new product semantics or lifecycle authority.\n\n"
        "## Dependencies and predecessor evidence\n"
        "#424 and de7d75ffc8d08a40be4ca46cfbd9336c9fa0b4ec.\n"
        f"{extra_dependency_text}\n\n"
        "## Ordered patch plan\n1. Exercise bounded producer-backed conformance.\n\n"
        "## Validation plan\nRun repository field policy and trusted producer commands.\n\n"
        "## Acceptance criteria\n"
        "Caller-fabricated evidence fails; trusted producer-backed evidence succeeds.\n\n"
        "## Completion gate\nManual review and merge remain required.\n\n"
        "## Open decisions or authority conflicts\nNone.\n\n"
        "## Successor work explicitly not authorized\nUnrelated work.\n"
    )


class FakeClient:
    instances = []
    classification = "bug-fix"
    authority_governed = True

    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.operations = []
        self.issues = {
            12: {
                "number": 12,
                "body": "ordinary unformatted intake body",
                "labels": [{"name": self.__class__.classification}],
            },
            34: {
                "number": 34,
                "body": "pre-promotion successor placeholder",
                "labels": [],
            },
            56: {
                "number": 56,
                "body": canonical_governed_body(),
                "labels": (
                    [{"name": "governed-work"}]
                    if self.__class__.authority_governed
                    else []
                ),
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


class ProducerEnvironment:
    def __init__(
        self,
        *,
        classification: str,
        governing_issue: int,
        operation: str,
        canonical_body_path: pathlib.Path,
        canonical_valid: bool = True,
        authorization_valid: bool = True,
    ):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)
        revision = hashlib.sha256(canonical_body_path.read_bytes()).hexdigest()

        canonical_payload = {
            "governing_issue": f"#{governing_issue}",
            "governed_operation": operation,
            "validated_revision": revision,
            "validation_artifact_id": f"field-policy:sha256:{revision}",
            "producer_id": "repository-canonical-validator",
            "canonical_structure_valid": canonical_valid,
        }
        canonical_cmd = self.dir / "canonical-governed-state-validator"
        canonical_cmd.write_text(
            "#!/usr/bin/env python3\n"
            "import json,sys\n"
            "request=json.load(sys.stdin)\n"
            "print(" + repr(json.dumps(canonical_payload)) + ")\n",
            encoding="utf-8",
        )
        canonical_cmd.chmod(canonical_cmd.stat().st_mode | stat.S_IXUSR)

        path = "audit" if classification == "bug-fix" else "feature-development"
        auth_payload = {
            "authority_issue": 56,
            "governing_issue": governing_issue if authorization_valid else 99,
            "governed_operation": operation,
            "routing_classification": classification,
            "authority_path": path,
            "lifecycle_artifact_id": (
                f"audit-run:accepted:56"
                if classification == "bug-fix"
                else "feature-development:approved:56"
            ),
            "producer_id": "repository-governance-authority",
        }
        auth_cmd = self.dir / "repository-governance-authorization-validator"
        auth_cmd.write_text(
            "#!/usr/bin/env python3\n"
            "import json,sys\n"
            "request=json.load(sys.stdin)\n"
            "print(" + repr(json.dumps(auth_payload)) + ")\n",
            encoding="utf-8",
        )
        auth_cmd.chmod(auth_cmd.stat().st_mode | stat.S_IXUSR)

    def __enter__(self):
        old = os.environ.get("PATH", "")
        self.patch = mock.patch.dict(
            os.environ,
            {"PATH": str(self.dir) + os.pathsep + old},
            clear=False,
        )
        self.patch.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.patch.stop()
        self.tmp.cleanup()


class HostedRoutingConformanceTests(unittest.TestCase):
    def setUp(self):
        FakeClient.instances.clear()
        FakeClient.classification = "bug-fix"
        FakeClient.authority_governed = True

    def invoke_apply(
        self,
        *,
        classification="bug-fix",
        promotion_form="successor",
        canonical_valid=True,
        authorization_valid=True,
        producer_paths=True,
    ):
        FakeClient.instances.clear()
        FakeClient.classification = classification
        governing_issue = 12 if promotion_form == "in-place" else 34
        operation = "operation-12" if promotion_form == "in-place" else "operation-34"

        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_governed_body())
            real_policy = subprocess_run = __import__("subprocess").run
            policy_result = real_policy(
                [str(POLICY), "--mode", "issue", "--body-file", str(body_path)],
                cwd=REPO_ROOT,
                text=True,
                stdout=__import__("subprocess").PIPE,
                stderr=__import__("subprocess").PIPE,
            )
            self.assertEqual(policy_result.returncode, 0, policy_result.stderr)

            env = ProducerEnvironment(
                classification=classification,
                governing_issue=governing_issue,
                operation=operation,
                canonical_body_path=body_path,
                canonical_valid=canonical_valid,
                authorization_valid=authorization_valid,
            )

            output = io.StringIO()
            errors = io.StringIO()
            context = env if producer_paths else contextlib.nullcontext()
            with (
                context,
                mock.patch.object(promotion, "GitHubClient", FakeClient),
                mock.patch.dict(os.environ, {"GITHUB_TOKEN": "test-token"}, clear=False),
                contextlib.redirect_stdout(output),
                contextlib.redirect_stderr(errors),
            ):
                rc = promotion.main(
                    [
                        "--repository", "wiigelec/repo-spec",
                        "--intake-issue", "12",
                        "--governing-issue", str(governing_issue),
                        "--authority-issue", "56",
                        "--governed-operation", operation,
                        "--promotion-form", promotion_form,
                        "--canonical-body-file", str(body_path),
                        "--apply",
                    ]
                )

            result = json.loads(output.getvalue()) if output.getvalue().strip() else None

        self.assertEqual(len(FakeClient.instances), 1)
        return rc, FakeClient.instances[0], result, errors.getvalue()

    def test_bug_fix_uses_trusted_producers_and_preserves_order(self):
        rc, client, result, _ = self.invoke_apply()
        self.assertEqual(rc, 0)
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )
        self.assertEqual(
            result["plan"]["repository_authorization"]["authority_path"],
            "audit",
        )
        self.assertEqual(
            result["plan"]["repository_authorization"]["producer_id"],
            "repository-governance-authority",
        )

    def test_feature_request_uses_trusted_feature_authority(self):
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

    def test_missing_trusted_producer_paths_fail_before_mutation(self):
        rc, client, result, error = self.invoke_apply(producer_paths=False)
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("producer is unavailable", error)
        self.assertEqual(client.operations, [])

    def test_wrong_authorization_target_fails_before_mutation(self):
        rc, client, result, error = self.invoke_apply(authorization_valid=False)
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("target governing issue", error)
        self.assertEqual(client.operations, [])

    def test_invalid_canonical_producer_result_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_governed_body())
            revision = hashlib.sha256(body_path.read_bytes()).hexdigest()
            observation = CanonicalGovernedStateObservation(
                governing_issue="#34",
                governed_operation="operation-34",
                observed_revision=revision,
            )
            with ProducerEnvironment(
                classification="bug-fix",
                governing_issue=34,
                operation="operation-34",
                canonical_body_path=body_path,
                canonical_valid=False,
            ):
                with self.assertRaisesRegex(ValueError, "validation failed"):
                    validate_canonical_governed_state(
                        observation=observation,
                        producer_id="repository-canonical-validator",
                    )

    def test_both_promotion_forms_remain_supported(self):
        for form in ("successor", "in-place"):
            with self.subTest(form=form):
                rc, client, result, _ = self.invoke_apply(promotion_form=form)
                self.assertEqual(rc, 0)
                self.assertEqual(result["plan"]["promotion_form"], form)
                self.assertEqual(
                    [operation[0] for operation in client.operations],
                    ["comment", "body", "labels"],
                )

    def test_workflow_remains_manual_and_producer_gated(self):
        source = SOURCE_WORKFLOW.read_text()
        installed = INSTALLED_WORKFLOW.read_text()
        self.assertEqual(source, installed)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("authority_issue:", source)
        helper = HELPER_PATH.read_text()
        self.assertIn("TRUSTED_REPOSITORY_AUTHORIZATION_PRODUCERS", helper)
        self.assertNotIn("parse_repository_governance_authorization", helper)


if __name__ == "__main__":
    unittest.main()
