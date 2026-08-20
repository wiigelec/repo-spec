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

REPO_ROOT = pathlib.Path(__file__).resolve().parents[4]
HELPER_PATH = REPO_ROOT / "repo/src/github_issue_promotion.py"
POLICY = REPO_ROOT / "repo/validation/github/github-field-policy"
CANONICAL_PRODUCER = REPO_ROOT / "repo/validation/github/canonical-governed-state-validator"
AUTHORIZATION_PRODUCER = (
    REPO_ROOT / "repo/validation/github/repository-governance-authorization-validator"
)
SOURCE_WORKFLOW = REPO_ROOT / "repo/profiles/github/workflows/governed-work-promotion.yml"
INSTALLED_WORKFLOW = REPO_ROOT / ".github/workflows/governed-work-promotion.yml"

spec = importlib.util.spec_from_file_location(
    "repository_hosted_conformance_promotion",
    HELPER_PATH,
)
assert spec and spec.loader
promotion = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = promotion
spec.loader.exec_module(promotion)

ALL_REPO_SPECS = (
    "repo.issue-routing-governance",
    "repo.issue-routing-classification",
    "repo.governed-work-provenance",
    "repo.issue-authority-routing",
    "repo.governed-work-promotion",
    "repo.issue-routing-platform-validation",
    "repo.issue-intake-governance-routing",
)


def canonical_governed_body() -> str:
    specs = ", ".join(ALL_REPO_SPECS)
    return (
        "## Change type\nMaintenance\n\n"
        "## Problem statement\nA bounded governed operation for hosted conformance.\n\n"
        "## Intended outcome\nExercise accepted hosted routing boundaries.\n\n"
        "## Governing specifications\n"
        "repo.governing-issue, repo.development-workflow, repo.validation, "
        "repo.repository-structure, repo.artifact-taxonomy, "
        "repo.implementation-plan, "
        f"{specs}, and the accepted "
        "`repo/docs/plans/REPOSITORY-IMPLEMENTATION-PLAN.md` composite.\n\n"
        "## Implementation-plan workstreams/stages\nIRP-I2\nIRP-I3\nIRP-I4\nIRP-I5\n\n"
        "## Accepted default-branch base\n"
        "main at 00030fcc48f2b7fefefacc42a4a4dd9cdba9cea4\n\n"
        "## In-scope behavior and paths\n"
        "- Exercise managed producer-backed promotion conformance.\n\n"
        "## Explicit exclusions\n"
        "- No new product semantics or lifecycle authority.\n\n"
        "## Dependencies and predecessor evidence\n"
        "Issue #426 governs this bounded correction after merged PR #425. "
        "The accepted baseline is "
        "`main@00030fcc48f2b7fefefacc42a4a4dd9cdba9cea4`, and the fixture "
        "exists only to exercise the accepted hosted routing boundaries.\n\n"
        "## Ordered patch plan\n1. Exercise bounded producer-backed conformance.\n\n"
        "## Validation plan\nRun repository field policy and managed producers.\n\n"
        "## Acceptance criteria\n"
        "Substituted producer artifacts fail; managed producer-backed evidence succeeds.\n\n"
        "## Completion gate\nManual review and merge remain required.\n\n"
        "## Open decisions or authority conflicts\nNone.\n\n"
        "## Successor work explicitly not authorized\nUnrelated work.\n"
    )


class FakeClient:
    instances = []
    classification = "bug-fix"

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
                "labels": [{"name": "governed-work"}],
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


