#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from issue_intake_governance_routing import (
    CanonicalGovernedStateObservation,
    validate_canonical_governed_state,
)

ROUTING_LABELS = frozenset({"bug-fix", "feature-request"})
GOVERNED_WORK = "governed-work"


class PromotionError(RuntimeError):
    pass


@dataclass(frozen=True)
class PromotionEvidence:
    repository: str
    intake_issue: int
    governing_issue: int
    governed_operation: str
    promotion_form: str
    routing_labels: tuple[str, ...]
    canonical_body_sha256: str
    validation_artifact_id: str
    provenance_comment_created: bool
    body_installed: bool
    governed_work_added: bool
    mutation_authorized_by_routing: bool = False


class GitHubClient:
    def __init__(self, repository: str, token: str):
        self.repository = repository
        self.base = f"https://api.github.com/repos/{repository}"
        self.token = token

    def request(
        self,
        method: str,
        path: str,
        payload: dict[str, Any] | None = None,
    ) -> Any:
        data = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "repo-spec-governed-work-promotion",
        }
        if payload is not None:
            data = json.dumps(payload).encode()
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(
            f"{self.base}{path}",
            data=data,
            headers=headers,
            method=method,
        )
        try:
            with urllib.request.urlopen(request) as response:
                body = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise PromotionError(
                f"GitHub API {method} {path} failed: {exc.code}: {detail}"
            ) from exc
        if not body:
            return None
        return json.loads(body)

    def get_issue(self, issue_number: int) -> dict[str, Any]:
        return self.request("GET", f"/issues/{issue_number}")

    def add_comment(self, issue_number: int, body: str) -> dict[str, Any]:
        return self.request(
            "POST",
            f"/issues/{issue_number}/comments",
            {"body": body},
        )

    def update_issue_body(self, issue_number: int, body: str) -> dict[str, Any]:
        return self.request(
            "PATCH",
            f"/issues/{issue_number}",
            {"body": body},
        )

    def add_labels(self, issue_number: int, labels: list[str]) -> list[dict[str, Any]]:
        return self.request(
            "POST",
            f"/issues/{issue_number}/labels",
            {"labels": labels},
        )





TRUSTED_REPOSITORY_AUTHORIZATION_PRODUCERS = {
    "repository-governance-authority": {
        "command_env": "REPO_SPEC_AUTHORIZATION_VALIDATOR",
        "sha256": "d53e2cf3eb841e00b2ee3cef5b233a1e178615ef6fc45e2b14f3600ef85bee27",
    },
}


@dataclass(frozen=True)
class RepositoryGovernanceAuthorization:
    authority_issue: int
    governing_issue: int
    governed_operation: str
    routing_classification: str
    authority_path: str
    lifecycle_artifact_id: str
    producer_id: str


