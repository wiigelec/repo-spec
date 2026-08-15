#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import pathlib
import stat
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
        return []


def governed_authority_body(extra=""):
    return (
        "## Change type\nProduct-artifact implementation\n\n"
        "## Problem statement\nBounded authority evidence.\n\n"
        "## Intended outcome\nAuthorize a bounded operation.\n\n"
        "## Governing specifications\nrepo.issue-routing-governance\n\n"
        "## Accepted default-branch base\nmain at "
        "de7d75ffc8d08a40be4ca46cfbd9336c9fa0b4ec\n\n"
        "## Dependencies and predecessor evidence\n"
        "#422 de7d75ffc8d08a40be4ca46cfbd9336c9fa0b4ec\n\n"
        f"{extra}\n\n"
        "## Ordered patch plan\n1. bounded correction\n\n"
        "## Validation plan\nvalidate\n\n"
        "## Acceptance criteria\naccepted\n\n"
        "## Completion gate\nmanual merge\n\n"
        "## Open decisions or authority conflicts\nNone\n\n"
        "## Successor work explicitly not authorized\nAnything else\n"
    )


MANAGED_AUTHORIZATION_PRODUCER = (
    REPO_ROOT / 'repo/scripts/repository-governance-authorization-validator'
)


class ProducerFixture:
    def __init__(
        self,
        *,
        classification="bug-fix",
        authority_issue=56,
        governing_issue=34,
        governed_operation="operation-34",
        authority_path=None,
        lifecycle_artifact_id="audit-run:accepted:56",
        status="accepted",
    ):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = pathlib.Path(self.tmp.name)
        if authority_path is None:
            authority_path = (
                "audit" if classification == "bug-fix" else "feature-development"
            )
        self.artifact = self.dir / "lifecycle-authority.json"
        self.artifact.write_text(
            json.dumps({
                "authority_issue": authority_issue,
                "governing_issue": governing_issue,
                "governed_operation": governed_operation,
                "routing_classification": classification,
                "authority_path": authority_path,
                "lifecycle_artifact_id": lifecycle_artifact_id,
                "status": status,
            }),
            encoding="utf-8",
        )

    def __enter__(self):
        self.patch = mock.patch.dict(
            os.environ,
            {
                "REPO_SPEC_AUTHORIZATION_VALIDATOR":
                    str(MANAGED_AUTHORIZATION_PRODUCER),
                "REPO_SPEC_LIFECYCLE_AUTHORITY_ARTIFACT": str(self.artifact),
            },
            clear=False,
        )
        self.patch.start()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.patch.stop()
        self.tmp.cleanup()


