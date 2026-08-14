from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import importlib.util
import sys


_POLICY_PATH = Path(__file__).with_name("github_field_policy.py")
_POLICY_SPEC = importlib.util.spec_from_file_location("github_field_policy", _POLICY_PATH)
_POLICY = importlib.util.module_from_spec(_POLICY_SPEC)
assert _POLICY_SPEC.loader is not None
sys.modules[_POLICY_SPEC.name] = _POLICY
_POLICY_SPEC.loader.exec_module(_POLICY)


class PromotionForm(str, Enum):
    IN_PLACE = "in-place"
    SUCCESSOR = "successor"


@dataclass(frozen=True)
class PromotionPlan:
    form: PromotionForm
    intake_issue: str
    governing_issue: str
    governed_body: str
    provenance_captured: bool
    branch_bypass_authorized: bool = False
    validation_bypass_authorized: bool = False
    review_bypass_authorized: bool = False
    acceptance_bypass_authorized: bool = False
    merge_bypass_authorized: bool = False

    @property
    def destructive_restructure_allowed(self) -> bool:
        return self.provenance_captured

    @property
    def unique_governing_issue(self) -> bool:
        return bool(self.governing_issue.strip())


def _validate_canonical_governed_body(governed_body: str, repo_root: Path) -> None:
    sections = _POLICY.parse_sections(governed_body)

    fields = _POLICY.load_fields(
        repo_root,
        "repo/specs/repo/governing-issue.json",
        "issue_fields",
    )

    for field in fields:
        value = _POLICY.require_section(sections, field["label"])
        _POLICY.validate_field_value(field, value)

    _POLICY.require_product_artifact_evidence(sections, repo_root, fields)


def plan_promotion(
    *,
    form: PromotionForm,
    intake_issue: str,
    governing_issue: str,
    governed_body: str,
    provenance_captured: bool,
    repo_root: Path,
) -> PromotionPlan:
    if not intake_issue.strip():
        raise ValueError("intake_issue is required")
    if not governing_issue.strip():
        raise ValueError("governing_issue is required")
    if not provenance_captured:
        raise ValueError("required intake provenance must be captured before promotion")

    _validate_canonical_governed_body(governed_body, repo_root)

    if form is PromotionForm.IN_PLACE and intake_issue.strip() != governing_issue.strip():
        raise ValueError("in-place promotion requires intake_issue to equal governing_issue")
    if form is PromotionForm.SUCCESSOR and intake_issue.strip() == governing_issue.strip():
        raise ValueError("successor promotion requires a distinct governing_issue")

    return PromotionPlan(
        form=form,
        intake_issue=intake_issue.strip(),
        governing_issue=governing_issue.strip(),
        governed_body=governed_body,
        provenance_captured=True,
    )