def require_repository_governance_authorization(
    *,
    client: GitHubClient,
    authority_issue: int,
    governing_issue: int,
    governed_operation: str,
    routing_labels: tuple[str, ...],
    policy_command: str,
    producer_id: str,
) -> RepositoryGovernanceAuthorization:
    if len(routing_labels) != 1:
        raise PromotionError(
            "repository authority requires exactly one routing classification"
        )
    classification = routing_labels[0]
    authority = client.get_issue(authority_issue)
    authority_labels = normalize_labels(authority)
    if GOVERNED_WORK not in authority_labels:
        raise PromotionError(
            "authority evidence issue must already be in governed-work state"
        )

    body = authority.get("body")
    if not isinstance(body, str) or not body.strip():
        raise PromotionError("authority evidence issue has no governed body")

    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False) as handle:
        handle.write(body)
        body_path = handle.name
    try:
        result = subprocess.run(
            [policy_command, "--mode", "issue", "--body-file", body_path],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    finally:
        try:
            os.unlink(body_path)
        except OSError:
            pass
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PromotionError(
            f"authority evidence issue failed governed field policy: {detail}"
        )

    descriptor = TRUSTED_REPOSITORY_AUTHORIZATION_PRODUCERS.get(producer_id)
    if descriptor is None:
        raise PromotionError(
            f"unrecognized repository-governance authorization producer: {producer_id}"
        )

    command_value = os.environ.get(descriptor["command_env"], "")
    if not command_value:
        raise PromotionError(
            f"trusted repository-governance authorization producer is unavailable: "
            f"{producer_id}"
        )
    command = Path(command_value).resolve()
    if not command.is_file():
        raise PromotionError(
            f"trusted repository-governance authorization producer is unavailable: "
            f"{producer_id}"
        )
    observed_command_sha256 = hashlib.sha256(command.read_bytes()).hexdigest()
    if observed_command_sha256 != descriptor["sha256"]:
        raise PromotionError(
            "repository-governance authorization producer artifact identity mismatch"
        )

    lifecycle_path = os.environ.get("REPO_SPEC_LIFECYCLE_AUTHORITY_ARTIFACT", "")
    if not lifecycle_path:
        raise PromotionError(
            "repository lifecycle authority artifact is unavailable"
        )
    try:
        lifecycle_authority = json.loads(Path(lifecycle_path).read_text())
    except (OSError, json.JSONDecodeError) as exc:
        raise PromotionError(
            "repository lifecycle authority artifact is invalid"
        ) from exc

    request = {
        "repository": client.repository,
        "authority_issue": authority_issue,
        "authority_issue_body_sha256": hashlib.sha256(body.encode()).hexdigest(),
        "governing_issue": governing_issue,
        "governed_operation": governed_operation,
        "routing_classification": classification,
        "producer_id": producer_id,
        "lifecycle_authority": lifecycle_authority,
    }
    producer = subprocess.run(
        [str(command)],
        input=json.dumps(request),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )
    if producer.returncode != 0:
        detail = producer.stderr.strip() or producer.stdout.strip()
        raise PromotionError(
            f"trusted repository-governance authorization producer failed: {detail}"
        )
    try:
        payload = json.loads(producer.stdout)
    except json.JSONDecodeError as exc:
        raise PromotionError(
            "trusted repository-governance authorization producer returned invalid JSON"
        ) from exc

    expected_fields = {
        "authority_issue",
        "governing_issue",
        "governed_operation",
        "routing_classification",
        "authority_path",
        "lifecycle_artifact_id",
        "producer_id",
    }
    if not isinstance(payload, dict) or set(payload) != expected_fields:
        raise PromotionError(
            "trusted repository-governance authorization producer returned invalid fields"
        )

    if payload["producer_id"] != producer_id:
        raise PromotionError(
            "repository-governance authorization does not match trusted producer"
        )
    if payload["authority_issue"] != authority_issue:
        raise PromotionError(
            "repository-governance authorization does not match authority issue"
        )
    if payload["governing_issue"] != governing_issue:
        raise PromotionError(
            "repository-governance authorization does not match target governing issue"
        )
    if payload["routing_classification"] != classification:
        raise PromotionError(
            "repository-governance authorization classification does not match intake"
        )
    if payload["governed_operation"] != governed_operation:
        raise PromotionError(
            "repository-governance authorization does not match governed operation"
        )

    if classification == "bug-fix":
        authority_path = "audit"
    elif classification == "feature-request":
        authority_path = "feature-development"
    else:
        raise PromotionError(
            "unsupported routing classification for repository-governance authorization"
        )
    if payload["authority_path"] != authority_path:
        raise PromotionError(
            "repository-governance authorization does not match accepted authority path"
        )
    lifecycle_artifact_id = payload["lifecycle_artifact_id"]
    if not isinstance(lifecycle_artifact_id, str) or not lifecycle_artifact_id.strip():
        raise PromotionError(
            "repository-governance authorization lacks lifecycle artifact identity"
        )

    return RepositoryGovernanceAuthorization(
        authority_issue=authority_issue,
        governing_issue=governing_issue,
        governed_operation=governed_operation,
        routing_classification=classification,
        authority_path=authority_path,
        lifecycle_artifact_id=lifecycle_artifact_id.strip(),
        producer_id=producer_id,
    )

def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Plan or apply provenance-preserving promotion of an existing GitHub "
            "issue into governed-work state."
        )
    )
    parser.add_argument("--repository", required=True)
    parser.add_argument("--intake-issue", type=int, required=True)
    parser.add_argument("--governing-issue", type=int, required=True)
    parser.add_argument("--authority-issue", type=int, required=True)
    parser.add_argument(
        "--authority-producer-id",
        default="repository-governance-authority",
    )
    parser.add_argument("--governed-operation", required=True)
    parser.add_argument(
        "--promotion-form",
        choices=("in-place", "successor"),
        required=True,
    )
    parser.add_argument("--canonical-body-file", type=Path, required=True)
    parser.add_argument(
        "--policy-command",
        default="repo/scripts/github-field-policy",
    )
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--apply", action="store_true")
    return parser.parse_args(argv)


