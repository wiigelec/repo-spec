from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

BUG_FIX = "bug-fix"
FEATURE_REQUEST = "feature-request"
GOVERNED_WORK = "governed-work"


class ClassificationState(str, Enum):
    UNCLASSIFIED = "unclassified"
    BUG_FIX = BUG_FIX
    FEATURE_REQUEST = FEATURE_REQUEST
    CONFLICT = "conflict"


@dataclass(frozen=True)
class ClassificationResult:
    state: ClassificationState
    routing_labels: frozenset[str]
    governed_work: bool

    @property
    def has_single_direction(self) -> bool:
        return self.state in {
            ClassificationState.BUG_FIX,
            ClassificationState.FEATURE_REQUEST,
        }


def classify_labels(labels: Iterable[str]) -> ClassificationResult:
    normalized = frozenset(str(label).strip() for label in labels if str(label).strip())
    routing = frozenset(label for label in normalized if label in {BUG_FIX, FEATURE_REQUEST})

    if not routing:
        state = ClassificationState.UNCLASSIFIED
    elif routing == {BUG_FIX}:
        state = ClassificationState.BUG_FIX
    elif routing == {FEATURE_REQUEST}:
        state = ClassificationState.FEATURE_REQUEST
    else:
        state = ClassificationState.CONFLICT

    return ClassificationResult(
        state=state,
        routing_labels=routing,
        governed_work=GOVERNED_WORK in normalized,
    )

def require_single_direction(labels: Iterable[str]) -> ClassificationState:
    result = classify_labels(labels)
    if result.state is ClassificationState.CONFLICT:
        raise ValueError(
            "unresolved routing classification conflict: both bug-fix and feature-request are present"
        )
    return result.state
