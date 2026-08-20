from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class HostedValidationDecision:
    governed_work_state: bool
    canonical_governed_state: bool
    repository_authority_conflict: bool
    validation_active: bool


def activate_hosted_validation(
    *,
    governed_work_state: bool,
    canonical_governed_state: bool,
    repository_authority_conflict: bool = False,
) -> HostedValidationDecision:
    if repository_authority_conflict:
        raise ValueError("hosting state conflicts with repository authority")
    if governed_work_state and not canonical_governed_state:
        raise ValueError(
            "governed-work hosting state cannot precede canonical governed repository state"
        )

    return HostedValidationDecision(
        governed_work_state=governed_work_state,
        canonical_governed_state=canonical_governed_state,
        repository_authority_conflict=False,
        validation_active=governed_work_state and canonical_governed_state,
    )