def issue_ref(repository: str, issue_number: int) -> str:
    return f"https://github.com/{repository}/issues/{issue_number}"


def normalize_labels(issue: dict[str, Any]) -> tuple[str, ...]:
    labels = issue.get("labels", [])
    names = []
    for label in labels:
        if isinstance(label, dict):
            value = label.get("name")
        else:
            value = label
        if isinstance(value, str) and value.strip():
            names.append(value.strip())
    return tuple(sorted(set(names)))


def require_promotion_form(
    promotion_form: str,
    intake_issue: int,
    governing_issue: int,
) -> None:
    if promotion_form == "in-place" and intake_issue != governing_issue:
        raise PromotionError(
            "in-place promotion requires intake issue to equal governing issue"
        )
    if promotion_form == "successor" and intake_issue == governing_issue:
        raise PromotionError(
            "successor promotion requires a distinct existing governing issue"
        )


def validate_canonical_body(
    policy_command: str,
    canonical_body_file: Path,
) -> str:
    if not canonical_body_file.is_file():
        raise PromotionError(
            f"canonical body file does not exist: {canonical_body_file}"
        )
    body = canonical_body_file.read_text(encoding="utf-8")
    if not body.strip():
        raise PromotionError("canonical governed body is empty")

    result = subprocess.run(
        [
            policy_command,
            "--mode",
            "issue",
            "--body-file",
            str(canonical_body_file),
        ],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise PromotionError(
            f"canonical governed body failed field policy: {detail}"
        )
    return body


def build_provenance_comment(
    *,
    repository: str,
    intake_issue: int,
    governing_issue: int,
    governed_operation: str,
    original_body: str,
    routing_labels: tuple[str, ...],
) -> str:
    labels = ", ".join(f"`{label}`" for label in routing_labels)
    return (
        "## Intake provenance\n\n"
        f"- Intake issue: {issue_ref(repository, intake_issue)}\n"
        f"- Governed operation: {governed_operation}\n"
        f"- Governing issue: {issue_ref(repository, governing_issue)}\n"
        f"- Routing classification labels before promotion: {labels}\n"
        "- Captured before body replacement/restructuring: yes\n\n"
        "### Original unformatted issue body\n\n"
        f"{original_body}"
    )


def inspect_and_plan(
    *,
    client: GitHubClient,
    repository: str,
    intake_issue: int,
    governing_issue: int,
    governed_operation: str,
    promotion_form: str,
    canonical_body: str,
) -> tuple[dict[str, Any], dict[str, Any], tuple[str, ...], str, str]:
    require_promotion_form(promotion_form, intake_issue, governing_issue)
    if not governed_operation.strip():
        raise PromotionError("governed operation is required")

    intake = client.get_issue(intake_issue)
    governing = (
        intake
        if intake_issue == governing_issue
        else client.get_issue(governing_issue)
    )

    intake_labels = normalize_labels(intake)
    routing_labels = tuple(
        label for label in intake_labels if label in ROUTING_LABELS
    )
    if len(routing_labels) != 1:
        raise PromotionError(
            "promotion requires exactly one pre-promotion routing classification"
        )

    governing_labels = normalize_labels(governing)
    if GOVERNED_WORK in governing_labels:
        raise PromotionError(
            "target governing issue is already in governed-work state"
        )

    original_body = intake.get("body")
    if original_body is None:
        original_body = ""
    if not isinstance(original_body, str):
        raise PromotionError("intake issue body is not textual")

    body_sha = hashlib.sha256(canonical_body.encode()).hexdigest()
    provenance_comment = build_provenance_comment(
        repository=repository,
        intake_issue=intake_issue,
        governing_issue=governing_issue,
        governed_operation=governed_operation.strip(),
        original_body=original_body,
        routing_labels=routing_labels,
    )
    return intake, governing, routing_labels, provenance_comment, body_sha


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        token = os.environ.get(args.token_env, "")
        if not token:
            raise PromotionError(
                f"required GitHub token environment variable is empty: {args.token_env}"
            )

        canonical_body = validate_canonical_body(
            args.policy_command,
            args.canonical_body_file,
        )
        client = GitHubClient(args.repository, token)
        (
            intake,
            governing,
            routing_labels,
            provenance_comment,
            body_sha,
        ) = inspect_and_plan(
            client=client,
            repository=args.repository,
            intake_issue=args.intake_issue,
            governing_issue=args.governing_issue,
            governed_operation=args.governed_operation,
            promotion_form=args.promotion_form,
            canonical_body=canonical_body,
        )

        canonical_revision = hashlib.sha256(
            canonical_body.encode()
        ).hexdigest()
        previous_subject = os.environ.get(
            "REPO_SPEC_CANONICAL_VALIDATION_SUBJECT"
        )
        os.environ["REPO_SPEC_CANONICAL_VALIDATION_SUBJECT"] = str(
            args.canonical_body_file.resolve()
        )
        try:
            try:
                canonical_evidence = validate_canonical_governed_state(
                    observation=CanonicalGovernedStateObservation(
                        governing_issue=f"#{args.governing_issue}",
                        governed_operation=args.governed_operation.strip(),
                        observed_revision=canonical_revision,
                    ),
                    producer_id="repository-canonical-validator",
                )
            except ValueError as exc:
                raise PromotionError(
                    f"trusted canonical validation failed: {exc}"
                ) from exc
        finally:
            if previous_subject is None:
                os.environ.pop("REPO_SPEC_CANONICAL_VALIDATION_SUBJECT", None)
            else:
                os.environ[
                    "REPO_SPEC_CANONICAL_VALIDATION_SUBJECT"
                ] = previous_subject

        authorization = require_repository_governance_authorization(
            client=client,
            authority_issue=args.authority_issue,
            governing_issue=args.governing_issue,
            governed_operation=args.governed_operation.strip(),
            routing_labels=routing_labels,
            policy_command=args.policy_command,
            producer_id=args.authority_producer_id,
        )

        plan = {
            "repository": args.repository,
            "intake_issue": args.intake_issue,
            "governing_issue": args.governing_issue,
            "governed_operation": args.governed_operation.strip(),
            "promotion_form": args.promotion_form,
            "routing_labels": list(routing_labels),
            "canonical_body_sha256": body_sha,
            "mutation_authorized_by_routing": False,
            "repository_authorization": asdict(authorization),
            "apply_requested": args.apply,
            "ordered_operations": [
                "create intake provenance comment",
                "install canonical governing issue body",
                "verify canonical governing issue body",
                "add governed-work label last",
            ],
        }

        if not args.apply:
            print(json.dumps({"status": "plan", "plan": plan}, indent=2))
            return 0

        client.add_comment(args.intake_issue, provenance_comment)

        client.update_issue_body(args.governing_issue, canonical_body)
        observed = client.get_issue(args.governing_issue)
        if observed.get("body") != canonical_body:
            raise PromotionError(
                "canonical governing issue body verification failed after update"
            )

        observed_labels_before = normalize_labels(observed)
        if GOVERNED_WORK in observed_labels_before:
            raise PromotionError(
                "governed-work became observable before explicit final label operation"
            )

        client.add_labels(args.governing_issue, [GOVERNED_WORK])
        final_issue = client.get_issue(args.governing_issue)
        final_labels = normalize_labels(final_issue)
        if GOVERNED_WORK not in final_labels:
            raise PromotionError(
                "governed-work label verification failed after final operation"
            )
        if final_issue.get("body") != canonical_body:
            raise PromotionError(
                "canonical body changed during governed-work activation"
            )

        evidence = PromotionEvidence(
            repository=args.repository,
            intake_issue=args.intake_issue,
            governing_issue=args.governing_issue,
            governed_operation=args.governed_operation.strip(),
            promotion_form=args.promotion_form,
            routing_labels=routing_labels,
            canonical_body_sha256=body_sha,
            validation_artifact_id=(
                f"github-issue:{args.repository}#{args.governing_issue}:"
                f"sha256:{body_sha}"
            ),
            provenance_comment_created=True,
            body_installed=True,
            governed_work_added=True,
            mutation_authorized_by_routing=False,
        )
        print(
            json.dumps(
                {
                    "status": "applied",
                    "plan": plan,
                    "canonical_state_evidence": {
                        "governing_issue": canonical_evidence.governing_issue,
                        "governed_operation": canonical_evidence.governed_operation,
                        "validated_revision": canonical_evidence.validated_revision,
                        "observed_revision": canonical_evidence.observed_revision,
                        "validation_artifact_id": (
                            canonical_evidence.validation_artifact_id
                        ),
                        "producer_id": canonical_evidence.producer_id,
                    },
                    "promotion_evidence": asdict(evidence),
                },
                indent=2,
            )
        )
        return 0

    except (PromotionError, OSError, json.JSONDecodeError) as exc:
        print(f"promotion error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