class ManagedProducerEnvironment:
    def __init__(
        self,
        *,
        classification: str,
        governing_issue: int,
        operation: str,
        lifecycle_governing_issue: int | None = None,
    ):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)
        path = "audit" if classification == "bug-fix" else "feature-development"
        lifecycle = {
            "authority_issue": 56,
            "governing_issue": (
                governing_issue
                if lifecycle_governing_issue is None
                else lifecycle_governing_issue
            ),
            "governed_operation": operation,
            "routing_classification": classification,
            "authority_path": path,
            "lifecycle_artifact_id": (
                "audit-run:accepted:56"
                if classification == "bug-fix"
                else "feature-development:approved:56"
            ),
            "status": "accepted",
        }
        self.lifecycle = self.dir / "lifecycle-authority.json"
        self.lifecycle.write_text(json.dumps(lifecycle), encoding="utf-8")

    def __enter__(self):
        self.patch = mock.patch.dict(
            os.environ,
            {
                "REPO_SPEC_CANONICAL_VALIDATOR": str(CANONICAL_PRODUCER),
                "REPO_SPEC_AUTHORIZATION_VALIDATOR": str(AUTHORIZATION_PRODUCER),
                "REPO_SPEC_LIFECYCLE_AUTHORITY_ARTIFACT": str(self.lifecycle),
            },
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

    def invoke_apply(
        self,
        *,
        classification="bug-fix",
        promotion_form="successor",
        lifecycle_governing_issue=None,
        extra_env=None,
    ):
        FakeClient.instances.clear()
        FakeClient.classification = classification
        governing_issue = 12 if promotion_form == "in-place" else 34
        operation = "operation-12" if promotion_form == "in-place" else "operation-34"

        with tempfile.TemporaryDirectory() as tmp:
            body_path = pathlib.Path(tmp) / "canonical.md"
            body_path.write_text(canonical_governed_body(), encoding="utf-8")
            env = ManagedProducerEnvironment(
                classification=classification,
                governing_issue=governing_issue,
                operation=operation,
                lifecycle_governing_issue=lifecycle_governing_issue,
            )

            output = io.StringIO()
            errors = io.StringIO()
            patch_env = (
                mock.patch.dict(os.environ, extra_env, clear=False)
                if extra_env
                else contextlib.nullcontext()
            )
            with (
                env,
                patch_env,
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

    def test_bug_fix_uses_managed_producers_before_mutation(self):
        rc, client, result, error = self.invoke_apply()
        self.assertEqual(rc, 0, error)
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )
        evidence = result["canonical_state_evidence"]
        self.assertEqual(evidence["producer_id"], "repository-canonical-validator")
        self.assertEqual(
            result["plan"]["repository_authorization"]["producer_id"],
            "repository-governance-authority",
        )
        self.assertEqual(
            result["plan"]["repository_authorization"]["authority_path"],
            "audit",
        )

    def test_feature_request_uses_managed_feature_authority(self):
        rc, client, result, error = self.invoke_apply(classification="feature-request")
        self.assertEqual(rc, 0, error)
        self.assertEqual(
            result["plan"]["repository_authorization"]["authority_path"],
            "feature-development",
        )
        self.assertEqual(
            [operation[0] for operation in client.operations],
            ["comment", "body", "labels"],
        )

    def test_wrong_lifecycle_target_fails_before_mutation(self):
        rc, client, result, error = self.invoke_apply(lifecycle_governing_issue=99)
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("governing issue mismatch", error)
        self.assertEqual(client.operations, [])

    def test_substituted_canonical_producer_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = pathlib.Path(tmp) / "canonical-governed-state-validator"
            fake.write_text(
                "#!/usr/bin/env python3\nprint('{}')\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            rc, client, result, error = self.invoke_apply(
                extra_env={"REPO_SPEC_CANONICAL_VALIDATOR": str(fake)}
            )
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("artifact identity mismatch", error)
        self.assertEqual(client.operations, [])

    def test_substituted_authorization_producer_fails_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = pathlib.Path(tmp) / "repository-governance-authorization-validator"
            fake.write_text(
                "#!/usr/bin/env python3\nprint('{}')\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            rc, client, result, error = self.invoke_apply(
                extra_env={"REPO_SPEC_AUTHORIZATION_VALIDATOR": str(fake)}
            )
        self.assertEqual(rc, 1)
        self.assertIsNone(result)
        self.assertIn("artifact identity mismatch", error)
        self.assertEqual(client.operations, [])

    def test_both_promotion_forms_remain_supported(self):
        for form in ("successor", "in-place"):
            with self.subTest(form=form):
                rc, client, result, error = self.invoke_apply(promotion_form=form)
                self.assertEqual(rc, 0, error)
                self.assertEqual(result["plan"]["promotion_form"], form)
                self.assertEqual(
                    [operation[0] for operation in client.operations],
                    ["comment", "body", "labels"],
                )

    def test_workflow_wires_managed_producers_and_lifecycle_artifact(self):
        source = SOURCE_WORKFLOW.read_text()
        installed = INSTALLED_WORKFLOW.read_text()
        self.assertEqual(source, installed)
        self.assertIn("workflow_dispatch:", source)
        self.assertIn("lifecycle_authority_base64:", source)
        self.assertIn("REPO_SPEC_CANONICAL_VALIDATOR=", source)
        self.assertIn("REPO_SPEC_AUTHORIZATION_VALIDATOR=", source)
        self.assertIn("REPO_SPEC_LIFECYCLE_AUTHORITY_ARTIFACT=", source)
        helper = HELPER_PATH.read_text()
        self.assertIn("validate_canonical_governed_state(", helper)
        self.assertIn("CanonicalGovernedStateObservation(", helper)


def run_issue_routing_hosted_conformance_tests(repo_root: pathlib.Path) -> None:
    if repo_root.resolve() != REPO_ROOT.resolve():
        raise AssertionError(
            f"hosted routing test root mismatch: expected {REPO_ROOT}, observed {repo_root}"
        )
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(HostedRoutingConformanceTests)
    result = unittest.TextTestRunner(verbosity=1).run(suite)
    if not result.wasSuccessful():
        raise AssertionError("repository hosted routing conformance tests failed")


if __name__ == "__main__":
    unittest.main()
