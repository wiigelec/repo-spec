from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .classification import ClassificationState, classify_labels


class AuthorityPath(str, Enum):
    AUDIT = "audit"
    FEATURE_DEVELOPMENT = "feature-development"
    NO_PATH = "no-path"


@dataclass(frozen=True)
class AuthorityRoutingResult:
    path: AuthorityPath
    classification_state: ClassificationState
    mutation_authorized: bool = False

    @property
    def has_unique_path(self) -> bool:
        return self.path in {AuthorityPath.AUDIT, AuthorityPath.FEATURE_DEVELOPMENT}


FEATURE_DEVELOPMENT_STAGES = (
    "whiteboard",
    "analysis",
    "candidate-functional-set",
    "explicit-functional-set-approval",
)


class AuditDisposition(str, Enum):
    ACCEPTED_AUTHORITY_VIOLATION = "accepted-authority-violation"
    MISSING_OR_UNACCEPTED_BEHAVIOR = "missing-or-unaccepted-behavior"


def route_labels(labels: Iterable[str]) -> AuthorityRoutingResult:
    classification = classify_labels(labels)
    if classification.state is ClassificationState.BUG_FIX:
        path = AuthorityPath.AUDIT
    elif classification.state is ClassificationState.FEATURE_REQUEST:
        path = AuthorityPath.FEATURE_DEVELOPMENT
    else:
        path = AuthorityPath.NO_PATH
    return AuthorityRoutingResult(
        path=path,
        classification_state=classification.state,
        mutation_authorized=False,
    )

def require_unique_authority_path(labels: Iterable[str]) -> AuthorityPath:
    result = route_labels(labels)
    if not result.has_unique_path:
        raise ValueError(
            f"no unique authority path for classification state: {result.classification_state.value}"
        )
    return result.path



def route_audited_bug(disposition: AuditDisposition) -> AuthorityPath:
    if disposition is AuditDisposition.ACCEPTED_AUTHORITY_VIOLATION:
        return AuthorityPath.AUDIT
    if disposition is AuditDisposition.MISSING_OR_UNACCEPTED_BEHAVIOR:
        return AuthorityPath.FEATURE_DEVELOPMENT
    raise ValueError(f"unsupported audit disposition: {disposition!r}")