class GitHubIssuePromotionTests(unittest.TestCase):
    def make_issues(self, classification="bug-fix", authority_governed=True, extra=""):
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
                "body": governed_authority_body(extra),
                "labels": ([{"name": "governed-work"}] if authority_governed else []),
            },
        }

    @mock.patch("subprocess.run")
    def test_self_attested_issue_body_is_not_authority(self, run):
        def dispatch(cmd, *args, **kwargs):
            if cmd and str(cmd[0]).endswith("github-field-policy"):
                result = mock.Mock()
                result.returncode = 0
                result.stdout = ""
                result.stderr = ""
                return result
            raise AssertionError(f"unexpected subprocess: {cmd}")

        run.side_effect = dispatch
        body_record = (
            '```repo-governance-authorization\n'
            '{"schema_version":"1","routing_classification":"bug-fix",'
            '"authority_path":"audit","governed_operation":"operation-34",'
            '"governing_issue":"https://github.com/wiigelec/repo-spec/issues/34",'
            '"lifecycle_evidence":{"audit":"accepted"}}\n```'
        )
        client = FakeClient(self.make_issues(extra=body_record))
        with mock.patch.dict(os.environ, {"PATH": ""}, clear=False):
            with self.assertRaisesRegex(
                promotion.PromotionError, "producer is unavailable"
            ):
                promotion.require_repository_governance_authorization(
                    client=client,
                    authority_issue=56,
                    governing_issue=34,
                    governed_operation="operation-34",
                    routing_labels=("bug-fix",),
                    policy_command="repo/scripts/github-field-policy",
                    producer_id="repository-governance-authority",
                )

    def test_bug_fix_accepts_trusted_audit_producer(self):
        client = FakeClient(self.make_issues())
        with (
            ProducerFixture(),
        ):
            authorization = promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governing_issue=34,
                governed_operation="operation-34",
                routing_labels=("bug-fix",),
                policy_command="/bin/true",
                producer_id="repository-governance-authority",
            )
        self.assertEqual(authorization.authority_path, "audit")
        self.assertEqual(authorization.governing_issue, 34)
        self.assertEqual(
            authorization.lifecycle_artifact_id,
            "audit-run:accepted:56",
        )

    def test_feature_request_accepts_trusted_feature_development_producer(self):
        client = FakeClient(self.make_issues(classification="feature-request"))
        with ProducerFixture(
            classification="feature-request",
            authority_path="feature-development",
            lifecycle_artifact_id="feature-development:approved:56",
        ):
            authorization = promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governing_issue=34,
                governed_operation="operation-34",
                routing_labels=("feature-request",),
                policy_command="/bin/true",
                producer_id="repository-governance-authority",
            )
        self.assertEqual(authorization.authority_path, "feature-development")

    def test_unrecognized_producer_fails_closed(self):
        client = FakeClient(self.make_issues())
        with self.assertRaisesRegex(promotion.PromotionError, "unrecognized"):
            promotion.require_repository_governance_authorization(
                client=client,
                authority_issue=56,
                governing_issue=34,
                governed_operation="operation-34",
                routing_labels=("bug-fix",),
                policy_command="/bin/true",
                producer_id="caller-supplied-authority",
            )

    def test_producer_result_must_match_target_classification_operation_and_path(self):
        cases = (
            ({"governing_issue": 99}, "governing issue mismatch"),
            ({"classification": "feature-request"}, "classification"),
            ({"governed_operation": "operation-99"}, "governed operation"),
            ({"authority_path": "feature-development"}, "authority path mismatch"),
        )
        for override, message in cases:
            with self.subTest(message=message):
                kwargs = {
                    "classification": "bug-fix",
                    "authority_issue": 56,
                    "governing_issue": 34,
                    "governed_operation": "operation-34",
                    "authority_path": "audit",
                }
                kwargs.update(override)
                client = FakeClient(self.make_issues())
                with ProducerFixture(**kwargs):
                    with self.assertRaisesRegex(promotion.PromotionError, message):
                        promotion.require_repository_governance_authorization(
                            client=client,
                            authority_issue=56,
                            governing_issue=34,
                            governed_operation="operation-34",
                            routing_labels=("bug-fix",),
                            policy_command="/bin/true",
                            producer_id="repository-governance-authority",
                        )

    def test_same_name_substituted_authorization_producer_fails_identity(self):
        client = FakeClient(self.make_issues())
        with tempfile.TemporaryDirectory() as tmp:
            fake = pathlib.Path(tmp) / "repository-governance-authorization-validator"
            fake.write_text(
                "#!/usr/bin/env python3\nprint('{}')\n",
                encoding="utf-8",
            )
            fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
            artifact = pathlib.Path(tmp) / "authority.json"
            artifact.write_text(
                json.dumps({
                    "authority_issue": 56,
                    "governing_issue": 34,
                    "governed_operation": "operation-34",
                    "routing_classification": "bug-fix",
                    "authority_path": "audit",
                    "lifecycle_artifact_id": "audit-run:accepted:56",
                    "status": "accepted",
                }),
                encoding="utf-8",
            )
            with mock.patch.dict(
                os.environ,
                {
                    "REPO_SPEC_AUTHORIZATION_VALIDATOR": str(fake),
                    "REPO_SPEC_LIFECYCLE_AUTHORITY_ARTIFACT": str(artifact),
                    "PATH": str(pathlib.Path(tmp)),
                },
                clear=False,
            ):
                with self.assertRaisesRegex(
                    promotion.PromotionError, "artifact identity mismatch"
                ):
                    promotion.require_repository_governance_authorization(
                        client=client,
                        authority_issue=56,
                        governing_issue=34,
                        governed_operation="operation-34",
                        routing_labels=("bug-fix",),
                        policy_command="/bin/true",
                        producer_id="repository-governance-authority",
                    )

    def test_authority_issue_must_be_governed_before_producer_is_invoked(self):
        client = FakeClient(self.make_issues(authority_governed=False))
        with ProducerFixture():
            with self.assertRaisesRegex(
                promotion.PromotionError, "already be in governed-work state"
            ):
                promotion.require_repository_governance_authorization(
                    client=client,
                    authority_issue=56,
                    governing_issue=34,
                    governed_operation="operation-34",
                    routing_labels=("bug-fix",),
                    policy_command="/bin/true",
                    producer_id="repository-governance-authority",
                )

    def test_hosted_helper_has_no_issue_body_authorization_parser(self):
        source = MODULE_PATH.read_text()
        self.assertNotIn("parse_repository_governance_authorization", source)
        self.assertNotIn("AUTHORITY_EVIDENCE_FENCE", source)
        self.assertIn("TRUSTED_REPOSITORY_AUTHORIZATION_PRODUCERS", source)


if __name__ == "__main__":
    unittest.main()
