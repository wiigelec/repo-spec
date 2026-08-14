from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
from typing import Iterable


_CLASSIFICATION_PATH = Path(__file__).with_name("issue_routing_classification.py")
_SPEC = spec_from_file_location("issue_routing_classification", _CLASSIFICATION_PATH)
_CLASSIFICATION = module_from_spec(_SPEC)
assert _SPEC.loader is not None
sys.modules[_SPEC.name] = _CLASSIFICATION
_SPEC.loader.exec_module(_CLASSIFICATION)


class AuthorityPath(str, Enum):
    AUDIT = "audit"
    FEATURE_DEVELOPMENT = "feature-development"
    NO_PATH = "no-path"


@dataclass(frozen=True)
class AuthorityRoutingResult:
    path: AuthorityPath
    classification_state: str
    mutation_authorized: bool = False

    @property
    def has_unique_path(self) -> bool:
        return self.path in {AuthorityPath.AUDIT, AuthorityPath.FEATURE_DEVELOPMENT}


def route_labels(labels: Iterable[str]) -> AuthorityRoutingResult:
    classification = _CLASSIFICATION.classify_labels(labels)

    if classification.state is _CLASSIFICATION.ClassificationState.BUG_FIX:
        path = AuthorityPath.AUDIT
    elif classification.state is _CLASSIFICATION.ClassificationState.FEATURE_REQUEST:
        path = AuthorityPath.FEATURE_DEVELOPMENT
    else:
        path = AuthorityPath.NO_PATH

    return AuthorityRoutingResult(
        path=path,
        classification_state=classification.state.value,
        mutation_authorized=False,
    )


def require_unique_authority_path(labels: Iterable[str]) -> AuthorityPath:
    result = route_labels(labels)
    if not result.has_unique_path:
        raise ValueError(
            f"no unique authority path for classification state: {result.classification_state}"
        )
    return result.path


FEATURE_DEVELOPMENT_STAGES = (
    "whiteboard",
    "analysis",
    "candidate-functional-set",
    "explicit-functional-set-approval",
)
